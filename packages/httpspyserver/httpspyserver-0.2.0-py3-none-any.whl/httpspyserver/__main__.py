import argparse
import ssl
from . import https_server

def main():
    parser = argparse.ArgumentParser(description="Run a simple HTTPS server")
    parser.add_argument("-p", "--port", type=int, default=8443, help="Port number")
    parser.add_argument("--cert", required=True, help="Path to SSL certificate (PEM file)")
    parser.add_argument("--key", required=True, help="Path to SSL private key (PEM file)")
    args = parser.parse_args()

    https_server.run_https_server(certfile=args.cert, keyfile=args.key, port=args.port)

if __name__ == "__main__":
    main()
