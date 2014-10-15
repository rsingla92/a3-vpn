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

RECV_LENGTH = 1024
RECV_ATTEMPTS = 16

class ConnectionDeadException(BaseException):
    pass

class Connector(object):
    def __init__(self, server=False, host=HOST, port=PORT):
        self.host = host
        self.port = int(port)
        self.server = server
        self.send_queue = None
        self.send_thread = None
        self.receive_queue = None
        self.receive_thread = None

    def connect(self):
        """
        Establish a connection between two VPN instances
        """
        if not self.is_alive():
            self.receive_queue = queue.Queue()
            self.send_queue = queue.Queue()
            sock = _get_socket()
            clientsocket = sock
            if self.server:
                logging.getLogger().info('Server is connecting to client: ' + sock)
                clientsocket = _server_connect(sock, self.port)
            else:
                logging.getLogger().info('Client is connecting to server: ' + self.host)
                _client_connect(sock, self.host, self.port)
            self.receive_thread = Receiver(clientsocket, self.host, self.port, self.receive_queue)
            self.send_thread = Sender(clientsocket, self.host, self.port, self.send_queue)
            self.receive_thread.daemon, self.send_thread.daemon = 1, 1
            self.send_thread.start()
            self.receive_thread.start()

    def send(self, message):
        """
        Send a message over the connection
        Raises:
            ConnectionDeadException if connection has failed
        """
        # self.assert_alive() # could use decorator
        logging.getLogger().info('Adding message to queue')
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
        # self.assert_alive() # could use decorator
        if not self.receive_queue.empty():
            logging.getLogger().info('Receiving message')
            return self.receive_queue.get()
        else:
            return None

    def receive_wait(self):
        """
        Waits until you receive something, then return it
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
        logging.getLogger().info('Closing connection thread')
        if self.receive_thread != None:
            self.receive_thread.close()
        if self.send_thread != None:
            self.send_thread.close()
        self.send_thread = None
        self.receive_thread = None

    def __del__(self):
        self.close()

def _get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this lets us use the same port for multiple sockets
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

def get_ip():
    ip = socket.gethostbyname(socket.gethostname())
    return ip

def _server_connect(sock, port):
    ip = socket.gethostbyname(socket.gethostname())
    print(ip)
    logging.getLogger().info('Connecting to IP: ' + ip)
    sock.bind((ip, port))
    logging.getLogger().info('Waiting for connection...')
    sock.listen(1)
    clientsocket, addr = sock.accept()
    print('Connected to {}'.format(addr))
    return clientsocket

def _client_connect(sock, host, port):
    failed_connections = 0
    while 1:
        try:
            sock.connect((host, port))
            break
        except ConnectionRefusedError as e:
            print('Receiver connection refused...')
            failed_connections += 1
            if failed_connections > RECV_ATTEMPTS:
                raise
            time.sleep(1)
        except OSError:
            print('Attempted to connect to host {} and port {}'.format(host, port))
            raise

class Receiver(threading.Thread):
    """
    Server class, receives messages on a socket and puts them in a queue
    """
    def __init__(self, sock, host, port, message_queue):
        threading.Thread.__init__(self)
        if sock is None:
            self.sock = _get_socket()
        else:
            self.sock = sock
        self.host = host
        self.port = port
        self.message_queue = message_queue
        self.failed_connections = 0
        self.cont = True

    def log_received(self, message):
        logger = logging.getLogger()
        to_log = "Received: {}".format(message)
        logger.info(to_log)

    def run(self):
        while self.cont:
            message = None
            try:
                message = self.sock.recv(RECV_LENGTH)
            except ConnectionError:
                break
            if message:
                self.message_queue.put(message)
                self.log_received(message)
            self.failed_connections = 0
        self.sock.close()

    def close(self):
        self.cont = False

class Sender(threading.Thread):
    """
    Sender class, sends messages from a queue as they are inserted
    """
    def __init__(self, sock, host, port, send_queue):
        threading.Thread.__init__(self)
        if sock is None:
            self.sock = _get_socket()
        else:
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
        while self.cont:
            if not self.send_queue.empty():
                message = self.send_queue.get()
                try:
                    self.sock.send(message)
                except ConnectionError:
                    break
                self.log_sent(message)
        self.sock.close()

    def close(self):
        self.cont = False
