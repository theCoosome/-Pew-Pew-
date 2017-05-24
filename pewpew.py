import sys
import time
import random
import pygame
import json
import math
import socket
from decimal import *
from pygame.locals import *
getcontext().prec = 2
pygame.init()
#colors
psych = False
connected, serverip, serverport = True, "174.25.72.161", 7778

Green = pygame.Color(0,255,0)
Black = pygame.Color(0,0,0)
White = pygame.Color(255,255,255)
#usefull
screenX, screenY = 250, 650
Screen = pygame.display.set_mode((screenX, screenY))
Line = pygame.draw.line
Rect = pygame.draw.rect
clock = pygame.time.Clock()
font = pygame.font.SysFont('Calibri', 15)
OP = False
#things

wall1 = pygame.image.load('imgs/pewpew_wall1.png')
wall2 = pygame.image.load('imgs/pewpew_wall2.png')
wall3 = pygame.image.load('imgs/pewpew_wall3.png')
wall4 = pygame.image.load('imgs/pewpew_enm_1.png')
wall5 = pygame.image.load('imgs/pewpew_enm2.png')
wall6 = pygame.image.load('imgs/pewpew_enm3.png')
pewpic = pygame.image.load('imgs/boolet.png')
drillpic = pygame.image.load('imgs/gundrill.png')
railpic = pygame.image.load('imgs/gunrail.png')
shieldpic = pygame.image.load('imgs/gunshield.png')
lazerpic = pygame.image.load('imgs/gunlazer.png')
hypershieldpic = pygame.image.load('imgs/hypershield.png')
backimage = pygame.image.load('imgs/pewpew_backdrop.png')
powerpic = pygame.image.load('imgs/powerup.png')
shippng = pygame.image.load('imgs/pewpewship.png')
dmgpng = pygame.image.load('imgs/damagepew.png')
upgradepng = pygame.image.load('imgs/powerup.png')

#other

debugon = False
def prints(stuff):
    global debugon
    if debugon:
        print stuff

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


class multipliers(object):
    def __init__(self, difficulty, hp, speed, cooldown, meteors, time):
        self.difficulty = difficulty
        self.hp = hp
        self.speed = speed
        self.cooldown = cooldown
        self.meteors = meteors
        self.time = time


def getpartimg(name, quant):
	images = []
	for i in range(quant):
		images.append(pygame.image.load('anim/{}/{}.png'.format(name, i)))
	return images
	
explosionpic = getpartimg("explosion", 5)
crumblepic = getpartimg("destintegrate", 4)
firebit = getpartimg("firebit", 11)

retimer = 5
class particle(object): #speed is tuple of x and y speed
	def __init__(self, coords, size, move, pics):
		self.frame = len(pics)-1
		self.coords = [coords[0]-(size[0]/2), coords[1]-(size[1]/2)]
		self.size = size
		self.move = move
		self.pics = pics
		global retimer
		self.timer = retimer
			
class proj(object):
	def __init__(self, hp, coords, size, speed, move, damage, pic):
		self.hp = hp
		self.basehp = hp
		self.coords = coords
		self.size = size
		self.speed = speed
		self.move = move
		self.dmg = damage
		self.pic = pic

class gun(object):
	def __init__(self, id, hpmod, hp, fires, size, speed, move, damage, cooldown, pic):
		self.hp = hp
		self.hpmod = hpmod
		self.fires = 0
		self.maxfires = fires-1
		self.size = size
		self.speed = speed
		self.move = move
		self.dmg = damage
		self.id = id
		self.cooldown = cooldown
		self.pic = pic

gunbase = gun("Pew Gun", 0, 1, 99999, (2, 5), 3, 2, 1, 25, pewpic)
gunrail = gun("Railgun", 1, 2, 18, (2, 10), 10, 10, 15, 28, railpic)
gunlazer = gun("Lazer Beam", 1, 1, 50, (2, 4), 5, 2, 1, 0, lazerpic)
gundrill = gun("Drill Launcher", 2, 15, 5, (6, 10), 2, 1, 5, 40, drillpic)
gunshield = gun("Shield Thrower", 10, 20, 1, (20, 5), 1, 1, 1, 50, shieldpic)
guntommy = gun("Tommy Gun", 2, 1, 80, (2, 2), 4, 3, 2, 15, pewpic)
gunop = gun("God gun", 50, 100, 1000, (50, 5), 6, 2, 30, 0, hypershieldpic)
gunwall = gun("Wall Placer", 1, 55, 1, (50, -5), 6, 0, 1, 50, hypershieldpic)
upgrades = [gunrail, gunlazer, gundrill, gunshield, guntommy, gunwall]
			
