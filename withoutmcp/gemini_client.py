
from google import genai
from tool_executor import execute_tool

client = genai.Client(api_key="AQ.Ab8RN6KCQdRA4X7lK7QV-9zDTy9uNVTTrDvsaN0VccmgX9WEQg")

tools = [{
    "function_declarations": [

        # INSERT
        {
            "name": "insert_details",
            "description": "Insert a new record into the details table",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "gender": {"type": "string"},
                    "country": {"type": "string"}
                },
                "required": ["name", "gender", "country"]
            }
        },

        # READ
        {
            "name": "read_details",
            "description": "Read all records from the details table",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },

        # UPDATE
        {
            "name": "update_details",
            "description": "Update an existing record using the old name",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_name": {"type": "string"},
                    "name": {"type": "string"},
                    "gender": {"type": "string"},
                    "country": {"type": "string"}
                },
                "required": [
                    "old_name", "name", "gender", "country"
                ]
            }
        },

        # DELETE
        {
            "name": "delete_details",
            "description": "Delete a record using its name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            }
        }
    ]
}]


def chat(prompt):

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "tools": tools
        }
    )

    candidate = response.candidates[0]

    for part in candidate.content.parts:

        if part.function_call:
            name = part.function_call.name
            args = dict(part.function_call.args)

            result = execute_tool(name, args)

            print("Tool:", name)
            print("Arguments:", args)
            print("Result:", result)

        elif part.text:
            print(part.text)


chat("Insert a new person named John, gender Male, country USA")
