import socket
import sys
from io import StringIO

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
    req = req.decode('UTF-8').splitlines()[0]
    req = req.rstrip('\r\n')
    reqlist = req.split()
    # Break down the request line into components
    return {'request_method': reqlist[0],
            'path': reqlist[1],
            'request_version': reqlist[2]}


def generateResponse(parsedReq):
    return """\
HTTP/1.1 200 OK

Hello, World!
"""


def handleSingleRequest(connection):
    req = connection.recv(CLIENT_DATA_BUFFER_SIZE)
    reqDetails = requestParse(req)

    # add raw request data to details
    reqDetails['request_data'] = req.decode('UTF-8')

    # reqDetails contains data for cgi variables
    set_wsgi(reqDetails)
    res = generateResponse(req)
    connection.sendall(bytes(res, 'UTF-8'))
    connection.close()


def run():
    socketListener = init(HOST, PORT)
    while True:
        connection, address = socketListener.accept()
        handleSingleRequest(connection)


def set_wsgi(cgiVariables):
    wsgiconfig = {}
    wsgiconfig['wsgi.version'] = (1, 0)  # works but why ?
    wsgiconfig['wsgi.url_scheme'] = 'http'
    wsgiconfig['wsgi.multithread'] = False
    wsgiconfig['wsgi.multiprocess'] = False
    wsgiconfig['wsgi.run_once'] = False
    wsgiconfig['wsgi.input'] = StringIO(cgiVariables['request_data'])
    wsgiconfig['wsgi.errors'] = sys.stderr

    # CGI VARIABLES
    wsgiconfig['REQUEST_METHOD'] = cgiVariables['request_method']  # GET
    wsgiconfig['PATH_INFO'] = cgiVariables['path']  # /hello
    wsgiconfig['SERVER_NAME'] = socket.getfqdn(HOST)  # localhost
    wsgiconfig['SERVER_PORT'] = PORT

    return wsgiconfig


def main(sysargs):
    if len(sysargs) < 2:
        print(
            "Expected application callable \nTry \n>> python3 server.py application:app")
        return

    path = sysargs[1]
    location, app = path.split(":")
    # importing the application
    imported_application = __import__(location)
    app = getattr(imported_application, app)
    print(app)

    run()
