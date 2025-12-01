import pygame, random, math, webbrowser   #Webbrowser is used for a clickable link which takes the user to our website source

pygame.init()   #Initializes all the built-in Pygame modules
pygame.font.init()   #Initializes the font module of Pygame (to render text)


"""Set global game variables"""
screenWidth, screenHeight = pygame.display.Info().current_w, pygame.display.Info().current_h   #Gets the measures of the user's screen
screen = pygame.display.set_mode((screenWidth, screenHeight))   #Window size adapts to any pc screen
backgrounds = {
    "menu": pygame.transform.scale(pygame.image.load ("menu.png"), (screenWidth, screenHeight)),
    "explanation": pygame.transform.scale(pygame.image.load ("explanation.png"),(screenWidth, screenHeight)), 
    "simulation": pygame.transform.scale(pygame.image.load("simulation.png"),(screenWidth, screenHeight)), 
    "warning": pygame.transform.scale(pygame.image.load("warning.png"),(screenWidth, screenHeight)),
}   #Dictionary that stores all our background images (preloaded and scaled)

currentImageIndex = 0
birds = []   #List to store all the birds' positions
moving = False   #Defines if it shows the simulation screen
running = True   #Defines if the game is running or not
firstTime = True   #Defines if it is the first time the simulation screen is being accessed
showDots = False   #Defines whether or not the dots are toggled
background = backgrounds["menu"]


""""Setup game"""
images = [pygame.image.load(f"bird_{i}.png") for i in range(1, 6)]   #Creates a list of all the images for the movement of the wings (using a formated string)


"""Clickable link, birdCount and colors setup"""
HOVER_BLUE = (100, 100, 255)   #Defines RGB color values
ORANGE = (255, 145, 77)
BROWN = (104, 76, 61)
fontPath = ("Chewy-Regular.ttf")
fontSize = 45   #Only for the birdCount
chewyFont = pygame.font.Font(fontPath, fontSize)
linkText = "Click here to open our website source"
linkURL = "https://www.discoverwildlife.com/animal-facts/birds/how-flocks-of-birds-are-able-to-fly-close-together"


"""Utility functions"""
def changeBackground(page):
    global background   #Declares these variables as global so their values can be modified throughout the program
    background = backgrounds[page]
    scaledBackround = pygame.transform.scale(background, (screenWidth, screenHeight))   #Transforms the image to the scale of the screen
    screen.blit(scaledBackround, (0, 0))   #"Draws" the image on the screen
    pygame.display.update()   #Refreshes the window to show any changes that have been done since the last update

def drawLink():
    global linkColor
    fontSize = 25
    chewyFont = pygame.font.Font(fontPath, fontSize)
    linkX = 10   #Positions the button on the left side of the screen, at the bottom
    linkY = screenHeight - 35

    mouseX, mouseY = pygame.mouse.get_pos()   #Tracks the mouse's position
    textWidth, textHeight = chewyFont.size(linkText)   #Calculates the dimensions of the rendered texts string "linkText"
    isHovering = linkX <= mouseX <= linkX + textWidth and linkY <= mouseY <= linkY + textHeight   #Checks if the mouse is between the edges of the link text

    linkColor = HOVER_BLUE if isHovering else ORANGE   #Changes colours
    renderedText = chewyFont.render(linkText, True, linkColor)   #True enables anti-aliasing (smoothing of text edges)
    screen.blit(renderedText, (linkX, linkY))

    return isHovering

def addBird():
    global showDots
    birdX = random.randint(0, screenWidth)   #Every bird is assigned to a random starting position, within the screen limits 
    birdY = random.randint(0, screenHeight)
    birds.append((birdX, birdY))   #Adds this position to the "birds" list 
    if showDots:   #If the user has toggled the dots
        color = BROWN if len(birds) == 1 else (0, 0, 0)   #The first bird is brown and the others are black
        pygame.draw.circle(screen, color, (birdX, birdY), 10)   #The characteristics of the dots (that represent the birds)
    else:
        drawBird(birdX, birdY)

def drawBird(birdX, birdY):
    global currentImageIndex
    birdImage = images[currentImageIndex]
    screen.blit(birdImage, (birdX, birdY))  
    pygame.time.delay(8)   #Delay between the different wing positions

def moveBird():
    global birds, currentImageIndex
    if not birds:
        return   #The rest of the function code doesn't run if there isn't any bird on the screen

    birdX, birdY = birds[0]   #Only applies to the first bird
    speed = 30

    if "birdDirection" not in globals():   #The code checks if "birdDirection" has already been initialized
        global birdDirection
        birdDirection = random.uniform(0, 2 * math.pi)   #If it hasn't, the main direction is defined

    birdDirection += random.uniform(-math.pi / 4, math.pi / 4)   #Direction is slightly ajusted throughout the movement (so it doesn't move so randomly)

    vx = math.cos(birdDirection) * speed   #Calculates the components of the velocity vector (using trigonometry)
    vy = math.sin(birdDirection) * speed

    newBirdX = birdX + vx   #Updated position
    newBirdY = birdY + vy

    newBirdX = max(50, min(screenWidth - 50, newBirdX))   #Keeps the bird within the screen boundaries
    newBirdY = max(50, min(screenHeight - 50, newBirdY))

    birds[0] = (newBirdX, newBirdY)   #Assigns the new coordinates to the first bird

    for i, (birdX, birdY) in enumerate(birds[1:]):   #Redraws all birds, except the first one
        if showDots:
            color = BROWN if i == 0 else (0, 0, 0)   #The "leader" dot is brown and all other dots are black
            pygame.draw.circle(screen, color, (birdX, birdY), 10)
        else:
            drawBird(birdX, birdY)
    birdCount()

