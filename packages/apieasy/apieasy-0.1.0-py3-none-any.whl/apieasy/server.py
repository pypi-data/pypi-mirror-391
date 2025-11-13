from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from .router import router
from .http_utils import json_response
import json


class APIHandler(BaseHTTPRequestHandler):
    def _handle(self):
        handler = router.resolve(self.command, self.path)

        if handler is None:
            json_response(self, 404, {"error": "Route not found"})
            return

        # Parse JSON body for POST requests
        data = None
        if self.command == "POST":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            if raw:
                data = json.loads(raw.decode("utf-8"))

        try:
            if data is not None:
                result = handler(data)
            else:
                result = handler()

            json_response(self, 200, result)
        except Exception as e:
            json_response(self, 500, {"error": str(e)})

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()


def run(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), APIHandler)
    print(f"apieasy running on http://{host}:{port}")
    server.serve_forever()
