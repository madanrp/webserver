#!/usr/bin/python
import socket
import os
import signal
import errno
import select

REQUEST_QUEUE_SIZE = 5

class BaseServer:
    def __init__(self, address):
        self._address = server_address
        self.shutdown = False
        self._socket = socket.socket(socket.AF_INET, sock.SOCK_STREAM)
        self.server_bind()
        self.server_activate()

    def server_activate(self):
        self._socket.listen(REQUEST_QUEUE_SIZE)

    def server_bind(self):
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(self._address)

    def server_close(self):
        self._socket.close() 

    def shutdown(self):
        self.shutdown = True

    def get_request(self):
        while not self.shutdown:
            readable = []
            try:
                readable, _, _ = select.select([self._socket,], [], [])
            except select.error as e:
                code, msg = e
                if code in [errno.EINTR, errno.EAGAIN]:
                    continue 
            
            if self._socket not in readable:
                continue

            client_connection, client_address = self._socket.accept()       
            return client_connection, client_address

    def serve_forever(self):
        while not self.shutdown:
            request, client_address = self.get_request()
            pid = os.fork()
            if pid == 0:
                # child process
                self._socket.close()
                self.process_request(request, client_address)
                os._exit(0)        
            else:
                # in parent
                client_connection.close()

    def get_request_line(self, request):
        rfile = request.makefile('rb', -1)
        raw_requestline = rfile.readline()
        requestline = raw_requestline
        if raw_requestline[-2:] == "\r\n":
            requestline = raw_requestline[:-2]
        elif raw_requestline[-1:] == "\n":
            requestline = raw_requestline[:-1]
        return requestline
    
    def validate_path(path):
        tokens = path.split("/")
        if ".." in tokens:
            return False
        return True

    def process_request(self, request):
        requestline = self.get_request_line(request)
        words = requestline.split()
        if len(words) != 3:
            send_error(request, 400, "Bad request syntax (%s)", requestline)
            self.close_request(request)
            return
        
        [command, path, version] = words
        if not validate_path(path):
            send_error(request, 400, "Bad path")
            self.close_request(request)
            return 

        handler = self.get_request_handler(path) 
        handle = handler(request, path, command) 
        handle.handle() 

    def is_cgi(path):
        for x in ['/cgi-bin']:
            i = len(x)
            if path[:i] == x:
                return True
        return False
    
    def get_request_handler(self, path):
        if is_cgi(path):
            return CGIHTTPHandler
        else:
            return SimpleHTTPHandler

    def send_error(request, error_code, message=None):
        try:
            short, long = self.responses[code]
        except:
            short, long = '', ''
        if not message:
            message = short
        wfile = request.makefile('wb', 0)
        wfile.write("%s %s %s\r\n" % ("HTTP/1.1", error_code, message))
        
    def handle_error(self, request, client_address):
        pass

    def verify_request(self, request):
        pass

    def close_request(self, request):
        request.finish()

    responses = {
        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Partial information', 'Request fulfilled from cache'),
        204: ('No response', 'Request fulfilled, nothing follows'),

        301: ('Moved', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('Method', 'Object moved -- see Method and URL list'),
        304: ('Not modified',
              'Document has not changed singe given time'),

        400: ('Bad request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not found', 'Nothing matches the given URI'),

        500: ('Internal error', 'Server got itself in trouble'),
        501: ('Not implemented',
              'Server does not support this operation'),
        502: ('Service temporarily overloaded',
              'The server cannot process the request due to a high load'),
        503: ('Gateway timeout',
              'The gateway server did not receive a timely response'),

        }
