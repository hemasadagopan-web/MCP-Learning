
import json
from openai import OpenAI
from tool_executor import execute_tool

client = OpenAI()

tools = [
    {
        "type": "function",
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
    {
        "type": "function",
        "name": "read_details",
        "description": "Read all records from the details table",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
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
    {
        "type": "function",
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


def chat(prompt):

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        tools=tools
    )

    while True:

        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            print(response.output_text)
            break

        # Preserve the model's response, including its tool calls
        inputs = list(response.output)

        for call in function_calls:

            name = call.name
            args = json.loads(call.arguments)

            result = execute_tool(name, args)

            print("Tool:", name)
            print("Arguments:", args)
            print("Result:", result)

            inputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result, default=str)
            })

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=inputs,
            tools=tools
        )


chat("Insert a new person named Pradheep, gender Male, country Sweden")

chat("Select all names from the table")
