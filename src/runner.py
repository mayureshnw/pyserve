import socket

addressFamily = socket.AF_INET
socketType = socket.SOCK_STREAM
queueSize = 1
HOST = ''
PORT = 8080
CLIENT_DATA_BUFFER_SIZE = 1024


def init(host, port):
    socketListener = socket.socket(
        addressFamily,
        socketType
    )

    socketListener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketListener.bind((host, port))
    socketListener.listen(queueSize)

    return socketListener


def requestParse(req):
    print(req)


def generateResponse(parsedReq):
    return """\
HTTP/1.1 200 OK

Hello, World!
"""


def handleSingleRequest(connection):
    req = connection.recv(CLIENT_DATA_BUFFER_SIZE)
    requestParse(req)
    res = generateResponse(req)
    connection.sendall(bytes(res, 'UTF-8'))
    connection.close()


def run():
    socketListener = init(HOST, PORT)
    while True:
        connection, address = socketListener.accept()
        handleSingleRequest(connection)


run()
