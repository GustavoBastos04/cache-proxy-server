from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from requests_cache import CachedSession
import os
import json

# Cria um servidor customizado para armazenar variáveis globais de estado
class ProxyHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, origin, cacheSession):
        super().__init__(server_address, RequestHandlerClass)
        self.origin = origin
        self.cacheSession = cacheSession

class CacheProxyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        url = self.server.origin
        if self.path.endswith("/payload"):
            url = f"{url}/payload"
            print(url)
        self.proxy_request(url=url)

        if self.path == '/clear-cache':
            self.server.cacheSession.cache.clear()
            self.send_response(200)
            self.end_headers()
            print("Cache cleaned")

    def proxy_request(self, url):
        try:
            response = self.server.cacheSession.get(url=url)
        except requests.exceptions.RequestException as e:
            self.send_response_only(e.code)
            self.end_headers()
            return

        self.send_response_only(response.status_code)
        for name, value in response.headers.items():
            self.send_header(name, value)

        if hasattr(response, 'from_cache') and response.from_cache:
            self.send_header('X-Cache', 'HIT')
            print("X-Cache: HIT")
        else:
            self.send_header('X-Cache', 'MISS')
            print("X-Cache", 'MISS')
        self.end_headers()
        self.wfile.write(response.content)

class CacheProxy:
    def __init__(self, port, origin):
        self.port = int(port)
        self.origin = origin
        self.cacheSession = self.startCacheSession()

    def startCacheSession(self):
        cachedSession = CachedSession(cache_name='proxy_cache', expire_after=300)
        return cachedSession

    def clearCache(self):
        self.cacheSession.cache.clear()

    def run(self, server_class=ProxyHTTPServer, handler_class=CacheProxyHandler):
        # '' == 0.0.0.0
        server_address = ('', self.port)
        httpd = server_class(server_address, handler_class, self.origin, self.cacheSession)

        metadata = {"port": self.port, "pid": os.getpid()}
        with open("proxy_meta.json", "w") as f:
            json.dump(metadata, f)

        httpd.serve_forever()