class upgrade(object):
	def __init__(self, coords, interval):
		self.coords = coords
		self.size = (15, 15)
		self.interval = interval
		self.speed = interval
		global upgradepng
		self.pic = upgradepng

class ships(object):
	def __init__(self, hp, coords, size, speed):
		self.hp = hp
		self.basehp = hp
		self.coords = coords
		self.size = size
		self.speed = speed
		self.dmg = 1
		self.mom = 0
		self.move = 0
		self.gun = 0
		
class Boss(object):
	def __init__(self, id, hp, dmg, size, speed, atkint, pic):
		self.id = id
		self.hp = hp
		self.dmg = dmg
		self.basehp = hp
		self.coords = ((screenX/2)-(size[0]/2), -size[1])
		self.size = size
		self.atkint = atkint
		self.speed = speed
		self.pic = pic
		self.on = 0
		
class meteor(object):
	def __init__(self, hp, coords, speed):
		self.hp = hp
		self.coords = coords
		self.size = (10, 10)
		self.speed = speed
		self.dmg = 1
		self.timer = random.randint(0, 300-((hp-3)*30))
		self.timerBase = 300-((hp-3)*30)
		
class timers(object):
	def __init__(self):
		self.guncool = -30
		self.meteors = 5
		self.time = 0
		self.move = 1
		self.movecheck = 0
		self.backdrop = 100
		self.bossatk = 300
		self.powerup = 400
		
#object one coord pair, size, object two coord pair and size
def collide(p1, p2, p3, p4):
	#if right side is right of left side, and left side left of right side
	if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
		#if bottom is below top and top is above bottom
		if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1]:
			return True
		

