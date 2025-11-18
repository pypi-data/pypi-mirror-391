import socket
import threading
import os

DEFAULT_PORT = 2323
BUFFER_SIZE = 4096
WEB_ROOT = "./www"

class Minnet:
    def __init__(self, port=DEFAULT_PORT):
        self.port = port

    # ----------------------------
    # Server part
    # ----------------------------
    def serve(self, host="0.0.0.0", handler=None):
        """
        Start a Minnet server.
        handler(path, body) -> response_text
        If no handler is provided, uses the default read-only handler.
        """
        if handler is None:
            handler = self.default_handler

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, self.port))
        server_socket.listen(5)
        print(f"[Server] Listening on {host}:{self.port}")

        def client_thread(client_sock, addr):
            try:
                data = b""
                while True:
                    chunk = client_sock.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    data += chunk
                    if len(chunk) < BUFFER_SIZE:
                        break
                request_text = data.decode()
                lines = request_text.split("\n")
                path = lines[0].strip() if lines else "/"
                body = "\n".join(lines[1:]) if len(lines) > 1 else ""

                response = handler(path, body)
                client_sock.sendall(response.encode())
            finally:
                client_sock.close()

        while True:
            client_sock, addr = server_socket.accept()
            threading.Thread(target=client_thread, args=(client_sock, addr), daemon=True).start()

    # ----------------------------
    # Client part
    # ----------------------------
    def request(self, url, body=""):
        """
        Send a Minnet request to a server using min://ip/path URLs.
        """
        ip, path = self.parse_url(url)
        full_request = path
        if body:
            full_request += "\n" + body
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, self.port))
            s.sendall(full_request.encode())
            data = b""
            while True:
                chunk = s.recv(BUFFER_SIZE)
                if not chunk:
                    break
                data += chunk
                if len(chunk) < BUFFER_SIZE:
                    break
        return data.decode()

    # ----------------------------
    # URL parsing
    # ----------------------------
    @staticmethod
    def parse_url(url):
        if not url.startswith("min://"):
            raise ValueError("Invalid Minnet URL")
        url_body = url[6:]  # remove 'min://'
        parts = url_body.split("/", 1)
        ip = parts[0]
        path = "/" + parts[1] if len(parts) > 1 else "/"
        return ip, path

    # ----------------------------
    # Default read-only handler
    # ----------------------------
    @staticmethod
    def default_handler(path, body):
        """
        Read-only Apache-like handler:
        - Serves existing files from WEB_ROOT.
        - Ignores request body (no writes).
        """
        if path == "/":
            path = "/index.txt"
        full_path = os.path.join(WEB_ROOT, path.lstrip("/"))
        full_path = os.path.normpath(full_path)

        # Prevent directory traversal
        if not full_path.startswith(os.path.abspath(WEB_ROOT)):
            return "403 Forbidden: Access denied"

        # Only read existing files
        if os.path.isfile(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"500 Internal Server Error: {e}"
        else:
            return "404 Not Found"
