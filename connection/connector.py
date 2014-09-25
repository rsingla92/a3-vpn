"""
VPN connector
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
SOCKET_TIMEOUT = 30.0

RECV_LENGTH = 1024

def setup_server():
    """
    Starts the VPN server
    Returns:
        queue which will be populated with incoming messages
    Note:
        rases a socket.timeout exception if a connection cannot be made
        quickly enough
    """
    return _setup(host=HOST, port=PORT, server=True)

def setup_client(server_host):
    """
    Starts the VPN client
    Returns:
        queue which messages will be sent from
    Note:
        rases a socket.timeout exception if a connection cannot be made
        quickly enough
    """
    return _setup(host=server_host, port=PORT)

def _setup(host, port, server=True):
    """
    Sets up and starts Client/Server processes
    """
    print("Host ip addr:")
    ip = socket.gethostbyname(socket.gethostname())
    print(ip, "\n")

    socket.setdefaulttimeout(SOCKET_TIMEOUT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))

    sock.listen(5)

    conn, addr = sock.accept()
    print("Connection Address", addr, "\n")

    message_queue = queue.queue()
    thread_class = Server if server else Client
    t = thread_class(socket, message_queue)

    # Setting this means the thread (t) will get killed when the program exits
    # Note that they don't get cleaned up, but it shouldn't be an issue
    t.daemon = 1
    t.start()
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
                encoded = message.encode()
                conn.send(encoded)
