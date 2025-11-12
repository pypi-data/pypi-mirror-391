from . import server
import argparse
def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description='Feishu Project MCP Server')
    parser.add_argument('--transport', type=str, default='stdio', help='Transport type')
    args = parser.parse_args()
    server.mcp.run(args.transport)