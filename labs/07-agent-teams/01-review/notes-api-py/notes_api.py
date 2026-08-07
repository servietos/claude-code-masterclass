import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import config
import store


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)

        if url.path == "/notes":
            self._send(200, {"notes": store.list_notes()})
            return

        if url.path.startswith("/notes/"):
            name = url.path[len("/notes/"):]
            self._send(200, {"name": name, "body": store.read_note(name)})
            return

        if url.path == "/search":
            term = query.get("q", [""])[0]
            self._send(200, {"term": term, "hits": store.search(term)})
            return

        self._send(404, {"error": "not found"})

    def do_POST(self):
        url = urlparse(self.path)
        token = self.headers.get("X-Api-Token", "")
        if token != config.API_TOKEN:
            self._send(401, {"error": "bad token"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length))
        written = store.write_note(payload["name"], payload["body"])
        self._send(201, {"name": payload["name"], "bytes": written})


def main():
    server = HTTPServer(("127.0.0.1", config.PORT), Handler)
    print(f"notes-api listening on http://127.0.0.1:{config.PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
