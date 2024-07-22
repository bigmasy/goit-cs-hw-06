import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import datetime
from pymongo import MongoClient
import threading
import json

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

        # Конвертуємо словник у JSON рядок для передачі через сокет
        json_data = json.dumps(data_dict).encode()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json_data, ('localhost', 5001))
        sock.close()

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

# Функція для запуску Socket сервера
def run_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 5001))
    print("Socket server running on port", 5001)

    # Підключення до MongoDB
    client = MongoClient('mongodb://mongo:27017/')
    db = client.messages_db
    collection = db.messages

    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data)
        message['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        collection.insert_one(message)
        print("Message received and stored:", message)

# Запуск серверів у різних потоках
if __name__ == "__main__":
    threading.Thread(target=run_http_server).start()
    threading.Thread(target=run_socket_server).start()
