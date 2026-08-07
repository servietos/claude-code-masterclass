#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp>=1.26.0",
#     "uvicorn>=0.34.0",
#     "starlette>=0.46.0",
# ]
# ///
"""
UUID MCP Server - Mints UUIDs on request
Compatible with MCP clients via stdio transport
"""
import os
import sys
import uuid
import logging

import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)

VIEW_URI = "ui://uuid-server/view.html"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "3002"))

mcp = FastMCP("UUID Server", stateless_http=True)

EMBEDDED_VIEW_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta name="color-scheme" content="light dark">
  <style>
    html, body { margin: 0; padding: 16px; font-family: system-ui, sans-serif; }
    code { font-size: 16px; }
  </style>
</head>
<body>
  <div id="uuids"></div>
  <script type="module">
    import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

    const app = new App({ name: "UUID View", version: "1.0.0" });

    app.ontoolresult = ({ content }) => {
      const text = content?.find(c => c.type === 'text');
      const target = document.getElementById('uuids');
      target.innerHTML = '';
      if (text) {
        const pre = document.createElement('pre');
        pre.appendChild(document.createTextNode(text.text));
        target.appendChild(pre);
      }
    };

    await app.connect();
  </script>
</body>
</html>"""


@mcp.tool(meta={
    "ui": {"resourceUri": VIEW_URI},
    "ui/resourceUri": VIEW_URI,
})
def mint_uuid(count: int = 1, version: int = 4, uppercase: bool = False) -> str:
    """Mint one or more UUIDs.

    Args:
        count: How many UUIDs to mint (default: 1, range: 1-100)
        version: UUID version, 1 or 4 (default: 4)
        uppercase: Return the UUIDs in uppercase (default: false)

    Returns:
        The minted UUIDs, one per line
    """
    count = max(1, min(count, 100))
    factory = uuid.uuid1 if version == 1 else uuid.uuid4
    values = [str(factory()) for _ in range(count)]
    if uppercase:
        values = [v.upper() for v in values]
    return "\n".join(values)


@mcp.resource(
    VIEW_URI,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com"]}}},
)
def view() -> str:
    """View HTML resource with CSP metadata for external dependencies."""
    return EMBEDDED_VIEW_HTML


if __name__ == "__main__":
    use_stdio = "--stdio" in sys.argv

    if use_stdio:
        mcp.run(transport="stdio")
    else:
        app = mcp.streamable_http_app()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        print(f"UUID Server listening on http://{HOST}:{PORT}/mcp")
        uvicorn.run(app, host=HOST, port=PORT)
