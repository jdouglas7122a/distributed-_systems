import sys
import selectors
import queue
import json
import io
import struct
import traceback
from threading import Thread
import socket

input_prompt = "Enter a command: "

class Module (Thread):
    def __init__(self, sock, addr):
        Thread.__init__(self)

        self._selector = selectors.DefaultSelector()
        self._sock = sock
        self._addr = addr
        self._incoming_buffer = queue.Queue()
        self._outgoing_buffer = queue.Queue()

        self._block_input = False
        self._data_loop = False
        self._recv_expn = False
        self._rset_ready = False
        self._quit_ready = False
        self._recv_mail = False

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self._selector.register(self._sock, events, data=None)

    def run(self):
            try:
                while True:
                    events = self._selector.select(timeout=1)
                    for key, mask in events:
                        message = key.data
                        try:
                            if mask & selectors.EVENT_READ:
                                self._read()
                            if mask & selectors.EVENT_WRITE and not self._outgoing_buffer.empty():
                                self._write()  # non user interact, for writing messages to buffer
                        except Exception:
                            break
                    # Check for a socket being monitored to continue.
                    if not self._selector.get_map():
                        break
            finally:
                self._selector.close()

    def _read(self):
        try:
            data = self._sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._incoming_buffer.put(data.decode())  # decrypt here
            else:
                raise RuntimeError("Peer closed.")

        self._process_response()

    def _write(self):
        try:
            message = self._outgoing_buffer.get_nowait()
        except:
            message = None

        if message:
            try:
                sent = self._sock.send(message)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass

    def create_message(self, content):
        nwencoded = str(content).encode()
        self._outgoing_buffer.put(nwencoded)

    def _process_response(self):
        message = self._incoming_buffer.get()
        #message = self._encryption.decrypt(message)
        self._respond(message)

    def _respond(self,message):
        try:
            type, content = str(message).split(' ',1)  # [HELO][Server.ServerDomain]

            print(message)

            self.prompt()

        except ValueError:
            print("ERROR: " + message)

    def prompt(self):
        message = ""
        while message == "":
            message = input(input_prompt)
        self.create_message(message)

    def __rset(self, message):
        self._diffy = SMTPClientDiffy.Diffy()
        self._encryption = SMTPEncryption.Encryption()
        self._block_input = False
        self._data_loop = False
        self._recv_expn = False
        self._rset_ready = False
        print(message)
        self.prompt()

    def close(self):
        print("closing connection to", self._addr)
        try:
            self._selector.unregister(self._sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self._addr}: {repr(e)}",
            )
        try:
            self._sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self._addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self._sock = None


