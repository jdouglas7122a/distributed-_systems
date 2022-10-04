import socket
import selectors
import ClientLib
import traceback

class ThreadedClient ():
    def __init__(self, host="127.0.0.1", port=12345):

        # Network components
        self._host = host
        self._port = port
        self._listening_socket = None
        self._selector = selectors.DefaultSelector()

        self._module = None

    def start_connection(self, host, port):
        addr = (host, port)
        print("starting connection to", addr)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)

        self._module = ClientLib.Module(sock, addr)
        self._module.start()

    def run(self):
        self.start_connection(self._host, self._port)
       # self._module.create_message(input("Enter a command: "))


if __name__ == "__main__":
    client = ThreadedClient()
    client.run()