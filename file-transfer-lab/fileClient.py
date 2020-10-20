#! /usr/bin/env python3

import os, re, socket, sys

sys.path.append("../lib") # for params
sys.path.append("../framed-echo") # for framedSock

import params
from framedSock import framedSend, framedReceive

PATH = "Files/"

def fileClient():
    switchesVarDefaults = (
        (('1', '--server'), 'server', "127.0.0.1:50001"),
        (('?', '--usage'), 'usage', False),
        (('d', '--debug'), 'debug', False),
    )

    paramMap = params.parseParams(switchesVarDefaults)
    server, usage, debug = paramMap['server'], paramMap['usage'], paramMap['debug']

    if usage:
        params.usage()

    try:
        serverHost, serverPort = re.split(":", server)
        serverPort = int(serverPort)
    except:
        print("Can't parse server:port from '%s'" % server)
        sys.exit(1)

    port = (serverHost, serverPort)

    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
    listenSocket.connect(port)

    while 50001:
        fileName = input("> ")
        fileName.strip()

        if fileName == "exit": 
            sys.exit(0) # exit loop
        else:
            if not fileName:
                continue
            elif os.path.exists(PATH + fileName):
                f = open(PATH + fileName, "rb") 
                data = f.read() # read

                if len(data) < 1:
                    print("File %s is blank" % fileName)
                    continue
                
                framedSend(listenSocket, fileName, data, debug)
                statusNumber = int(listenSocket.recv(1024).decode()) # checks if server received the file

                if not statusNumber:
                    print("File %s was not received by server." % fileName)
                    sys.exit(1)
                else:
                    print("File %s was received by server." % fileName)
                    sys.exit(0)
            else:
                print("File %s not found" % fileName) # repeat loop if file does not exist

if __name__ == "__main__":
    fileClient()