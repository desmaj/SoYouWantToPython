import eventlet
eventlet.monkey_patch()
from eventlet.queue import Queue

import json
import sys
import uuid

class LineBuffer(object):
    DELIMITER = '\n'
    
    def __init__(self, callback, *args, **kwargs):
        self._buffer = ""
        self._callback = callback
        self._args = args
        self._kwargs = kwargs
    
    def receive(self, chunk):
        self._buffer += chunk
        while self.DELIMITER in self._buffer:
            line, self._buffer = self._buffer.split(self.DELIMITER, 1)
            self._callback(line, *self._args, **self._kwargs)

class RelayServer(object):
    
    def __init__(self, hostname, port):
        self._address = (hostname, port)
        self._clients = {}
        self._messages = []
        self._pool = eventlet.GreenPool(256)
        self._queue = Queue()

    def start(self):
        server = eventlet.listen(self._address)
        eventlet.spawn(self._broadcast)
        while True:
            sock, address = server.accept()
            print "Accepted connection from {}".format(address)
            self._clients[address] = sock
            self._pool.spawn_n(self._handle_client, sock, address)
    
    def _handle_client(self, client, address):
        buffer = LineBuffer(self._receive, address)
        while True:
            buffer.receive(client.recv(4096))
    
    def _receive(self, message, address):
        self._handle_message(message, address)
    
    def _handle_message(self, message, address):
        try:
            structure = json.loads(message)
        except ValueError:
            structure = {"id": str(uuid.uuid4()),
                         "message": message.rstrip()}
        
        payload = structure['message']
        if payload.startswith("connect "):
            address = payload[8:].split(':')
            self._connect((address[0], int(address[1])))
        elif payload == "source":
            self._clients[address].sendall(open(__file__).read())
        else:
            structure['address'] = address
            self._send(json.dumps(structure), address)
    
    def _send(self, message, address):
        self._queue.put((message, address))
    
    def _broadcast(self):
        while True:
            message, address = self._queue.get()
            try:
                payload = json.loads(message)
            except ValueError:
                print "Unable to send message: '{!r}'".format(message)
                continue
            
            if payload['id'] not in self._messages:
                self._messages = [payload['id']] + self._messages[:256]
                for client_address, client in self._clients.items():
                    if client_address != address:
                        client.sendall(message + "\n")
    
    def _connect(self, address):
        sock = eventlet.connect(address)
        self._clients[address] = sock
        self._pool.spawn_n(self._handle_client, sock, address)
        print "Connected to {!r}".format(address)

if __name__ == '__main__':
    print "Listening on {}:{}".format(*sys.argv[1:])
    server = RelayServer(sys.argv[1], int(sys.argv[2]))
    server.start()
