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

RECV_LENGTH = 1024
RECV_ATTEMPTS = 16

class ConnectionDeadException(BaseException):
    pass

class Connector(object):
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = int(port)
        self.send_queue = None
        self.send_thread = None
        self.receive_queue = None
        self.receive_thread = None

    def connect(self):
        """
        Establish a connection between two VPN instances
        """
        if not self.is_alive():
            self.send_queue, st = setup_sender(host='', port=self.port)
            self.receive_queue, rt = setup_receiver(port=self.port)
            self.send_thread = st
            self.receive_thread = rt

    def send(self, message):
        """
        Send a message over the connection
        Raises:
            ConnectionDeadException if connection has failed
        """
        self.assert_alive() # could use decorator
        self.send_queue.put(message)

    def receive(self):
        """
        Recieve a message over the connection
        Returns:
            string received if there is data in queue
            otherwise None
        Raises:
            ConnectionDeadException if connection has failed
        """
        self.assert_alive() # could use decorator
        if not self.receive_queue.empty():
            return self.receive_queue.get()
        else:
            return None

    def receive_wait(self):
        """
        Waits until you receive somehthing, then return it
        """
        rcv = None
        while rcv == None:
            rcv = self.receive()
        return rcv

    def assert_alive(self):
        if not self.is_alive():
            self.close()
            raise ConnectionDeadException('Lost connection')

    def is_alive(self):
        if self.send_thread != None and self.receive_thread != None:
            return (self.send_thread.is_alive() 
                    and self.receive_thread.is_alive())
        else:
            return False

    def close(self):
        if self.receive_thread != None:
            self.receive_thread.close()
        if self.send_thread != None:
            self.send_thread.close()
        self.send_thread = None
        self.receive_thread = None

    def __del__(self):
        self.close()

def setup_receiver(port=PORT):
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
    Server class, receives messages on a socket and puts them in a queue
    """
    def __init__(self, sock, host, port, message_queue):
        threading.Thread.__init__(self)
        self.message_queue = message_queue
        self.host = host
        self.port = port
        self.failed_connections = 0
        self.cont = True

    def log_received(self, message):
        logger = logging.getLogger()
        to_log = "Recieved: {}".format(message)
        logger.info(to_log)

    def run(self):
        p_tup = (self.host, self.port)
        while self.cont:
            try:
                s = _get_socket()
                print(self.host)
                s.connect(p_tup)
                message = s.recv(RECV_LENGTH)
                if message:
                    self.message_queue.put(message)
                    self.log_received(message)
                self.failed_connections = 0
            except ConnectionRefusedError as e:
                print('Reciever connection refused...')
                self.failed_connections += 1
                if self.failed_connections > RECV_ATTEMPTS:
                    raise
                time.sleep(1)
            except OSError:
                print('Attempted to connect to {}'.format(p_tup))
                raise
            finally:
                s.close()

    def close(self):
        self.cont = False

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
        self.cont = True

    def log_sent(self, message):
        logger = logging.getLogger()
        to_log = "Sent: {}".format(message)
        logger.info(to_log)

    def run(self):
        p_tup = (self.host, self.port)
        self.sock.bind(p_tup)
        self.sock.listen(5)
        while self.cont:
            if not self.send_queue.empty():
                try:
                    conn, addr = self.sock.accept()
                    message = self.send_queue.get()
                    conn.send(message)
                    self.log_sent(message)
                finally:
                    conn.close()

    def close(self):
        self.sock.close()
        self.cont = False
