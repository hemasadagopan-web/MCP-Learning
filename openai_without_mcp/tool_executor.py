
from db_tools import (
    read_details,
    insert_details,
    update_details,
    delete_details
)

def execute_tool(name, args):

    if name == "read_details":
        return read_details()

    if name == "insert_details":
        return insert_details(
            args["name"],
            args["gender"],
            args["country"]
        )

    if name == "update_details":
        return update_details(
            args["old_name"],
            args["name"],
            args["gender"],
            args["country"]
        )

    if name == "delete_details":
        return delete_details(args["name"])

    return {"error": "Unknown tool"}

