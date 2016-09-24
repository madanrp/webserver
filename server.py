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

def validate_request(client_connection, http_method, path, http_version):
    is_valid = True
    if http_method != "GET":
        send_response(client_connection, 501, "Unsupported method %s" % http_method)
        is_valid = False
    elif not os.path.isfile(STATIC_FILE_PATH+path):
        send_response(client_connection, 404, "file not found")
        is_valid = False
    else:
        pass

    return is_valid
        

def handle_request(client_connection):
    request = client_connection.recv(1024)
    headers = request.decode().split("\r\n")
    method, path, http_version = headers[0].split()
    if path == "/":
        path = "/index.html"
    if not validate_request(client_connection, method, path, http_version):
        send_end_headers(client_connection)
        return
    file_name = "%s%s" % (STATIC_FILE_PATH, path)

    response = b"""\
HTTP/1.1 200 OK

"""

    with open(file_name, "r") as f:
        response += f.read()
        response += "\r\n"

    #TODO: this does not handle client crashing and exiting
    client_connection.sendall(response)

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
