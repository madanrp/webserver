
class BaseRequestHandler:
    def __init__(self, request, path, command):
        self.request = request
        self.path = path
        self.command = command
    
    def setup(self):
        self.connection = self.request
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)

    def handle():
        mname = 'do_' + self.command
    def finish(self):
        self.wfile.flush()
        self.wfile.close()
        self.rfile.close()

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
