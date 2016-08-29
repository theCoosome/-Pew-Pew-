import sys
import time
import random
import pygame
import json
import math
from decimal import *
from pygame.locals import *
getcontext().prec = 2
pygame.init()
#colors

psych = False

Red = pygame.Color(200,0,0)
Green = pygame.Color(0,255,0)
Blue = pygame.Color(0,0,200)
Black = pygame.Color(0,0,0)
White = pygame.Color(255,255,255)
L_gray = pygame.Color(180,180,180)
D_gray = pygame.Color(80,80,80)
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

class multipliers(object):
    def __init__(self, hp, speed, cooldown, meteors, time):
        self.hp = hp
        self.speed = speed
        self.cooldown = cooldown
        self.meteors = meteors
        self.time = time

Running = True
while Running:
    Screen.fill(Black)
    dialog = font.render("Pew Pew", True, White)	
    Screen.blit(dialog, [0,50])
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
    dialog = font.render("See your stats at bottom", True, White)	
    Screen.blit(dialog, [0,50+140])
    dialog = font.render("Press an arrow key to start game", True, White)	
    Screen.blit(dialog, [0,300])
    dialog = font.render("And look out for someone at 10000m...", True, White)	
    Screen.blit(dialog, [0,500])
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            #movement
            if event.key == K_LEFT:
                Running = False
                mult = multipliers(1, 1, 1, 28, 1)
            if event.key == K_UP:
                Running = False
                mult = multipliers(2, 2, 2, 18, 2)
            if event.key == K_RIGHT:
                Running = False
                mult = multipliers(3.5, 3, 2, 10, 4)
            if event.key == K_DOWN:
                Running = False
                mult = multipliers(40, 5, 5, 8, 10)
    pygame.display.update()
    clock.tick(60)

print "setup complete."
#Version
print "pewpew version 0.1.2"

def getpartimg(name, quant):
    images = []
    for i in range(quant):
        images.append(pygame.image.load('anim/{}/{}.png'.format(name, i)))
    return images
    
explosionpic = getpartimg("explosion", 5)
crumblepic = getpartimg("destintegrate", 4)
    
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
        
particles = []
        
class proj(object):
    def __init__(self, hp, coords, size, speed, move, damage, pic):
        self.hp = hp
        self.coords = coords
        self.size = size
        self.speed = speed
        self.move = move
        self.dmg = damage
        self.pic = pic

projectiles = []
        
class gun(object):
    def __init__(self, id, hpmod, hp, fires, size, speed, move, damage, cooldown, pic):
        self.hp = hp
        #self.basehp = hp
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
        
gunbase = gun("Pew Gun", 0, 1, 1000, (2, 5), 3, 2, 1, 25, pewpic)
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
powerups = []
powerups.append(upgrade(((screenX/2)-7, 50), 1))

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
        self.alive = True
        
        self.guncool = -30
        global pewpic
        self.img = pewpic
        
        self.pressing = False
        self.lefting = False
        self.righting = False
        self.shooting = False
        self.mommod = 2
        
    def shoot(self):
        if self.alive:
            global projectiles
            global timer
            print "pew!"
            self.guncool = self.gun.cooldown
            #           hp,             coords,                                                                 size,           speed,          damage,     pic)
            temp = proj(self.gun.hp, (self.coords[0]+(self.size[0]/2)-(self.gun.size[0]/2), self.coords[1]-1), self.gun.size, self.gun.speed, self.gun.move, self.gun.dmg, self.gun.pic)
            projectiles.append(temp)
            self.gun.fires += 1
            if self.gun.fires > self.gun.maxfires:
                global gunbase
                self.equip(gunbase)

    def equip(self, weapon):
        weapon.fires = 0
        self.gun = weapon
        self.hp += weapon.hpmod
        print weapon.pic
        
ship1 = ships(4, ((screenX/2)-15, 500), (6, 10), 1)
ship2 = ships(4, ((screenX/2)-15, 500), (6, 10), 1)
allships = [ship1, ship2]

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
        