AllMeteors = [[
	[2, [1, 2, 1],[2, 3, 2],[1, 2, 1]],
	
	[1, [0, 0, 1, 1, 0, 0],
	[0, 1, 2, 2, 1, 0],
	[1, 2, 2, 3, 2, 1],
	[0, 1, 1, 2, 1, 0],
	[0, 0, 0, 1, 0, 0]],
	
	[1, [0, 0, 0, 0, 1, 1, 1],
	[0, 0, 0, 1, 2, 2, 1],
	[0, 0, 1, 2, 3, 1, 0],
	[0, 0, 1, 3, 2, 1, 0],
	[0, 1, 2, 3, 4, 2, 0],
	[1, 1, 3, 4, 2, 1, 0],
	[1, 2, 2, 2, 1, 0, 0],
	[0, 1, 1, 1, 0, 0, 0]
	],
	
	[3, [0, 1, 0, 0],
	[0, 0, 0, 0], 
	[0, 0, 1, 0],
	[0, 1, 2, 0],
	[2, 3, 3, 2],
	[3, 3, 3, 2],
	[3, 4, 3, 3],
	[2, 3, 2, 2],
	[0, 2, 3, 0]],
	
	[2, [0, 1, 0],
	[0, 0, 0],
	[1, 0, 0],
	[0, 0, 1],
	[0, 1, 0],
	[1, 2, 0],
	[2, 3, 2],
	[3, 3, 3],
	[1, 3, 1]],
	
	[1, [0, 0, 0, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 0, 0],
	[0, 1, 0, 1, 0, 0, 0],
	[0, 0, 0, 1, 1, 0, 0],
	[0, 1, 0, 0, 0, 0, 1],
	[0, 0, 0, 0, 0, 0, 0],
	[1, 0, 1, 0, 1, 0, 0],
	[0, 0, 0, 0, 0, 1, 0],
	[1, 0, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1],
	[0, 1, 0, 1, 0, 0, 0]],
	
	[1, [0, 1, 1, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 1, 0],
	[0, 1, 0, 1, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 1, 1, 0],
	[0, 1, 0, 0, 1, 1, 0],
	[1, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1],
	[0, 1, 0, 0, 1, 0, 0],
	[0, 0, 0, 1, 0, 1, 0]],

	[1, [0, 0, 0, 0, 1, 0, 0],
	[0, 1, 0, 0, 0, 0, 0],
	[0, 0, 0, 1, 0, 0, 1],
	[1, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0]],
	
	[2, [0, 1, 1, 0],
	[1, 1, 1, 1],
	[1, 1, 1, 1],
	[0, 1, 1, 0]],
	
	[1, [0, 1, 1, 0],
	[1, 2, 2, 1],
	[1, 2, 2, 1],
	[0, 1, 1, 0]],
	
	[2, [1, 1], [1, 1]],
	[1, [1, 1], [1, 1]]
], [
	[2, [1, 2, 1],[2, 3, 2],[1, 2, 1]],
	
	[1, [0, 0, 1, 1, 0, 0],
	[0, 1, 2, 2, 1, 0],
	[1, 2, 2, 3, 2, 1],
	[0, 1, 1, 2, 1, 0],
	[0, 0, 0, 1, 0, 0]],
	
	[1, [0, 0, 0, 0, 1, 1, 1],
	[0, 0, 0, 1, 2, 2, 1],
	[0, 0, 1, 2, 3, 1, 0],
	[0, 0, 1, 3, 2, 1, 0],
	[0, 1, 2, 3, 4, 2, 0],
	[1, 1, 3, 4, 2, 1, 0],
	[1, 2, 2, 2, 1, 0, 0],
	[0, 1, 1, 1, 0, 0, 0]
	],
	
	[3, [0, 1, 0, 0],
	[0, 0, 0, 0], 
	[0, 0, 1, 0],
	[0, 1, 2, 0],
	[2, 3, 3, 2],
	[3, 3, 3, 2],
	[3, 5, 3, 3],
	[2, 3, 2, 2],
	[0, 2, 3, 0]],
	
	[3, [0, 1, 0],
	[0, 0, 0],
	[1, 0, 0],
	[0, 0, 1],
	[0, 1, 0],
	[1, 2, 0],
	[2, 3, 2],
	[3, 3, 3],
	[1, 3, 1]],
	
	[1, [0, 0, 0, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 0, 0],
	[0, 1, 0, 1, 0, 0, 0],
	[0, 0, 0, 1, 1, 0, 0],
	[0, 1, 0, 0, 0, 0, 1],
	[0, 0, 0, 0, 0, 0, 0],
	[1, 0, 1, 0, 1, 0, 0],
	[0, 0, 0, 0, 0, 1, 0],
	[1, 0, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1],
	[0, 1, 0, 1, 0, 0, 0]],
	
	[1, [0, 1, 1, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 1, 0],
	[0, 1, 0, 1, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 1, 1, 0],
	[0, 1, 0, 0, 1, 1, 0],
	[1, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1],
	[0, 1, 0, 0, 1, 0, 0],
	[0, 0, 0, 1, 0, 1, 0]],
	
	[2, [0, 1, 1, 0],
	[1, 1, 1, 1],
	[1, 1, 1, 1],
	[0, 1, 1, 0]],
	
	[1, [0, 1, 1, 0],
	[1, 2, 2, 1],
	[1, 2, 2, 1],
	[0, 1, 1, 0]],
	
	[2, [1, 1], [1, 1]],
	[1, [1, 1], [1, 1]]
],[
	[2, [1, 2, 1],[2, 3, 2],[1, 2, 1]],
	
	[1, [0, 0, 1, 1, 0, 0],
	[0, 1, 2, 2, 1, 0],
	[1, 2, 2, 3, 2, 1],
	[0, 1, 1, 2, 1, 0],
	[0, 0, 0, 1, 0, 0]],

	[2, [0, 0, 1, 1, 0, 0],
	[0, 1, 2, 2, 1, 0],
	[1, 2, 2, 3, 2, 1],
	[0, 1, 1, 2, 1, 0],
	[0, 0, 0, 1, 0, 0]],
	
	[1, [0, 1, 1, 0, 0, 0, 0],
	[0, 1, 2, 1, 0, 0, 0],
	[0, 1, 2, 3, 1, 0, 0],
	[0, 1, 3, 2, 1, 0, 0],
	[0, 1, 2, 3, 4, 2, 0],
	[1, 1, 4, 3, 2, 1, 0],
	[1, 2, 2, 2, 1, 0, 0],
	[0, 0, 1, 1, 1, 0, 0]
	],
	
	[3, [0, 1, 0, 0],
	[0, 0, 0, 0], 
	[0, 0, 1, 0],
	[0, 1, 2, 0],
	[2, 3, 3, 2],
	[3, 3, 3, 2],
	[3, 6, 3, 3],
	[2, 3, 2, 2],
	[0, 2, 3, 0]],
	
	[3, [0, 1, 0],
	[0, 0, 0],
	[1, 0, 0],
	[0, 0, 1],
	[0, 1, 0],
	[1, 2, 0],
	[2, 3, 2],
	[3, 3, 3],
	[1, 3, 1]],
	
	[1, [0, 0, 0, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 0, 0],
	[0, 1, 0, 1, 0, 0, 0],
	[0, 0, 0, 1, 1, 0, 0],
	[0, 1, 0, 0, 0, 0, 1],
	[0, 0, 0, 0, 0, 0, 0],
	[1, 0, 1, 0, 1, 0, 0],
	[0, 0, 0, 0, 0, 1, 0],
	[1, 0, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1],
	[0, 1, 0, 1, 0, 0, 0]],
	
	[1, [0, 2, 1, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 1, 0],
	[0, 1, 0, 1, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 2, 1, 0],
	[0, 1, 0, 0, 1, 2, 0],
	[2, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1],
	[0, 1, 0, 0, 1, 0, 0],
	[0, 0, 0, 1, 0, 1, 0]],
	
	[2, [0, 1, 1, 0],
	[1, 1, 1, 1],
	[1, 1, 1, 1],
	[0, 1, 1, 0]],
	
	[1, [0, 1, 1, 0],
	[1, 2, 2, 1],
	[1, 2, 2, 1],
	[0, 1, 1, 0]],
	
	[2, [1, 1], [1, 1]],
	[1, [1, 1], [1, 1]]
],[
	[2, [1, 2, 1],[2, 3, 2],[1, 2, 1]],
	
	[1, [0, 0, 1, 1, 0, 0],
	[0, 1, 2, 2, 1, 0],
	[1, 2, 2, 3, 2, 1],
	[0, 1, 1, 2, 1, 0],
	[0, 0, 0, 1, 0, 0]],
	
	[1, [0, 0, 0, 0, 1, 1, 1],
	[0, 0, 0, 1, 2, 2, 1],
	[0, 0, 1, 2, 3, 1, 0],
	[0, 0, 1, 3, 2, 1, 0],
	[0, 1, 2, 3, 4, 2, 0],
	[1, 1, 3, 4, 2, 1, 0],
	[1, 2, 2, 2, 1, 0, 0],
	[0, 1, 1, 1, 0, 0, 0]
	],
	
	[5, [1]],
	
	[3, [0, 1, 0],
	[0, 0, 0],
	[1, 0, 0],
	[0, 0, 1],
	[0, 1, 0],
	[1, 2, 0],
	[2, 3, 2],
	[3, 3, 3],
	[1, 3, 1]],
	
	[1, [0, 0, 0, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 0, 0],
	[0, 1, 0, 1, 0, 0, 0],
	[0, 0, 0, 1, 1, 0, 0],
	[0, 1, 0, 0, 0, 0, 1],
	[0, 0, 0, 0, 0, 0, 0],
	[1, 0, 1, 0, 1, 0, 0],
	[0, 0, 0, 0, 0, 1, 0],
	[1, 0, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1],
	[0, 1, 0, 1, 0, 0, 0]],
	
	[1, [0, 1, 1, 0, 1, 0, 0],
	[0, 0, 1, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 1, 0],
	[0, 1, 0, 1, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 1, 1, 0],
	[0, 1, 0, 0, 1, 1, 0],
	[1, 0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0, 1],
	[0, 1, 0, 0, 1, 0, 0],
	[0, 0, 0, 1, 0, 1, 0]],
	
	[2, [0, 1, 1, 0],
	[1, 1, 1, 1],
	[1, 1, 1, 1],
	[0, 1, 1, 0]],
	
	[1, [0, 1, 1, 0],
	[1, 2, 2, 1],
	[1, 2, 2, 1],
	[0, 1, 1, 0]],
	
	[2, [1, 1], [1, 1]],
	[1, [1, 1], [1, 1]]
  ]]
