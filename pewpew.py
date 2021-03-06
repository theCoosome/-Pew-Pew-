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
Font = pygame.font.SysFont('Calibri', 30)
pygame.display.set_caption("Pew Pew")
OP = True
#things

wall1 = pygame.image.load('imgs/pewpew_wall1.png')
wall2 = pygame.image.load('imgs/pewpew_wall2.png')
wall3 = pygame.image.load('imgs/pewpew_wall3.png')
wall4 = pygame.image.load('imgs/pewpew_enm_1.png')
wall5 = pygame.image.load('imgs/pewpew_enm2.png')
wall6 = pygame.image.load('imgs/pewpew_enm3.png')
pewpic = pygame.image.load('imgs/boolet.png')
bossimg = pygame.image.load('imgs/pewpew_enmBoss.png')
drillpic = pygame.image.load('imgs/gundrill.png')
railpic = pygame.image.load('imgs/gunrail.png')
shieldpic = pygame.image.load('imgs/gunshield.png')
lazerpic = pygame.image.load('imgs/gunlazer.png')
chargepic = pygame.image.load('imgs/charged.png')
excavpic = pygame.image.load('imgs/excavator.png')
hypershieldpic = pygame.image.load('imgs/hypershield.png')
lightpic = pygame.image.load('imgs/light.png')
bombpic = pygame.image.load('imgs/bomb.png')
backimage = pygame.image.load('imgs/pewpew_backdrop.png')
powerpic = pygame.image.load('imgs/powerup.png')
shippng = pygame.image.load('imgs/pewpewship.png')
dmgpng = pygame.image.load('imgs/damagepew.png')
upgradepng = pygame.image.load('imgs/powerup.png')

#other
debugon = False
RecentDamage = 0

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
        self.hp = hp #boss hp multiplier
        self.speed = speed # meteor speed multiplier
        self.cooldown = cooldown # cooldown for upgrades and boss shots (higher is faster)
        self.meteors = meteors # cooldown between meteors
        self.time = time # distance multiplier (affects score and boss spawns)

def getpartimg(name, quant):
	images = []
	for i in range(quant):
		images.append(pygame.image.load('anim/{}/{}.png'.format(name, i)))
	return images
	
explosionpic = getpartimg("explosion", 5)
crumblepic = getpartimg("destintegrate", 4)
firebit = getpartimg("firebit", 11)
sparks = getpartimg("spark", 5)

#build the hud
backColor = (40, 40, 40)
backAccent = (50, 50, 50)
Hud = pygame.Surface((screenX, 95), pygame.SRCALPHA, 32).convert_alpha()
pygame.draw.rect(Hud, (100, 100, 100), (0, 0, screenX, 5))
pygame.draw.rect(Hud, (80, 80, 80), (0, 5, screenX, 10))
pygame.draw.rect(Hud, backAccent, (0, 42, 58, 15))
pygame.draw.rect(Hud, backAccent, (screenX, 42, -58, 15))
for i in range(0, 30):
	pygame.draw.arc(Hud, backAccent, (i/2, 42+i/2, 100-i, 50-i), 0, 1.56, 1)
	pygame.draw.arc(Hud, backAccent, (150+i/2, 42+i/2, 100-i, 50-i), 1.57, 3.14, 1)
pygame.draw.rect(Hud, backAccent, (101, 42, 8, 53))
pygame.draw.rect(Hud, backAccent, (141, 42, 8, 53))

def center(obj):
	return (obj.coords[0]+(obj.size[0]/2), obj.coords[1]+(obj.size[1]/2))

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
			
#note to future: probably can make faster by directly referencing to the gun's base object
#and grabbing it's stats. May also need to reference the modifiers if they apply
class proj(object):
	def __init__(self, hp, coords, size, speed, move):
		self.hp = hp
		self.basehp = hp
		self.coords = coords
		self.size = size
		self.speed = speed
		self.move = move
		self.dmg = 0
		self.pic = None
		self.id = None
		self.crit = 0
		self.counts = True

	def complete(self, damage, pic, id, crit, counts):
		self.dmg = damage
		self.pic = pic
		self.id = id
		self.crit = crit
		self.counts = counts