boss1 = Boss(1, 200*mult.hp, 10, (150, 50), 10, 500/mult.cooldown, pygame.image.load('imgs/pewpew_enmBoss.png'))
bossstufff = [1, 200, 10, (150, 50), 10, 500]
boss = boss1
bossesbeat = 0

class meteor(object):
    def __init__(self, hp, coords, speed):
        self.hp = hp
        self.coords = coords
        self.size = (10, 10)
        self.speed = speed
        self.dmg = 1
        self.timer = random.randint(0, 300-((hp-3)*30))
        self.timerBase = 300-((hp-3)*30)
meteors = []

for i in range(5):
    boolet = meteor(1, (random.randint(0,25)*10, 10), random.randint(1, 2))
    meteors.append(boolet)
        
class timers(object):
    def __init__(self):
        self.meteors = 5
        self.time = 0
        self.move = 1
        self.movecheck = 0
        self.backdrop = 100
        self.bossatk = 300
        self.powerup = 400
        
timer = timers()
#object one coord pair, size, object two coord pair and size
def collide(p1, p2, p3, p4):
    #if right side is right of left side, and left side left of right side
    if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
        #if bottom is below top and top is above bottom
        if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1]:
            #print "Object 1: ", p1, ",", p2
            #print "Object 2: ", p3, ",", p4
            return True
Screen.fill(Black)

Meteors = [
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
            [3, 6, 3, 3],
            [2, 3, 2, 2],
            [0, 2, 3, 0]],
            
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
          ]

def genMeteor(thisMet, mod):
    speed = thisMet[0]
    for h in range(len(thisMet)):
        if h != 0:
            for w in range(len(thisMet[h])):
                temp = thisMet[h][w]
                if temp != 0:
                    boolet = meteor(temp, (w*10+mod[0], h*10+mod[1]), speed)#--------------------------------------------------------------------------make time mod
                    meteors.append(boolet)
        

        
for i in allships:
    i.equip(gunbase)
    
t = 100
eventTimer = 10000
walls = 0
bosstime = 10000

Line(Screen, Green, (0,0), (600,600), 3)
pygame.display.update()
print "updated screen"
time.sleep(.1)



