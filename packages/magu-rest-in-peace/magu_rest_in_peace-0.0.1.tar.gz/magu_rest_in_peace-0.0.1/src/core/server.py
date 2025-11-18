from http.server import HTTPServer
from services.handler import Handler
from core.router import Router
import properties as properties

class ServerHandler(Handler):
    router = Router()

    def do_GET(self):
        self.router.get(self)
        

def run_server():
    httpd = HTTPServer((properties.SERVER_HOST, properties.SERVER_PORT), ServerHandler)
    print(f"[Server] Server running on {properties.SERVER_ADDRESS}")
    httpd.serve_forever()