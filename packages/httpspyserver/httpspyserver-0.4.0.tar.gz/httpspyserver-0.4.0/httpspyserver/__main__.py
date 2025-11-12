import argparse
from .server import run_https_server

def main():
    parser = argparse.ArgumentParser(description="Run a simple HTTPS server")
    parser.add_argument("--cert", required=True, help="Path to SSL certificate (PEM file)")
    parser.add_argument("--key", required=True, help="Path to SSL private key (PEM file)")
    parser.add_argument("-p", "--port", type=int, default=8443, help="Port number")
    args = parser.parse_args()

    run_https_server(args.cert, args.key, args.port)

if __name__ == "__main__":
    main()
