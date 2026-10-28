from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class ServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/payload"):
            data = self.downloadJson()
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            print("Payload here")
        else:
            self.send_response(200)
            self.end_headers()
            print("GET for server")

    def downloadJson(self):
        with open("payload.json", "r") as file:
            data = json.load(file)
        return data
class Server:

    def __init__(self, origin):
        self.origin = origin
        self.port = 3002

    def run(self, server_class=HTTPServer, handler_class=ServerRequestHandler):
        server_address = (self.origin, self.port)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()