def moveFlock():
    global birds, currentImageIndex
    updatedBirds = []
    separationDistance = 75   #Minimum distance to avoid collisions
    speed = 30   #Speed of the birds

    leaderX, leaderY = birds[0]   #Defines the first bird as the leader

    for i, (birdX, birdY) in enumerate(birds[1:]):   #Skips the first bird since it's already moving
        moveX, moveY = 0, 0   #By default, their movement vectors have no length; by default they don't need to move
        separationX, separationY = 0, 0

        for otherX, otherY in birds:
            if (birdX, birdY) != (otherX, otherY):   #So we're not comparing a bird to itself
                distance = math.sqrt((otherX - birdX) ** 2 + (otherY - birdY) ** 2)   #Calculates the distance between the 2 birds
                if distance < separationDistance:   #If they're too close, the birds will move away from  each other
                    separationX -= (otherX - birdX)
                    separationY -= (otherY - birdY)

        moveX += (leaderX - birdX) * 0.1   #All birds (except the leader) follow the first bird while avoiding collisions
        moveY += (leaderY - birdY) * 0.1
        moveX += separationX * 0.8 
        moveY += separationY * 0.8

        length = math.sqrt(moveX ** 2 + moveY ** 2)
        if length > 0:
            moveX = (moveX / length) * speed   #We divide the move vectors by their length so that their length is one and the movement is regular
            moveY = (moveY / length) * speed

        newBirdX = max(50, min(screenWidth - 50, birdX + int(moveX)))   #Bird is updated but doesn't leave the screen
        newBirdY = max(50, min(screenHeight - 50, birdY + int(moveY)))
        updatedBirds.append((newBirdX, newBirdY))
    updatedBirds.insert(0, birds[0])   #Re-adds the first bird to the start of the array, ensuring it still moves randomly

    currentImageIndex = (currentImageIndex + 1) % len(images)   #Cycles through wing pictures
    screen.blit(background, (0, 0)) 

    for i, (birdX, birdY) in enumerate(updatedBirds):   #Redraws all birds
        if showDots:
            color = BROWN if i == 0 else (0, 0, 0)  
            pygame.draw.circle(screen, color, (birdX, birdY), 10)
        else:
            drawBird(birdX, birdY)

    birdCount()
    birds = updatedBirds

def birdCount():
    birdCountText = chewyFont.render(f"{len(birds)}", True, ORANGE)   #True makes the letters' edges smooth
    BirdCountRect = birdCountText.get_rect()   #Creates a bounding rectangle around the text surface (used to manage the position and alignment of the text easily)
    BirdCountRect.right = screenWidth - 72.5   #Positions the text
    BirdCountRect.centery = (screenHeight // 2) - 20
    screen.blit(birdCountText, BirdCountRect)


"""Main entrypoint"""
changeBackground("menu")
while running:
    screen.blit(background, (0, 0)) 
    isHovering = False
    if background == backgrounds["explanation"]:   #Link is only displayed on the explanation screen
        isHovering = drawLink()   #Draws the link and checks if the user is hovering
        pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            if background == backgrounds["explanation"] and isHovering:
                webbrowser.open(linkURL)   #Opens the website on the user's browser
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:   #By pressing A you enter the explanation screen
                moving = False
                changeBackground("explanation")
            elif event.key == pygame.K_d:   #By pressing D you enter the simulation screen
                if firstTime:
                    addBird()   #Adds the first bird as soon as the simulation starts, only if it's the first time you open it
                    firstTime = False
                changeBackground("simulation")
                moving = True
            elif event.key == pygame.K_e:   #By pressing E you add another bird, if you have less than the maximum
                if len(birds) < 45:
                    addBird()
                else:
                    changeBackground("warning")   #Else, a pop-up appears
            elif event.key == pygame.K_TAB:   #Click TAB to go back to the menu
                moving = False
                changeBackground("menu")
            elif event.key == pygame.K_ESCAPE:   #Click ESC to close the app
                running = False
            elif event.key == pygame.K_SPACE:   #Toggles between the dots and birds
                showDots = not showDots
            elif event.key == pygame.K_x:   #Closes the pop-up
                changeBackground("simulation")
    if moving:
        moveBird()
        moveFlock()
        birdCount()
        pygame.display.update()
    pygame.time.delay(50)   #A delay of 50 milisseconds between each frame (20 FPS)
pygame.quit()