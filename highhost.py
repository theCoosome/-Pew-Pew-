print "Starting Host"
import sys
import socket, asyncore
import io

import math
from decimal import *
getcontext().prec = 4
#Send $ to pass, % to disconnect

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
    
class player(object):
    def __init__(self, clientsocket, address):
        #fancy connection stuff
        self.s = clientsocket
        self.ip = address[0]
        self.port = address[1]
        self.connected = True
        
    def myreceive(self):
        #Recieve quantity of words
        chunks = []
        bytes_recd = 0
        while bytes_recd < 4 and self.connected:
            chunk = self.s.recv(min(4 - bytes_recd, 2048))
            if chunk == '':
                self.connected = False
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        if self.connected:
            try:
                MSGLEN = int(''.join(chunks))
            except ValueError:
                MSGLEN = 1000000
            #recieve the words
            chunks = []
            bytes_recd = 0
            while bytes_recd < MSGLEN and self.connected:
                chunk = self.s.recv(min(MSGLEN - bytes_recd, 2048))
                if chunk == '':
                    self.connected = False
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            return ''.join(chunks)
        
    def sendinfo(self, typewords):
        #send size of packet
        try:
            msg = cuttofour(len(typewords))
            totalsent = 0
            while totalsent < 4:
                sent = self.s.send(msg[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                    break
                totalsent = totalsent + sent
            #send packet
            totalsent = 0
            while totalsent < int(msg):
                sent = self.s.send(typewords[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                    break
                totalsent = totalsent + sent
        except socket.error:
            self.connected = False
    
def getwords(input, quant):
    retreving = True
    words = []
    while retreving:
        word = ""
        getting = True
        for i in input:
            if i == " " and getting:
                words.append(word)
                word = ""
                if len(words)+1 >= quant:
                    getting = False
            else:
                word = word+i
        words.append(word)
        if len(words) == quant:
            return words
            retreving = False
        else:
            print "Missing "+str(quant-len(words))+" values"
            return ["0", "0"]
            retreving = False
    
serverport = 7778
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((socket.gethostname(), serverport))
serversocket.listen(5)

    

while True:
    print "Accepting connections"
    (clientsocket, address) = serversocket.accept()
    thisplayer = player(clientsocket, address)
    print "Connected "+str(thisplayer.ip)+" on port "+str(thisplayer.port)
    allin = thisplayer.myreceive()
    mode, score = getwords(allin, 2)
    print "scoring:", mode, score
    scores, out = open("high.txt", 'r'), ""
    for i in range(4):
        high = scores.readline()
        if i == int(mode) and int(score) => int(high):
            out = "New Highscore!"
            print "high score:", i, score
            try:
                allhigh += str(score)+"\n"
            except:
                allhigh = str(score)+"\n"
        #not highscore
        else:
            try:
                allhigh += str(high)
            except:
                allhigh = str(high)
        if i == int(mode) and int(score) < int(high):
            out = "Global high score: "+str(high)
    scores.close()
    thisplayer.sendinfo(out)
    scores = open("high.txt", 'w')
    scores.write(allhigh)
    scores.close()
    del allhigh