#temp = proj(ship.gun.hp, (ship.coords[0]+(ship.size[0]/2)-(ship.gun.size[0]/2), ship.coords[1]-1), ship.gun.size, ship.gun.speed, ship.gun.move, ship.gun.dmg, ship.gun.pic, ship.gun.id)

class gun(object):
	def __init__(self, id, hpmod, hp, fires, size, speed, move, damage, cooldown, pic):
		self.hp = hp
		self.hpmod = hpmod
		self.fires = 0
		self.maxfires = fires-1
		self.size = size
		self.speed = speed #times to loop
		self.move = move #ammount to move each loop
		self.dmg = damage
		self.id = id
		self.cooldown = cooldown
		self.pic = pic
		self.ban = False # if this weapon is not supported
		self.crit = 1
		self.screenCount = True #if this weapon counts against bullet efficiency
	def setBonus(self, ban, crit = 1, counts = True):
		self.ban = ban
		self.crit = crit
		self.screenCount = counts;
	def makeProj(self, shipCoords):

		temp = proj(self.hp, (ship.coords[0]+(ship.size[0]/2)-(ship.gun.size[0]/2), ship.coords[1]-1), self.size, self.speed, self.move)
		temp.complete(self.dmg, self.pic, self.id, self.crit, self.screenCount)
		return temp

gunbase = gun("Pew Gun", 0, 1, 99999, (2, 5), 3, 2, 1, 25, pewpic)
gunrail = gun("Railgun", 1, 2, 10, (2, 10), 10, 10, 25, 28, railpic)
Gunrail = gun("Scientific", -2, 2000, 2, (30, 30), 50, 10, 30, 60, chargepic)
Gunrail.setBonus(True, 1, False) #destructive to ship
#gunlazer = gun("Lazer Beam", 1, 1, 50, (2, 4), 5, 2, 1, 0, lazerpic) #Time dialator
pewlazer = gun("Laser Beam", 0, 1, 220, (2, 10), 50, 10, 0.5, -1, lightpic)
Gunlazer = gun("Decimator", -1, 1, 220, (4, 10), 50, 10, 1, -1, lightpic)
GunGod = gun("Ender", -50, 200, 300, (20, 500), 1, 500, 1, -1, chargepic)
GunGod.setBonus(True, 0.25, False) #don't fall to ender spam and -1000 hp
gunbomb = gun("Bomb Launcher", 2, 4, 6, (4, 4), 2, 1, 1, 30, bombpic)
gunbomb.setBonus(True, 0.8)
Gunbomb = gun("Nuclear Charge", 2, 4, 1, (4, 4), 1, 2, 1, 30, bombpic)
Gunbomb.setBonus(False, 0.8)

gundrill = gun("Drill Launcher", 2, 15, 5, (6, 10), 2, 1, 5, 40, drillpic)
Gundrill = gun("Excavator", 3, 200, 1, (30, 30), 1, 1, 1, 40, excavpic)
Gundrill.setBonus(False, 1, False)
gunshield = gun("Shield Thrower", 10, 20, 1, (20, 5), 1, 1, 1, 50, shieldpic)
Gunbarrer = gun("Shielding", 20, 10, 1, (20, 5), 1, 1, 1, 50, shieldpic)
guntommy = gun("Tommy Gun", 2, 1, 80, (2, 2), 4, 3, 2, 15, pewpic)
guntommy.setBonus(True, 6) #bootleg
Gungatling = gun("Gatling", 2, 1, 200, (2, 4), 3, 5, 2, 10, pewpic)
Gungatling.setBonus(False, 8)
gunop = gun("God gun", 50, 100, 1000, (50, 5), 6, 2, 30, 0, hypershieldpic)
gunwall = gun("Wall Placer", 1, 56, 1, (50, 20), 1, 5, 1, 50, hypershieldpic)
gunwall.setBonus(False, 0.5) #lessen passive crit gen (health op much)
Gunwall = gun("Defender", 2, 20, 1, (20, 10), 1, 3, 1, 50, shieldpic)
#gunwall.setBonus(False, 0.5)

