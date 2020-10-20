#! /usr/bin/env python3

import os, socket, sys, threading, time

sys.path.append("../lib") # for params

import params
from threading import Thread
from framedSock import framedSock

PATH = "./Receive"
HOST = "127.0.0.1"


switchesVarDefaults = (
    (('1', '--listenPort'), 'listenPort', 50001),
    (('?', '--usage'), 'usage', False),
    (('d', '--debug'), 'debug', False),
)

paramMap = params.parseParams(switchesVarDefaults)
listenPort, usage, debug = paramMap['listenPort'], paramMap['usage'], paramMap['debug']

if usage:
    params.usage()

bind = (HOST, listenPort)

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listenSocket.bind(bind)

listenSocket.listen(10) # 10 connections
print("Listening on: ", bind)

lock = threading.Lock()

class Server(Thread):

    def __init__(self, sockAddress):
        Thread.__init__(self)
        self.sock, self.address = sockAddress
        self.fsock = framedSock(sockAddress)

    def run(self):
        print("new thread handling connection from", self.address)
        while 1:
            try:
                fileName, contents = self.fsock.receive(debug)
            except:
                print("Error: File transfer was not successful!")
                self.fsock.sendStatus(0, debug)
                self.fsock.close()
                sys.exit(1)

            if debug:
                print("Received", contents)

            # client closed = data not received
            if fileName is None or contents is None:
                print ("Client ", self.address, " has disconnected")
                sys.exit(0)
            
            lock.acquire()
            if debug:
                time.sleep(5)
            
            # write file
            fileName = fileName.decode()
            self.writeFile(fileName, contents)

            self.fsock.sendStatus(1, debug) # success
            lock.release()

    def writeFile(self, fileName, contents):

        if fileName is None:
            raise TypeError
        if contents is None:
            raise TypeError

        try:
            if not os.path.exists(PATH): # check if directory exists or create a new one
                os.makedirs(PATH)
            os.chdir(PATH) # move to directory
 
            writer = open(fileName, 'w+b') # write and binary
            writer.write(contents)
            writer.close() 
            print("File %s received from %s" % (fileName, self.address))
        except FileNotFoundError:
            print("File Not Found Error: File %s not found" % fileName)
            self.fsock.Status(0, debug)
            sys.exit(1)

def main():
    while 50001:
        sockAddress = listenSocket.accept()
        server = Server(sockAddress)
        server.start()

if __name__ == "__main__":
    main()