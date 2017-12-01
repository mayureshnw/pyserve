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
    req = str(req)
    req = req.splitlines()[0]
    print(req, "\n>>>>>>\n")
    req = req.rstrip('\\r\\n')
    print(req, "\n>>>>>>\n")
    reqparams = req.split("\\r\\n")
    for param in reqparams:
        print(param)

    print("=========================================\n\n")
    # print(request_method, path, request_version)


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


def main(sysargs):
    if len(sysargs) < 2:
        print(
            "Expected application callable \nTry \n>> python3 server.py application:app")
        return

    path = sysargs[1]
    location, app = path.split(":")
    # importing the application
    imported_application = __import__(location)
    print(imported_application)
