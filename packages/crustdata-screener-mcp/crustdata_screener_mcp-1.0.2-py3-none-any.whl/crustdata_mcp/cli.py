#!/usr/bin/env python3
"""CLI entry point for CrustData MCP Server."""

import sys
import os
import asyncio

def main():
    """Main entry point for the CLI command."""
    # Add src directory to path so we can import server
    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if os.path.exists(src_dir):
        sys.path.insert(0, src_dir)
    else:
        # For installed package, look for src in site-packages
        import site
        for site_dir in site.getsitepackages():
            potential_src = os.path.join(site_dir, 'src')
            if os.path.exists(potential_src):
                sys.path.insert(0, potential_src)
                break
    
    try:
        from server import main as server_main
        asyncio.run(server_main())
    except ImportError as e:
        print(f"Error: Could not import server module: {e}", file=sys.stderr)
        print(f"Python path: {sys.path}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down MCP server...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()