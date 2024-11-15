import pygame
import time
import random
import sys

pygame.init()

screenWidth, screenHeight = 1525, 800     #set window size
screen = pygame.display.set_mode((screenWidth, screenHeight))

background = pygame.image.load ("background.png")
background = pygame.transform.scale(background, (screenWidth, screenHeight))
firstBirdX = random.randint(0,1525) #ensures the bird stays within the window
firstBirdY = random.randint(0,800)
firstBird = firstBirdX, firstBirdY

def setBird (birdX,birdY):  
    position = (birdX, birdY)
    radius = 5
    pygame.draw.circle (screen, 'black', position, radius)
    pygame.display.update()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    screen.blit(background, (0,0))
    setBird(firstBirdX, firstBirdY)
    pygame.display.update()



pygame.quit()
sys.exit()
