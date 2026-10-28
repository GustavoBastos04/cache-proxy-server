import argparse
from cacheProxy import CacheProxy
from server import Server
import urllib.request
import threading
import sys
import os
import json

def initialize(port, origin):

    proxyUrl = f"http://127.0.0.1:{port}"
    serverUrl = f"{origin}:3002"
    startProxy = checkServerStarted(url=proxyUrl)
    startServer = checkServerStarted(url=serverUrl)

    startServers(port=port, origin=origin, startProxy=startProxy, startServer=startServer)

def checkServerStarted(url):
    try:
        status_code = urllib.request.urlopen(url=url).getcode()
        print(f"Status code for {url} is {status_code}")
        if status_code == 200:
            return False
        else:
            return True
    except:
        print(f"{url} did not started, let's start it!")
        return True



def startServers(port, origin, startProxy, startServer):

    try:
        if startServer:
            print("Time to start the server...")
            origin2 = f"{origin}:3002"
            ipOrigin = origin.split("//")[1]
            server = Server(origin=ipOrigin)
            tServer = threading.Thread(target=server.run)
            tServer.start()
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
    try:
        if startProxy:
            print("Time to start the proxy...")
            proxy = CacheProxy(port=port, origin=origin2)
            tProxy = threading.Thread(target=proxy.run)
            tProxy.start()

    except Exception as e:
        print(f"Error to iniate proxy: {e}")



    return

def parserBuilder():
    
    parser = argparse.ArgumentParser(description="Choose port and origin")
    parser.add_argument('-p', '--port', type=str, help='Choose Proxy Port')    
    parser.add_argument('-o', '--origin', type=str, help='Choose server origin')
    args = parser.parse_args()

    return args.port, args.origin

def cleanCache():
    if "--clear-cache" in sys.argv and len(sys.argv) == 2:
        if os.path.exists("proxy_meta.json"):
            with open("proxy_meta.json", "r") as f:
                metadata = json.load(f)
                port = metadata["port"]

            try:
                url_admin = f"http://127.0.0.1:{port}/clear-cache"
                response = urllib.request.urlopen(url=url_admin)
                print(response.read().decode())
            except Exception as e:
                print(f"Error communicatiing with proxy in {port}: {e}")
        else:
            print(f"No proxy founded (no proxy_meta.json)")
        sys.exit(0)

if __name__ == '__main__':
    cleanCache()
    port, origin = parserBuilder()
    initialize(port=port, origin=origin)