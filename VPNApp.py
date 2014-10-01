#!/usr/bin/env python3
from tkinter import *
import logging
import struct
import sys
import hashlib

import dh
import aes
import connector

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

        self.quit_button = Button(self, text="Quit", command=self.quit_mode)
        self.quit_button.grid(row=11, column=4)

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
        self.shared_value_entry = Entry(self)
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
        # TODO: get these from wherever they come from
        # need port and host params for Connector constructor
        host = self.ip_addr_entry.get()
        port = self.port_entry.get()
        self.connector = connector.Connector(host, port)

        # Generate a 16 byte key, from a hash of the shared secret value.
        # Then use that value, to encrypt a Deffie-Hellman exchange to 
        # ensure Perfect Forward Secrecy.
        md5_key = hashlib.md5()
        shared_val = self.shared_value_entry.get().encode('utf-8')
        md5_key.update(shared_val)
        long_term_key = md5_key.digest()
        
        session_key = []
        if self.is_client:
            #Client DH exchange            
            client_transport = dh.gen_public_transport(True, long_term_key)

            waiting_for_message = True
            while waiting_for_message:
                server_transport = (1, 1)
                return # TEMP
            session_key = dh.gen_session_key(client_transport[dh.PUB_TRANSPORT_IDX], server_transport[dh.LOC_EXPONENT_IDX], True, long_term_key)
            
        else:
            #Server DH exchange        
            server_transport = dh.gen_public_transport(True, long_term_key)
            waiting_for_message = True
            while waiting_for_message:
                client_transport = (1, 1)
                return # TEMP
            session_key = dh.gen_session_key(server_transport[dh.PUB_TRANSPORT_IDX], client_transport[dh.LOC_EXPONENT_IDX], True, long_term_key)
    
        # Enforce Perfect Forward Security by forgetting local exponent 
        client_transport = (0,0)
        server_transport = (0,0)
        
        self.session_key = session_key
    
        return     

    def send_callback(self):
        pass

    def continue_callback(self):
        pass

    def stop_callback(self):
        pass

    def help_callback(self):
        pass

def main():
    #dh.run_test()

    # Create a root window that will hold everything for us
    root = Tk()
    root.geometry("500x500+300+300")

    # Create a calibration application using that root
    app = VPNApp(root)

    # Draw the window
    app.mainloop()

if __name__ == '__main__':
    main()
