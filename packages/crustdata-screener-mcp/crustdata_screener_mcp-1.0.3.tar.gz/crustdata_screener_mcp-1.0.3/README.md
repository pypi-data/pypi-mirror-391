# CrustData Screener MCP Server

Connect Claude Desktop to CrustData's B2B data platform. Search companies, enrich data, and find decision makers directly from Claude.

## Installation

```bash
pip install crustdata-screener-mcp
```

## Setup

### 1. Get your CrustData API token
- Sign up at [crustdata.com](https://crustdata.com)
- Get your API token from your dashboard

### 2. Configure Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crustdata": {
      "command": "crustdata-mcp",
      "env": {
        "CRUSTDATA_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

That's it! The CrustData tools are now available in Claude.

## For Claude CLI Users

If you're using Claude CLI instead of Claude Desktop:

```bash
claude mcp add crustdata "crustdata-mcp" \
  -e "CRUSTDATA_API_TOKEN=your_api_token_here"

# Verify connection
claude mcp list
```

## Usage Examples

Ask Claude:
- "Search for AI companies with 50-200 employees"
- "Get information about Stripe including funding and headcount"
- "Find the LinkedIn profile of John Doe at Apple"
- "Search for recent LinkedIn posts about product launches"

## Available Tools

- **Company Search & Enrichment**
  - `search_companies` - Search with filters
  - `enrich_company_data` - Get detailed company info
  - `identify_company` - Find companies by name/domain

- **People Search & Enrichment**  
  - `search_people` - Find people by title, company, location
  - `enrich_person_profile` - Get detailed person info

- **LinkedIn Data**
  - `get_linkedin_posts` - Retrieve LinkedIn posts
  - `search_linkedin_posts_by_keyword` - Search posts by keywords

## Environment Variables

- `CRUSTDATA_API_TOKEN` (required) - Your CrustData API token
- `CRUSTDATA_API_BASE_URL` (optional) - API base URL (defaults to production)

## Support

- Documentation: [docs.crustdata.com](https://docs.crustdata.com)
- Issues: [github.com/crustdata/mcp-server/issues](https://github.com/crustdata/mcp-server/issues)
- Email: support@crustdata.com

## License

MIT