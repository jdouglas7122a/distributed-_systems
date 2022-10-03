import selectors
import queue
import traceback
from threading import Thread
import datetime
import os
import random

class Module(Thread):
    def __init__(self, sock, addr):
        Thread.__init__(self)

        self._domain = "server.domain"

        self._selector = selectors.DefaultSelector()
        self._sock = sock
        self._addr = addr

        self._incoming_buffer = queue.Queue()
        self._outgoing_buffer = queue.Queue()

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self._selector.register(self._sock, events, data=None)

        self.__log_connection()

        self._create_message("220 service ready")

    def run(self):
        try:
            while True:
                events = self._selector.select(timeout=None)
                for key, mask in events:
                    try:
                        if mask & selectors.EVENT_READ:
                            self._read()
                        if mask & selectors.EVENT_WRITE and not self._outgoing_buffer.empty():
                            self._write()
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{self._addr}:\n{traceback.format_exc()}",
                        )
                        self._sock.close()
                if not self._selector.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self._selector.close()

    def _read(self):
        try:
            data = self._sock.recv(4096)
        except BlockingIOError:
            print("blocked")
            pass
        else:
            if data:
                self._incoming_buffer.put(data.decode())
            else:
                raise RuntimeError("Peer closed.")

        self._process_response()

    def _write(self):
        try:
            message = self._outgoing_buffer.get_nowait()
        except:
            message = None

        if message:
            print("Sending: {}: to: {}".format(repr(message),self._addr))
            try:
                sent = self._sock.send(message)
            except BlockingIOError:
                pass

    def _create_message(self, content):
        #encoded = self._encryption.encrypt(content)
        #nwencoded = str(encoded).encode()
        #self._outgoing_buffer.put(nwencoded)
        self._outgoing_buffer.put("RSPN{}".format(content))

    def _process_response(self):
        message = self._incoming_buffer.get()
        header_length = 4
        self._create_message(message)
        #message = self._encryption.decrypt(message)