#-
def genMeteor(thisMet, mod):
	speed = thisMet[0]
	for h in range(len(thisMet)):
		if h != 0:
			for w in range(len(thisMet[h])):
				temp = thisMet[h][w]
				if temp != 0:
					boolet = meteor(temp, (w*10+mod[0], h*10+mod[1]), speed)#--------------------------------------------------------------------------make time mod
					meteors.append(boolet)
		
def shoot():
	global ship
	global projectiles
	global timer
	#print "pew"
	timer.guncool = ship.gun.cooldown
	temp = proj(ship.gun.hp, (ship.coords[0]+(ship.size[0]/2)-(ship.gun.size[0]/2), ship.coords[1]-1), ship.gun.size, ship.gun.speed, ship.gun.move, ship.gun.dmg, ship.gun.pic)
	projectiles.append(temp)
	ship.gun.fires += 1
	if ship.gun.fires > ship.gun.maxfires:
		global gunbase
		equip(gunbase)

def equip(weapon):
	global ship
	weapon.fires = 0
	ship.gun = weapon
	ship.hp += weapon.hpmod
	
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def calcEff():
	global allshots
	global pershots
	global bossesbeat
	global mult
	global metdestroyed
	global timer
	global s
	try:
		efficiency = float(allshots - pershots)/float(allshots)
	except ZeroDivisionError:
		efficiency = 1
	score, keeping = timer.time + math.floor(10 * metdestroyed * efficiency) + ((mult.difficulty+1) * 500 * bossesbeat), True
	score, nscore = str(score), ""
	for i in score:
		if i == ".":
			keeping = False
		if keeping:
			nscore += i
	score = int(nscore)
	prints("your score: "+str(score)+"\nYour tier: "+str(mult.difficulty))
	if OP:
		out = "You were opped. High scores not counted."
	else:
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((serverip, serverport))
		print "Connected"
		sendinfo(str(mult.difficulty)+" "+str(int(score)))
		out = myreceive()
		out = out[:len(out)-1]
		#s.shutdown(SHUT_RDWR)
		s.close()
	return out, score, efficiency
		
		
