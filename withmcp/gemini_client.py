
"""
Gemini Client with MCP Server Integration

Architecture:
    User
      |
      v
    Gemini Client
      |
      v
    MCP Server
      |
      v
    db_tools.py
      |
      v
    Database

How it works:
1. User enters a natural-language request.
2. Gemini understands the request and decides which tool to use.
3. Gemini sends a function call to the client.
4. The client forwards the function call to the MCP server.
5. MCP server executes the corresponding database function.
6. The database result is returned to Gemini.
7. Gemini generates a human-readable response.

Required packages:
    pip install google-genai "mcp>=1.20,<2"

Project files:
    db_tools.py
    mcp_server.py
    gemini_client.py
"""

# asyncio is used to execute asynchronous operations.# This is important because communication with Gemini and MCP# involves waiting for network and process responses.
import asyncio

# json is used to check whether tool results can be converted # into JSON format before sending them back to Gemini.
import json

# sys provides access to the current Python interpreter.# We use it to launch the MCP server with the same Python environment.
import sys

# traceback helps display detailed error information# when something goes wrong during execution.
import traceback

# Path helps locate mcp_server.py relative to this file.
from pathlib import Path

# Import Google's Gemini SDK.
from google import genai
from google.genai import types

# Import MCP client components. # ClientSession manages communication with the MCP server.# StdioServerParameters defines how the MCP server is started.
from mcp import ClientSession, StdioServerParameters

# stdio_client establishes communication with the MCP server # using standard input and standard output (STDIO).
from mcp.client.stdio import stdio_client


# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------

# Gemini API key used to authenticate requests to Google's API.# Replace the placeholder with your key or preferably load it
# from an environment variable.
GEMINI_API_KEY = "GEMINI_API_KEY"

# Gemini model used to understand user requests and decide # which database operation or MCP tool should be called.
MODEL = "gemini-3.5-flash-lite"


# -------------------------------------------------
# INITIALIZE GEMINI CLIENT
# -------------------------------------------------

# Create the Gemini client using the API key.
# This client is used to send prompts and receive responses
# from the Gemini model.
client = genai.Client(
    api_key=GEMINI_API_KEY
)


# -------------------------------------------------
# CONVERT MCP TOOLS INTO GEMINI TOOLS
# -------------------------------------------------

def convert_mcp_tools(mcp_tools):

    # This list will contain Gemini-compatible function declarations.
    function_declarations = []

    # Loop through all tools discovered from the MCP server.
    for tool in mcp_tools:

        # Each MCP tool provides an input schema describing        # the parameters it expects.        # Convert the schema into a normal Python dictionary.
        schema = dict(tool.inputSchema or {})

        # Remove JSON Schema metadata fields that are not        # required when passing the schema to Gemini.
        schema.pop("$schema", None)
        schema.pop("$id", None)

        # Convert the MCP tool definition into a Gemini
        # function declaration.
        #
        # name        = MCP tool name
        # description = What the tool does
        # parameters  = Input parameters required by the tool
        function_declarations.append(
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or "",
                parameters_json_schema=schema
            )
        )

    # Return the converted declarations inside a Gemini Tool object.
    # Gemini uses these declarations to decide which function to call.
    return [
        types.Tool(
            function_declarations=function_declarations
        )
    ]


# -------------------------------------------------
# CONVERT TOOL RESULTS INTO JSON
# -------------------------------------------------

def json_safe(value):

    # MCP tool results may contain Python objects that cannot
    # be directly converted into JSON.
    # Gemini function responses should contain JSON-compatible data.
    try:
        json.dumps(value)

        # If conversion succeeds, return the original value.
        return value

    except (TypeError, ValueError):

        # If conversion fails, convert the value into a string
        # so it can still be passed back to Gemini.
        return str(value)


# -------------------------------------------------
# CHAT FUNCTION
# -------------------------------------------------

