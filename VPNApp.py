#!/usr/bin/env python
from tkinter import *
import logging

# Meant to be a TkInter text widget that sets up logging
class WidgetLogger(logging.Handler):
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

# Main class that creates the GUI and provides button functionality
class VPNApp(Frame):

    # Constructor
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("VPN Window")
        self.pack(fill=BOTH, expand=1)
    
		# Use the GridManager
        self.setupGrid()
        self.setupButtons()
        self.setupEntries()
        logging.info('Completed construction!')

    def setupGrid(self):
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
        
    def setupButtons(self):
		# TODO: Add the command parameter to all button constructor calls. 
        modeButton = Button(self, text="Mode: Client (press to switch)", command = self.toggleMode )
        modeButton.grid(row=6, column=2)

        connectButton = Button(self, text="Connect")
        connectButton.grid(row=7, column=2)
        
        sendButton = Button(self, text="Send")
        sendButton.grid(row=8, column=2)
        
        stopButton = Button(self, text="Stop")
        stopButton.grid(row=10, column=2)

        continueButton = Button(self, text="Continue")
        continueButton.grid(row=9, column=2)

        quitButton = Button(self, text="Quit")
        quitButton.grid(row=11, column=4)

        helpButton = Button(self, text="Help")
        helpButton.grid(row=11, column=0)
   
    def toggleMode(self):
		# TODO: Add some logging here
        if modeButton.config('text')[-1] == "Mode: Client (press to switch)":
            isClient = false
        else:
            modeButton.config(text="Mode: Client (press to switch)")
            isClient = true

    def setupEntries(self):
        ipAddrLabel = Label(self, text="IP Addr")
        ipAddrLabel.grid(row=6, column=0)
        ipAddrEntry = Entry(self)
        ipAddrEntry.grid(row=6, column=1)

        portLabel = Label(self,text="Port")
        portLabel.grid(row=7, column=0)
        portEntry = Entry(self)
        portEntry.grid(row=7, column=1)

        sharedValueLabel = Label(self,text="Secret Shared Value")
        sharedValueLabel.grid(row=8, column=0)
        sharedValueEntry = Entry(self)
        sharedValueEntry.grid(row=8, column=1)

        sendLabel = Label(self, text="Data to be Sent")
        sendLabel.grid(row=9, column=0)
        sendEntry = Entry(self)
        sendEntry.grid(row=9, column=1)

        receivedLabel = Label(self, text="Data as Received")
        receivedLabel.grid(row=10, column=0)
        receivedEntry = Entry(self)
        receivedEntry.grid(row=10, column=1)
        
def main():
    # Create a root window that will hold everything for us
    root = Tk()
    root.geometry("500x500+300+300")

    # Create a calibration application using that root
    app = VPNApp(root)

    # Draw the window
    app.mainloop()

if __name__ == '__main__':
    main()
