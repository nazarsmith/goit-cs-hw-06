from http.server import HTTPServer
from src.models.models import HttpHandler, SocketServer
from multiprocessing import Process


def start_listener():
    socket = SocketServer()
    socket.receive()


def start_web_page(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def main():
    p1 = Process(target=start_listener, args=())
    p2 = Process(target=start_web_page, args=())

    p1.start()
    p2.start()

    p1.join()
    p2.join()


if __name__ == "__main__":
    main()
