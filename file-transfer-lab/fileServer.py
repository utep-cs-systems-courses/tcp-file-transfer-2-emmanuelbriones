#! /usr/bin/env python3

import os, socket, sys

sys.path.append("../lib") # for params
sys.path.append("../framed-echo")

import params
from framedSock import framedReceive

PATH = "./Receive"
HOST = "127.0.0.1"

def fileServer():
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

    if not os.path.exists(PATH): # check if directory exists or create a new one
        os.makedirs(PATH)
    os.chdir(PATH) # move to directory

    while 50001:
        connection, address = listenSocket.accept()

        if not connection or not address:
            sys.exit(1) #exit loop

        if not os.fork():
            print("Connected by: ", address)

            # receive files 
            try:
                fileName, contents = framedReceive(connection, debug)
            except:
                print("Error: File transfer was not successful!")
                connection.sendall(str(0).encode())
                sys.exit(1)
            
            # save files 
            fileName = fileName.decode()
            writeFile(connection, address, fileName, contents)

            connection.sendall(str(1).encode()) # success
            sys.exit(0)

def writeFile(connection, address, fileName, contents):
    if connection is None: # check if None
        raise TypeError
    if address is None: # check if None
        raise TypeError
    if fileName is None: # check if None
        raise TypeError
    if contents is None: # check if None
        raise TypeError

    try:
        writer = open(fileName, 'w+b') # write and binary
        writer.write(contents)
        writer.close() 
        print("File %s received from %s" % (fileName, address))
    except FileNotFoundError:
        print("File %s not found" % fileName)
        connection.sendall(str(0).encode())
        sys.exit(1)

if __name__ == "__main__":
    fileServer()