import sys
import socket

import math
from decimal import *
getcontext().prec = 4

connected = True
serverip = "63.225.86.64"
serverport = 7778
#serverip = "10.159.38.42"

def cuttofour(number):
    number = str(number)
    leng = len(number)
    if leng > 4:
        print "Packet too long. Cutting " + str(int(number)-int(number[:4])) + " digits"
        number = number[:4]
    if leng < 4:
        rand = 4-leng
        #print "splicing " + str(rand) + " leading zeros"
        for i in range(rand):
            number = "0"+number
    return number

def sendinfo(typewords):
    global s
    #send size of packet
    msg = cuttofour(len(typewords))
    totalsent = 0
    while totalsent < 4:
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
            break
        totalsent = totalsent + sent
    #send packet
    totalsent = 0
    while totalsent < int(msg):
        sent = s.send(typewords[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
            break
        totalsent = totalsent + sent
        
def myreceive():
    #Recieve quantity of words
    global s
    global connected
    chunks = []
    bytes_recd = 0
    while bytes_recd < 4 and connected:
        chunk = s.recv(min(4 - bytes_recd, 2048))
        if chunk == '':
            print "Server has disconnected"
            connected = False
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    if connected:
        MSGLEN = int(''.join(chunks))
        #recieve the words
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN and connected:
            chunk = s.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == '':
                print "Server has disconnected"
                connected = False
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)
        
        
print "Connecting to ", serverip

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#try:
s.connect((serverip, serverport))
print "Connected"

tosend = raw_input(":")

sendinfo(tosend)
recieved = myreceive()

print recieved


tosend = raw_input(":")
#except socket.error:
#    print "ain't woikin!"