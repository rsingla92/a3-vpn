"""
VPN connector
"""

import time
import socket
import queue
import threading
import logging

# Any host on the machine will work
HOST = ''
PORT = 50002
SOCKET_TIMEOUT = 30.0

RECV_ATTEMPTS = 16

def establish_connection(host=HOST, port=PORT):
    """
    Establish a connection between two VPN instances
    Returns:
        tuple of send_queue, recieve_queue
    """
    send_queue, st = setup_sender(host=host, port=port)
    recieve_queue, rt = setup_reciever(port=port)
    return send_queue, recieve_queue

def setup_reciever(port=PORT):
    """
    Starts the VPN server
    Returns:
        queue which will be populated with incoming messages,
        process
    Note:
        rases a socket.timeout exception if a connection cannot be made
        quickly enough
    """
    return _setup(host=HOST, port=port, server=True)

def setup_sender(host=HOST, port=PORT):
    """
    Starts the VPN client
    Returns:
        queue which messages will be sent from,
        process
    Note:
        rases a socket.timeout exception if a connection cannot be made
        quickly enough
    """
    return _setup(host=host, port=port, server=False)

def _setup(host, port, server=True):
    """
    Sets up and starts Client/Server processes
    Returns queue and process
    """
    print("Host ip addr:")
    ip = socket.gethostbyname(socket.gethostname())
    print(ip, "\n")

    # socket.setdefaulttimeout(SOCKET_TIMEOUT)
    sock = _get_socket()

    message_queue = queue.Queue()
    thread_class = Reciever if server else Sender
    t = thread_class(sock, host, port, message_queue)

    # Setting this means the thread (t) will get killed when the program exits
    # Note that they don't get cleaned up, but it shouldn't be an issue
    t.daemon = 1
    t.start()
    return message_queue, t

def _get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this lets us use the same port for multiple sockets
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

class Reciever(threading.Thread):
    """
    Server class, recieves messages on a socket and puts them in a queue
    """
    def __init__(self, sock, host, port, message_queue):
        threading.Thread.__init__(self)
        self.message_queue = message_queue
        self.host = host
        self.port = port
        self.failed_connections = 0

    def log_recieved(self, message):
        logger = logging.getLogger()
        to_log = "Recieved: {}".format(message)
        logger.info(to_log)

    def run(self):
        p_tup = (self.host, self.port)
        while True:
            try:
                s = _get_socket()
                s.connect(p_tup)
                message = s.recv(RECV_LENGTH)
                if message:
                    decoded = message.decode()
                    self.message_queue.put(decoded)
                s.close()
                self.log_recieved(message)
                self.failed_connections = 0
            except ConnectionRefusedError as e:
                print('Reciever connection refused...')
                self.failed_connections += 1
                if failed_connections > RECV_ATTEMPTS:
                    raise
                time.sleep(1)


class Sender(threading.Thread):
    """
    Sender class, sends messages from a queue as they are inserted
    """
    def __init__(self, sock, host, port, send_queue):
        threading.Thread.__init__(self)
        self.sock = sock
        self.send_queue = send_queue
        self.host = host
        self.port = port

    def log_sent(self, message):
        logger = logging.getLogger()
        to_log = "Sent: {}".format(message)
        logger.info(to_log)

    def run(self):
        p_tup = (self.host, self.port)
        self.sock.bind(p_tup)
        self.sock.listen(5)
        while True:
            if not self.send_queue.empty():
                try:
                    conn, addr = self.sock.accept()
                    message = self.send_queue.get()
                    encoded = message.encode()
                    conn.send(encoded)
                    conn.close()
                    self.log_sent(message)
                except OSError as e:
                    raise
                    print(e)
