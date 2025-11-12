# https-server

A minimal HTTPS server built purely with Python’s standard library.

## 🚀 Usage
```bash
pip install httpspyserver
httpspyserver --cert cert.pem --key key.pem -p 8443


Create a Self-Signed Certificate

openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
