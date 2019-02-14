# Creating Tetris on python
# Author: Harsha Valluru
# Date: 13-02-2019

import random, time, pygame, sys
from pygame.locals import *

FPS = 25
WINDOWWIDTH = 700
WINDOWHEIGHT = 500
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVESDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOMMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#RGB
WHITE       =  (255, 255, 255)
GREY        =  (185, 185, 185)
BLACK       =  (0, 0, 0)
RED         =  (155, 0, 0)
LIGHTRED    =  (175, 20, 20)
GREEN       =  (0, 155, 0)
LIGHTGREEN  =  (20, 175, 20)
BLUE        =  (0, 0, 155)
LIGHTBLUE   =  (20, 20, 175)
YELLOW      =  (155, 155, 0)
LIGHTYELLOW =  (175, 175, 20)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GREY
COLORS = (BLUE, GREEN, RED, YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) #each color must have a light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..00.',
                     '.00..',
                     '.....'],
                    ['.....',
                     '..0..',
                     '..00.',
                     '...0.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....'
                     '.00..',
                     '..00.',
                     '.....'],
                    ['.....',
                     '..0..',
                     '.00..',
                     '.0...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..0..',
                     '..0..',
                     '..0..',
                     '..0..',
                     '.....'],
                    ['.....',
                     '.....',
                     '0000.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.00..',
                     '.00..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.0...',
                     '.000.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..00.',
                     '..0..',
                     '..0..',
                     '.....'],
                    ['.....',
                     '.....'
                     '.000.',
                     '...0.',
                     '.....'],
                    ['.....',
                     '..0..',
                     '..0..',
                     '.00..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...0.',
                     '.000.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..0..',
                     '..0..',
                     '..00.'
                     '.....'],
                    ['.....',
                     '.....',
                     '.000.',
                     '.0...',
                     '.....'],
                    ['.....',
                     '.00..',
                     '..0..',
                     '..0..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..0..',
                     '.000.',
                     '.....'
                     '.....'],
                    ['.....',
                     '..0..',
                     '..00.',
                     '..0..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.000.',
                     '..0..',
                     '.....'],
                    ['.....',
                     '..0..',
                     '.00..',
                     '..0..',
                     '.....']]

SHAPES = {
    'S' : S_SHAPE_TEMPLATE,
    'Z' : Z_SHAPE_TEMPLATE,
    'J' : J_SHAPE_TEMPLATE,
    'L' : L_SHAPE_TEMPLATE,
    'I' : I_SHAPE_TEMPLATE,
    'O' : O_SHAPE_TEMPLATE,
    'T' : T_SHAPE_TEMPLATE
    }

def main():
    global FPSCLOCK, DISPLAYSURF, BASICCONF, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetris')
    
    showTextScreen('Tetris')
    while True: #This is the game loop
        if random.randint(0, 1) == 0:
            pygame.mixer.music.load('tetrisb.mid')
        else:
            pygame.mixer.music.load('tetrisb.mid')
        pygame.mixer.music.play(-1, 0.0)
        runGame()
        pygame.mixer.music.stop()
        showTextScreen('Game Over')

