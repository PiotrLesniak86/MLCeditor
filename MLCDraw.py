########################################
# SCRIPT GET INFORMATION ABOUT MLC LEAFS POSITIONS FROM DICOM RTPLAN FILE EXPORTED FROM MONACO (ELKETA) 
# AND PREPARE VISUALIZATION FOR EVERY CONTROL POINT IN EVERY BEAM.
# TO USE THIS SCRIPT YOU HAVE TO EXPORT RTPLAN TO FILE FROM YOUR TPS (MONACO) AND PUT PATH TO THIS FILE INTO 'source' VARIABLE. 
# LEFT/RIGHT ARROWS - CHANGE CONTROL POINT
# UP/DOWN ARROWS - CHANGE BEAMS


from pydicom import dcmread
from os import system
from math import floor
from sys import argv

import pygame

#####################################################################################################

#get path to dicom from cmd parameters
source = argv[1]

#improting mlc possitions from dicom rtplan file
def getLeafsPossitions(source):
    ds = dcmread(source, force=True)
    beams=[]
    cp_list = []
    leafs=[]

    BEAM_count = len(ds[0x300a, 0x00b0].value)
    #iteration by beams
    for beam in range(BEAM_count): 
        CP_count = len(ds[0x300a, 0x00b0][beam][0x300a, 0x0111].value)
        #iteration by control points
        for cp in range(CP_count):
            Leafs_count = len(ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][1][0x300a, 0x011c].value)
            #iteration by leafs
            for leaf in range(Leafs_count): 
                leafs.append(ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][1][0x300a, 0x011c][leaf])
                print("Importing leaf: "+str(leaf)+" from cp: "+str(cp)+" in beam: "+str(beam))
            cp_list.append(leafs)
            leafs=[] 
        beams.append(cp_list)
        cp_list=[]
    return beams
###############################################################################

#Draw single mlc for bank A or B
def drawSingleMLCLeaf(leafNumber, leafDicomPosition, bank, screen):
    if bank == "A":
        leafPosition_In = leafNumber*leafHeight+leafOffset_Y
        leafPosition_Cr = leafOffset_X+leafDicomPosition
        rectA = pygame.Rect(leafPosition_Cr, leafPosition_In, leafWidth, leafHeight)
        pygame.draw.rect(screen, (13,13,222), rectA, 1, 0)
    if bank =="B":
        leafPosition_In = (leafNumber-80)*leafHeight+leafOffset_Y
        leafPosition_Cr = leafOffset_X+200+leafDicomPosition
        rectB = pygame.Rect(leafPosition_Cr, leafPosition_In, leafWidth, leafHeight)
        pygame.draw.rect(screen, (13,13,222), rectB, 1, 0)

#draw all mlc's. If leaf number is less then 80 drawing it in bank A. If not in bank B.
def drawAllMLCLeafs(leafDicomPositions, beam, cp):
    n=0
    for leaf in leafDicomPositions[beam][cp]:
        if n<80:
            drawSingleMLCLeaf(n, leaf, "A", screen)
        else:
            drawSingleMLCLeaf(n, leaf, "B", screen)
        n+=1

########################################################################

#SCREEN PARAMETERS
screen_with = 600
screen_height = 600
pygame.display.set_caption('MLC Editor - Visualization')

#SCREEN COLOR
screen_R = 255
screen_G = 255
screen_B = 255

#LEAFES PARAMETERS
leafHeight = 5
leafWidth = 200
leafOffset_Y = 30
leafOffset_X = 100

#IMPORTING LEAFS POSITION FROM DICOM RTPLAN
beam=0
cp=0
leafsDicomPosition = getLeafsPossitions(source)
pygame.init()
screen = pygame.display.set_mode([screen_with, screen_height])
running = True
font = pygame.font.Font('freesansbold.ttf', 12)
green = (0, 255, 0)

#pygame drawing loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if beam > 0:
                    beam -= 1
            if event.key == pygame.K_DOWN:
                if beam < len(leafsDicomPosition)-1:
                    beam += 1
            if event.key == pygame.K_LEFT:
                if cp > 0:
                    cp -= 1
            if event.key == pygame.K_RIGHT:
                if cp < len(leafsDicomPosition[0])-1:   
                    cp += 1

    screen.fill((screen_R, screen_G, screen_B))
    txt = "CP: "+str(cp)+" / BEAM: "+str(beam)
    print(txt)
    text = font.render(txt, True, green, (255,255,255))
    textRect = text.get_rect()
    textRect.center = (screen_with/2, screen_height-50)
    screen.blit(text, textRect)
    try:
        drawAllMLCLeafs(leafsDicomPosition, beam, cp)
    except IndexError:
        cp=0
        beam=0
    pygame.display.flip()

pygame.quit()