#main loop
Running = True
while Running:
    for i in allships:
        i.img = shippng
        if i.guncool > -1:
            i.guncool -= 1
        if i.guncool < 0 and i.shooting:
            i.shoot()
    
    timer.time += mult.time
    if timer.time == bosstime:
        boss.on = 1
    timer.meteors -= 1
    if timer.meteors <= 0:
        timer.meteors = mult.meteors
        #print "New meteor"
        genMeteor(Meteors[random.randint(0,len(Meteors)-1)], (random.randint(0-20, screenX+20), 0-100))
        
    
    Screen.fill(Black)
    timer.backdrop += 1
    if timer.backdrop == 0:
        timer.backdrop = screenY-1000
    Screen.blit(backimage, (0, timer.backdrop))
    
    #print timer.guncool
    
    #boolet movement
    for i in projectiles:
        if not collide(i.coords, i.size, (0, 0), (screenX, screenY)):
            projectiles.remove(i)
        else:
            alive = True
            for n in range(i.speed):
                i.coords = (i.coords[0], i.coords[1]-i.move)
                for x in meteors:
                    if collide(i.coords, i.size, x.coords, x.size):
                        print "collided"
                        particles.append(particle([x.coords[0]+(x.size[0]/2), x.coords[1]], [10, 10], [0, random.randint(x.speed-1, x.speed+1)], crumblepic))
                        temp = i.dmg
                        i.hp -= x.dmg
                        print "Boolet: " + str(i.hp)
                        if i.hp <= 0:
                            Screen.blit(i.pic, i.coords)
                            projectiles.remove(i)
                            alive = False
                        x.hp -= temp
                        print "Meteor: " + str(x.hp)
                        if x.hp <= 0:
                            meteors.remove(x)
                    if not alive:
                        break
                    else:
                        if collide(i.coords, i.size, boss.coords, boss.size) and boss.on == 1:
                            particles.append(particle([i.coords[0]+(i.size[0]/2), i.coords[1]-i.move], [10, 10], [0, 1], explosionpic))
                            print "hit boss"
                            temp = i.dmg
                            i.hp -= boss.dmg
                            print "Boolet: " + str(i.hp)
                            if i.hp <= 0:
                                Screen.blit(i.pic, i.coords)
                                projectiles.remove(i)
                                alive = False
                            boss.hp -= temp
                            print "Boss: " + str(boss.hp)
                            if boss.hp <= 0:
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
    
    #exponential movement speed?
    '''timer.movecheck -= 1
    if timer.movecheck <= 0:
        timer.movecheck = 5
        if pressing and ship.move > 3:
            ship.move -= 1
        if not pressing and ship.move <= 50:
            ship.move += 2'''
    #player movement
    for i in allships:
        i.coords = (i.coords[0]+i.mom, i.coords[1])
        if i.coords[0] > screenX-i.size[0]:
            i.coords = (screenX-i.size[0], i.coords[1])
            print "Don't go out of Bounds!"
        if i.coords[0] < 0:
            i.coords = (0, i.coords[1])
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
            for ship in allships:
                if collide(ship.coords, ship.size, i.coords, i.size):
                    print "collided"
                    particles.append(particle([ship.coords[0]+(ship.size[0]/2), ship.coords[1]], [10, 10], [0, 1], explosionpic))
                    ship.img = dmgpng
                    temp = i.dmg
                    i.hp -= ship.dmg
                    print "Meteor: " + str(i.hp)
                    if i.hp <= 0:
                        try:
                            meteors.remove(i)
                            alive = False
                        except ValueError:
                            alive = False
                    ship.hp -= temp
                    print "Ship: " + str(ship.hp)
                    if ship.hp <= 0:
                        ship.alive = False
                        for x in range(6):
                            particles.append(particle([ship.coords[0]+(ship.size[0]/2), ship.coords[1]], [10, 10], [random.randint(ship.mom-1, ship.mom+1), random.randint(-1, 1)], explosionpic))
                        for x in range(4):
                            particles.append(particle([ship.coords[0]+(ship.size[0]/2), ship.coords[1]], [10, 10], [random.randint(ship.mom-1, ship.mom+1), random.randint(-2, 0)], crumblepic))
                        ship.coords = [ship.coords[0], screenY+5]
                        
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
            print timer.bossatk
            genMeteor([1, [1, 2, 1, 0, 0, 0, 0, 0, 1, 2, 1], [2, 5, 2, 1, 1, 2, 1, 1, 2, 5, 2], [1, 2, 1, 1, 2, 6, 2, 1, 1, 2, 1], [0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0]], (boss.coords[0]+20, boss.coords[1]-15))
        t -= 1
        if t < 1:
            ship = allships[len(allships)-1]
            if boss.coords[0]+(boss.size[0]/2) > ship.coords[0]+(ship.size[0]/2):
                boss.coords = (boss.coords[0]-1, boss.coords[1])
            if boss.coords[0]+(boss.size[0]/2) < ship.coords[0]+(ship.size[0]/2):
                boss.coords = (boss.coords[0]+1, boss.coords[1])
            if boss.coords[0]+75 == ship.coords[0]+15:
                pass
            if boss.coords[1] < 10:
                boss.coords = (boss.coords[0], boss.coords[1]+1)
            t = boss.speed
            allships[len(allships)-1] = ship
        
        
    #user input
    for event in pygame.event.get():
        ship = allships[0]
        ship2 = allships[1]
        if event.type == pygame.KEYDOWN:
            #movement
            if event.key == K_LEFT:
                ship.mom = -1 * ship.mommod
                ship.pressing = True
                ship.lefting = True
            if event.key == K_RIGHT:
                ship.mom = 1 * ship.mommod
                ship.pressing = True
                ship.righting = True
            if event.key == K_DOWN:
                ship.mommod = 1
            #Weapons
            if event.key == K_UP:
                ship.shooting = True
                
            #Ship 2
            if event.key == K_a:
                ship2.mom = -1 * ship2.mommod
                ship2.pressing = True
                ship2.lefting = True
            if event.key == K_d:
                ship2.mom = 1 * ship2.mommod
                ship2.pressing = True
                ship2.righting = True
            if event.key == K_s:
                ship2.mommod = 1
            #Weapons
            if event.key == K_w:
                ship2.shooting = True
                
                
            if event.key == K_p:
                Running = False
            if event.key == K_f:
                print 'lazer cooldown: ', timer.guncool
                print 'Backdrop: ', backdrop
                print 'T: ', t
                print 'Boss Cooldown: ', timer.bossatk
                print 'Boss HP: ', bosshp
                print 
            if event.key == K_b:
                boss.on = 1
        if event.type == pygame.KEYUP:
            if event.key == K_LEFT:
                ship.lefting = False
            if event.key == K_RIGHT:
                ship.righting = False
            if not ship.lefting and not ship.righting:
                ship.pressing = False
                ship.mom = 0
            if event.key == K_UP:
                ship.shooting = False
            if event.key == K_DOWN:
                ship.mommod = 2
                
            if event.key == K_a:
                ship2.lefting = False
            if event.key == K_d:
                ship2.righting = False
            if not ship2.lefting and not ship2.righting:
                ship2.pressing = False
                ship2.mom = 0
            if event.key == K_w:
                ship2.shooting = False
            if event.key == K_s:
                ship2.mommod = 2
        allships = [ship, ship2]
        
    if OP:
        pass
    
    for i in powerups:
        if not collide(i.coords, i.size, (0, 0), (screenX, screenY)):
            powerups.remove(i)
        for n in range(i.speed):
            i.coords = (i.coords[0], i.coords[1]+2)
            for x in allships:
                if collide(i.coords, i.size, x.coords, x.size):
                    try:
                        powerups.remove(i)
                    except ValueError:
                        pass
                    misc = random.randint(0, len(upgrades)-1)
                    x.equip(upgrades[misc])
                    break
                    
        
    timer.powerup -= 1
    if timer.powerup < 0:
        timer.powerup = random.randint(500/mult.cooldown, 900/mult.cooldown)
        powerups.append(upgrade((random.randint(20, screenX-20), 50), random.randint(1, 2)))
        
    
    #Displays
    #if timer.guncool > 0:        
    #    Line(Screen, Red, (ship.coords[0]+15, ship.coords[1]), (ship.coords[0]+15, 0), 5)
        
    if boss.on == 1:
        Screen.blit(boss.pic, boss.coords)
        
    for i in powerups:
        Screen.blit(i.pic, i.coords)
    for i in allships:
        Screen.blit(i.img, i.coords)
        
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
        
    dialog = font.render("Meters: "+str(timer.time), True, White)
    Screen.blit(dialog, [screenX/3, screenY-16])
    
    hpratio = (Decimal(allships[0].hp)/Decimal(allships[0].basehp))*100
    if hpratio >= 100:
        hpratio = float(hpratio)
    misc = "Health: "+str(hpratio)+"%"
    Screen.blit(font.render(misc, True, White), [screenX/2,screenY-64])
    if allships[0].gun.id > 0:
        dialog = font.render("::"+allships[0].gun.id, True, White)    
        Screen.blit(dialog, [screenX/2, screenY-48])
        dialog = font.render("Fires remaining: "+str(allships[0].gun.maxfires-allships[0].gun.fires+1), True, White)
        Screen.blit(dialog, [screenX/2, screenY-32])
        
    hpratio = (Decimal(allships[1].hp)/Decimal(allships[1].basehp))*100
    if hpratio >= 100:
        hpratio = float(hpratio)
    misc = "Health: "+str(hpratio)+"%"
    Screen.blit(font.render(misc, True, White), [0,screenY-64])
    if allships[1].gun.id > 0:
        dialog = font.render("::"+allships[1].gun.id, True, White)    
        Screen.blit(dialog, [0, screenY-48])
        dialog = font.render("Fires remaining: "+str(allships[1].gun.maxfires-allships[1].gun.fires+1), True, White)
        Screen.blit(dialog, [0, screenY-32])
    
    pygame.display.update()
    clock.tick(60)

print "Boss hp: ", boss.hp
print "Meters: ", timer.time