gunreduce = gun("Reducer", 1, 10000, 1, (screenX*2, screenY), 1, screenY, 1, 1, backimage)
gunreduce.setBonus(True, 1, False) #not confirmed safe

upgrades = [gunrail, pewlazer, gundrill, gunshield, guntommy, gunwall, gunbomb]
supers = [Gunrail, Gunlazer, Gundrill, Gunbarrer, Gungatling, Gunwall, Gunbomb, gunreduce]
			
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
		self.neardead = 0.0
		
#object one coord pair, size, object two coord pair and size
def collide(p1, p2, p3, p4):
	#if right side is right of left side, and left side left of right side
	if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1]:
		#if bottom is below top and top is above bottom
		if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
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
	], [
		[1, [0, 1, 2, 2, 1, 0],
		[1, 2, 3, 3, 2, 1],
		[2, 3, 3, 3, 3, 2],
		[2, 3, 3, 3, 3, 2],
		[1, 2, 3, 3, 2, 1],
		[0, 1, 2, 2, 1, 0]],
		
		[1, [2, 2],
		[2, 2, 2],
		[0, 2, 2, 2],
		[0, 0, 2, 2, 2],
		[0, 0, 0, 2, 2, 2],
		[0, 0, 0, 0, 2, 2, 2],
		[0, 0, 0, 0, 0, 2, 2, 2],
		[0, 0, 0, 0, 0, 0, 2, 2]],
		
		[1, [2, 2],
		[2, 2],
		[2, 2],
		[2, 2],
		[2, 2],
		[2, 2]],
		
		[1, [1]]
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
	#temp = proj(ship.gun.hp, (ship.coords[0]+(ship.size[0]/2)-(ship.gun.size[0]/2), ship.coords[1]-1), ship.gun.size, ship.gun.speed, ship.gun.move, ship.gun.dmg, ship.gun.pic, ship.gun.id)
	temp = ship.gun.makeProj(ship.coords)
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
	global psych
	try:
		efficiency = float(allshots - pershots)/float(allshots)
	except ZeroDivisionError:
		efficiency = 1
	score, keeping = timer.time + math.floor(10 * metdestroyed * efficiency) + ((mult.difficulty+1) * 500 * bossesbeat), True
	if psych:
		score = math.floor(score * 1.5)
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
print "pewpew version 0.3.1"

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
					mult = multipliers(0, 1, 1.5, 1, 28, 1) #18:1
				if event.key == K_UP:
					Running = False
					mult = multipliers(1, 2, 2, 2, 20, 2) #14:1
				if event.key == K_RIGHT:
					Running = False
					mult = multipliers(2, 3.5, 3, 2, 10, 4) #25:1
				if event.key == K_DOWN:
					Running = False
					mult = multipliers(3, 40, 5, 5, 8, 10) #12.5:1
				if event.key == K_t: #testing. some regular shaped meteors
					Running = False
					mult = multipliers(4, 2, 2, 2, 50, 1)
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
	

	if mult.difficulty == 2:
		equip(Gunbarrer)
	elif mult.difficulty == 3:
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
	hasDefender = False
	mommod = 2
	allshots, pershots = 0, float(0)
	alldam, potdam = 0, 0
	fps = 60
	isAlive = True
	RecentDamage = 0
	crit = 0
	buttonPush = 0
	print "Let the game begin."
	#Version
	print "pewpew version 0.3"
	localrand = False
	
	def killBoss():
		global fps
		global mult
		global boss
		global particles
		global bossesbeat
		global bosstime
		global timer
		
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
		boss = Boss(1+bossesbeat, (300+(150*bossesbeat))*mult.hp, 5+bossesbeat, (150, 50), 10, rand, bossimg)
		boss.coords = ((screenX/2)-(boss.size[0]/2), -boss.size[1])
		bosstime = timer.time + 6000

	#genMeteor(genMetor.genMetor(mult.difficulty, 5, 5, 5), (screenX/2, 20))

	#main loop
	Running = True
	while Running:
		if not psych:
			Screen.fill(Black) #Reset screen
			timer.backdrop += mult.speed
			if timer.backdrop >= 0:
				timer.backdrop = screenY-1000
			Screen.blit(backimage, (0, timer.backdrop))
					
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
			timer.neardead += 1/float(fps) #seconds? probably. 1/60th of a second at 60 fps to 1/1 at 1 fps
			if fps < 2:
				Running = False
		#add near death counter?
				
		timer.meteors -= 1
		if timer.meteors <= 0:
			timer.meteors = mult.meteors
			#print "New meteor"
			genMeteor(Meteors[random.randint(0,len(Meteors)-1)], (random.randint(0-20, screenX+20), 0-100))
		if timer.time % 12 == 0 and RecentDamage > 0:
			RecentDamage -= 1
			if RecentDamage < 1:
				RecentDamage = 0
			if RecentDamage > 60 and not (ship.gun.id in [Gungatling.id, guntommy.id]):
				RecentDamage -= 2
				if RecentDamage > 300:
					RecentDamage -= 2
		
		#player movement
		timer.move -= 1
		if timer.move <= 0:
			timer.move = ship.move
			ship.coords = (ship.coords[0]+ship.mom, ship.coords[1])
			if ship.coords[0] > screenX-ship.size[0]:
				ship.coords = (screenX-ship.size[0], ship.coords[1])
			if ship.coords[0] < 0:
				ship.coords = (0, ship.coords[1])
			for i in projectiles:
				if i.id == "Defender":
					i.coords = (ship.coords[0] - 7, i.coords[1])
				
		if isAlive:
			thisship = shippng
		if timer.guncool > -1:
			timer.guncool -= 1
		if timer.guncool < 0 and shooting:
			shoot()
				
		#boolet movement
		for i in projectiles:
			if not collide(i.coords, i.size, (0, 0), (screenX, screenY)):
				if i.counts:
					pershots = Decimal(float(pershots) + float(i.hp)/float(i.basehp))
				else:
					#pershots = Decimal(float(pershots) + float(i.basehp)-float(i.hp))
					pass #I don't remember how this works
				allshots += 1
				projectiles.remove(i)
			else:
				alive = True
				if i.id == "Skipper":
					if boss.on:
						mult.meteors /= 2
						localrand = math.floor(boss.size[0]/10)
						boss.on = 0
						rand = (500/mult.cooldown)-(bossesbeat*10)
						if rand < 10:
							rand = 10
						boss = Boss(1+bossesbeat, (300+(150*bossesbeat))*mult.hp, 5+bossesbeat, (150, 50), 10, rand, bossimg)
						boss.coords = ((screenX/2)-(boss.size[0]/2), -boss.size[1])
						bosstime = timer.time + 6000

				for n in range(i.speed):
					i.coords = (i.coords[0], i.coords[1]-i.move)
					if i.id in ["Wall Placer", "Defender"]:
						if i.move > 0:
							i.move -= 1
						if i.move == 0:
							i.speed = 4
					for x in meteors:
						if collide(i.coords, i.size, x.coords, x.size):
							particles.append(particle(center(x), [10, 10], [0, random.randint(x.speed-1, x.speed+1)], crumblepic))
							RecentDamage += (i.dmg*i.crit) if x.hp > i.dmg else (x.hp*i.crit)
							x.hp -= i.dmg
							i.hp -= x.dmg
							prints("Boolet: " + str(i.hp))
							if i.hp <= 0:
								Screen.blit(i.pic, i.coords)
								alive = False
								allshots += 1
								if i.id == "Defender":
									hasDefender = False
									particles.append(particle(center(i), [10, 10], [random.randint(-1, 1), random.randint(-1, 1)], sparks))
								if i.id == "Wall Placer":
									misc = center(i)
									particles.append(particle([misc[0]-random.randint(1, 10), 2], [10, 10], [random.randint(-1, 1), random.randint(-1, 1)], sparks))
									particles.append(particle([misc[0], 2], [10, 10], [random.randint(-1, 1), random.randint(-1, 1)], sparks))
									particles.append(particle([misc[0]+random.randint(1, 10), 2], [10, 10], [random.randint(-1, 1), random.randint(-1, 1)], sparks))
							prints("Meteor: " + str(x.hp))
							if x.hp <= 0:
								meteors.remove(x)
								metdestroyed += 1
						if not alive:
							break
					
					if alive:
						if collide(i.coords, i.size, boss.coords, boss.size) and boss.on == 1:
							particles.append(particle([i.coords[0]+(i.size[0]/2), i.coords[1]-i.move], [10, 10], [0, 1], explosionpic))
							prints("hit boss")
							RecentDamage += (i.dmg*i.crit) if x.hp > i.dmg else (x.hp*i.crit)
							boss.hp -= i.dmg
							i.hp -= boss.dmg
							prints("Boolet: " + str(i.hp))
							if i.hp <= 0:
								Screen.blit(i.pic, i.coords)
								alive = False
							prints("Boss: " + str(boss.hp))
							if boss.hp <= 0:
								killBoss()
					else:
						break
						
				if i.id in ["Wall Placer", "Defender"]: #draw hp lines / regen
					hpratio = Decimal(i.hp)/Decimal(i.basehp)
					pygame.draw.aaline(Screen, (max(225-225*hpratio, 0), max(225*hpratio, 0), 0), (i.coords[0], i.coords[1]+5), (i.coords[0]+int(hpratio*i.size[0]/2), i.coords[1]+5), True)
					pygame.draw.aaline(Screen, (max(225-225*hpratio, 0), max(225*hpratio, 0), 0), (i.coords[0]+i.size[0], i.coords[1]+5), (i.coords[0]+i.size[0]-int(hpratio*i.size[0]/2), i.coords[1]+5), True)
					if i.hp < i.basehp:
						i.hp += 0.5
						if i.hp < i.basehp * (5-mult.difficulty)/4:
							i.hp -= 0.25
				if i.id == "Laser Beam": #draw line
					pygame.draw.line(Screen, (130, 0, 0), (ship.coords[0]+2, ship.coords[1]), (ship.coords[0]+2, i.coords[1]), 2)
				if i.id == "Decimator": #draw line
					pygame.draw.line(Screen, (200, 0, 0), (ship.coords[0]+2, ship.coords[1]), (ship.coords[0]+2, i.coords[1]), 4)
				if i.id == "Ender": #draw lines
					pygame.draw.line(Screen, (100, 0, 0), (ship.coords[0]+2, ship.coords[1]-10), (ship.coords[0]+2, 0), 20)
					pygame.draw.line(Screen, (200, 0, 0), (ship.coords[0]+2, ship.coords[1]), (ship.coords[0]+2, 0), 4)
				if i.id == "Scientific": #draw lines
					pygame.draw.line(Screen, (90, 70, 70), (ship.coords[0]+2, ship.coords[1]-10), (ship.coords[0]+2, 0), 30)
					pygame.draw.line(Screen, (255, 255, 255), (ship.coords[0]+2, ship.coords[1]), (ship.coords[0]+2, 0), 2)
				Screen.blit(i.pic, i.coords)
				if not alive:
					if i.id in ["Bomb Launcher", "Nuclear Charge"]:
						if i.id == "Nuclear Charge":
							B = 3 #boost
						else:
							B = 1
						localrand2 = len(meteors)
						#particles
						#Boss
						BR = (i.coords[0]-58*B, i.coords[1]-58*B) #blast radius
						if collide(BR, (120*B, 120*B), boss.coords, boss.size) and boss.on:
							Xover = max(0, min(boss.coords[0]+boss.size[0], BR[0]+120*B)-max(boss.coords[0], BR[0]))
							Yover = max(0, min(boss.coords[1]+boss.size[1], BR[1]+120*B)-max(boss.coords[1], BR[1]))
							overlap = Xover * Yover
							#print overlap
							RecentDamage += i.crit*B*overlap/100 if boss.hp > overlap/100 else boss.hp*i.crit
							boss.hp -= B*overlap/100
							if boss.hp <= 0:
								killBoss()
						
						pygame.draw.circle(Screen, (200, 200, 200, 0.05), center(i), 60*B)
						pygame.draw.circle(Screen, (250, 250, 250, 0.1), center(i), 35*B)
						
						#Meteors
						for n in range(localrand2):
							x = meteors[localrand2-(n+1)]
							xdiff = (center(i)[0]-(center(x)[0]))
							'''if int(xdiff) == 0:
								xdiff = 0.1'''
							ydiff = (center(i)[1]-(center(x)[1]))
							'''if int(ydiff) == 0:
								ydiff = -0.1'''
							distance = math.hypot(xdiff, ydiff)
							if distance < 60*B:
								if distance < 0.1:
									distance = 0.1
								dmg = math.floor(80*B / distance)
								if distance > 35*B:
									dmg *= 0.6
								else:
									if psych:
										particles.append(particle(center(x), [10, 10], [xdiff*(1/distance), (abs(x.speed)*ydiff)*(1/distance)], crumblepic))
									else:
										particles.append(particle(center(x), [10, 10], [xdiff*(-1/distance), (abs(x.speed)*ydiff)*(-1/distance)], crumblepic))
								RecentDamage += int(dmg)*i.crit if x.hp > dmg else x.hp*i.crit
								x.hp -= int(dmg)
								if x.hp <= 0:
									meteors.remove(x)
									metdestroyed += 1
					projectiles.remove(i)
		
		
		#meteors
		for i in meteors:
			if not collide(i.coords, i.size, (0, 0-100), (screenX, screenY)):
				meteors.remove(i)
			alive = True
			if int(i.hp) >= 4:
				i.timer -= 1
				if i.timer <= 0:
					i.timer = i.timerBase
					meteors.append(meteor(i.hp-3, i.coords, (i.hp-2)*2))
			#movement
			for n in range(int(i.speed)):
				i.coords = (i.coords[0], i.coords[1]+mult.speed)
				if collide(ship.coords, ship.size, i.coords, i.size):
					if isAlive:
						temp = center(ship)
						particles.append(particle([temp[0], ship.coords[1]], [10, 10], [0, 1], explosionpic))
						particles.append(particle([temp[0]+random.randint(-1, 1), temp[1]+random.randint(-1, 1)], [10, 10], [0, 1], sparks))
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
				if int(i.hp) == 1:
					thiswall = wall1
				if int(i.hp) == 2:
					thiswall = wall2
				if int(i.hp) == 3:
					thiswall = wall3
				if int(i.hp) == 4:
					thiswall = wall4
				if int(i.hp) == 5:
					thiswall = wall5
				if int(i.hp) == 6:
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
				if OP:
					if event.key == K_p:
						pause = True
						while pause:
							for event in pygame.event.get():
								if event.type == pygame.KEYDOWN:
									if event.key == K_p:
										pause = False
							#pygame.display.update()
							clock.tick(30)

					if event.key == K_EQUALS:
						buttonPush += 1
					if event.key == K_MINUS:
						buttonPush -= 1
					if event.key == K_LEFTBRACKET:
						equip(upgrades[buttonPush%len(upgrades)])
					if event.key == K_RIGHTBRACKET:
						equip(supers[buttonPush%len(supers)])
					if event.key == K_b:
						mult.meteors *= 2
						boss.on = 1
					if event.key == K_v:
						equip(gunop)
					if event.key == K_h:
						boss.hp = 1
					if event.key == K_y:
						ship.hp += 50
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
					crit = ship.hp * (mult.difficulty+0.5) + RecentDamage
					print "       "+str(crit)
					if random.randint(30, 400) <= crit:
						if crit > 400 and random.randint(400, 1000) < crit:
							equip(GunGod)
						else:
							if misc == 5:
								if hasDefender:
									equip(gunwall)
								else:
									equip(Gunwall)
									hasDefender = True
							else:
								equip(supers[misc])
					else:
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
		
		pygame.draw.rect(Screen, (40, 40, 40), (0, screenY, screenX, -80))

		if isAlive:
			hpratio = (Decimal(ship.hp)/Decimal(ship.basehp))*100
			if hpratio >= 100:
				hpratio = float(hpratio)
			if ship.hp < 0:
				misc = "Open hull"
				dialog = Font.render(misc, True, (255, 100, 100))
				pygame.draw.line(Screen, (255, 10, 10), (0, 0), (0, screenY-95), 1)
				pygame.draw.line(Screen, (255, 10, 10), (249, 0), (249, screenY-95), 1)
			else:
				Screen.blit(font.render("Health", True, White), [5,screenY-35])
				dialog = Font.render(str(hpratio)+"%", True, White)    
			Screen.blit(dialog, [5,screenY-23])
			dialog = font.render("Meters: "+str(timer.time), True, White)
			Screen.blit(dialog, [190, screenY-35])
			
			
			dialog = font.render("dmg: "+str(RecentDamage), True, White)
			Screen.blit(dialog, [0, 0])
			dialog = font.render("Crit: "+str(ship.hp * (mult.difficulty+0.5) + RecentDamage), True, White)
			Screen.blit(dialog, [0, 20])
			dialog = font.render(str(buttonPush), True, White)
			Screen.blit(dialog, [0, 40])
			
			#gun name
			dialog = Font.render("::"+ship.gun.id, True, White)
			Screen.blit(dialog, [0, screenY-78])

			#Gun cooldown visual
			if ship.gun.cooldown > 0:
				fireratio = Decimal(timer.guncool)/Decimal(ship.gun.cooldown)
				fireratio = max(min(1, fireratio), 0)
				pygame.draw.line(Screen, (255, 0, 0), (0, screenY-55), (100, screenY-55), 1) #background
				pygame.draw.line(Screen, (255, 0, 0), (100, screenY-55), (100, screenY-33), 1)
				color = (max(225*fireratio, 0), max(225-(225*fireratio), 0), 0)
				pygame.draw.rect(Screen, color, (0, screenY-56, 100-int(fireratio*100), 16))
				pygame.draw.rect(Screen, color, (250, screenY-56, -100+int(fireratio*100), 16))
				
				if fireratio <= 0.1: #extra bright when ready to fire
					pygame.draw.rect(Screen, (0, 255, 0), (90, screenY-40, 10-(fireratio*100), 7))
					pygame.draw.rect(Screen, (0, 255, 0), (160, screenY-40, -(10-(fireratio*100)), 7))
			else: #if no cooldown
				pygame.draw.rect(Screen, (0, 255, 0), (0, screenY-56, 100, 15))
				pygame.draw.rect(Screen, (0, 255, 0), (90, screenY-40, 10, 7))
				pygame.draw.rect(Screen, (0, 255, 0), (150, screenY-56, 100, 15))
				pygame.draw.rect(Screen, (0, 255, 0), (150, screenY-40, 10, 7))

			dialog = font.render(str(ship.gun.maxfires-ship.gun.fires+1), True, White)    
			Screen.blit(dialog, [111, screenY-14])
			#ammo visual
			if (ship.gun.maxfires):
				fireratio = float(Decimal(ship.gun.fires) / Decimal(ship.gun.maxfires+1))
				pygame.draw.rect(Screen, (10, 30, 10), (109, screenY-56, 32, 42))
				pygame.draw.rect(Screen, (200, 200, 200), (110, screenY-55, 30, 40*(1-fireratio)))
				#pygame.draw.line(Screen, (120, 150, 120), (screenX, screenY-54), (screenX/2, screenY-54), 2) #backing color
				#pygame.draw.line(Screen, (0, 255, 0), (screenX, screenY-54), (screenX * (0.5 + 0.5*fireratio), screenY-54), 2) #ammo
			else: #blue if only one shot
				pygame.draw.rect(Screen, (80, 80, 255), (110, screenY-55, 30, 40))
				#pygame.draw.line(Screen, (80, 80, 255), (screenX, screenY-54), (screenX/2, screenY-54), 2)
 			

		else:
			pass

		'''if localrand != False:
			pygame.draw.circle(Screen, (255, 255, 255), localrand, 60, 2)
			pygame.draw.circle(Screen, (255, 255, 255), localrand, 40, 2)
			pygame.display.update()
			raw_input("")'''
 		Screen.blit(Hud, (0, screenY-95))
			
		pygame.display.update()
		clock.tick(fps)

	print timer.neardead
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
