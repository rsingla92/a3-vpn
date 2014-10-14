#!/usr/bin/env python3
from tkinter import *
import logging
import struct
import sys
import hashlib

import dh
import dh_auth
import aes
import mac
import connector
from multiprocessing.pool import ThreadPool

# States of the connection
DISCONNECTED, CONNECTING, CONNECTED = 0, 1, 2
MAC_KEY = b'CHANGE THIS'

pool = ThreadPool(processes=1)

class WidgetLogger(logging.Handler):
    """TkInter text widget to setup logging"""
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p|')
        self.setFormatter(formatter)
        self.widget = widget
        self.widget.config(state='disabled')

    def emit(self,record):
        self.widget.config(state='normal')
        self.widget.insert(END, self.format(record)+'\n')
        self.widget.config(state='disabled')
        self.widget.see(END)
        print(self.format(record))

class VPNApp(Frame):
    """Main class. Creates GUI and provides button functionality"""

    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("VPN Window")
        self.pack(fill=BOTH, expand=1)

        self.is_client = True
        self.connector = None
        self.connect_result = None
        self.state = DISCONNECTED

        # Use the GridManager
        self.setup_grid()
        self.setup_buttons()
        self.setup_entries()

    def setup_grid(self):
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(3, pad=7)

        self.logLabel = Label(self, text="Log Window")
        self.logLabel.grid(sticky=W, pady=5, padx=5)

        self.textArea = Text(self)
        self.textArea.grid(row=1, column=0, columnspan=3, rowspan=5, padx=5, sticky=E+W+S+N)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        self.handler = WidgetLogger(self.textArea)
        self.logger.addHandler(self.handler)

    def setup_buttons(self):
        # TODO: Add the command parameter to all button constructor calls.
        self.mode_button = Button(self, text="Mode: Client (press to switch)", command = self.toggle_mode )
        self.mode_button.grid(row=6, column=2)

        connect_button = Button(self, text="Connect", command=self.connect_callback)
        connect_button.grid(row=7, column=2)

        send_button = Button(self, text="Send", command=self.send_callback)
        send_button.grid(row=8, column=2)

        stop_button = Button(self, text="Stop", command=self.stop_callback)
        stop_button.grid(row=10, column=2)

        continue_button = Button(self, text="Continue", command=self.continue_callback)
        continue_button.grid(row=9, column=2)

        # self.quit_button = Button(self, text="Quit", command=self.quit_mode)
        # self.quit_button.grid(row=11, column=4)

        self.help_button = Button(self, text="Help", command=self.help_callback)
        self.help_button.grid(row=11, column=0)

    def toggle_mode(self):
        # TODO: Add some logging here
        # TODO: Depending on the mode, disable certain text fields
        self.is_client = not self.is_client

        if self.is_client:
            # Changing into the client
            self.mode_button.config(text="Mode: Client (press to switch)")
            self.ip_addr_entry.config(state='normal')
        else:
            # Changing into the server
            self.mode_button.config(text="Mode: Server (press to switch)")
            self.ip_addr_entry.delete(0, END)
            self.ip_addr_entry.config(state='disabled')

    def quit_mode(self):
        sys.exit(0) 

    def setup_entries(self):
        self.ip_addr_label = Label(self, text="IP Addr")
        self.ip_addr_label.grid(row=6, column=0)
        self.ip_addr_entry = Entry(self)
        self.ip_addr_entry.grid(row=6, column=1)

        self.port_label = Label(self,text="Port")
        self.port_label.grid(row=7, column=0)
        self.port_entry = Entry(self)
        self.port_entry.grid(row=7, column=1)

        self.shared_value_label = Label(self,text="Shared Secret Value")
        self.shared_value_label.grid(row=8, column=0)
        self.shared_value_entry = Entry(self, show="*")
        self.shared_value_entry.grid(row=8, column=1)

        self.send_label = Label(self, text="Data to be Sent")
        self.send_label.grid(row=9, column=0)
        self.send_entry = Entry(self)
        self.send_entry.grid(row=9, column=1)

        self.received_label = Label(self, text="Data as Received")
        self.received_label.grid(row=10, column=0)
        self.received_entry = Entry(self)
        self.received_entry.grid(row=10, column=1)

    def connect_callback(self):
        if self.state == DISCONNECTED:
            self.state = CONNECTING
            arg_tuple = (self.ip_addr_entry.get(), self.port_entry.get(), 
                self.shared_value_entry.get(), not self.is_client)
            self.connect_result = pool.apply_async(connect, arg_tuple)
        else:
            self.logger.info('Already connected.')

    def send_callback(self):
        if self.state != CONNECTED:
            print("No connection established.")
            return
        to_send = self.send_entry.get()
        if to_send and self.connector:
            encrypted = aes.aes_encrypt(to_send, self.session_key)
            encoded = bytes(encrypted)
            mac_val = mac.get_mac(to_send, MAC_KEY)
            self.connector.send(encoded+mac_val)

    def continue_callback(self):
        pass

    def stop_callback(self):
        self.connector.close()
        self.state = DISCONNECTED
        pass

    def help_callback(self):
        pass

    def receive(self):
        if self.connector is None:
            return
        encrypted = self.connector.receive()
        if encrypted:
            print(encrypted)
            msg_bytes = aes.aes_decrypt(encrypted, self.session_key)
            message = bytes(msg_bytes)
            # Not 100% on taking out the last block of message
            verified_message = mac.check_mac(message[:-16], encrypted, MAC_KEY)
            print(verified_message)
            self.received_entry.delete(0, END)
            self.received_entry.insert(0, verified_message)

    def disconnected(self):
        return not self.connector.is_alive()

