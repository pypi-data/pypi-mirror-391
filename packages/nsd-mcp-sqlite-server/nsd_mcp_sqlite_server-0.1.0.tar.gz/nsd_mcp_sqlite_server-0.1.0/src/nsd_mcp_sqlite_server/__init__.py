from nsd_mcp_sqlite_server import mcp

def main():
    print("Hello from nsd-mcp-sqlite-server!")
    mcp.run(transport="stdio")
