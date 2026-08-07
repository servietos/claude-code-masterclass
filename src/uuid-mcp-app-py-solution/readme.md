# UUID MCP Server

Mint UUIDs on demand from any MCP client.

## Setup

Install dependencies:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
# or with uv: uv run server.py --stdio
```

## Run

```bash
.venv/Scripts/python.exe server.py --stdio
```

Omit `--stdio` to serve the streamable HTTP transport on `http://0.0.0.0:3002/mcp` (override with the `HOST` and `PORT` environment variables).

## Parameters

- `count` - How many UUIDs to mint (default: 1, range: 1-100)
- `version` - UUID version, 1 or 4 (default: 4)
- `uppercase` - Return uppercase UUIDs (default: false)