def runGame():
    #Setting up variables to start the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False
    movingRight = False
    movingLeft = False
    score = 0
    level, fallFreq = calculateLevelFallAndFreq(score)
    
    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()
    
    while True:
        if fallingPiece == None:
            #no falling piece in play, so start a new piece at top
            fallingPiece = nextPiece
            nexPiece = getNewPiece()
            lastFallTime = time.time() #reset FallTime
            
            if not isValidPosition(board, fallingPiece):
                return #can't fit a new piece on the board, so game over
            
        checkForQuit()
        for event in pygame.event.get(): #event handling loop
            if event.type == KEYUP:
                if (event.key == K_p):
                    #Pausing the game
                    DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.stop()
                    showTextScreen('Paused') #pause until key press
                    pygame.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                elif (event.key == K_LEFT or event.key == K_a):
                    movingLeft = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    movingRight = False
                elif (event.key == K_DOWN or event.key == K_s):
                    movingDown = False
                
            elif event.type == KEYDOWN:
                #moving the block sideways
                if (event.key == K_LEFT or event.key == K_a) and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                    movingLeft = True
                    movingRight = False
                    lastMoveSidewaysTime = time.time()
                    
                elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                    movingRight = True
                    movingLeft = False
                    lastMoveSidewaysTime = time.time()
                    
                #Rotating the block (if only there's room to rotate)
                elif(event.key == K_UP or event.key == K_w):
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(SHAPES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(SHAPES[fallingPiece['shape']])
                elif(event.key == K_q):
                    fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(SHAPES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(SHAPES[fallingPiece['shape']])
                        
                #Making the block fall faster with the down key
                elif(event.key == K_DOWN or event.key == K-s):
                    movingDown = True
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1
                    lastMoveDownTime = time.time()
                    
                #Moving current block all the way down
                elif event.key == K_SPACE:
                    movingDown = False
                    movingLeft = False
                    movingRight = False
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                        fallingPiece['y'] += i - 1
             
            # handle moving the block because of user input
            if (movingLeft or movingRight) and time.time() - lastMoveSideWaysTime > MOVESIDEWAYSFREQ:
                if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                lastMoveSideWaysTime = time.time()
            
            if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and isValidPosition(board, fallingPiece, adjY=1):
                fallingPiece['y'] += 1
                lastMoveDownTime = time.time()
            
            #let the piece fall if it's time to fall
            if time.time() - lastFallTime > fallFreq:
                #see if the piece has landed
                if not isValidPosition(board, fallingPiece, adjY=1):
                    #fallng piece has landed, set it on the board
                    addToBoard(board, fallingPiece)
                    score += removeCompleteLines(board)
                    level, fallFreq = calculateLevelAndFallFreq(score)
                else:
                    #piece did not land, just move one block down
                    fallingPiece['y'] += 1
                    lastFallTime = time.time()
                    
            # drawing everything on screen
            DISPLAYSURF.fill(BGCOLOR)
            drawBoard(board)
            drawStatus(score, level)
            drawNextPiece(nextPiece)
            if fallingPiece != None:
                drawPiece(fallingPiece)
                
            pygame.display.update()
            FPSCLOCK.tick(FPS)


def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()
    

def checkForKeyPress():
    #Go through event queue looking for KEYUP event
    #Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()
    
    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showTextScreen(text):
    #This function displays large text in the
    #center of the screen until a key is pressed.
    #Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)
    
    #Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)
    
    #Draw addition "Press a key to play" text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)
    
    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()
        
        
def checkForQuit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event) #put the other KEYUP event objects back
        

def calculateLevelAndFallFreq(score):
    #Based on the score, return the level the player is on and
    #how many seconds pass until a falling piece falls in one space.
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level + 0.02)
    return level, fallFreq


def getNewPiece():
    #return a random new piece in random rotation and color
    shape = random.choice(list(PIECES.keys()))
    newPiece = {'shape': shape,
                'rotation' : random.randint(0, len(PIECES[shape]) - 1),
                'x' : int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y' : -2, #start it above the board
                'color' : random.randint(0, len(COLORS) - 1)}
    return newPiece


def addToBoard(board, piece):
    #fill in the board based on piece's location, shape and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']
                

def getBlankBoard():
    #create and return a blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board


def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    #Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']]['y']['x'] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True


def isCompletedLine(board, y):
    #Return truw if the line filled with boxes with no gapes.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return FALSE
    return True


def removeCompletedLines(board):
    #Remove any completed lines on the board, move everything above them down and return the number of completed lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompletedLine(board, y):
            #Remove the line and pull boxes down by one line.
            for pullDownY in range[y, 0, -1]:
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY - 1]
                #set the very top line to blank
                for x in range(BOARDWIDTH):
                    board[x][0] = BLANK
                numLinesRemoved += 1
                #note on the next iteration, y is the same
                #This is so that if the line that was pulled down is also
                #complete, it will be removed
        else:
            y -= 1 #move on to check next row up
    return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
    #Convert the given xy coordinates of the board to xy
    #coordinates of the location on the screen
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    if color == BLANK:
        return
    if pixelx == None and pixelY == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLOR[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLOR[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))
    
    
def drawBoard(board):
    #draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)
    
    #fill in the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDSIZE, BOXSIZE * BOARDHEIGHT))
    #draw in individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])
        
    
def drawStatus(score, level):
    #draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAY.blit(scoreSurf, scoreRect)
    
    #draw the level text
    levelSurf = BASICFONT.render('Leve;: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOW - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)
    
    
def drawPiece(piece, pixelx=None, pixelY=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        #if pixelx and pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])
        
    #draw each of the boxes that make up the pieces
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][y] != BLANK:
                drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y + BOXSIZE))
                

def drawNextPiece(piece):
    #draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWODTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    #draw the next piece
    drawPiece(piece, pixelx = WINDOWWIDTH-120, pixely=100)
    

if __name__ == '__main__':
    main()