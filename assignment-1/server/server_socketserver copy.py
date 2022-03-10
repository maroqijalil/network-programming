import socket
import threading
import socketserver


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
  def handle(self):
    data = str(self.request.recv(1024), "ascii")
    cur_thread = threading.current_thread()
    response = bytes("{}: {}".format(cur_thread.name, data), "ascii")
    self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
  pass


def client(ip, port, message):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((ip, port))
    sock.sendall(bytes(message, "ascii"))
    response = str(sock.recv(1024), "ascii")
    print("Received: {}".format(response))


if __name__ == "__main__":
  HOST, PORT = "localhost", 0

  server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
  with server:
    ip, port = server.server_address

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    client(ip, port, "Hello World 1")
    client(ip, port, "Hello World 2")
    client(ip, port, "Hello World 3")

    server.shutdown()
