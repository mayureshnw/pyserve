import socket
#
# HOST, PORT = '', 8888
#
#
# print('Serving HTTP on port 8888 ...')
# while True:
#     client_connection, client_address = listen_socket.accept()
#     request = client_connection.recv(1024)
#     print(request)
#
#     http_response = """\
# HTTP/1.1 200 OK
#
# Hello, World!
# """
#     client_connection.sendall(bytes(http_response, 'UTF-8'))
#     client_connection.close()


class Server(object):
    """docstring for Server."""

    def __init__(self, host, port):
        super(Server, self).__init__()
        self.HOST = host
        self.PORT = port

        print(self.HOST, self.PORT)

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((self.HOST, self.PORT))
        self.listen_socket.listen(1)

    def run(self):
        while True:
            client_connection, client_address = self.listen_socket.accept()
            request = client_connection.recv(1024)
            print(request)

            http_response = """\HTTP/1.1 200 OK
            Hello, World!
            """
            client_connection.sendall(bytes(http_response, 'UTF-8'))
            client_connection.close()
