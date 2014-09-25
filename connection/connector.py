"""
VPN connector
Portions adapted from https://github.com/jordenh/DE2VTT/blob/master/pysrc/middleman.py
"""

import sys
import socket
import select
import signal
import queue
import threading
import time

# Any host on the machine will work
HOST = ''
PORT = 50002

RECV_LENGTH = 1024

def setup_server():
    return setup(HOST, PORT, True)

def setup_client():
    return setup(HOST, PORT)

def _setup(host, port, server=True):
    print("Host ip addr:")
    print(socket.gethostbyname(socket.gethostname()), "\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))

    sock.listen(5)

    conn, addr = sock.accept()
    print("Connection Address", addr, "\n")

    message_queue = queue.queue()
    actor_class = Server if server else Client
    actor = actor_class(socket, message_queue)

    # Setting this means the actor will get killed when the program exits
    # Note that they don't get cleaned up, but it shouldn't be an issue
    actor.daemon = 1
    actor.start()
    return message_queue

class Server(threading.Thread):
    """
    Server class, recieves messages on a socket and puts them in a queue
    """
    def __init__(self, socket, message_queue):
        threading.Thread.__init__(self)
        self.sock = socket
        self.message_queue = message_queue

    def run(self):
        while True:
            # Not 100% that we need to accept every time on the server
            conn, addr = self.sock.accept()
            message = conn.recv(RECV_LENGTH)
            if message:
                decoded = message.decode()
                print(decoded)
                message_queue.put(decoded)

class Client(threading.Thread):
    """
    Client class, sends messages from a queue as they are inserted
    """
    def __init__(self, socket, send_queue):
        threading.Thread.__init__(self)
        self.sock = socket
        self.send_queue = send_queue

    def run(self):
        while True:
            if not send_queue.empty():
                conn, addr = self.sock.accept()
                message = send_queue.get()
                conn.send(message.encode())