async def chat(prompt):

    # Locate mcp_server.py in the same directory as this file.
    # This avoids hardcoding the full file path.
    server_script = Path(__file__).with_name(
        "mcp_server.py"
    )

    # Check whether the MCP server script exists.
    # Stop execution with a clear error if it cannot be found.
    if not server_script.exists():
        raise FileNotFoundError(
            f"MCP server not found: {server_script}"
        )

    # Configure how the MCP server should be started.
    #
    # command = Current Python interpreter
    # args    = Path to the MCP server script
    #
    # Using sys.executable ensures that the MCP server
    # uses the same Python environment as this client.
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_script)]
    )

    # Start the MCP server as a separate process and establish
    # communication using STDIO.
    #
    # read_stream  = Receives responses from the MCP server.
    # write_stream = Sends requests to the MCP server.
    async with stdio_client(server_params) as (
        read_stream,
        write_stream
    ):

        # Create an MCP client session using the communication streams.
        # The session manages requests and responses between
        # the Gemini client and the MCP server.
        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            # Initialize the MCP session.
            # This completes the initial handshake between
            # the client and the MCP server.
            await session.initialize()

            print("\nConnected to MCP Server")

            # Ask the MCP server to provide its available tools.
            # For example:
            # insert_details, read_details,
            # update_details and delete_details.
            mcp_response = await session.list_tools()

            print("\nAvailable MCP Tools:")

            # Display all tools exposed by the MCP server.
            for tool in mcp_response.tools:
                print("-", tool.name)

            # Convert the discovered MCP tools into Gemini-compatible
            # function declarations.
            # This allows Gemini to understand which operations
            # are available and what parameters they require.
            gemini_tools = convert_mcp_tools(
                mcp_response.tools
            )

            # Prepare the initial user prompt in Gemini's
            # expected conversation format.
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=prompt)
                    ]
                )
            ]

            # -------------------------------------------------
            # GEMINI AND MCP TOOL INTERACTION LOOP
            # -------------------------------------------------

            # Allow up to 10 rounds of interaction.
            # A round may involve Gemini requesting a tool,
            # receiving the result, and deciding what to do next.
            for _ in range(10):

                # Send the current conversation to Gemini.
                #
                # The available MCP tools are provided so Gemini
                # can decide whether it needs to call a tool
                # to fulfil the user's request.
                response = await client.aio.models.generate_content(
                    model=MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools
                    )
                )

                # Check whether Gemini returned any candidates.
                # If not, stop because there is no response to process.
                if not response.candidates:
                    print("No response from Gemini")
                    return

                # Get the content generated by Gemini.
                model_content = response.candidates[0].content

                # Add Gemini's response to the conversation history.
                # This is important because subsequent requests
                # need the previous conversation context.
                contents.append(model_content)

                # -------------------------------------------------
                # IDENTIFY GEMINI FUNCTION CALLS
                # -------------------------------------------------

                # Check whether Gemini has requested any function calls.
                # For example, it may decide to call read_details
                # when the user asks to retrieve database records.
                function_calls = [
                    part.function_call
                    for part in (model_content.parts or [])
                    if part.function_call
                ]

                # If Gemini has not requested any tool calls,
                # it means it has generated a normal text response.
                # Display that response and finish this interaction.
                if not function_calls:

                    for part in (model_content.parts or []):

                        if part.text:
                            print("\nGemini:", part.text)

                    return

                # This list will hold the results returned by
                # the MCP tools.
                # These results will be sent back to Gemini.
                function_response_parts = []

                # -------------------------------------------------
                # EXECUTE MCP TOOLS
                # -------------------------------------------------

                # Process each function call requested by Gemini.
                for function_call in function_calls:

                    # Get the name of the MCP tool Gemini wants to call.
                    # Example: read_details.
                    tool_name = function_call.name

                    # Extract the arguments provided by Gemini.
                    # Example: table name, record ID or other parameters.
                    arguments = dict(
                        function_call.args or {}
                    )

                    # Display the requested tool and its arguments.
                    print("\nCalling MCP Tool:", tool_name)
                    print("Arguments:", arguments)

                    try:

                        # Send the tool request to the MCP server.
                        #
                        # The MCP server receives the tool name
                        # and arguments, then executes the corresponding
                        # function from db_tools.py.
                        result = await session.call_tool(
                            tool_name,
                            arguments
                        )

                        # Check whether the MCP server reported
                        # an error while executing the tool.
                        if result.isError:

                            # Prepare the error details to send
                            # back to Gemini.
                            tool_result = {
                                "error": True,
                                "content": [
                                    getattr(item, "text", str(item))
                                    for item in (result.content or [])
                                ]
                            }

                        # If the MCP server returned structured data,
                        # use that data directly.
                        elif result.structuredContent is not None:

                            tool_result = json_safe(
                                result.structuredContent
                            )

                        else:

                            # Otherwise, extract the text content
                            # from the MCP tool response.
                            tool_result = [
                                getattr(item, "text", str(item))
                                for item in (result.content or [])
                            ]

                    except Exception as error:

                        # Catch unexpected errors during tool execution.
                        # Store the error so Gemini can receive it
                        # and potentially explain the problem.
                        tool_result = {
                            "error": str(error)
                        }

                    # Display the result returned by the MCP server.
                    print("MCP Result:", tool_result)

                    # Convert the MCP result into a Gemini
                    # function-response message.
                    #
                    # This tells Gemini what happened when
                    # the requested tool was executed.
                    function_response_parts.append(
                        types.Part.from_function_response(
                            name=tool_name,
                            response={
                                "result": json_safe(tool_result)
                            }
                        )
                    )

                # -------------------------------------------------
                # SEND MCP RESULTS BACK TO GEMINI
                # -------------------------------------------------

                # Add the MCP tool results to the conversation.
                #
                # Gemini can now understand the database response
                # and generate a natural-language answer for the user.
                #
                # Gemini may also request another tool call if needed.
                contents.append(
                    types.Content(
                        role="user",
                        parts=function_response_parts
                    )
                )

            # If Gemini continues requesting tools beyond
            # the allowed 10 interaction rounds, stop execution.
            print("\nMaximum tool interaction limit reached.")


# -------------------------------------------------
# MAIN PROGRAM
# -------------------------------------------------

async def main():

    # Check whether the API key is still the placeholder.
    # If so, stop and ask the user to configure a valid key.
    if GEMINI_API_KEY == "GEMINI_API_KEY":
        raise RuntimeError(
            "Please enter your Gemini API key "
            "in the GEMINI_API_KEY variable."
        )

    # Display the application title.
    print("===================================")
    print("   GEMINI + MCP DATABASE CLIENT")
    print("===================================")

    # Keep the application running so the user can
    # submit multiple requests without restarting the program.
    while True:

        # Read a natural-language request from the user.
        prompt = input(
            "\nEnter your request (type exit to quit): "
        )

        # Allow the user to exit the application.
        if prompt.lower().strip() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Ignore empty prompts and ask for another request.
        if not prompt.strip():
            continue

        try:

            # Send the user's request to the chat function.
            # The chat function handles Gemini and MCP communication.
            await chat(prompt)

        except Exception as e:

            # If an unexpected error occurs, display the full
            # traceback to help identify where the problem happened.
            print("\nFull error details:")
            traceback.print_exception(type(e), e, e.__traceback__)


# -------------------------------------------------
# START APPLICATION
# -------------------------------------------------

# This condition ensures that main() runs only when
# gemini_client.py is executed directly.
#
# asyncio.run() starts and manages the asynchronous event loop
# required by the Gemini and MCP client operations.
if __name__ == "__main__":
    asyncio.run(main())
