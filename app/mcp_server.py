from fastmcp import FastMCP

server = FastMCP(
    name="sql-intent",
)

@server.tool()
def sql_intent(query_text: str, env: str = "DEV") -> dict:
    """Executes a stored SQL template based on natural language query and environment."""
    from app.main import handle_query
    payload = {"query_text": query_text, "env": env}
    response = handle_query(payload)
    return response
