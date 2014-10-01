#!/usr/bin/env python3
from tkinter import *
import logging

import dh
import aes
import struct

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

        # Use the GridManager
        self.setup_grid()
        self.setup_buttons()
        self.setup_entries()
        logging.info('Completed construction!')

    def setup_grid(self):
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(3, pad=7)

        logLabel = Label(self, text="Log Window")
        logLabel.grid(sticky=W, pady=5, padx=5)

        textArea = Text(self)
        textArea.grid(row=1, column=0, columnspan=3, rowspan=5, padx=5, sticky=E+W+S+N)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        handler = WidgetLogger(textArea)
        logger.addHandler(handler)

    def setup_buttons(self):
        # TODO: Add the command parameter to all button constructor calls.
        mode_button = Button(self, text="Mode: Client (press to switch)", command = self.toggle_mode )
        mode_button.grid(row=6, column=2)

        connect_button = Button(self, text="Connect")
        connect_button.grid(row=7, column=2)

        send_button = Button(self, text="Send")
        send_button.grid(row=8, column=2)

        stop_button = Button(self, text="Stop")
        stop_button.grid(row=10, column=2)

        continue_button = Button(self, text="Continue")
        continue_button.grid(row=9, column=2)

        quit_button = Button(self, text="Quit")
        quit_button.grid(row=11, column=4)

        help_button = Button(self, text="Help")
        help_button.grid(row=11, column=0)

    def toggle_mode(self):
        # TODO: Add some logging here
        if mode_button.config('text')[-1] == "Mode: Client (press to switch)":
            is_client = false
        else:
            mode_button.config(text="Mode: Server (press to switch)")
            is_client = true

    def setup_entries(self):
        ip_addr_label = Label(self, text="IP Addr")
        ip_addr_label.grid(row=6, column=0)
        ip_addr_entry = Entry(self)
        ip_addr_entry.grid(row=6, column=1)

        port_label = Label(self,text="Port")
        port_label.grid(row=7, column=0)
        port_entry = Entry(self)
        port_entry.grid(row=7, column=1)

        shared_value_label = Label(self,text="Secret Shared Value")
        shared_value_label.grid(row=8, column=0)
        shared_value_entry = Entry(self)
        shared_value_entry.grid(row=8, column=1)

        send_label = Label(self, text="Data to be Sent")
        send_label.grid(row=9, column=0)
        send_entry = Entry(self)
        send_entry.grid(row=9, column=1)

        received_label = Label(self, text="Data as Received")
        received_label.grid(row=10, column=0)
        received_entry = Entry(self)
        received_entry.grid(row=10, column=1)

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
