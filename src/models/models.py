import os
import mimetypes
import pathlib
import re
import socket
import threading
import time
import urllib

from http.server import BaseHTTPRequestHandler
from src.utils.utils import connect_to_db, insert_one


class HttpHandler(BaseHTTPRequestHandler):
    # @staticmethod
    def send_to_socket(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                try:
                    s.connect(("127.0.0.1", 5000))
                    contents = [f"{message['username']}", f"{message['message']}"]
                    for c in contents:
                        s.sendall(c.encode("utf-8"))
                    break
                except ConnectionRefusedError:
                    time.sleep(0.5)

    def send_static(self, file_path):
        self.send_response(200)
        mt = mimetypes.guess_type(file_path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(file_path, "rb") as file:
            self.wfile.write(file.read())

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        current_path = os.getcwd()
        if pr_url.path == "/":
            page_loc = os.path.join(current_path, "front-init", "index.html")
            self.send_html_file(page_loc)
        elif pr_url.path == "/message":
            page_loc = os.path.join(current_path, "src", "front-init", "message.html")
            self.send_html_file(page_loc)
        else:
            page_loc = pathlib.Path(
                os.path.join(current_path, "src", "front-init", pr_url.path[1:])
            )
            print(page_loc)
            if page_loc.exists():
                self.send_static(page_loc)
            else:
                page_loc = os.path.join(current_path, "src", "front-init", "error.html")
                self.send_html_file(page_loc, 404)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data.decode("utf-8"))

        # Log the received form data
        print("Received POST data:")
        for key, value in post_data.items():
            print(f"{key}: {value}")

        self.send_to_socket(post_data)

        # Respond back to the client
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        response = (
            "<html><head><meta http-equiv='refresh' content='3;url=/message'></head>"
        )
        response += "<html><body><h2>Message saved.</h2>"
        response += "<p>Redirecting back to the form in 3 seconds...</p>"
        response += "</body></html>"
        self.wfile.write(response.encode("utf-8"))

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())


class SocketServer:
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 5000

        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.bind((self.HOST, self.PORT))
        self.SERVER.listen()
        try:
            self.DB_CLIENT = connect_to_db()
            self.DB_CLIENT.test_db.command("ping")
            print("Connected to MongoDB")
        except Exception as e:
            print(f"An error occurred: {e}")

    def send_to_db(self, message):
        db = self.DB_CLIENT.test_db
        message = message.split("][")
        processed_message = [re.sub("['\[\]]", "", m) for m in message]
        insert_one(
            db.homework_project, name=processed_message[0], message=processed_message[1]
        )

    def handle(self, client):
        while True:
            try:
                # get a message from the client
                message = client.recv(1024)
                message = message.decode("utf-8")
                if message == "" or message is None:
                    break
                self.send_to_db(message)
            except Exception:
                client.close()
                break

    def receive(self):
        while True:
            client, address = self.SERVER.accept()
            print(f"Connected by {str(address)}")

            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()