print "setup complete."
#Version
print "pewpew version 0.3"

Looping = True
while Looping:
	Running = True
	while Running:
		Screen.fill(Black)
		dialog = font.render("Pew Pew", True, White)
		Screen.blit(dialog, [70,25])
		dialog = font.render("Use left and right arrows to move", True, White)	
		Screen.blit(dialog, [0,50+20])
		dialog = font.render("Up arrow to fire weapons.", True, White)	
		Screen.blit(dialog, [0,50+20+20])
		dialog = font.render("Collect Poweups to upgrade your ship", True, White)	
		Screen.blit(dialog, [0,50+20+20+20])
		Screen.blit(powerpic, [screenX/2-20,50+80])
		dialog = font.render("Avoid meteors, and especially camps.", True, White)	
		Screen.blit(dialog, [0,50+100])
		Screen.blit(wall1, [60,50+120])
		Screen.blit(wall5, [200,50+120])
		dialog = font.render("See your stats at bottom of screen.", True, White)	
		Screen.blit(dialog, [0,50+140])
		dialog = font.render("Press an arrow key to select difficulty", True, White)	
		Screen.blit(dialog, [0,300])
		dialog = font.render("difficulty increases clockwise,", True, White)	
		Screen.blit(dialog, [0,300+16])
		dialog = font.render("from left as easy to down as impossible.", True, White)	
		Screen.blit(dialog, [0,300+32])
		dialog = font.render("And look out for someone at 10000m...", True, White)	
		Screen.blit(dialog, [0,500])
		
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				#movement
				if event.key == K_LEFT:
					Running = False
					mult = multipliers(0, 1, 1, 1, 28, 1)
				if event.key == K_UP:
					Running = False
					mult = multipliers(1, 2, 2, 2, 18, 2)
				if event.key == K_RIGHT:
					Running = False
					mult = multipliers(2, 3.5, 3, 2, 10, 4)
				if event.key == K_DOWN:
					Running = False
					mult = multipliers(3, 40, 5, 5, 8, 10)
		pygame.display.update()
		clock.tick(60)


	Screen.fill(Black)
	Line(Screen, Green, (0,0), (600,600), 3)
	pygame.display.update()
	print "updated screen"

	particles = []
	projectiles = []
	powerups = []
	powerups.append(upgrade(((screenX/2)-7, 50), 1))
	ship = ships(4, ((screenX/2)-15, 500), (6, 10), 1)
	boss1 = Boss(1, 200*mult.hp, 10, (150, 50), 10, 500/mult.cooldown, pygame.image.load('imgs/pewpew_enmBoss.png'))
	bossstufff = [1, 200, 10, (150, 50), 10, 500]
	boss = boss1
	bossesbeat = 0
	meteors = []
	for i in range(5):
		boolet = meteor(1, (random.randint(0,25)*10, 10), random.randint(1, 2))
		meteors.append(boolet)
	timer = timers()
	Meteors = AllMeteors[mult.difficulty]
	

	if mult.difficulty == 3:
		equip(upgrades[random.randint(0, len(upgrades)-1)])
	else:
		equip(gunbase)
	t = 100
	eventTimer = 10000
	walls = 0
	bosstime = 10000
	metdestroyed = 0
	pressing = False
	lefting = False
	righting = False
	shooting = False
	mommod = 2
	allshots, pershots = 0, float(0)
	alldam, potdam = 0, 0
	fps = 60
	isAlive = True
	print "setup complete."
	#Version
	print "pewpew version 0.3"

	#genMeteor(genMetor.genMetor(mult.difficulty, 5, 5, 5), (screenX/2, 20))

	#main loop
	Running = True
	while Running:
		if isAlive:
			thisship = shippng
		if timer.guncool > -1:
			timer.guncool -= 1
		if timer.guncool < 0 and shooting:
			shoot()
		timer.time += mult.time
		if timer.time == bosstime:
			boss.on = 1
			mult.meteors *= 2
			prints("Enter Boss")
		if fps < 60 and isAlive:
			fps += 1
			if fps > 60:
				fps = 60
		if not isAlive and fps > 0:
			fps -= 1
			if fps < 2:
				Running = False
		timer.meteors -= 1
		if timer.meteors <= 0:
			timer.meteors = mult.meteors
			#print "New meteor"
			genMeteor(Meteors[random.randint(0,len(Meteors)-1)], (random.randint(0-20, screenX+20), 0-100))
			
		Screen.fill(Black)
		timer.backdrop += mult.speed
		if timer.backdrop >= 0:
			timer.backdrop = screenY-1000
		Screen.blit(backimage, (0, timer.backdrop))
		
		#boolet movement
		for i in projectiles:
			if not collide(i.coords, i.size, (0, 0), (screenX, screenY)):
				pershots = Decimal(float(pershots) + float(i.hp)/float(i.basehp))
				allshots += 1
				projectiles.remove(i)
			else:
				alive = True
				for n in range(i.speed):
					i.coords = (i.coords[0], i.coords[1]-i.move)
					for x in meteors:
						if collide(i.coords, i.size, x.coords, x.size):
							particles.append(particle([x.coords[0]+(x.size[0]/2), x.coords[1]], [10, 10], [0, random.randint(x.speed-1, x.speed+1)], crumblepic))
							x.hp -= i.dmg
							i.hp -= x.dmg
							prints("Boolet: " + str(i.hp))
							if i.hp <= 0:
								Screen.blit(i.pic, i.coords)
								projectiles.remove(i)
								alive = False
								allshots += 1
							prints("Meteor: " + str(x.hp))
							if x.hp <= 0:
								meteors.remove(x)
								metdestroyed += 1
						if not alive:
							break
						else:
							if collide(i.coords, i.size, boss.coords, boss.size) and boss.on == 1:
								particles.append(particle([i.coords[0]+(i.size[0]/2), i.coords[1]-i.move], [10, 10], [0, 1], explosionpic))
								prints("hit boss")
								boss.hp -= i.dmg
								i.hp -= boss.dmg
								prints("Boolet: " + str(i.hp))
								if i.hp <= 0:
									Screen.blit(i.pic, i.coords)
									projectiles.remove(i)
									alive = False
								prints("Boss: " + str(boss.hp))
								if boss.hp <= 0:
									fps = 10
									mult.meteors /= 2
									localrand = math.floor(boss.size[0]/10)
									for z in range(9):
										pos1 = random.randint((boss.coords[0]+(z*localrand)), (boss.coords[0]+((z+1)*localrand)))
										pos2 = random.randint(boss.coords[1], (boss.coords[1]+boss.size[1]))
										particles.append(particle([pos1, pos2], [10, 10], [random.randint(-2, 2), random.randint(-1, 3)], firebit))
									boss.on = 0
									bossesbeat += 1
									rand = (500/mult.cooldown)-(bossesbeat*10)
									if rand < 10:
										rand = 10
									boss = Boss(1+bossesbeat, (300+(150*bossesbeat))*mult.hp, 5+bossesbeat, (150, 50), 10, rand, pygame.image.load('imgs/pewpew_enmBoss.png'))
									boss.coords = ((screenX/2)-(boss.size[0]/2), -boss.size[1])
									bosstime = timer.time + 6000
									
					if not alive:
						break
				try:
					if i.hp >0:
						Screen.blit(i.pic, i.coords)
				except NameError:
					pass
		
		 
		#player movement
		timer.move -= 1
		if timer.move <= 0:
			timer.move = ship.move
			ship.coords = (ship.coords[0]+ship.mom, ship.coords[1])
			if ship.coords[0] > screenX-ship.size[0]:
				ship.coords = (screenX-ship.size[0], ship.coords[1])
				print "Don't go out of Bounds!"
			if ship.coords[0] < 0:
				ship.coords = (0, ship.coords[1])
				print "Don't go out of Bounds!"
		
		
		#meteors
		for i in meteors:
			if not collide(i.coords, i.size, (0, 0-100), (screenX, screenY)):
				meteors.remove(i)
			alive = True
			if i.hp >= 4:
				i.timer -= 1
				if i.timer <= 0:
					i.timer = i.timerBase
					meteors.append(meteor(i.hp-3, i.coords, (i.hp-2)*2))
			#movement
			for n in range(i.speed):
				i.coords = (i.coords[0], i.coords[1]+mult.speed)
				if collide(ship.coords, ship.size, i.coords, i.size):
					if isAlive:
						particles.append(particle([ship.coords[0]+(ship.size[0]/2), ship.coords[1]], [10, 10], [0, 1], explosionpic))
					thisship = dmgpng
					temp = i.dmg
					i.hp -= ship.dmg
					prints("Meteor: " + str(i.hp))
					if i.hp <= 0:
						meteors.remove(i)
						metdestroyed += 2
						alive = False
					ship.hp -= temp
					prints("Ship: " + str(ship.hp))
					if ship.hp <= 0 and isAlive:
						isAlive = False
						highscore, score, efficiency = calcEff()
				if not alive:
					break
			try:
				if i.hp == 1:
					thiswall = wall1
				if i.hp == 2:
					thiswall = wall2
				if i.hp == 3:
					thiswall = wall3
				if i.hp == 4:
					thiswall = wall4
				if i.hp == 5:
					thiswall = wall5
				if i.hp == 6:
					thiswall = wall6
				Screen.blit(thiswall, i.coords)
			except NameError:
				pass
		
		
		#enemy action
		if boss.on == 1:
			timer.bossatk -= 1
			if timer.bossatk <= 0:
				timer.bossatk = boss.atkint
				genMeteor([1, [1, 2, 1, 0, 0, 0, 0, 0, 1, 2, 1], [2, 5, 2, 1, 1, 2, 1, 1, 2, 5, 2], [1, 2, 1, 1, 2, 6, 2, 1, 1, 2, 1], [0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0]], (boss.coords[0]+20, boss.coords[1]-15))
			t -= 1
			if t < 1:
				if boss.coords[0]+(boss.size[0]/2) > ship.coords[0]+(ship.size[0]/2):
					boss.coords = (boss.coords[0]-1, boss.coords[1])
				if boss.coords[0]+(boss.size[0]/2) < ship.coords[0]+(ship.size[0]/2):
					boss.coords = (boss.coords[0]+1, boss.coords[1])
				if boss.coords[0]+75 == ship.coords[0]+15:
					pass
				if boss.coords[1] < 10:
					boss.coords = (boss.coords[0], boss.coords[1]+1)
				t = boss.speed
		
		
		#user input
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				#movement
				if event.key == K_LEFT:
					ship.mom = -1 * mommod
					pressing = True
					lefting = True
				if event.key == K_RIGHT:
					ship.mom = 1 * mommod
					pressing = True
					righting = True
				if event.key == K_DOWN:
					mommod = 1
				#Weapons
				if event.key == K_UP:
					shooting = True
				if event.key == K_q:
					Running, ship.hp, isAlive = False, 0, False
					highscore, score, efficiency = calcEff()
				#OP
				if event.key == K_g:
					OP = True
					print "Opped."
				if event.key == K_b and OP:
					boss.on = 1
				if event.key == K_v and OP:
					equip(gunop)
				if event.key == K_h and OP:
					boss.hp = 1
				if event.key == K_y and OP:
					ship.hp += 5
				#debug
				if event.key == K_d:
					if debugon:
						debugon = False
					else:
						debugon = True
					print 'lazer cooldown: ', timer.guncool
					print 'Next boss: ', bosstime
					print 'Boss Cooldown: ', timer.bossatk
					print 'Boss HP: ', boss.hp
			if event.type == pygame.KEYUP:
				if event.key == K_LEFT:
					lefting = False
				if event.key == K_RIGHT:
					righting = False
				if not lefting and not righting:
					pressing = False
					ship.mom = 0
				if event.key == K_UP:
					shooting = False
				if event.key == K_DOWN:
					mommod = 2
		
		for i in powerups:
			if not collide(i.coords, i.size, (0, 0), (screenX, screenY)):
				powerups.remove(i)
			for n in range(i.speed):
				i.coords = (i.coords[0], i.coords[1]+2)
				if collide(i.coords, i.size, ship.coords, ship.size):
					powerups.remove(i)
					misc = random.randint(0, len(upgrades)-1)
					equip(upgrades[misc])
					break
				else:
					Screen.blit(i.pic, i.coords)
			
		timer.powerup -= 1
		if timer.powerup < 0:
			timer.powerup = random.randint(500/mult.cooldown, 900/mult.cooldown)
			powerups.append(upgrade((random.randint(20, screenX-20), 50), random.randint(1, 2)))
			
		if ship.hp > 0:
			isAlive = True

		if boss.on == 1:
			Screen.blit(boss.pic, boss.coords)
		Screen.blit(thisship, ship.coords)
		

		for i in particles:
			if not collide(i.coords, i.size, (0, 0), (screenX, screenY)):
				particles.remove(i)
			else:
				i.coords = (i.coords[0]+i.move[0], i.coords[1]+i.move[1])
				i.timer -= 1
				alive = True
				if i.timer == 0:
					i.frame -= 1
					i.timer = retimer
					if i.frame < 0:
						particles.remove(i)
						alive = False
				if alive:
					Screen.blit(i.pics[i.frame], i.coords)
		
		if isAlive:
			hpratio = (Decimal(ship.hp)/Decimal(ship.basehp))*100
			if hpratio >= 100:
				hpratio = float(hpratio)
			misc = "Health: "+str(hpratio)+"%"
			dialog = font.render(misc, True, White)    
			Screen.blit(dialog, [0,screenY-32])
			dialog = font.render("Meters: "+str(timer.time), True, White)
			Screen.blit(dialog, [screenX/2, screenY-32])
			if ship.gun.id > 0:
				dialog = font.render("::"+ship.gun.id, True, White)    
				Screen.blit(dialog, [0, screenY-64])
				dialog = font.render("Fires remaining: "+str(ship.gun.maxfires-ship.gun.fires+1), True, White)    
				Screen.blit(dialog, [screenX/2, screenY-64])
		else:
			pass

		pygame.display.update()
		clock.tick(fps)


	if mult.difficulty == 0:
		l1 = "You cleaned up "+str(timer.time)+" meters."
		l2, l5 = str(metdestroyed) + " meteor units sweeped ", "at "+str(math.floor(efficiency*100))+"% efficiency."
		l3 = str(bossesbeat) + " Anti-Gonists encountered."
		l4 = "Total score: " + str(score)
	if mult.difficulty == 1:
		l1 = "You cleared "+str(timer.time)+" meters."
		l2, l5 = str(metdestroyed) + " meteor units eliminated ", "at "+str(math.floor(efficiency*100))+"% efficiency."
		l3 = str(bossesbeat) + " Anti-Gonists fought."
		l4 = "Total score: " + str(score)
	if mult.difficulty == 2:
		l1 = "You trekked "+str(timer.time)+" meters!"
		l2, l5 = str(metdestroyed) + " meteor units removed ", "at "+str(math.floor(efficiency*100))+"% efficiency."
		l3 = str(bossesbeat) + " Anti-Gonists eliminated."
		l4 = "Total score: " + str(score)
	if mult.difficulty == 3:
		l1 = "You survived "+str(timer.time)+" meters!"
		l2, l5 = str(metdestroyed) + " meteor units swiped ", "at "+str(math.floor(efficiency*100))+"% efficiency."
		l3 = str(bossesbeat) + " Anti-Gonists destroyed."
		l4 = "Total score: " + str(score)

	Running = True
	while Running:
		dialog = font.render(highscore, True, White)
		Screen.blit(dialog, [5,screenY-16])
		dialog = font.render(l1, True, White) 
		Screen.blit(dialog, [5,screenY-96])
		dialog = font.render(l2, True, White) 
		Screen.blit(dialog, [5,screenY-80])
		dialog = font.render(l5, True, White) 
		Screen.blit(dialog, [5,screenY-64])
		dialog = font.render(l3, True, White) 
		Screen.blit(dialog, [5,screenY-48])
		dialog = font.render(l4, True, White) 
		Screen.blit(dialog, [5,screenY-32])
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				Running = False
		pygame.display.update()
		clock.tick(4)

	dialog = font.render("Pew Pew", True, White)    
	Screen.blit(dialog, [0,50])
