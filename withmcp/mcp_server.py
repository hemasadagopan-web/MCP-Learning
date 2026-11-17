"""MCP server exposing database operations from db_tools.py.""" 
import sys
print("MCP server process started", file=sys.stderr)

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("details-database")

from db_tools import read_details, insert_details, update_details, delete_details

mcp = FastMCP("details-database")


@mcp.tool(name="insert_details")
def insert_details_tool(name: str, gender: str, country: str):
    """Insert a new record into the details table."""
    return insert_details(name, gender, country)


@mcp.tool(name="read_details")
def read_details_tool():
    """Read all records from the details table."""
    return read_details()


@mcp.tool(name="update_details")
def update_details_tool(old_name: str, name: str, gender: str, country: str):
    """Update an existing record using the old name."""
    return update_details(old_name, name, gender, country)


@mcp.tool(name="delete_details")
def delete_details_tool(name: str):
    """Delete a record using its name."""
    return delete_details(name)


if __name__ == "__main__":
    import sys
    print("Starting MCP server...", file=sys.stderr)
    mcp.run(transport="stdio")
