from . import mcp_sqlite_server_d

def main() -> None:
    print("Hello from mcp-sqlite-server-d!")
    obj = mcp_sqlite_server_d
    obj.run_mcp()
