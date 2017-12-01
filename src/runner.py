import socket
import sys
from io import StringIO
from .statuscodes import getStatusDefinition

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
    print(">> In requestParse")
    req = req.decode('UTF-8').splitlines()[0]
    req = req.rstrip('\r\n')
    reqlist = req.split()
    # Break down the request line into components
    print(">> before return, exiting requestParse")
    return {'request_method': reqlist[0],
            'path': reqlist[1],
            'request_version': reqlist[2]}


def generateResponse(status, headersByteString, res):
    status_def = 'OK'
    try:
        status_def = getStatusDefinition(status)
    except:
        status = 500
        status_def = getStatusDefinition(status)
    response = 'HTTP/1.1 {status} {status_def}\r\n'.format(
        status=status, status_def=status_def)

    response = bytes(response, 'UTF-8')
    response += headersByteString
    response += bytes('\r\n', 'UTF-8')

    for data in res:
        response += data

    return response


def start_response(status, response_headers, exec_info=None):
    """
    PEP333 start_response method signature
    start_response(status, response_headers, exc_info=None)

    Supplied as second parameter to application callable

    NOTE: Interstingly it seems like write() callableshould be able to writ to the output stream straight away.
    Since we are not implementing outut asstreams per se, we'll sip this for now.

    A parallell argument seems to be that no one realy uses it either (doubtful about that).
    Adding a todo for same

    TODO: return write() cllable to end dat to output stream
    SHOULD Return write(body_data) callable
    """

    preset_headers = [('Server', 'WSGIServer 1.0')]

    # Following HTTP Spec https://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html

    # status line format ==> Status-Line = HTTP-Version SP Status-Code SP Reason-Phrase CRLF
    # if status == None:
    #     status = 500
    # status_def = getStatusDefinition(status)

    # Application sending error informaton as a part of staus
    res_status_line = "HTTP/1.1 {status} \r\n".format(status=status)
    res_headers = preset_headers + response_headers
    response = res_status_line

    for header in res_headers:
        response += '{0}: {1}\r\n'.format(*header)
        response += '\r\n'


def handleSingleRequest(connection, app):
    print(">> in handleSingleRequest")
    req = connection.recv(CLIENT_DATA_BUFFER_SIZE)
    reqDetails = requestParse(req)

    # add raw request data to details
    reqDetails['request_data'] = req.decode('UTF-8')

    # reqDetails contains data for cgi variables
    env = set_wsgi(reqDetails)

    print(">> calling app callable")
    response = app(env, start_response)
    print()
    print(response.status_code)
    print(">> app call success, response recieved")
    print(">> generating response")

    headers = response._headers
    del headers['content-length']
    response._headers = headers
    #
    # res = bytes('', 'UTF-8')

    response = generateResponse(
        response.status_code, response.serialize_headers(), response)

    print(response)
    connection.sendall(response)
    connection.close()
    print(">> connection closed, exiting handleSingleRequest")


def run(application):
    socketListener = init(HOST, PORT)
    while True:
        print(">> in while True")
        connection, address = socketListener.accept()
        handleSingleRequest(connection, application)


def set_wsgi(cgiVariables):
    print(">> in set_wsgi")
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
    # wsgiconfig['SERVER_NAME'] = socket.getfqdn(HOST)  # localhost
    wsgiconfig['SERVER_NAME'] = '127.0.0.1'
    wsgiconfig['SERVER_PORT'] = PORT

    print(">> exiting set_wsgi")
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

    run(app)
