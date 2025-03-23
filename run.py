#!/usr/bin/env python3
import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Healthcare MCP Server")
    parser.add_argument("--http", action="store_true", help="Run in HTTP mode")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")), help="Port for HTTP server")
    args = parser.parse_args()

    if args.http:
        # Run in HTTP mode (for web clients)
        from src.server import app
        import uvicorn

        print(f"Starting HTTP server on port {args.port}...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        # Run in stdio mode (for Cline)
        from src.main import mcp

        print("Starting MCP server in stdio mode...")
        sys.exit(mcp.run())
