import json


def json_response(connection, code, data):
    body = json.dumps(data).encode("utf-8")

    connection.send_response(code)
    connection.send_header("Content-Type", "application/json")
    connection.send_header("Content-Length", str(len(body)))
    connection.end_headers()
    connection.wfile.write(body)