def connect(host, port, shared_value, is_server):
    # TODO: get these from wherever they come from
    # need port and host params for Connector constructor
    global MAC_KEY
    ctr = None
    if port:
        ctr = connector.Connector(is_server, host, port)
    else:
        ctr = connector.Connector(is_server, host)

    # Generate a 16 byte key, from a hash of the shared secret value.
    # Then use that value, to encrypt a Diffie-Hellman exchange to 
    # ensure Perfect Forward Secrecy.
    md5_key = hashlib.md5()
    shared_val = shared_value.encode('utf-8')
    md5_key.update(shared_val)
    long_term_key = md5_key.digest()

    md5_key = hashlib.md5()
    md5_key.update(long_term_key)
    MAC_KEY = md5_key.digest()
    
    ctr.connect()
    
    session_key = []
    '''if not is_server:
        #Client DH exchange            
        client_dh_tup = dh.gen_public_transport(True, long_term_key)
        ctr.send(bytes(client_dh_tup[dh.PUB_TRANSPORT_IDX]))
        server_dh_tup_encrypted = ctr.receive_wait()
        session_key = dh.gen_session_key(server_dh_tup_encrypted, client_dh_tup[dh.LOC_EXPONENT_IDX], True, long_term_key)
        
    else:
        #Server DH exchange        
        server_dh_tup = dh.gen_public_transport(True, long_term_key)
        ctr.send(bytes(server_dh_tup[dh.PUB_TRANSPORT_IDX]))
        client_dh_tup_encrypted = ctr.receive_wait()
        session_key = dh.gen_session_key(client_dh_tup_encrypted, server_dh_tup[dh.LOC_EXPONENT_IDX], True, long_term_key)'''
    
    if not is_server:
        #Client Authenticated DH exchange
        # Send initial DH trigger message
        client_dh_init_msg = dh_auth.gen_auth_msg()
        ctr.send(bytes(client_dh_init_msg))
        
        # Receive server authentication response
        rcv_server_public_transport = ctr.receive_wait()
        rcv_server_nonce = rcv_server_public_transport[:16]
        rcv_server_dh_data_encrypted = rcv_server_public_transport[16:]  
        
        # Send back client authentication response
        client_auth_msg = dh_auth.gen_auth_msg(rcv_server_nonce)
        client_dh_data_tup = dh_auth.gen_public_transport(long_term_key, client_auth_msg)
        client_public_transport = client_dh_data_tup[dh_auth.PUB_TRANSPORT_IDX]
        ctr.send(bytes(client_public_transport))
        
        # Authenticate received data from server
        expect_rcv_server_id = [int(byte) for byte in host.split('.')]
        expect_rcv_server_auth_msg = expect_rcv_server_id + client_dh_init_msg[4:]
        
        session_key = dh_auth.gen_session_key(rcv_server_dh_data_encrypted, client_dh_data_tup[dh_auth.LOC_EXPONENT_IDX], long_term_key, expect_rcv_server_auth_msg)
        
    else:
        #Server Authenticated DH exchange
        # Receive initial DH trigger message 
        rcv_client_dh_data = ctr.receive_wait()
        rcv_client_id = rcv_client_dh_data[:4]
        rcv_client_nonce = rcv_client_dh_data[4:]
        
        # send response
        server_nonce = dh_auth.gen_nonce()
        server_auth_msg = dh_auth.gen_auth_msg(rcv_client_nonce) 
        server_dh_data_tup = dh_auth.gen_public_transport(long_term_key, server_auth_msg)
        server_public_transport = server_nonce + server_dh_data_tup[dh_auth.PUB_TRANSPORT_IDX]
        ctr.send(bytes(server_public_transport))
        
        # Receive client authentication response - client_public_transport is the same as rcv_client_dh_data_encrypted
        rcv_client_public_transport = ctr.receive_wait()
        
        # Authenticate received data from client
        expect_rcv_client_auth_msg = list(rcv_client_id) + list(server_nonce)
        session_key = dh_auth.gen_session_key(rcv_client_public_transport, server_dh_data_tup[dh_auth.LOC_EXPONENT_IDX], long_term_key, expect_rcv_client_auth_msg)

    if session_key == 0:
        logging.getLogger().info('Failed to authenticate: session key invalid')

    # Enforce Perfect Forward Security by forgetting local exponent 
    client_dh_data_tup = (0,0)
    server_dh_data_tup = (0,0)

    return (session_key, ctr)

def task_loop(app, root):
    if app.state == CONNECTING:
        if app.connect_result.ready():
             res = app.connect_result.get()
             app.session_key = res[0]
             app.connector = res[1] 
             app.state = CONNECTED
    elif app.state == CONNECTED:
        if app.disconnected():
            app.state = DISCONNECTED
        else:
            app.receive()
    root.after(500, task_loop, app, root)

def main():
    #dh.run_test()

    # Create a root window that will hold everything for us
    root = Tk()
    root.geometry("500x500+300+300")

    # Create a calibration application using that root
    app = VPNApp(root)

    root.after(500, task_loop, app, root)
    # Draw the window
    app.mainloop()

if __name__ == '__main__':
    main()
