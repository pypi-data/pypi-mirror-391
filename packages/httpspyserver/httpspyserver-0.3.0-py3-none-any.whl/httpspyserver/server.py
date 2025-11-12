import http.server
import ssl

def run_https_server(certfile, keyfile, port=8443):
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)

    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        certfile=certfile,
        keyfile=keyfile,
        server_side=True
    )

    print(f"✅ HTTPS server running at https://localhost:{port}")
    httpd.serve_forever()
