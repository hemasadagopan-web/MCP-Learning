
import json
import anthropic
from tool_executor import execute_tool

client = anthropic.Anthropic()

tools = [
    {
        "name": "insert_details",
        "description": "Insert a new record into the details table",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "gender": {"type": "string"},
                "country": {"type": "string"}
            },
            "required": ["name", "gender", "country"]
        }
    },
    {
        "name": "read_details",
        "description": "Read all records from the details table",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_details",
        "description": "Update an existing record using the old name",
        "input_schema": {
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
    {
        "name": "delete_details",
        "description": "Delete a record using its name",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
    }
]


def chat(prompt):

    messages = [
        {"role": "user", "content": prompt}
    ]

    while True:

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=messages,
            tools=tools
        )

        # Check whether Claude wants to use a tool
        tool_calls = [
            block for block in response.content
            if block.type == "tool_use"
        ]

        if not tool_calls:
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        # Preserve Claude's assistant response
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        tool_results = []

        for tool in tool_calls:

            name = tool.name
            args = tool.input

            result = execute_tool(name, args)

            print("Tool:", name)
            print("Arguments:", args)
            print("Result:", result)

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": json.dumps(result, default=str)
            })

        # Send the database results back to Claude
        messages.append({
            "role": "user",
            "content": tool_results
        })


chat("Insert a new person named Pradheep, gender Male, country Sweden")

chat("Select all names from the table")
