#!/usr/bin/python
import socket
import os
import signal
import errno
import select

SERVER_ADDRESS = (HOST, PORT) = '127.0.0.1', 8000
REQUEST_QUEUE_SIZE = 5
STATIC_FILE_PATH = "../data"
PROTOCOL_VERSION = "HTTP/1.1"
shutdown_flag = False

def send_end_headers(client_connection):
    client_connection.sendall("\r\n")

def send_response(client_connection, code, message=None):
    if message is None:
        message = ''
    client_connection.sendall("%s %d %s" % (PROTOCOL_VERSION, code, message))

def validate_path(path):
    tokens = path.split("/")
    if ".." in tokens:
        return False
    return True

def validate_request(client_connection, http_method, path, http_version):
    is_valid = True
    if http_method != "GET":
        send_response(client_connection, 501, "Unsupported method %s" % http_method)
        is_valid = False
    elif not validate_path(path):
        send_response(client_connection, 400, "Bad Request")
        is_valid = False
    elif not path.endswith("/") and not os.path.isfile(STATIC_FILE_PATH+path):
        send_response(client_connection, 404, "file not found")
        is_valid = False
    elif path.endswith("/") and path != "/" and not os.path.exists(STATIC_FILE_PATH+path):
        send_response(client_connection, 404, "file not found")
        is_valid = False
    else:
        pass

    return is_valid
        
def get_directory_listing(relative_path, absolute_path):
    directory_listing = ""
    print absolute_path, os.listdir(absolute_path)
    #TODO: pagination, if too many files in single directory
    files = [ relative_path+f if os.path.isfile(absolute_path+f) \
                                else relative_path+f+"/" \
                                for f in os.listdir(absolute_path)]
    print files
    for f in files:
       directory_listing += "<li><a href=\"%s\">%s</a></li>\n" % (f, f)
    html_listing = b"""\
<html>
<head>
    <title>
        Diretory listing for %s
    </title>
</head>
<body>
    <h2>Directory listing for %s</h2>
    <hr>/<hr>
    <ul>
        %s
    </ul>
</body>
</html>
""" % (relative_path, relative_path, directory_listing)
    return html_listing 

def get_content_type(file_path):
    type_to_content_dict = {"html": "text/html", "jpg": "image/jpeg"}
    if file_path.endswith("/"):
        content_type = "text/html"
    else:
        file_type = file_path.rsplit(".", 1)[1]
        content_type = type_to_content_dict.get(file_type, "text/html")
    return content_type

def handle_request(client_connection):
    request = client_connection.recv(1024)
    headers = request.decode().split("\r\n")
    print headers
    method, relative_path, http_version = headers[0].split()
    if not validate_request(client_connection, method, relative_path, http_version):
        send_end_headers(client_connection)
        return
    print "relative_path:", relative_path
    absolute_path = "%s%s" % (STATIC_FILE_PATH, relative_path)

    response = b"""\
HTTP/1.1 200 OK
Content-Length: %d
Content-Type: %s

"""
    content_length = 0
    result = ""
    content_type = get_content_type(relative_path)
    if relative_path == "/":
        if os.path.isfile(absolute_path+"index.html"):
            with open(absolute_path+"index.html", "r") as f:
                result = f.read()
                content_length = len(result)
        else:
            result = get_directory_listing(relative_path, absolute_path)
            content_length = len(result)
    elif relative_path.endswith("/"):
        #list directory
        result = get_directory_listing(relative_path, absolute_path)
        content_length = len(result)
    else:
        with open(absolute_path, "r") as f:
            result = f.read()
            content_length = len(result)

    #TODO: this does not handle client crashing and exiting
    response = response % (content_length, content_type) + result 
    client_connection.sendall(response )
 
def sigchld_handler(signum, frame):
    global shutdown_flag
    while not shutdown_flag:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError:
            return

        if pid == 0:
            #no more childern
            return

def sigterm_handler(signum, frame):
    global shutdown_flag
    print "sigterm received"
    shutdown_flag = True

def register_handlers():
    signal.signal(signal.SIGCHLD, sigchld_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

def main():
    global shutdown_flag
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print "listening on %s:%d" % (HOST, PORT)

    register_handlers()

    while not shutdown_flag:
        readable = []
        try:
            readable, _, _ = select.select([listen_socket,], [], [])
        except select.error as e:
            # 'select' was interrupted
            code, msg = e
            if code in [errno.EINTR, errno.EAGAIN]:
                continue
            
        if listen_socket not in readable:
            continue

        client_connection, client_address = listen_socket.accept()
        pid = os.fork()
        if pid == 0:
            # child process
            # since child process inherits all the open fds
            # close the server socket
            listen_socket.close()
            handle_request(client_connection)
            client_connection.close()
            os._exit(0)
        else:
            # close client socket
            # decrement reference count by 1
            client_connection.close()

if __name__ == "__main__":
    main()
