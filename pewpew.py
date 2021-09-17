import sys
import time
import random
import pygame
import math
import socket
from decimal import *
from pygame.locals import *
getcontext().prec = 2
pygame.init()

OP = True
DebugMode = False
RecentDamage = 0
Psych = False

ConnectToServer, ServerIP, ServerPort = True, "174.25.72.161", 7778
Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ClrGreen = pygame.Color(0, 255, 0)
ClrBlack = pygame.Color(0, 0, 0)
ClrWhite = pygame.Color(255, 255, 255)
ClrAccent = (50, 50, 50)
ScreenX, ScreenY = 250, 650
Screen = pygame.display.set_mode((ScreenX, ScreenY))
Line = pygame.draw.line
Rect = pygame.draw.rect
Clock = pygame.time.Clock()
FontSmall = pygame.font.SysFont('Calibri', 15)
FontLarge = pygame.font.SysFont('Calibri', 30)
pygame.display.set_caption("Pew Pew")


# Global variables that are currently undefined
Particles = []
Projectiles = []
Powerups = []
Meteors = []
PlayerShip = None
Boss = None
TicksToFrame = 5
BossesBeat = 0

# The set of all meteor clusters that can be encountered.
AllMeteors = [[
	[2, [1, 2, 1],
	[2, 3, 2],
	[1, 2, 1]],
	
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
		[2, [1, 2, 1],
		[2, 3, 2],
		[1, 2, 1]],
		
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
	], [
		[2, [1, 2, 1],
		[2, 3, 2],
		[1, 2, 1]],
		
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
	], [
		[2, [1, 2, 1],
		[2, 3, 2],
		[1, 2, 1]],
		
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

# Image loading
ImgProjDefault = pygame.image.load('imgs/boolet.png')
ImgBoss = pygame.image.load('imgs/pewpew_enmBoss.png')
ImgProjDrill = pygame.image.load('imgs/gundrill.png')
ImgProjRailgun = pygame.image.load('imgs/gunrail.png')
ImgProjShield = pygame.image.load('imgs/gunshield.png')
ImgProjLazer = pygame.image.load('imgs/gunlazer.png')
ImgProjHyper = pygame.image.load('imgs/charged.png')
ImgProjExcavator = pygame.image.load('imgs/excavator.png')
ImgProjShield2 = pygame.image.load('imgs/hypershield.png')
ImgProjLight = pygame.image.load('imgs/light.png')
ImgProjBomb = pygame.image.load('imgs/bomb.png')
ImgBackground = pygame.image.load('imgs/pewpew_backdrop.png')
ImgPowerup = pygame.image.load('imgs/powerup.png')
ImgPlayer = pygame.image.load('imgs/pewpewship.png')
ImgPlayerDamaged = pygame.image.load('imgs/damagepew.png')
ImgUpgrade = pygame.image.load('imgs/powerup.png')

# Returns a list of quant images from the animation folder with the given name.
def getImgset(name, quant):
	images = []
	for i in range(quant):
		images.append(pygame.image.load('anim/{}/{}.png'.format(name, i)))
	return images
	
ImgsetExplosion = getImgset("explosion", 5)
ImgsetCrumble = getImgset("destintegrate", 4)
ImgsetFlareup = getImgset("firebit", 11)
ImgsetSparks = getImgset("spark", 5)
ImgsetWalls = getImgset("meteor", 6)

# Prints data only if the game is in debug mode
def prints(text):
	global DebugMode
	if DebugMode:
		print(text)

# Displays given text at the position on screen.
def textWrite(text, pos, font=FontSmall, color=ClrWhite, Onto=None):
	if Onto == None:
		global Screen
		Screen.blit(font.render(text, True, color), pos)
	else:
		Onto.blit(font.render(text, True, color), pos)
		

# Returns the coordinates of the center of an object that has coords and size attributes.
def center(obj):
	return (obj.coords[0] + (obj.size[0] / 2), obj.coords[1] + (obj.size[1] / 2))

# Returns true if rectangles with corner/size pairs (p1,p2) (p3,p4) overlap.
def collide(p1, p2, p3, p4):
	if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1] and p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
			return True

# CLASSES

# Stores multipliers that change based on difficulty or other changing factors.
class multipliers(object):
	def __init__(self, difficulty, hp, speed, cooldown, meteors, time):
		# Difficulty for deciders that use it
		self.difficulty = difficulty
		# Boss hp multiplier
		self.hp = hp 
		# Meteor speed multiplier
		self.speed = speed
		# Cooldown for upgrades and boss shots (higher is faster)
		self.cooldown = cooldown 
		# Cooldown between meteors
		self.meteors = meteors 
		# Distance multiplier (affects score and boss spawns)
		self.time = time 

# Basic object for particle system.
class particle(object):
	def __init__(self, coords, size, move, pics):
		self.frame = len(pics) - 1
		self.coords = [coords[0] - (size[0] / 2), coords[1] - (size[1] / 2)]
		self.size = size
		self.move = move
		self.pics = pics
		global TicksToFrame
		self.timer = TicksToFrame
			
# Base class for projectiles created by the player.
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
		self.regen = False

	# Created to reduce arguments in default constructor. Must be called.
	def complete(self, damage, pic, id, crit, counts, Regen):
		self.dmg = damage
		self.pic = pic
		self.id = id
		self.crit = crit
		self.counts = counts
		self.regen = Regen

# Base class for guns the player can equip.
class gun(object):
	def __init__(self, id, hpmod, hp, fires, size, speed, move, damage, cooldown, pic):
		self.hp = hp
		self.hpmod = hpmod
		self.fires = 0
		self.maxfires = fires - 1
		self.size = size
		# Times to loop
		self.speed = speed
		# Ammount to move each loop
		self.move = move
		self.dmg = damage
		self.id = id
		self.cooldown = cooldown
		self.pic = pic
		self.ban = False
		self.crit = 1
		# If this weapon counts against bullet efficiency
		self.screenCount = True
		self.regen = False

	# Sets extra data that is consistent for most guns. Created to reduce constructor length.
	def setBonus(self, ban, crit = 1, counts = True):
		self.ban = ban
		self.crit = crit
		self.screenCount = counts;

	def statMods(self, dmgmod = 0, hpmodder = 0, ammomod = 0, cooldownmod = 0, hpmod = 0, toRegen = False):
		self.dmg += dmgmod
		self.hpmod += hpmodder
		self.maxfires += ammomod
		self.cooldown += cooldownmod
		self.hp += hpmod
		self.regen = toRegen

	# Returns a new projectile object corresponding to the gun.
	def makeProj(self, shipCoords):
		global PlayerShip
		newProj = proj(self.hp, (PlayerShip.coords[0] + (PlayerShip.size[0] / 2) - (PlayerShip.gun.size[0] / 2), PlayerShip.coords[1] - 1), self.size, self.speed, self.move)
		newProj.complete(self.dmg, self.pic, self.id, self.crit, self.screenCount, self.regen)
		return newProj
		
# Base class for powerups the player picks up.
class powerup(object):
	def __init__(self, coords, interval):
		self.coords = coords
		self.size = (15, 15)
		self.interval = interval
		self.speed = interval
		global ImgUpgrade
		self.pic = ImgUpgrade

# Base class for the player ship.
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
		
# Base class for boss enemies.
class boss(object):
	def __init__(self, id, hp, dmg, size, speed, atkint, pic):
		self.id = id
		self.hp = hp
		self.dmg = dmg
		self.basehp = hp
		self.coords = ((ScreenX / 2) - (size[0] / 2), -size[1])
		self.size = size
		self.atkint = atkint
		self.speed = speed
		self.pic = pic
		self.on = 0
		
# Base class for single meteors.
class meteor(object):
	def __init__(self, hp, coords, speed):
		self.hp = hp
		self.coords = coords
		self.size = (10, 10)
		self.speed = speed
		self.dmg = 1
		self.timer = random.randint(0, 300 - ((hp - 3) * 30))
		self.timerBase = 300 - ((hp - 3) * 30)
		
# Base class to contain global timers and counters.
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
		self.ticks = 0

# Base class for the weighted table system
class lots(object):
	def __init__(self, weightlist, guns):
		self.items = guns
		self.weights = weightlist
		self.netsum = 0
		self.count = 0
		for i in self.weights:
			self.netsum += i
			self.count += 1

	# Returns an item from the table
	def getItem(self, cap = 0):
		randval = random.randint(0, self.netsum - sum(self.weights[(self.count - cap):self.count]))
		for i in range(0, self.count - cap):
			randval -= self.weights[i]
			if randval <= 0:
				return self.items[i]

	# Adds and subtracts from the weightlist
	def alter(self, itempos, modval):
		prev = self.weights[itempos]
		if prev + modval >= 0:
			self.weights[itempos] += modval
			self.netsum += modval
	

GunBase = gun("Pew Gun", 0, 1, 99999, (2, 5), 3, 2, 1, 25, ImgProjDefault)
GunRail = gun("Railgun", 1, 2, 10, (2, 10), 10, 10, 25, 28, ImgProjRailgun)
GunRail2 = gun("Scientific", -2, 2000, 2, (30, 30), 50, 10, 30, 60, ImgProjHyper)
GunRail2.setBonus(True, 1, False)
#gunlazer = gun("Lazer Beam", 1, 1, 50, (2, 4), 5, 2, 1, 0, ImgProjLazer) #Time dialator
GunLazer = gun("Laser Beam", 0, 1, 220, (2, 10), 50, 10, 0.5, -1, ImgProjLight)
GunLazer2 = gun("Decimator", -1, 1, 220, (4, 10), 50, 10, 1, -1, ImgProjLight)
GunLazer3 = gun("Ender", -50, 200, 300, (20, 500), 1, 500, 1, -1, ImgProjHyper)
GunLazer3.setBonus(True, 0.25, False)
GunBomb = gun("Bomb Launcher", 2, 4, 6, (4, 4), 2, 1, 1, 30, ImgProjBomb)
GunBomb.setBonus(True, 0.8)
GunBomb2 = gun("Nuclear Charge", 2, 4, 1, (4, 4), 1, 2, 1, 30, ImgProjBomb)
GunBomb2.setBonus(False, 0.8)

GunDrill = gun("Drill Launcher", 2, 15, 5, (6, 10), 2, 1, 5, 40, ImgProjDrill)
GunDrill2 = gun("Excavator", 3, 200, 1, (30, 30), 1, 1, 1, 40, ImgProjExcavator)
GunDrill2.setBonus(False, 1, False)
GunShielding = gun("Shield Thrower", 10, 20, 1, (20, 5), 1, 1, 1, 50, ImgProjShield)
GunShielding2 = gun("Shielding", 20, 10, 1, (20, 5), 1, 1, 1, 50, ImgProjShield)
GunGatling = gun("Tommy Gun", 2, 1, 80, (2, 2), 4, 3, 2, 15, ImgProjDefault)
GunGatling.setBonus(True, 6)
GunGatling2 = gun("Gatling", 2, 1, 200, (2, 4), 3, 5, 2, 10, ImgProjDefault)
GunGatling2.setBonus(False, 8)
GunOP = gun("God gun", 50, 100, 1000, (50, 5), 6, 2, 30, 0, ImgProjShield2)
GunWall = gun("Wall Placer", 1, 56, 1, (50, 20), 1, 5, 1, 50, ImgProjShield2)
GunWall.setBonus(False, 0.5)
GunDefender = gun("Defender", 2, 20, 1, (20, 10), 1, 3, 1, 50, ImgProjShield)

#GunDrill2.statMods(toRegen = True)
#GunShielding.statMods(toRegen = True)
#GunShielding2.statMods(toRegen = True)
#GunWall.statMods(toRegen = True)
#GunDefender.statMods(toRegen = True)
#GunBomb2.statMods(toRegen = True)

GunReducer = gun("Reducer", 1, 10000, 1, (ScreenX * 2, ScreenY), 1, ScreenY, 1, 1, ImgBackground)
GunReducer.setBonus(True, 1, False)

Upgrades = [GunRail, GunLazer, GunDrill, GunShielding, GunGatling, GunBomb, GunWall]
Upgrades2 = [GunRail2, GunLazer2, GunDrill2, GunShielding2, GunGatling2, GunBomb2, GunReducer, GunDefender]

LowTable = lots([3, 3, 3, 3, 3, 3, 3], Upgrades)
HighTable = lots([3, 3, 3, 3, 3, 3, 3, 3], Upgrades2)



# Pre-render images for backgrounds and unchanging overlays
buttonSize = 60
buttonSpace = 20
buttonFull = buttonSize + buttonSpace
cursor = 0

# Main Menu
OverlayMenu = pygame.Surface((ScreenX, ScreenY))
OverlayMenu.fill(ClrBlack)
for i in range(5):
	pygame.draw.rect(OverlayMenu, ClrAccent, (buttonSpace, (50 + i * buttonFull), 250 - (buttonSpace * 2), buttonSize))
textWrite("Casual", (30, 60), Onto=OverlayMenu)
textWrite("Full Job", (30, 60 + buttonFull), Onto=OverlayMenu)
textWrite("Hard", (30, 60 + buttonFull * 2), Onto=OverlayMenu)
textWrite("Impossible", (30, 60 + buttonFull * 3), Onto=OverlayMenu)
textWrite("Test mode", (30, 60 + buttonFull * 4), Onto=OverlayMenu)

# Main Menu Help subsection
OverlayHelp = pygame.Surface((ScreenX, ScreenY))
OverlayHelp.fill(ClrBlack)
textWrite("Pew Pew", [70, 25], Onto=OverlayHelp)
textWrite("Use left and right arrows to move", [0, 50 + 20], Onto=OverlayHelp)
textWrite("Up arrow to fire weapons.", [0, 50 + 40], Onto=OverlayHelp)
textWrite("Collect Poweups to upgrade your ship", [0, 50 + 60], Onto=OverlayHelp)
OverlayHelp.blit(ImgPowerup, [(ScreenX / 2) - 20, 50 + 80])
textWrite("Avoid meteors, and especially camps.", [0, 50 + 100], Onto=OverlayHelp)
OverlayHelp.blit(ImgsetWalls[0], [60, 50 + 120])
OverlayHelp.blit(ImgsetWalls[4], [200, 50 + 120])
textWrite("See your stats at bottom of screen.", [0, 50 + 140], Onto=OverlayHelp)
textWrite("Press an arrow key to select difficulty", [0, 300], Onto=OverlayHelp)
textWrite("difficulty increases clockwise,", [0, 300 + 16], Onto=OverlayHelp)
textWrite("from left as easy to down as impossible.", [0, 300 + 32], Onto=OverlayHelp)
textWrite("And look out for someone at 10000m...", [0, 500], Onto=OverlayHelp)

# In game Hud
Hud = pygame.Surface((ScreenX, 95), pygame.SRCALPHA, 32).convert_alpha()
pygame.draw.rect(Hud, (100, 100, 100), (0, 0, ScreenX, 5))
pygame.draw.rect(Hud, (80, 80, 80), (0, 5, ScreenX, 10))
pygame.draw.rect(Hud, ClrAccent, (0, 42, 58, 15))
pygame.draw.rect(Hud, ClrAccent, (ScreenX, 42, -58, 15))
for i in range(0, 30):
	pygame.draw.arc(Hud, ClrAccent, (i / 2, 42 + i / 2, 100 - i, 50 - i), 0, 1.56, 1)
	pygame.draw.arc(Hud, ClrAccent, (150 + i / 2, 42 + i / 2, 100 - i, 50 - i), 1.57, 3.14, 1)
pygame.draw.rect(Hud, ClrAccent, (101, 42, 8, 53))
pygame.draw.rect(Hud, ClrAccent, (141, 42, 8, 53))

# Frontal Icons layer
Frontal = pygame.Surface((ScreenX, ScreenY), pygame.SRCALPHA, 32).convert_alpha()



# Fires the player's currently equipped gun.
def shoot():
	global PlayerShip
	global Projectiles
	global Timer
	Timer.guncool = PlayerShip.gun.cooldown
	Projectiles.append(PlayerShip.gun.makeProj(PlayerShip.coords))
	
	PlayerShip.gun.fires += 1
	if PlayerShip.gun.fires > PlayerShip.gun.maxfires:
		global GunBase
		equip(GunBase)

# Sets the players equipped gun to the specified weapon.
def equip(weapon):
	global PlayerShip
	weapon.fires = 0
	PlayerShip.gun = weapon
	PlayerShip.hp += weapon.hpmod

# Appends meteors to the global list to create the given thisCluster cluster.
def genMeteor(thisCluster, mod):
	global Meteors
	speed = thisCluster[0]
	for h in range(len(thisCluster)):
		if h != 0:
			for w in range(len(thisCluster[h])):
				thisMet = thisCluster[h][w]
				if thisMet != 0:
					Meteors.append(meteor(thisMet, ((w * 10) + mod[0], (h * 10) + mod[1]), speed))
	
# Cuts a number into a list of strings that are 4 digits long
def cutToFour(number):
	number = str(number)
	leng = len(number)
	if leng > 4:
		print("Packet too long. Cutting " + str(int(number) - int(number[:4])) + " digits")
		number = number[:4]
	if leng < 4:
		for i in range(4 - leng):
			number = "0" + number
	return number

# Sends typewords to the server connected in Socket.
def sendInfo(typewords):
	global Socket
	# Send size of packet
	msg = cutToFour(len(typewords))
	totalsent = 0
	while totalsent < 4:
		sent = Socket.send(msg[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
			break
		totalsent = totalsent + sent
	# Send packet
	totalsent = 0
	while totalsent < int(msg):
		sent = Socket.send(typewords[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
			break
		totalsent = totalsent + sent
		
# Recieve data sent from the server.
# The server should only be sending high score data back.
def serverRecieve():
	# Recieve quantity of words
	global Socket
	global ConnectToServer
	chunks = []
	bytes_recd = 0
	while bytes_recd < 4 and ConnectToServer:
		chunk = Socket.recv(min(4 - bytes_recd, 2048))
		if chunk == '':
			print("Server has disconnected")
			ConnectToServer = False
		chunks.append(chunk)
		bytes_recd = bytes_recd + len(chunk)
	if ConnectToServer:
		MSGLEN = int(''.join(chunks))
		# Recieve the words
		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN and ConnectToServer:
			chunk = Socket.recv(min(MSGLEN - bytes_recd, 2048))
			if chunk == '':
				print("Server has disconnected")
				ConnectToServer = False
			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		return ''.join(chunks)

# Calculates the players score and interacts with the server.
def calcEff():
	global ShotCount
	global HitEfficiency
	global BossesBeat
	global Multiplier
	global MeteorsDestroyed
	global Timer
	global Socket
	global Psych
	try:
		efficiency = float(ShotCount - HitEfficiency) / float(ShotCount)
	except ZeroDivisionError:
		efficiency = 1
	score, keeping = Timer.time + math.floor(10 * MeteorsDestroyed * efficiency) + ((Multiplier.difficulty + 1) * 500 * BossesBeat), True
	if Psych:
		score = math.floor(score * 1.5)
	score, nscore = str(score), ""
	for i in score:
		if i == ".":
			keeping = False
		if keeping:
			nscore += i
	score = int(nscore)
	prints("your score: " + str(score) + "\nYour tier: " + str(Multiplier.difficulty))
	if OP:
		out = "You were opped. High scores not counted."
	else:
		
		Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		Socket.connect((ServerIP, ServerPort))
		print("Connected")
		sendInfo(str(Multiplier.difficulty) + " " + str(int(score)))
		out = serverRecieve()
		out = out[:len(out) - 1]
		Socket.close()
	return out, score, efficiency


print("setup complete.")
# Version
print("pewpew version 0.3.1")

Looping = True
while Looping:
	Running = True
	redraw = True
	Menu = "title"
	# Mode selection screen loop
	while Running:
		keyLeft = False
		keyRight = False
		keyUp = False
		keyDown = False
		keyExtra = False

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				Running = False
				Looping = False
			if event.type == pygame.KEYDOWN:
				redraw = True
				# Difficulty selectors
				if event.key == K_LEFT:
					keyLeft = True
				if event.key == K_UP:
					keyUp = True
				if event.key == K_RIGHT:
					keyRight = True
				if event.key == K_DOWN:
					keyDown = True
				if event.key == K_t:
					keyExtra = True

		if redraw:
			Frontal.fill((0, 0, 0, 0))

		if Menu == "title":
			Screen.blit(OverlayMenu, (0, 0))

			if keyUp:
				cursor -= 1
				cursor %= 6
			if keyDown:
				cursor += 1
				cursor %= 6
			
			if redraw:
				Frontal.blit(ImgProjBomb, (buttonSpace, 50 + cursor * buttonFull))
				Frontal.blit(ImgProjBomb, (ScreenX - buttonSpace, 50 + cursor * buttonFull + buttonSize))

			if keyLeft or keyRight or keyExtra:
				if cursor == 0:
					Running = False
					# 18:1
					Multiplier = multipliers(0, 1, 1.5, 1, 28, 1) 
				if cursor == 1:
					Running = False
					# 14:1
					Multiplier = multipliers(1, 2, 2, 2, 20, 2)
				if cursor == 2:
					Running = False
					# 25:1
					Multiplier = multipliers(2, 3.5, 3, 2, 10, 4) 
				if cursor == 3:
					Running = False
					# 12.5:1
					Multiplier = multipliers(3, 40, 5, 5, 8, 10) 
				if cursor == 4:
					Running = False
					Multiplier = multipliers(4, 2, 2, 2, 50, 1)
				#if cursor = 5:
			
		Screen.blit(Frontal, (0, 0))
		pygame.display.update()
		Clock.tick(60)
		redraw = False

	# Main variable resetting
	Screen.fill(ClrBlack)
	Line(Screen, ClrGreen, (0, 0), (600, 600), 3)
	pygame.display.update()
	print("updated screen")

	Particles = []
	Projectiles = []
	Powerups = []
	Powerups.append(powerup(((ScreenX / 2) - 7, 50), 1))
	PlayerShip = ships(4, ((ScreenX / 2) - 15, 500), (6, 10), 1)
	Boss = boss(1, 200 * Multiplier.hp, 10, (150, 50), 10, 500 / Multiplier.cooldown, ImgBoss)
	BossesBeat = 0
	Meteors = []
	for i in range(5):
		boolet = meteor(1, (random.randint(0, 25) * 10, 10), random.randint(1, 2))
		Meteors.append(boolet)
	Timer = timers()
	MeteorsSubset = AllMeteors[Multiplier.difficulty]

	if Multiplier.difficulty == 2:
		equip(GunShielding2)
	elif Multiplier.difficulty == 3:
		equip(Upgrades[random.randint(0, len(Upgrades) - 1)])
	else:
		equip(GunBase)
	
	BossMoveTime = 100
	BossSpawnTime = 10000
	MeteorsDestroyed = 0
	MovePress = False
	LeftMove = False
	RightMove = False
	Shooting = False
	HasDefender = False
	MoveModifier = 2
	ShotCount, HitEfficiency = 0, float(0)
	# alldam, potdam = 0, 0 # Would be a much better indicator of shot efficiency.
	Fps = 60
	PlayerAlive = True
	RecentDamage = 0
	SelectorIndex = 0

	print("Let the game begin.")
	# Version
	print("pewpew version 0.3")
	
	# Creates particles, resets variables, and sets up the next boss encounter
	def killBoss():
		global Fps
		global Multiplier
		global Boss
		global Particles
		global BossesBeat
		global BossSpawnTime
		global Timer
		
		Fps = 10
		Multiplier.meteors /= 2
		particleRange = math.floor(Boss.size[0] / 10)
		for z in range(9):
			pos1 = random.randint((Boss.coords[0] + (z * particleRange)), (Boss.coords[0] + ((z + 1) * particleRange)))
			pos2 = random.randint(Boss.coords[1], (Boss.coords[1] + Boss.size[1]))
			Particles.append(particle([pos1, pos2], [10, 10], [random.randint(-2, 2), random.randint(-1, 3)], ImgsetFlareup))
		Boss.on = 0
		BossesBeat += 1
		rand = (500 / Multiplier.cooldown) - (BossesBeat * 10)
		if rand < 10:
			rand = 10
		Boss = boss(1 + BossesBeat, (300 + (150 * BossesBeat)) * Multiplier.hp, 5 + BossesBeat, (150, 50), 10, rand, ImgBoss)
		Boss.coords = ((ScreenX / 2) - (Boss.size[0] / 2), - Boss.size[1])
		BossSpawnTime = Timer.time + 6000

	# Main game loop
	Running = True
	while Running and Looping:

		# Resetting screen and background
		if not Psych:
			Screen.fill(ClrBlack)
			Timer.backdrop += Multiplier.speed
			if Timer.backdrop >= 0:
				Timer.backdrop = ScreenY - 1000
			Screen.blit(ImgBackground, (0, Timer.backdrop))
					
		Timer.time += Multiplier.time
		Timer.ticks += 1

		if Timer.time == BossSpawnTime:
			Boss.on = 1
			Multiplier.meteors *= 2
			prints("Enter Boss")
		if Fps < 60 and PlayerAlive:
			Fps += 1
			if Fps > 60:
				Fps = 60
		if not PlayerAlive and Fps > 0:
			Fps -= 1
			# Seconds? probably. 1/60th of a second at 60 Fps to 1/1 at 1 Fps
			Timer.neardead += 1 / float(Fps) 
			if Fps < 2:
				Running = False
				
		Timer.meteors -= 1
		if Timer.meteors <= 0:
			Timer.meteors = Multiplier.meteors
			genMeteor(MeteorsSubset[random.randint(0, len(MeteorsSubset) - 1)], (random.randint(-20, ScreenX + 20), -100))

		if Timer.time % 12 == 0 and RecentDamage > 0:
			RecentDamage -= 1
			if RecentDamage < 1:
				RecentDamage = 0
			if RecentDamage > 60 and not (PlayerShip.gun.id in [GunGatling2.id, GunGatling.id]):
				RecentDamage -= 2
				if RecentDamage > 300:
					RecentDamage -= 2
		
		# Player movement
		Timer.move -= 1
		if Timer.move <= 0:
			Timer.move = PlayerShip.move
			PlayerShip.coords = (PlayerShip.coords[0] + PlayerShip.mom, PlayerShip.coords[1])
			if PlayerShip.coords[0] > ScreenX - PlayerShip.size[0]:
				PlayerShip.coords = (ScreenX - PlayerShip.size[0], PlayerShip.coords[1])
			if PlayerShip.coords[0] < 0:
				PlayerShip.coords = (0, PlayerShip.coords[1])
			for i in Projectiles:
				if i.id == "Defender":
					i.coords = (PlayerShip.coords[0] - 7, i.coords[1])
				
		if PlayerAlive:
			thisship = ImgPlayer
		if Timer.guncool > -1:
			Timer.guncool -= 1
		if Timer.guncool < 0 and Shooting:
			shoot()
				
		# Bullet movement
		for i in Projectiles:
			if not collide(i.coords, i.size, (0, 0), (ScreenX, ScreenY)):
				if i.counts:
					HitEfficiency = Decimal(float(HitEfficiency) + (float(i.hp) / float(i.basehp)))
				ShotCount += 1
				Projectiles.remove(i)
			else:
				ProjAlive = True
				if i.id == "Skipper":
					if Boss.on:
						Multiplier.meteors /= 2
						Boss.on = 0
						attackInterval = (500 / Multiplier.cooldown) - (BossesBeat * 10)
						if attackInterval < 10:
							attackInterval = 10
						Boss = boss(1 + BossesBeat, (300 + (150 * BossesBeat)) * Multiplier.hp, 5 + BossesBeat, (150, 50), 10, attackInterval, ImgBoss)
						Boss.coords = ((ScreenX / 2) - (Boss.size[0] / 2), - Boss.size[1])
						BossSpawnTime = Timer.time + 6000

				# Speed movement
				for n in range(i.speed):
					i.coords = (i.coords[0], i.coords[1] - i.move)
					if i.id in ["Wall Placer", "Defender"]:
						if i.move > 0:
							i.move -= 1
						if i.move == 0:
							i.speed = 4
					for x in Meteors:
						if collide(i.coords, i.size, x.coords, x.size):
							Particles.append(particle(center(x), [10, 10], [0, random.randint(x.speed - 1, x.speed + 1)], ImgsetCrumble))
							RecentDamage += (i.dmg * i.crit) if x.hp > i.dmg else (x.hp * i.crit)
							x.hp -= i.dmg
							i.hp -= x.dmg
							prints("Boolet: " + str(i.hp))
							if i.id == "Wall Placer":
								metCenter = center(x)
								pygame.draw.line(Screen, (180, 0, 0), (i.coords[0] + 5, i.coords[1] + 1), metCenter, 2)
								pygame.draw.line(Screen, (180, 0, 0), (i.coords[0] + 45, i.coords[1] + 1), metCenter, 2)
							if i.hp <= 0:
								Screen.blit(i.pic, i.coords)
								ProjAlive = False
								ShotCount += 1
								if i.id == "Defender":
									HasDefender = False
									Particles.append(particle(center(i), [10, 10], [random.randint(-1, 1), random.randint(-1, 1)], ImgsetSparks))
								if i.id == "Wall Placer":
									misc = center(i)
									Particles.append(particle([misc[0] - random.randint(1, 10), 2], [10, 10], [random.randint(-1, 1), random.randint(-1, 1)], ImgsetSparks))
									Particles.append(particle([misc[0], 2], [10, 10], [random.randint(-1, 1), random.randint(-1, 1)], ImgsetSparks))
									Particles.append(particle([misc[0] + random.randint(1, 10), 2], [10, 10], [random.randint(-1, 1), random.randint(-1, 1)], ImgsetSparks))
							prints("Meteor: " + str(x.hp))
							if x.hp <= 0:
								Meteors.remove(x)
								MeteorsDestroyed += 1
						if not ProjAlive:
							break
					
					if ProjAlive:
						if collide(i.coords, i.size, Boss.coords, Boss.size) and Boss.on == 1:
							Particles.append(particle([i.coords[0] + (i.size[0] / 2), i.coords[1] - i.move], [10, 10], [0, 1], ImgsetExplosion))
							prints("hit boss")
							RecentDamage += (i.dmg * i.crit) if x.hp > i.dmg else (x.hp * i.crit)
							Boss.hp -= i.dmg
							i.hp -= Boss.dmg
							prints("Boolet: " + str(i.hp))
							if i.hp <= 0:
								Screen.blit(i.pic, i.coords)
								ProjAlive = False
							prints("Boss: " + str(Boss.hp))
							if Boss.hp <= 0:
								killBoss()
					else:
						break
						
				if i.regen and i.hp < i.basehp and Timer.ticks % (4 + (i.basehp / 4)) == 0:
					i.hp += 1
					print (i.id, " Regen")
				# Projectile ID specific operations
				if i.id in ["Wall Placer", "Defender"]:
					# Draw hp lines and regenerate health
					hpratio = Decimal(i.hp) / Decimal(i.basehp)
					pygame.draw.aaline(Screen, (max(225 - (225 * hpratio), 0), max(225 * hpratio, 0), 0), (i.coords[0], i.coords[1] + 5), (i.coords[0] + int(hpratio * i.size[0] / 2), i.coords[1] + 5), True)
					pygame.draw.aaline(Screen, (max(225 - (225 * hpratio), 0), max(225 * hpratio, 0), 0), (i.coords[0] + i.size[0], i.coords[1] + 5), (i.coords[0] + i.size[0] - int(hpratio * i.size[0] / 2), i.coords[1] + 5), True)
					if i.hp < i.basehp:
						i.hp += 0.5
						if i.hp < i.basehp * (5 - Multiplier.difficulty) / 4:
							i.hp -= 0.25
				if i.id == "Laser Beam":
					pygame.draw.line(Screen, (130, 0, 0), (PlayerShip.coords[0] + 2, PlayerShip.coords[1]), (PlayerShip.coords[0] + 2, i.coords[1]), 2)
				if i.id == "Decimator":
					pygame.draw.line(Screen, (200, 0, 0), (PlayerShip.coords[0] + 2, PlayerShip.coords[1]), (PlayerShip.coords[0] + 2, i.coords[1]), 4)
				if i.id == "Ender":
					pygame.draw.line(Screen, (100, 0, 0), (PlayerShip.coords[0] + 2, PlayerShip.coords[1] - 10), (PlayerShip.coords[0] + 2, 0), 20)
					pygame.draw.line(Screen, (200, 0, 0), (PlayerShip.coords[0] + 2, PlayerShip.coords[1]), (PlayerShip.coords[0] + 2, 0), 4)
				if i.id == "Scientific":
					pygame.draw.line(Screen, (90, 70, 70), (PlayerShip.coords[0] + 2, PlayerShip.coords[1] - 10), (PlayerShip.coords[0] + 2, 0), 30)
					pygame.draw.line(Screen, (255, 255, 255), (PlayerShip.coords[0] + 2, PlayerShip.coords[1]), (PlayerShip.coords[0] + 2, 0), 2)
				Screen.blit(i.pic, i.coords)
				if not ProjAlive:
					if i.id in ["Bomb Launcher", "Nuclear Charge"]:
						boost = 1
						if i.id == "Nuclear Charge":
							boost = 3
						# Blast radius
						BR = (i.coords[0] - (58 * boost), i.coords[1] - (58 * boost))
						if collide(BR, (120 * boost, 120 * boost), Boss.coords, Boss.size) and Boss.on:
							Xover = max(0, min(Boss.coords[0] + Boss.size[0], BR[0] + (120 * boost)) - max(Boss.coords[0], BR[0]))
							Yover = max(0, min(Boss.coords[1] + Boss.size[1], BR[1] + (120 * boost)) - max(Boss.coords[1], BR[1]))
							overlap = Xover * Yover
							RecentDamage += i.crit * boost * overlap / 100 if Boss.hp > overlap / 100 else Boss.hp * i.crit
							Boss.hp -= boost * overlap / 100
							if Boss.hp <= 0:
								killBoss()
						
						pygame.draw.circle(Screen, (200, 200, 200, 0.05), center(i), 60 * boost)
						pygame.draw.circle(Screen, (250, 250, 250, 0.1), center(i), 35 * boost)
						
						# Meteor destruction loop
						MeteorQuant = len(Meteors)
						for n in range(MeteorQuant):
							x = Meteors[MeteorQuant - (n + 1)]
							xdiff = (center(i)[0] - (center(x)[0]))
							ydiff = (center(i)[1] - (center(x)[1]))
							distance = math.hypot(xdiff, ydiff)
							if distance < 60 * boost:
								if distance < 0.1:
									distance = 0.1
								dmg = math.floor(80 * boost / distance)
								if distance > 35 * boost:
									dmg *= 0.6
								else:
									if Psych:
										Particles.append(particle(center(x), [10, 10], [xdiff / distance, (abs(x.speed) * ydiff / distance)], ImgsetCrumble))
									else:
										Particles.append(particle(center(x), [10, 10], [0 - (xdiff / distance), 0 - (abs(x.speed) * ydiff / distance)], ImgsetCrumble))
								RecentDamage += int(dmg) * i.crit if x.hp > dmg else x.hp * i.crit
								x.hp -= int(dmg)
								if x.hp <= 0:
									Meteors.remove(x)
									MeteorsDestroyed += 1
					Projectiles.remove(i)
		
		
		# Meteors
		for i in Meteors:
			if not collide(i.coords, i.size, (0, -100), (ScreenX, ScreenY)):
				Meteors.remove(i)
			MeteorAlive = True
			if int(i.hp) >= 4:
				i.timer -= 1
				if i.timer <= 0:
					i.timer = i.timerBase
					Meteors.append(meteor(i.hp - 3, i.coords, (i.hp - 2) * 2))
			# Movement
			for n in range(int(i.speed)):
				i.coords = (i.coords[0], i.coords[1] + Multiplier.speed)
				if collide(PlayerShip.coords, PlayerShip.size, i.coords, i.size):
					if PlayerAlive:
						shipCenter = center(PlayerShip)
						Particles.append(particle([shipCenter[0], PlayerShip.coords[1]], [10, 10], [0, 1], ImgsetExplosion))
						Particles.append(particle([shipCenter[0] + random.randint(-1, 1), shipCenter[1] + random.randint(-1, 1)], [10, 10], [0, 1], ImgsetSparks))
					thisship = ImgPlayerDamaged
					i.hp -= PlayerShip.dmg
					PlayerShip.hp -= i.dmg
					prints("Meteor: " + str(i.hp))
					if i.hp <= 0:
						Meteors.remove(i)
						MeteorsDestroyed += 2
						MeteorAlive = False
					prints("Ship: " + str(PlayerShip.hp))
					if PlayerShip.hp <= 0 and PlayerAlive:
						PlayerAlive = False
						highscore, score, efficiency = calcEff()
				if not MeteorAlive:
					break
			Screen.blit(ImgsetWalls[int(math.ceil(i.hp)) - 1], i.coords)
		
		
		# Enemy action
		if Boss.on == 1:
			Timer.bossatk -= 1
			if Timer.bossatk <= 0:
				Timer.bossatk = Boss.atkint
				genMeteor([1, [1, 2, 1, 0, 0, 0, 0, 0, 1, 2, 1], [2, 5, 2, 1, 1, 2, 1, 1, 2, 5, 2], [1, 2, 1, 1, 2, 6, 2, 1, 1, 2, 1], [0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0]], (Boss.coords[0] + 20, Boss.coords[1] - 15))
			BossMoveTime -= 1
			if BossMoveTime < 1:
				if Boss.coords[0] + (Boss.size[0] / 2) > PlayerShip.coords[0] + (PlayerShip.size[0] / 2):
					Boss.coords = (Boss.coords[0] - 1, Boss.coords[1])
				if Boss.coords[0] + (Boss.size[0] / 2) < PlayerShip.coords[0] + (PlayerShip.size[0] / 2):
					Boss.coords = (Boss.coords[0] + 1, Boss.coords[1])
				if Boss.coords[1] < 10:
					Boss.coords = (Boss.coords[0], Boss.coords[1] + 1)
				BossMoveTime = Boss.speed
		
		
		# User input
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				# Movement
				if event.key == K_LEFT:
					PlayerShip.mom = -1 * MoveModifier
					MovePress = True
					LeftMove = True
				if event.key == K_RIGHT:
					PlayerShip.mom = 1 * MoveModifier
					MovePress = True
					RightMove = True
				if event.key == K_DOWN:
					MoveModifier = 1
				# Weapons
				if event.key == K_UP:
					Shooting = True
				if event.key == K_q:
					Running, PlayerShip.hp, PlayerAlive = False, 0, False
					highscore, score, efficiency = calcEff()
				# OP
				if event.key == K_g:
					OP = True
					print("Opped.")
				if OP:
					if event.key == K_p:
						pause = True
						while pause:
							for subevent in pygame.event.get():
								if subevent.type == pygame.QUIT:
									Running = False
									Looping = False
									pause = False
								if subevent.type == pygame.KEYDOWN:
									if subevent.key == K_p:
										pause = False
							Clock.tick(30)

					if event.key == K_EQUALS:
						SelectorIndex += 1
					if event.key == K_MINUS:
						SelectorIndex -= 1
					if event.key == K_LEFTBRACKET:
						equip(Upgrades[SelectorIndex % len(Upgrades)])
					if event.key == K_RIGHTBRACKET:
						equip(Upgrades2[SelectorIndex % len(Upgrades2)])
					if event.key == K_b:
						Multiplier.meteors *= 2
						Boss.on = 1
					if event.key == K_v:
						equip(GunOP)
					if event.key == K_h:
						Boss.hp = 1
					if event.key == K_y:
						PlayerShip.hp += 50
				# Debug
				if event.key == K_d:
					if DebugMode:
						DebugMode = False
					else:
						DebugMode = True
					print ('lazer cooldown: ', Timer.guncool)
					print ('Next boss: ', BossSpawnTime)
					print ('Boss Cooldown: ', Timer.bossatk)
					print ('Boss HP: ', Boss.hp)
			if event.type == pygame.KEYUP:
				if event.key == K_LEFT:
					LeftMove = False
				if event.key == K_RIGHT:
					RightMove = False
				if not LeftMove and not RightMove:
					MovePress = False
					PlayerShip.mom = 0
				if event.key == K_UP:
					Shooting = False
				if event.key == K_DOWN:
					MoveModifier = 2
			if event.type == pygame.QUIT:
				Running = False
				Looping = False
		
		# Powerup sourced interactions
		for i in Powerups:
			if not collide(i.coords, i.size, (0, 0), (ScreenX, ScreenY)):
				Powerups.remove(i)
			for n in range(i.speed):
				i.coords = (i.coords[0], i.coords[1] + 2)
				if collide(i.coords, i.size, PlayerShip.coords, PlayerShip.size):
					Powerups.remove(i)

					crit = PlayerShip.hp * (Multiplier.difficulty + 0.5) + RecentDamage
					randVal = random.random() + (crit / 400)
					print ("        damage " + str(RecentDamage) + " is crit " + str(crit) + " is mod " + str(crit / 400) + " for randval " + str(randVal))

					# Player is doing too well
					if randVal > 2.0:
						equip(GunLazer3)
					# Player is doing well
					elif randVal > 1.02:
						if HasDefender:
							equip(HighTable.getItem(1))
						else:
							equip(HighTable.getItem())
							if PlayerShip.gun.id == "Defender":
								HasDefender = True
					else:
						equip(LowTable.getItem())

					break
				else:
					Screen.blit(i.pic, i.coords)
			
		Timer.powerup -= 1
		if Timer.powerup < 0:
			Timer.powerup = random.randint(500 / Multiplier.cooldown, 900 / Multiplier.cooldown)
			Powerups.append(powerup((random.randint(20, ScreenX - 20), 50), random.randint(1, 2)))
			
		if PlayerShip.hp > 0:
			PlayerAlive = True

		if Boss.on == 1:
			Screen.blit(Boss.pic, Boss.coords)
		Screen.blit(thisship, PlayerShip.coords)
		
		# Particle system incrementing
		for i in Particles:
			if not collide(i.coords, i.size, (0, 0), (ScreenX, ScreenY)):
				Particles.remove(i)
			else:
				i.coords = (i.coords[0] + i.move[0], i.coords[1] + i.move[1])
				i.timer -= 1
				ParticleAlive = True
				if i.timer == 0:
					i.frame -= 1
					i.timer = TicksToFrame
					if i.frame < 0:
						Particles.remove(i)
						ParticleAlive = False
				if ParticleAlive:
					Screen.blit(i.pics[i.frame], i.coords)
		
		pygame.draw.rect(Screen, (40, 40, 40), (0, ScreenY, ScreenX, -80))

		# Hud drawing
		if PlayerAlive:
			hpratio = (Decimal(PlayerShip.hp) / Decimal(PlayerShip.basehp)) * 100
			if hpratio >= 100:
				hpratio = float(hpratio)
			if PlayerShip.hp < 0:
				misc = "Open hull"
				dialog = FontLarge.render(misc, True, (255, 100, 100))
				pygame.draw.line(Screen, (255, 10, 10), (0, 0), (0, ScreenY - 95), 1)
				pygame.draw.line(Screen, (255, 10, 10), (249, 0), (249, ScreenY - 95), 1)
			else:
				Screen.blit(FontSmall.render("Health", True, ClrWhite), [5, ScreenY - 35])
				dialog = FontLarge.render(str(hpratio) + "%", True, ClrWhite)    
			Screen.blit(dialog, [5, ScreenY - 23])
			textWrite("Meters: " + str(Timer.time), [190, ScreenY - 35])
			
			textWrite("dmg: " + str(RecentDamage), [0, 0])
			textWrite("Crit: " + str(PlayerShip.hp * (Multiplier.difficulty + 0.5) + RecentDamage), [0, 20])
			textWrite(str(SelectorIndex), [0, 40])
			
			# Gun name
			textWrite("::" + PlayerShip.gun.id, [0, ScreenY - 78], FontLarge)

			# Gun cooldown visual
			if PlayerShip.gun.cooldown > 0:
				fireratio = Decimal(Timer.guncool) / Decimal(PlayerShip.gun.cooldown)
				fireratio = max(min(1, fireratio), 0)
				pygame.draw.line(Screen, (255, 0, 0), (0, ScreenY - 55), (100, ScreenY - 55), 1)
				pygame.draw.line(Screen, (255, 0, 0), (100, ScreenY - 55), (100, ScreenY - 33), 1)
				color = (max(225 * fireratio, 0), max(225 - (225 * fireratio), 0), 0)
				pygame.draw.rect(Screen, color, (0, ScreenY - 56, 101 - int(fireratio * 100), 16))
				pygame.draw.rect(Screen, color, (150 + int(fireratio * 100), ScreenY - 56, 101 - int(fireratio * 100), 16))
				# Extra bright when ready to fire
				if fireratio <= 0.1: 
					pygame.draw.rect(Screen, (0, 255, 0), (90, ScreenY - 40, 11 - int(fireratio * 100), 7))
					pygame.draw.rect(Screen, (0, 255, 0), (150 + int(fireratio * 100), ScreenY - 40, 11 - int(fireratio * 100), 7))
			else:
				# No cooldown weapons
				pygame.draw.rect(Screen, (0, 255, 0), (0, ScreenY - 56, 100, 15))
				pygame.draw.rect(Screen, (0, 255, 0), (90, ScreenY - 40, 10, 7))
				pygame.draw.rect(Screen, (0, 255, 0), (150, ScreenY - 56, 100, 15))
				pygame.draw.rect(Screen, (0, 255, 0), (150, ScreenY - 40, 10, 7))

			dialog = FontSmall.render(str(PlayerShip.gun.maxfires - PlayerShip.gun.fires + 1), True, ClrWhite)    
			Screen.blit(dialog, [111, ScreenY - 14])
			# Ammo visual
			if (PlayerShip.gun.maxfires):
				fireratio = float(Decimal(PlayerShip.gun.fires) / Decimal(PlayerShip.gun.maxfires + 1))
				pygame.draw.rect(Screen, (10, 30, 10), (109, ScreenY - 56, 32, 42))
				pygame.draw.rect(Screen, (200, 200, 200), (110, ScreenY - 55, 30, 40 * (1 - fireratio)))
			else: 
				# Blue if only one shot
				pygame.draw.rect(Screen, (80, 80, 255), (110, ScreenY - 55, 30, 40))

		if Running:
			Screen.blit(Hud, (0, ScreenY - 95))
			
		pygame.display.update()
		Clock.tick(Fps)

	# Post game review text
	print(Timer.neardead)
	if Multiplier.difficulty == 0:
		l1 = "You cleaned up " + str(Timer.time) + " meters."
		l2, l5 = str(MeteorsDestroyed) + " meteor units sweeped ", "at " + str(math.floor(efficiency * 100)) + "% efficiency."
		l3 = str(BossesBeat) + " Anti-Gonists encountered."
		l4 = "Total score: " + str(score)
	if Multiplier.difficulty == 1:
		l1 = "You cleared " + str(Timer.time) + " meters."
		l2, l5 = str(MeteorsDestroyed) + " meteor units eliminated ", "at " + str(math.floor(efficiency * 100)) + "% efficiency."
		l3 = str(BossesBeat) + " Anti-Gonists fought."
		l4 = "Total score: " + str(score)
	if Multiplier.difficulty == 2:
		l1 = "You trekked " + str(Timer.time) + " meters!"
		l2, l5 = str(MeteorsDestroyed) + " meteor units removed ", "at " + str(math.floor(efficiency * 100)) + "% efficiency."
		l3 = str(BossesBeat) + " Anti-Gonists eliminated."
		l4 = "Total score: " + str(score)
	if Multiplier.difficulty == 3:
		l1 = "You survived " + str(Timer.time) + " meters!"
		l2, l5 = str(MeteorsDestroyed) + " meteor units swiped ", "at " + str(math.floor(efficiency * 100)) + "% efficiency."
		l3 = str(BossesBeat) + " Anti-Gonists destroyed."
		l4 = "Total score: " + str(score)

	Running = True
	while Running and Looping:
		textWrite(highscore, [5, ScreenY - 16])
		textWrite(l1, [5, ScreenY - 96])
		textWrite(l2, [5, ScreenY - 80])
		textWrite(l5, [5, ScreenY - 64])
		textWrite(l3, [5, ScreenY - 48])
		textWrite(l4, [5, ScreenY - 32])
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				Running = False
				Looping = False
			if event.type == pygame.KEYDOWN:
				Running = False
		pygame.display.update()
		Clock.tick(4)

	dialog = FontSmall.render("Pew Pew", True, ClrWhite)    
	Screen.blit(dialog, [0, 50])
