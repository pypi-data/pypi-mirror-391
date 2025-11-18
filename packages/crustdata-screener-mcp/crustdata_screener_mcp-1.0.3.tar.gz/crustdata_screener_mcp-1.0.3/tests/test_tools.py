#!/usr/bin/env python3
"""
Test script for CrustData MCP tools.

Usage:
    python tests/test_tools.py enrich_company_data --company_domain stripe.com
    python tests/test_tools.py search_people --filters '{"job_title": "CEO"}'
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import CrustDataMCPServer


async def test_tool(server: CrustDataMCPServer, tool_name: str, **kwargs):
    """Test a specific tool with given arguments."""
    print(f"\n{'='*60}")
    print(f"Testing tool: {tool_name}")
    print(f"Arguments: {json.dumps(kwargs, indent=2)}")
    print(f"{'='*60}\n")
    
    # Find tool config
    tool_config = None
    for tool in server.config["tools"]:
        if tool["name"] == tool_name:
            tool_config = tool
            break
    
    if not tool_config:
        print(f"❌ Tool '{tool_name}' not found")
        return
    
    try:
        # Call the API
        result = await server._call_api(tool_config, kwargs)
        
        # Pretty print result
        print("✅ Success!")
        print(f"\nResponse:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test CrustData MCP tools")
    parser.add_argument("tool", help="Tool name to test")
    # Company enrichment params
    parser.add_argument("--company_domain", help="Company domain(s)")
    parser.add_argument("--company_name", help="Company name(s)")
    parser.add_argument("--company_id", help="Company ID(s)")
    parser.add_argument("--company_linkedin_url", help="Company LinkedIn URL")
    # Identify company params (POST method)
    parser.add_argument("--query_company_website", help="Company website for identification")
    parser.add_argument("--query_company_name", help="Company name for identification")
    parser.add_argument("--query_company_linkedin_url", help="LinkedIn URL for identification")
    parser.add_argument("--query_company_id", type=int, help="Company ID for identification")
    parser.add_argument("--count", type=int, help="Number of results")
    # Person params
    parser.add_argument("--person_linkedin_url", help="Person LinkedIn URL")
    parser.add_argument("--person_email", help="Person email")
    # Other params
    parser.add_argument("--fields", help="Fields to return")
    parser.add_argument("--filters", help="JSON filters")
    parser.add_argument("--keywords", help="Keywords for search")
    parser.add_argument("--limit", type=int, help="Limit results")
    parser.add_argument("--offset", type=int, help="Offset for pagination")
    parser.add_argument("--exact_match", action="store_true", help="Exact match")
    parser.add_argument("--enrich_realtime", action="store_true", help="Enrich realtime")
    
    args = parser.parse_args()
    
    # Check environment
    if not os.environ.get("CRUSTDATA_API_TOKEN"):
        print("❌ Error: CRUSTDATA_API_TOKEN environment variable is required")
        print("Set it with: export CRUSTDATA_API_TOKEN=your_token_here")
        sys.exit(1)
    
    # Load config
    config_path = os.path.join(
        os.path.dirname(__file__),
        "../config/api_endpoints.yaml"
    )
    
    # Create server instance
    server = CrustDataMCPServer(config_path)
    
    # Build kwargs from args
    kwargs = {}
    for key, value in vars(args).items():
        if key != "tool" and value is not None:
            kwargs[key] = value
    
    # Run test
    try:
        await test_tool(server, args.tool, **kwargs)
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
