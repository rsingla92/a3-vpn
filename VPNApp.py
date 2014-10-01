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

        self.connect_button = Button(self, text="Connect")
        self.connect_button.grid(row=7, column=2)

        self.send_button = Button(self, text="Send")
        self.send_button.grid(row=8, column=2)

        self.stop_button = Button(self, text="Stop")
        self.stop_button.grid(row=10, column=2)

        self.continue_button = Button(self, text="Continue")
        self.continue_button.grid(row=9, column=2)

        self.quit_button = Button(self, text="Quit")
        self.quit_button.grid(row=11, column=4)

        self.help_button = Button(self, text="Help")
        self.help_button.grid(row=11, column=0)

    def toggle_mode(self):
        # TODO: Add some logging here
        # TODO: Depending on the mode, disable certain text fields
        if self.mode_button.config('text')[-1] == "Mode: Client (press to switch)":
            self.is_client = False
        else:
            self.mode_button.config(text="Mode: Server (press to switch)")
            self.is_client = True

    def setup_entries(self):
        self.ip_addr_label = Label(self, text="IP Addr")
        self.ip_addr_label.grid(row=6, column=0)
        self.ip_addr_entry = Entry(self)
        self.ip_addr_entry.grid(row=6, column=1)

        self.port_label = Label(self,text="Port")
        self.port_label.grid(row=7, column=0)
        self.port_entry = Entry(self)
        self.port_entry.grid(row=7, column=1)

        self.shared_value_label = Label(self,text="Secret Shared Value")
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
