import socket
import selectors
import os
import threading

import ServerLib

class ThreadedServer():
    def __init__(self,host='127.0.0.1',port=10000):
        # old code set self._host = host
        self._host = socket.gethostbyname(socket.gethostname())
        self._port = port
        self._listening_socket = None
        self._selector = selectors.DefaultSelector()

        # stores each active connection
        self._modules = []

    def _configureServer(self):
        # creates listening socket
        self._listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        self._listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listening_socket.bind((self._host, self._port))
        self._listening_socket.listen()

        print("Listening for new users on: {}, {}.".format(self._host, self._port))

        self._listening_socket.setblocking(False)
        self._selector.register(self._listening_socket, selectors.EVENT_READ, data=None)

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("Accepted connection from: ", addr)
        conn.setblocking(False)
        module = ServerLib.Module(conn, addr)
        self._modules.append(module)
        module.start()

    def run(self):
        self._configureServer()

        try:
            while True:
                events = self._selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                       pass
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self._selector.close()

if __name__ == "__main__":
    server = NWSThreadedServer()
    server.run()


