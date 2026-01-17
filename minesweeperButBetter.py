from cmu_graphics import *
import math
import random

'''
Hello hello hello.
Welcome to my wonderful world of minesweeper.

Here's a general description (the feature list is further down):
Minesweeper with three game modes!
- Normal
    Good 'ol minesweeper, with the thing where if you select a revealed cell
    that has already been correctly flagged, it reveals the rest of the cells
    around it. This is the only game mode with adjustable size and difficulty
    (a percentage of the size of the board).
- Competitve
    Race against a clock instead. You can earn points based on the cells you
    reveal and time remaning on the clock. Hitting a bomb doesn't end the game
    but takes points off and hinders you for a couple seconds. If you don't beat
    the clock, you don't get the points. Use the points to buy more themes! This
    has adjustable difficulties, but size is part of the difficulty.
- Musical
    A hidden gamemode! Like normal minesweeper but notes are added to a song
    based on the number on the cells you reveal, adding notes an interval away
    based on it. Play the song at the end when you win! (I've been obsessed
    with ways you can visualize music, and this is a very cool way!)
- Themes Galore!
    Customize your gameplay! You get three given for free and five to unlock!
    Some are based on me... (joyful noise is my acapella group, tridelta is my
    sorority, meche is my major)


FEATURE LIST:
    - animated button presses
    - themes with a store
    - 3 free themes, 5 to buy
    - three game modes: normal, competitive, musical
    - competitive where you compete against a timer and keep score
        - hindrance mechanic for hitting bomb instead of game over
    - musical where the notes you press correspond to notes, so you can hear
        what your gameplay sounds like
    - gameplay that includes flood fill, chording, flagging, auto-start,
        and clear game win and game over states (competitive mode intentionally 
        doesn't include chording)
    - customizable board sizes and difficulties (normal mode is the only mode
        to pick sizes intentionally) from 8x8 to 15x15
    - updating bomb counter with flagging cells
    - clicking sound effects with mute button
    - smiley face status (as in minesweeper usually: smiley on normal, suspicicious
        when revealing cells, sad when you lose, happy when you win!)
    - special notes for joyful noise and tridelta themes
        - (these themes are based on the clubs I'm in haha)
    - comp mode leaderboard

initally normal mode will be the only mode unlocked
    - unlock competitive by winning normal 5 times
    - unlock musical mode (as it is a secret mode) by clicking the mute/unmute
        button on the menu screen at least 10 times

GRADING SHORTCUTS:

- 'c' will unlock comp mode (this works to both lock and unlock comp mode when you press)
- 'm' will unlock musical mode (this works to both lock and unlock musical mode when you press)
- '0' will add 500 to your total points
- '!' will automatically clear and win the given board (while this will win the board in musical mode
        you will not get a song at the end since it's contigent on you pressing numbers to correspond
        to notes)
        

- also 'f' is to flag and click is to reveal cells.


'''

###SETTING A CELL CLASS###

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.bomb = False
        self.flagged = False
        self.revealed = False
        self.bombCount = 0
        self.wrongFlag = False
        
    def __repr__(self):
        return f'row:{self.row} col:{self.col}'
    
    def flagCell(self):
        self.flagged = not self.flagged
        
    def reveal(self):
        self.revealed = True
        
    def becomeBomb(self):
        self.bomb = True
        
    def addCounts(self, n):
        self.bombCount = n
        
    def isWrong(self):
        self.wrongFlag = True
        
### SETTING A BUTTON CLASS ###

# this feature was planned with help of AI (Claude)
# but none of it was written by AI
# I simply asked for ideas to improve because I was
# tediously making tons of buttons

class Button:
    def __init__(self, x, y, width, height, label, action, size, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.action = action
        self.size = size
        self.color = color
        self.hoverColor = 'red'
        self.pressed = False
        self.isHovered = False
        self.price = None
        
    def draw(self, app):
        themeName = app.unlockedThemes[app.selectedTheme]
        cover = 10
        pressed = 13
        if self.pressed:
            buttonCover = app.imageBoard[themeName][pressed]
        else:
            buttonCover = app.imageBoard[themeName][cover]
        drawImage(buttonCover, self.x, self.y, width=self.width, height=self.height, align='center')
        if self.label != None:
            drawLabel(self.label, self.x, self.y, fill='white', size=self.size, bold=True, font=app.font)
    
    def contains(self, mouseX, mouseY):
        left = self.x - self.width / 2
        right = self.x + self.width / 2
        top = self.y - self.height / 2
        bottom = self.y + self.height / 2
        return (left <= mouseX <= right) and (top <= mouseY <= bottom)
        
    def isPressed(self, value):
        self.pressed = value
        
    def givePrice(self, value):
        self.price = value
        
        
### APP SET UP ###

def onAppStart(app):
    
    app.normalWins = 0
    app.compWins = []
    app.musicalWins = 0
    
    app.width = 400
    app.height = 500
    
    setUpMenu(app)
    setUpLevelOneMenu(app)
    setUpLevelTwoMenu(app)
    setUpLevelThreeMenu(app)
    setUpThemes(app)
    
    app.compLocked = True
    app.musicLocked = True
    app.font = 'montserrat'
    
    app.totalPoints = 0
    app.lastSong = ()
    app.noteDict = {0: 'C', 1: 'D', 2: 'E', 3: 'F', 4: 'G', 5: 'A', 6: 'B', 7: 'C', 8: 'D'}
    
    app.muted = False
    app.soundCount = 0
    
    # app.numColors = {0: 'black', 1: 'blue', 2: 'green', 3: 'red', 4: 'purple', 
    #                  5: 'maroon', 6: 'cyan', 7: 'mediumSlateBlue', 8: 'deepPink'}
    
    app.normalNext = Button(app.width-40, 130, 30, 30, '>', 'howComp', 18, 'red')
    app.compBack = Button(40, 130, 30, 30, '<', 'howNormal', 18, 'red')
    app.compNext = Button(app.width-40, 130, 30, 30, '>', 'howMusical', 18, 'red')
    app.musicalBack = Button(40, 130, 30, 30, '<', 'howComp', 18, 'red')
    
    app.goBack = Button(app.width-30, 30, 30, 30, 'X', 'startScreen', 18, 'red')
    
    setUpGame1(app)
    setUpGame2(app)
    setUpGame3(app)
    
def setUpThemes(app):
    
    #theme dict
    app.themes = {0: 'midnight', 1: 'honeybutter', 2: 'oceanmilk', 3: 'orangecream', 4: 'tridelta', 5: 'joyfulnoise', 6: 'meche', 7: 'cranberry'}
    
    app.unlockedThemes = {0: 'midnight', 1: 'honeybutter', 2: 'oceanmilk'}
    
    app.backgroundColors = {'midnight': rgb(144, 155, 187), 
                            'honeybutter': rgb(244, 218, 157), 
                            'oceanmilk': rgb(168, 209, 240), 
                            'orangecream': rgb(244, 181, 128), 
                            'tridelta': rgb(0, 70, 184),
                            'joyfulnoise': rgb(38, 88, 46),
                            'meche': rgb(214, 177, 187),
                            'cranberry': rgb(114, 37, 31)
    }
    
    app.secondaryColors = {'midnight': rgb(123, 133, 159), 
                           'honeybutter': rgb(230, 198, 122), 
                           'oceanmilk': rgb(130, 161, 184), 
                           'orangecream': rgb(212, 185, 161), 
                           'tridelta': rgb(27, 141, 159),
                           'joyfulnoise': rgb(122, 196, 135),
                           'meche': rgb(221, 129, 154),
                           'cranberry': rgb(148, 46, 39)
    }
                           
    app.selectedTheme = 0
    
    app.imageBoard = dict()
    
    app.baseUrl = 'https://raw.githubusercontent.com/wonderella/compMinesweeper/main'

    #building lists
    for theme in app.themes:
        themeName = app.themes[theme]

        numList = [f'{app.baseUrl}/{themeName}/{i}.png' for i in range(9)]
        # 9: bomb, 10: cover, 11: flagged, 12: wrongFlag, 13: pressed
        xtraList = [f'{app.baseUrl}/{themeName}/bomb.png', 
                        f'{app.baseUrl}/{themeName}/cover.png', 
                        f'{app.baseUrl}/{themeName}/flagged.png', 
                        f'{app.baseUrl}/{themeName}/wrongFlag.png',
                        f'{app.baseUrl}/{themeName}/pressed.png']
        numList.extend(xtraList)
        
        app.imageBoard[themeName] = numList
    
    
    themeName = app.unlockedThemes[app.selectedTheme]
    app.background = app.backgroundColors[themeName]
    
    app.buttonSound = Sound(f'{app.baseUrl}/buttonSound.mp3')
    
def setUpMenu(app):
    
    game1 = Button(app.width//2, 250, 150, 40, 'Normal', 'levelOneMenu', 18, 'blue')
    game2 = Button(app.width//2, 300, 150, 40, 'Competitive', 'levelTwoMenu', 18, 'red')
    game3 = Button(app.width//2, 350, 150, 40, 'Musical', 'levelThreeMenu', 18, 'red')
    
    themeRight = Button(app.width/2 + 90, 400, 30, 30, '>', 'themeRight', 18, 'green')
    themeLeft = Button(app.width/2 - 90, 400, 30, 30, '<', 'themeLeft', 18, 'green')
    
    statButton = Button(app.width-30, 30, 30, 30, '=', 'openStats', 25, 'red')
    
    storeButton = Button(30, 30, 30, 30, '$', 'openStore', 18, 'red')
    
    soundButton = Button(app.width-70, 30, 30, 30, None, 'sound', 18, 'red')
    
    howToButton = Button(app.width-30, app.height-30, 30, 30, '?', 'howNormal', 20, 'red')
    
    app.menuButtons = [game1, game2, game3, themeRight, themeLeft, statButton, storeButton, soundButton, howToButton]
    
    app.statScreen = False
    app.storeScreen = False
    
    backButton = Button(app.width - 70, 70, 30, 30, 'X', 'goBack', 18, 'red')

    playSong = Button(app.width/2, 400, 30, 30, None, 'playSong', 18, 'red')
    
    app.statButtons = [backButton, playSong]
    
    theme1 = Button(app.width/2 - 40, 180, 180, 40, 'orangecream', 'orangecream', 18, 'red')
    theme2 = Button(app.width/2 - 40, 240, 180, 40, 'cranberry', 'cranberry', 18, 'red')
    theme3 = Button(app.width/2 - 40, 300, 180, 40, 'meche', 'meche', 18, 'red')
    theme4 = Button(app.width/2 - 40, 360, 180, 40, 'tridelta', 'tridelta', 18, 'red')
    theme5 = Button(app.width/2 - 40, 420, 180, 40, 'joyfulnoise', 'joyfulnoise', 18, 'red')
    
    theme1.givePrice(500)
    theme2.givePrice(750)
    theme3.givePrice(1000)
    theme4.givePrice(1500)
    theme5.givePrice(2250)
    
    app.storeButtons = [backButton, theme1, theme2, theme3, theme4, theme5]
    

    
    app.drawLockedHover = False
    app.mouseXHover = 0
    app.mouseYHover = 0
    
def setUpLevelOneMenu(app):
    #size selector
    increaseSize = Button(app.width/2 + 60, 170, 20, 20, '↑', 'increase', 18, 'green')
    decreaseSize = Button(app.width/2 - 60, 170, 20, 20, '↓', 'decrease', 18, 'red')
    
    #difficulty
    easyButton = Button(app.width//2, 260, 110, 30, 'Easy', 'easy', 18, 'green')
    mediumButton = Button(app.width//2, 290, 110, 30, 'Medium', 'medium', 18, 'orange')
    hardButton = Button(app.width//2, 320, 110, 30, 'Hard', 'hard', 18, 'red')
    
    #start game
    startButton = Button(app.width//2, 430, 150, 50, 'Start Game', 'levelOne', 18, 'pink')
    
    app.levelOneMenuButtons = [increaseSize, decreaseSize, easyButton, mediumButton, hardButton, startButton]
    
def setUpLevelTwoMenu(app):
    #difficulty
    easyButton = Button(app.width//2, 240, 110, 30, 'Small', 'small', 18, 'green')
    mediumButton = Button(app.width//2, 270, 110, 30, 'Medium', 'medium', 18, 'orange')
    hardButton = Button(app.width//2, 300, 110, 30, 'Large', 'large', 18, 'red')
    
    #start game
    startButton = Button(app.width//2, 410, 150, 50, 'Start Game', 'levelTwo', 18, 'pink')
    
    app.levelTwoMenuButtons = [easyButton, mediumButton, hardButton, startButton]
    
def setUpLevelThreeMenu(app):
    #difficulty
    easyButton = Button(app.width//2, 240, 110, 30, 'Easy', 'easy', 18, 'green')
    mediumButton = Button(app.width//2, 270, 110, 30, 'Medium', 'medium', 18, 'orange')
    hardButton = Button(app.width//2, 300, 110, 30, 'Hard', 'hard', 18, 'red')
    
    #start game
    startButton = Button(app.width//2, 410, 150, 50, 'Start Game', 'levelThree', 18, 'pink')
    
    app.levelThreeMenuButtons = [easyButton, mediumButton, hardButton, startButton]
    
    

### GAME 1: REGULAR MINESWEEPER ###
    
def setUpGame1(app):
    app.difficulty = 'medium'
    app.difficultyDict = {'easy': 0.1, 'medium': 0.15, 'hard': 0.22}
    app.bombTotal = 20
    app.rows = 10
    app.cols = 10
    
    backButton = Button(app.width-30, 30, 30, 30, 'X', 'startScreen', 18, 'red')
    reset = Button(app.width/2, 50, 50, 50, None, 'reset', 18, None)
    
    app.levelOneButtons = [backButton, reset]
    
def boardSetUp(app):
    app.boardWidth = 380
    app.boardHeight = app.boardWidth
    app.boardLeft = app.width//2 - app.boardWidth//2
    app.boardTop = app.height//2 - app.boardHeight//2 + 40
    app.cellBorderWidth = 1
    app.cellSelection = None
    
def internalBoard(app):
    rows = app.rows
    cols = app.cols
    
    #2D Board the size of board
    board = []
    for row in range(rows):
        rowList = []
        for col in range(cols):
            rowList.append(Cell(row, col))
        board.append(rowList)
        
    app.internalBoard = board
    
def generateBombs(app):
    rows = app.rows
    cols = app.cols
    
    i = 0
    while i < app.bombTotal:
        randRow = random.randrange(0, rows)
        randCol = random.randrange(0, cols)
        newLocation = (randRow, randCol)
        
        thisCell = app.internalBoard[randRow][randCol]
        if not thisCell.bomb:
            thisCell.becomeBomb()
            i += 1

def countSurroundings(app):
    rows = app.rows
    cols = app.cols
    
    for row in range(rows):
        for col in range(cols):
            thisCell = app.internalBoard[row][col]
            bombCounts = surround(app, thisCell)
            thisCell.addCounts(bombCounts)
            
def surround(app, cell):
    row = cell.row
    col = cell.col
    
    bombCounts = 0
    for drow in [-1, 0, +1]:
        for dcol in [-1, 0, +1]:
            nextRow = row + drow
            nextCol = col + dcol
            if ((0 <= nextRow < app.rows) and
               (0 <= nextCol < app.cols) and
               (drow, dcol != (0,0))):
                   surroundCell = app.internalBoard[nextRow][nextCol]
                   if surroundCell.bomb:
                       bombCounts += 1
                       
    return bombCounts


def revealStart(app):
    rows = app.rows
    cols = app.cols
    
    found = False
    while not found:
        randRow = random.randrange(0, rows)
        randCol = random.randrange(0, cols)
        newLocation = (randRow, randCol)
        
        thisCell = app.internalBoard[randRow][randCol]
        if thisCell.bombCount == 0:
            floodFill(app, randRow, randCol)
            found = True
            

def levelOne_redrawAll(app):
    #top menu
    drawLabel(f'Remaining Bombs: {app.bombRemain}', 310, app.boardTop - 10, size=15, font=app.font)
    
    for button in app.levelOneButtons:
        button.draw(app)
        
    if app.gameWin:
        smiley = f'{app.baseUrl}/smileyWin.png'
    elif app.gameOver:
        smiley = f'{app.baseUrl}/smileyLose.png'
    elif app.smileyOnPress:
        smiley = f'{app.baseUrl}/smileyOnPress.png'
    else:
        smiley = f'{app.baseUrl}/smileyNormal.png'
    drawImage(smiley, app.width/2, app.boardTop/2, width=50, height=50, align='center')
    
    if app.gameOver:
        drawGameOver(app)
    elif app.gameWin:
        drawGameWin(app)
        
    else:
        drawBoard(app)
        drawBorder(app)
        
def levelOne_onScreenActivate(app):
    resetBoardOne(app)
    
def resetBoardOne(app):
    boardSetUp(app)
    internalBoard(app)

    generateBombs(app)
    
    countSurroundings(app)
    
    revealStart(app)
    
    app.bombRemain = int(app.bombTotal)
    
    app.gameOver = False
    app.gameWin = False
    app.smileyOnPress = False
    
### GAME 2: COMPETITIVE MINESWEEPER ###

def setUpGame2(app):
    app.gameTwoSize = 'medium'
    app.timer = 90
    app.bombTotal = 20
    app.rows = 10
    app.cols = 10
    
    app.difficultyDictTwo = {'small': 0.1, 'medium': 0.15, 'large': 0.22}
    app.gameTwoSizeDict = {'small': 8, 'medium': 10, 'large': 15}
    app.gameTwoTimeDict = {'small': 60, 'medium': 90, 'large': 135}
    
    backButton = Button(app.width-30, 30, 30, 30, 'X', 'startScreen', 18, 'red')
    pauseButton = Button(app.width/2 + 50, 30, 30, 30, '||', 'pause', 18, 'blue')
    
    app.levelTwoButtons = [backButton]

def levelTwo_onScreenActivate(app):
    resetBoardTwo(app)
    
def resetBoardTwo(app):
    boardSetUp(app)
    internalBoard(app)

    generateBombs(app)
    
    countSurroundings(app)
    
    revealStart(app)
    
    app.bombRemain = int(app.bombTotal)
    
    app.stepsPerSecond = 1
    
    app.points = 0
    
    app.hindered = False
    app.hinderedTimer = 3
    app.paused = False
    
    app.gameWin = False
    
def levelTwo_redrawAll(app):
    #top menu
    
    seconds = app.timer % 60
    minutes = app.timer // 60
    
    if seconds < 10:
        drawLabel(f'{minutes}:0{seconds}', app.width/2, app.boardTop/2, size=40, fill='white', font=app.font)
    else:
        drawLabel(f'{minutes}:{seconds}', app.width/2, app.boardTop/2, size=40, fill='white', font=app.font)
        
    drawLabel(f'Remaining Bombs: {app.bombRemain}', 310, app.boardTop - 10, size=15, font=app.font)
    drawLabel(f'Points: {app.points}', 50, app.boardTop - 10, size=15, font=app.font)
    
    for button in app.levelTwoButtons:
        button.draw(app)

    if app.gameWin:
        drawGameWinTwo(app)
        
    else:
        drawBoard(app)
        drawBorder(app)
        if app.hindered:
            drawHinderance(app)

### GAME 3: MUSICAL MINESWEEPER ###

def setUpGame3(app):   
    app.difficulty = 'medium'
    app.difficultyDict = {'easy': 0.1, 'medium': 0.15, 'hard': 0.22}
    app.bombTotal = 20

    backButton = Button(app.width-30, 30, 30, 30, 'X', 'startScreen', 18, 'red')
    reset = Button(app.width/2, 50, 50, 50, None, 'reset', 18, None)
    
    playSong = Button(app.width/2 - 70, 50, 50, 50, None, 'playSong', 18, None)
    
    app.levelThreeButtons = [backButton, reset, playSong]
    
def levelThree_onScreenActivate(app):
    resetBoardThree(app)
    
    
def resetBoardThree(app):
    boardSetUp(app)
    internalBoard(app)

    generateBombs(app)
    
    countSurroundings(app)
    
    revealStart(app)
    
    app.rows = 15
    app.cols = 15
    
    app.bombRemain = int(app.bombTotal)
    
    app.gameOver = False
    app.gameWin = False
    app.smileyOnPress = False
    
    app.songNotes = []
    
def levelThree_redrawAll(app):
    #top menu
    drawLabel(f'Remaining Bombs: {app.bombRemain}', 310, app.boardTop - 10, size=15, font=app.font)
    
    for button in app.levelThreeButtons:
        if button.action != 'playSong':
            button.draw(app)
        elif button.action == 'playSong' and app.gameWin:
            button.draw(app)
            drawImage(f'{app.baseUrl}/sound.png', app.width/2-70, 50, width=50, height=50, align='center')
        
    if app.gameWin:
        smiley = f'{app.baseUrl}/smileyWin.png'
    elif app.gameOver:
        smiley = f'{app.baseUrl}/smileyLose.png'
    elif app.smileyOnPress:
        smiley = f'{app.baseUrl}/smileyOnPress.png'
    else:
        smiley = f'{app.baseUrl}/smileyNormal.png'
    drawImage(smiley, app.width/2, app.boardTop/2, width=50, height=50, align='center')

    
    if app.gameOver:
        drawGameOver(app)
    elif app.gameWin:
        drawGameWin(app)
        
    else:
        drawBoard(app)
        drawBorder(app)
    
###DRAWING THE BOARD###  

# modified from notes

def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)
            
def drawCell(app, row, col):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    
    theme = app.unlockedThemes[app.selectedTheme]
    themeList = app.imageBoard[theme]
    bomb, cover, flagged, wrongFlag = 9, 10, 11, 12
    
    thisCell = app.internalBoard[row][col]
    
    if not thisCell.bomb:
        numberImg = themeList[thisCell.bombCount]
        drawImage(numberImg, cellLeft, cellTop, width=cellWidth, height=cellHeight)
    else:
        bombImg = themeList[bomb]
        drawImage(bombImg, cellLeft, cellTop, width=cellWidth, height=cellHeight)
    
    coverImg = themeList[cover]
    if not thisCell.revealed:
        drawImage(coverImg, cellLeft, cellTop, width=cellWidth, height=cellHeight)
        
    flaggedImg = themeList[flagged]
    if thisCell.flagged:
        drawImage(flaggedImg, cellLeft, cellTop, width=cellWidth, height=cellHeight)
        
        
    # IN A GAME OVER STATE
    wrongImg = themeList[wrongFlag]
    if thisCell.wrongFlag:
        drawImage(wrongImg, cellLeft, cellTop, width=cellWidth, height=cellHeight)
        
        
    
             
def getCellLeftTop(app, row, col):
    width, height = getCellSize(app)
    left = app.boardLeft + col*width
    top = app.boardTop + row*height
    return left, top
    
def getCellSize(app):
    width = app.boardWidth/app.cols
    height = app.boardHeight/app.rows
    return width, height
    
def drawBorder(app):
    themeName = app.unlockedThemes[app.selectedTheme]
    color = app.secondaryColors[themeName]
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight,
             fill=None, border=color, borderWidth=2*app.cellBorderWidth)
             
             
###GAME OVER###

def drawGameOver(app):
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.internalBoard[row][col]
            
            if cell.flagged and not cell.bomb:
                cell.isWrong()
            
            else:
                cell.reveal()
        
    drawBoard(app)
    drawBorder(app)
    
###GAME WIN ONE###

def drawGameWin(app):
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.internalBoard[row][col]
            
            if cell.bomb and not cell.flagged:
                cell.flagCell()
                
    drawBoard(app)
    drawBorder(app)
    
    
###GAME WIN TWO###

def drawGameWinTwo(app):
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.internalBoard[row][col]
            
            if cell.bomb and not cell.flagged:
                cell.flagCell()
            else:
                cell.reveal()
        
    drawBoard(app)
    drawBorder(app)
    
    
###HINDERANCE###

def drawHinderance(app):
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight,
            fill='red', opacity=50)
    drawLabel('YOU HIT A BOMB', app.boardLeft + app.boardWidth/2, app.boardTop + app.boardHeight/2,
             size=20, fill='white', bold=True, font=app.font)
             
    drawLabel(f'Time Left: {app.hinderedTimer}', app.boardLeft + app.boardWidth/2, app.boardTop + app.boardHeight/2 + 20,
             size=20, fill='white', bold=True, font=app.font)

###START SCREEN###

def startScreen_redrawAll(app):
    drawStartScreen(app)

def drawStartScreen(app):
    #title
    drawImage(f'{app.baseUrl}/title.png', app.width//2, 170, width=390, height=390, align='center')
    #drawLabel('Minesweeper', app.width//2, 170, size=60, font=app.font)
    
    #jn & tridelt special
    themeName = app.unlockedThemes[app.selectedTheme]
    if themeName == 'joyfulnoise':
        drawLabel(""" Shout for joy to the Lord, """, 200, 40, size=16, fill='white', font=app.font)
        drawLabel(""" all the Earth! (Psalm 100:1) """, 200, 55, size=16, fill='white', font=app.font)
    elif themeName == 'tridelta':
        drawLabel(""" Let us steadfastly """, 200, 40, size=16, fill='white', font=app.font)
        drawLabel('love one another', 200, 55, size=16, fill='white', font=app.font)
    
    #menu buttons
    for button in app.menuButtons:
        if button.action != 'levelThreeMenu':
            button.draw(app)
        elif button.action == 'levelThreeMenu' and not app.musicLocked:
            button.draw(app)
        
    #locked Comp
    if app.compLocked:
        drawImage(f'{app.baseUrl}/lock.png', app.width//2, 300, width=30, height=30, align='center')
        
        if app.drawLockedHover:
            themeName = app.unlockedThemes[app.selectedTheme]
            drawRect(app.mouseXHover, app.mouseYHover, 140, 40, fill=app.secondaryColors[themeName],
                                 opacity=50)
                        
            gamesLeft = 5 - app.normalWins
            if gamesLeft == 1:
                drawLabel(f'Win {gamesLeft} more time',app.mouseXHover + 70, app.mouseYHover + 13.5, fill='white', font=app.font, bold=True)
            else:
                drawLabel(f'Win {gamesLeft} more times',app.mouseXHover + 70, app.mouseYHover + 13.5, fill='white', font=app.font, bold=True)
            
            drawLabel('to unlock this!',app.mouseXHover + 70, app.mouseYHover + 27.5, fill='white', font=app.font, bold=True)
    
    #theme
    drawLabel(f'{app.unlockedThemes[app.selectedTheme]}', app.width//2, 400, size=18, fill='white', font=app.font)
    
    #sound button
    drawImage(f'{app.baseUrl}/sound.png', app.width-85, 15, width=30, height=30)
    if app.muted:
        drawLabel('/', app.width-70, 30, size=30, fill='white')
    
    #stats
    if app.statScreen:
        drawStats(app)
        
    elif app.storeScreen:
        drawStore(app)
    
    
def drawStats(app):
    themeName = app.unlockedThemes[app.selectedTheme]
    color = app.secondaryColors[themeName]
    drawRect(app.width//2, app.height//2, 300, 400, fill=color, align='center')
    left, top = app.width//2 - 300//2, app.height//2 - 400//2
    width, height = 300, 400
    
    # drawLabel('Stats:', app.width//2, top + 40, size=25, font=app.font)
    drawImage(f'{app.baseUrl}/stats.png', app.width//2, top + 45, width=200, height=200, align='center')
    
    drawLabel(f'Normal Wins: {app.normalWins}', app.width//2, top + 100, size=20, font=app.font)
    
    drawLabel(f'Competitive Leaderboard:', app.width//2, top + 150, size=20, font=app.font)
    
    drawHighScores(app)
    
    if not app.musicLocked:
        drawLabel(f'Musical Wins: {app.musicalWins}', app.width//2, top + 300, size=20, font=app.font)
            
    for button in app.statButtons:
        if button.action != 'playSong':
            button.draw(app)
        elif (app.musicalWins >= 1):
            drawLabel(f'Last Song:', app.width//2, top + 320, size=12, font=app.font)
            button.draw(app)
            drawImage(f'{app.baseUrl}/sound.png', app.width/2, 400, width=30, height=30, align='center')
            
def drawStore(app):
    themeName = app.unlockedThemes[app.selectedTheme]
    color = app.secondaryColors[themeName]
    drawRect(app.width//2, app.height//2, 300, 400, fill=color, align='center')
    left, top = app.width//2 - 300//2, app.height//2 - 400//2
    width, height = 300, 400
    
    # drawLabel('Buy Themes!', app.width//2, top + 40, size=25, font=app.font)
    drawImage(f'{app.baseUrl}/specialThemes.png', app.width//2, top + 45, width=200, height=200, align='center')
    
    drawLabel(f'Points: {app.totalPoints}', app.width//2, top + 85, size=16, font=app.font)
    
    for button in app.storeButtons:
        if button.action != 'goBack':
            x = button.x
            y = button.y
            price = button.price
            
            if button.action in app.unlockedThemes.values():
                drawLabel('owned', x + 130, y, size=16, font=app.font)
            else:
                drawLabel(f'{price}', x + 130, y, size=16, font=app.font)
        button.draw(app)

#high scores taken from my custom tetris case study
def drawHighScores(app):
    for i in range(len(app.compWins)):
        if i >= 5:
            break
        score = app.compWins[i]
        spacing = 20
        x = app.width//2
        y = 230 + spacing * i
        drawLabel(f'{i+1}. {score}', x, y, font=app.font, size=16)
    
    
def startScreen_onMouseRelease(app, mouseX, mouseY):
    if app.statScreen:
        for button in app.statButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(False)
                action = button.action
                if action == 'goBack':
                    app.statScreen = False
                elif action == 'playSong':
                    app.lastSong.play()
    
    elif app.storeScreen:
        for button in app.storeButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(False)
                action = button.action
                if action == 'goBack':
                    app.storeScreen = False
                elif button.action not in app.unlockedThemes.values():
                    if action == 'orangecream':
                        if app.totalPoints >= button.price:
                            app.totalPoints -= button.price
                            nextNum = len(app.unlockedThemes)
                            app.unlockedThemes[nextNum] = 'orangecream'
                    elif action == 'cranberry':
                        if app.totalPoints >= button.price:
                            app.totalPoints -= button.price
                            nextNum = len(app.unlockedThemes)
                            app.unlockedThemes[nextNum] = 'cranberry'
                    elif action == 'meche':
                        if app.totalPoints >= button.price:
                            app.totalPoints -= button.price
                            nextNum = len(app.unlockedThemes)
                            app.unlockedThemes[nextNum] = 'meche'
                    elif action == 'tridelta':
                        if app.totalPoints >= button.price:
                            app.totalPoints -= button.price
                            nextNum = len(app.unlockedThemes)
                            app.unlockedThemes[nextNum] = 'tridelta'
                    elif action == 'joyfulnoise':
                        if app.totalPoints >= button.price:
                            app.totalPoints -= button.price
                            nextNum = len(app.unlockedThemes)
                            app.unlockedThemes[nextNum] = 'joyfulnoise'
    else:
        for button in app.menuButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(False)
                if button.action == 'levelOneMenu':
                    setActiveScreen(button.action)
                    break
                elif button.action == 'levelTwoMenu':
                    if not app.compLocked:
                        setActiveScreen(button.action)
                        break
                elif button.action == 'levelThreeMenu':
                    if not app.musicLocked:
                        setActiveScreen('levelThreeMenu')
                        break
                elif button.action == 'themeLeft':
                    app.selectedTheme = (app.selectedTheme - 1) % len(app.unlockedThemes)
                    themeName = app.unlockedThemes[app.selectedTheme]
                    app.background = app.backgroundColors[themeName]
                elif button.action == 'themeRight':
                    app.selectedTheme = (app.selectedTheme + 1) % len(app.unlockedThemes)
                    themeName = app.unlockedThemes[app.selectedTheme]
                    app.background = app.backgroundColors[themeName]
                elif button.action == 'openStats':
                    app.statScreen = True
                elif button.action == 'openStore' and not app.compLocked:
                    app.drawLockedHover = False
                    app.storeScreen = True
                elif button.action == 'sound':
                    app.muted = not app.muted
                    app.soundCount += 1
                    if app.soundCount == 10:
                        app.musicLocked = False
                elif button.action == 'howNormal':
                    setActiveScreen('howNormal')
                    break
    
                    
def startScreen_onMouseDrag(app, mouseX, mouseY):
    if app.statScreen:
        for button in app.statButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(True)
            else:
                button.isPressed(False)
    
    elif app.storeScreen:
        for button in app.storeButtons:
            if button.contains(mouseX, mouseY):
                if button.price == None:
                    button.isPressed(True)
                else:
                    if (button.action in app.unlockedThemes.values()) or app.totalPoints <= button.price:
                        return
                    else:
                        button.isPressed(True)
            else:
                button.isPressed(False)
    
    else:
        for button in app.menuButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(True)
            else:
                button.isPressed(False)
                
def startScreen_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    if app.statScreen:
        for button in app.statButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(True)
                
    if app.storeScreen:
        for button in app.storeButtons:
            if button.contains(mouseX, mouseY):
                if button.price == None:
                    button.isPressed(True)
                else:
                    if (button.action in app.unlockedThemes.values()) or app.totalPoints <= button.price:
                        return
                    else:
                        button.isPressed(True)
    else:
        for button in app.menuButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(True)
                
def startScreen_onMouseMove(app, mouseX, mouseY):
    if app.statScreen or app.storeScreen:
        return
    
    app.drawLockedHover = False
    
    for button in app.menuButtons:
        if (button.action == 'levelTwoMenu' or button.action == 'openStore'):
            if button.contains(mouseX, mouseY) and (app.compLocked):
                app.drawLockedHover = True
                app.mouseXHover = mouseX
                app.mouseYHover = mouseY
                break

                        

### SIZE & DIFFULTY: LEVEL ONE ###

def levelOneMenu_redrawAll(app):
    #title
    drawImage(f'{app.baseUrl}/normal.png', app.width//2, 90, width=300, height=300, align='center')
    
    #size selector
    drawLabel('select size:', app.width//2, 140, size=20, font=app.font)
    drawLabel('x', app.width//2, 170, size=18, font=app.font)
    
    drawLabel(f'{app.cols}', app.width//2 - 30, 170, size=18, font=app.font)
    drawLabel(f'{app.rows}', app.width//2 + 30, 170, size=18, font=app.font)
    
    #difficulty
    drawLabel('select difficulty:', app.width//2, 220, size=20, font=app.font)
    drawLabel(f'selected: {app.difficulty}', app.width//2, 370, size=20, font=app.font)
    
    for button in app.levelOneMenuButtons:
        button.draw(app)

    
def levelOneMenu_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    for button in app.levelOneMenuButtons:
        if button.contains(mouseX, mouseY):
            button.isPressed(True)
    
def levelOneMenu_onMouseDrag(app, mouseX, mouseY):
    for button in app.levelOneMenuButtons:
        if button.contains(mouseX, mouseY):
            button.isPressed(True)
        else:
            button.isPressed(False)
    
    
def levelOneMenu_onMouseRelease(app, mouseX, mouseY):
    for button in app.levelOneMenuButtons:
        if button.contains(mouseX, mouseY):
            action = button.action
            button.isPressed(False)
            if action == 'increase':
                if app.rows < 15:
                    app.rows += 1
                    app.cols += 1
            elif action == 'decrease':
                if app.rows > 8:
                    app.rows -= 1
                    app.cols -= 1
            elif action == 'easy':
                app.difficulty = 'easy'
            elif action == 'medium':
                app.difficulty = 'medium'
            elif action == 'hard':
                app.difficulty = 'hard'
            elif action == 'levelOne':
                app.bombTotal = int((app.difficultyDict[app.difficulty])*(app.rows*app.cols))
                print(app.bombTotal)
                setActiveScreen(action)
                
def levelOneMenu_onMouseMove(app, mouseX, mouseY):
    for button in app.levelOneMenuButtons:
        if button.contains(mouseX, mouseY):
            if button.action == 'levelOne':
                button.isHovered = True
        else:
            button.isHovered = False

### SIZE & DIFFULTY: LEVEL TWO ###

def levelTwoMenu_redrawAll(app):
    #title
    drawImage(f'{app.baseUrl}/competitive.png', app.width//2, 120, width=300, height=300, align='center')
    
    #difficulty
    drawLabel('select size:', app.width//2, 200, size=20, font=app.font)
    drawLabel(f'selected: {app.gameTwoSize}', app.width//2, 350, size=20, font=app.font)
    
    for button in app.levelTwoMenuButtons:
        button.draw(app)

    
def levelTwoMenu_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    for button in app.levelTwoMenuButtons:
        if button.contains(mouseX, mouseY):
            button.isPressed(True)
    
def levelTwoMenu_onMouseDrag(app, mouseX, mouseY):
    for button in app.levelTwoMenuButtons:
        if button.contains(mouseX, mouseY):
            button.isPressed(True)
        else:
            button.isPressed(False)
    
    
def levelTwoMenu_onMouseRelease(app, mouseX, mouseY):
    for button in app.levelTwoMenuButtons:
        if button.contains(mouseX, mouseY):
            action = button.action
            button.isPressed(False)
            if action == 'small':
                app.gameTwoSize = 'small'
            elif action == 'medium':
                app.gameTwoSize = 'medium'
            elif action == 'large':
                app.gameTwoSize = 'large'
            elif action == 'levelTwo':
                
                app.rows = app.gameTwoSizeDict[app.gameTwoSize]
                app.cols = app.gameTwoSizeDict[app.gameTwoSize]
                app.bombTotal = (app.difficultyDictTwo[app.gameTwoSize])*(app.rows*app.cols)
                app.timer = app.gameTwoTimeDict[app.gameTwoSize]
                
                setActiveScreen(action)
                
def levelTwoMenu_onMouseMove(app, mouseX, mouseY):
    for button in app.levelTwoMenuButtons:
        if button.contains(mouseX, mouseY):
            if button.action == 'levelTwo':
                button.isHovered = True
        else:
            button.isHovered = False

### SIZE & DIFFULTY: LEVEL THREE ###

def levelThreeMenu_redrawAll(app):
    #title
    drawImage(f'{app.baseUrl}/musical.png', app.width//2, 120, width=300, height=300, align='center')
    
    #difficulty
    drawLabel('select difficulty:', app.width//2, 200, size=20, font=app.font)
    drawLabel(f'selected: {app.difficulty}', app.width//2, 350, size=20, font=app.font)
    
    for button in app.levelThreeMenuButtons:
        button.draw(app)
    
def levelThreeMenu_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    for button in app.levelThreeMenuButtons:
        if button.contains(mouseX, mouseY):
            button.isPressed(True)
    
def levelThreeMenu_onMouseDrag(app, mouseX, mouseY):
    for button in app.levelThreeMenuButtons:
        if button.contains(mouseX, mouseY):
            button.isPressed(True)
        else:
            button.isPressed(False)
    
    
def levelThreeMenu_onMouseRelease(app, mouseX, mouseY):
    for button in app.levelThreeMenuButtons:
        if button.contains(mouseX, mouseY):
            action = button.action
            button.isPressed(False)
            if action == 'easy':
                app.difficulty = 'easy'
            elif action == 'medium':
                app.difficulty = 'medium'
            elif action == 'hard':
                app.difficulty = 'hard'
            elif action == 'levelThree':
            
                app.rows = 15
                app.cols = 15
                app.bombTotal = int((app.difficultyDict[app.difficulty])*(app.rows*app.cols))
                print(int((app.difficultyDict[app.difficulty])*(app.rows*app.cols)))
                print(app.difficulty)
                print(app.bombTotal)

                setActiveScreen(action)

###CELL SELECTION GAME ONE###

def levelOne_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        app.smileyOnPress = True
        selectRow, selectCol = selectedCell
        thisCell = app.internalBoard[selectRow][selectCol]
        if thisCell.flagged:
            return
        
        if thisCell.bomb:
            app.gameOver = True
        elif (not thisCell.flagged) and (not thisCell.revealed):
            floodFill(app, selectRow, selectCol)
        elif thisCell.revealed:
            surroundFill(app, selectRow, selectCol)
            
        checkGameWin(app)
    else:
        for button in app.levelOneButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(True)
    
def levelOne_onMouseDrag(app, mouseX, mouseY):
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        app.smileyOnPress = True
    
    for button in app.levelOneButtons:
        if button.contains(mouseX, mouseY):
            button.isPressed(True)
        else:
            button.isPressed(False)

def levelOne_onMouseRelease(app, mouseX, mouseY):   
    app.smileyOnPress = False
    for button in app.levelOneButtons:
        if button.contains(mouseX, mouseY):
            action = button.action
            button.isPressed(False)
            if action == 'startScreen':
                setActiveScreen('startScreen')
            elif action == 'reset':
                resetBoardOne(app)
            
def levelOne_onMouseMove(app, mouseX, mouseY):
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        if app.cellSelection == selectedCell:
            return None
        else:
            app.cellSelection = selectedCell
    else:
        app.cellSelection = None
            
def getCell(app, x, y):
    dx = x - app.boardLeft
    dy = y - app.boardTop
    width, height = getCellSize(app)
    
    selectRow = math.floor(dy/height)
    selectCol = math.floor(dx/width)
    
    if ((0 <= selectRow < app.rows) and
       (0 <= selectCol < app.cols)):
           return (selectRow, selectCol)
    else:
        return None
        
def checkGameWin(app):
    if app.gameWin or app.gameOver:
        return
    
    rows, cols = len(app.internalBoard), len(app.internalBoard[0])
    for row in range(rows):
        for col in range(cols):
            thisCell = app.internalBoard[row][col]
            if not thisCell.revealed and not thisCell.bomb:
                return
                
    app.gameWin = True
    app.normalWins += 1
    app.bombRemain = 0
    if app.normalWins >= 5:
        app.compLocked = False
    
### FLAGGING GAME ONE###

def levelOne_onKeyPress(app, key):
    if app.gameOver or app.gameWin:
        return
    
    if key == 'f':
        selectRow, selectCol = app.cellSelection
        thisCell = app.internalBoard[selectRow][selectCol]
        if not thisCell.revealed:
            thisCell.flagCell()
        
        countRemaining(app)
    
    #FOR DEMO/GRADING PURPOSES
    elif key == '!':
        rows, cols = len(app.internalBoard), len(app.internalBoard[0])
        for row in range(rows):
            for col in range(cols):
                thisCell = app.internalBoard[row][col]
                if thisCell.bomb:
                    thisCell.flagCell()
                else:
                    thisCell.reveal()
                    
                checkGameWin(app)
        
def countRemaining(app):
    countFlags = 0
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.internalBoard[row][col]
            if cell.flagged:
                countFlags += 1
                
    app.bombRemain = int(app.bombTotal - countFlags)
    

###CELL SELECTION GAME TWO###

def levelTwo_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    for button in app.levelTwoButtons:
        if button.contains(mouseX, mouseY):
            action = button.action
            if action == 'startScreen':
                setActiveScreen('startScreen')
            elif action == 'pause':
                app.paused = not app.paused
                
    if app.gameWin:
        return
    
    selectedCell = getCell(app, mouseX, mouseY)
    if app.hindered:
        return
    if selectedCell != None:
        selectRow, selectCol = selectedCell
        thisCell = app.internalBoard[selectRow][selectCol]
        if thisCell.flagged:
            return
        
        if thisCell.bomb:
            app.hinderedTimer = 3
            app.points -= 10
            thisCell.flagCell()
            app.hindered = True
        elif (not thisCell.flagged) and (not thisCell.revealed):
            floodFillTwo(app, selectRow, selectCol)
            
    checkGameWinTwo(app)

            
def levelTwo_onMouseMove(app, mouseX, mouseY):
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        if app.cellSelection == selectedCell:
            return None
        else:
            app.cellSelection = selectedCell
    else:
        app.cellSelection = None
        
        
def levelTwo_onStep(app):
    if not app.gameWin and not app.paused:
        takeStep(app)
        
def takeStep(app):
    if app.timer > 0:
        app.timer -= 1
    elif app.timer == 0:
        app.gameWin = True
    
    if app.hindered:
        if app.hinderedTimer > 0:
            app.hinderedTimer -= 1
        elif app.hinderedTimer == 0:
            app.hindered = False
            
        
def checkGameWinTwo(app):
    if app.gameWin:
        return
    
    rows, cols = len(app.internalBoard), len(app.internalBoard[0])
    for row in range(rows):
        for col in range(cols):
            thisCell = app.internalBoard[row][col]
            if not thisCell.revealed and not thisCell.bomb:
                return
                
    app.gameWin = True
    app.points += app.timer
    app.compWins.append(app.points)
    app.compWins.sort(reverse=True)
    print(app.compWins)
    app.totalPoints += app.points

### FLAGGING GAME TWO###

def levelTwo_onKeyPress(app, key):
    if app.gameWin or app.hindered:
        return
    
    if key == 'f':
        selectRow, selectCol = app.cellSelection
        thisCell = app.internalBoard[selectRow][selectCol]
        if not thisCell.revealed:
            thisCell.flagCell()
        
        countRemaining(app)
        
    #FOR DEMO PURPOSES
    elif key == '!':
        rows, cols = len(app.internalBoard), len(app.internalBoard[0])
        for row in range(rows):
            for col in range(cols):
                thisCell = app.internalBoard[row][col]
                if thisCell.bomb:
                    thisCell.flagCell()
                else:
                    thisCell.reveal()
                    
                checkGameWinTwo(app)

###CELL SELECTION GAME THREE###

def levelThree_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        app.smileyOnPress = True
        selectRow, selectCol = selectedCell
        thisCell = app.internalBoard[selectRow][selectCol]
        if thisCell.flagged:
            return
        
        if thisCell.bomb:
            app.gameOver = True
        elif (not thisCell.flagged) and (not thisCell.revealed):
            floodFillMusic(app, selectRow, selectCol)
        elif thisCell.revealed:
            surroundFillMusic(app, selectRow, selectCol)
            
        checkGameWinThree(app)
    else:
        for button in app.levelThreeButtons:
            if button.contains(mouseX, mouseY):
                button.isPressed(True)
    
def levelThree_onMouseDrag(app, mouseX, mouseY):
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        app.smileyOnPress = True
    
    for button in app.levelThreeButtons:
        if button.contains(mouseX, mouseY):
            button.isPressed(True)
        else:
            button.isPressed(False)

def levelThree_onMouseRelease(app, mouseX, mouseY):   
    app.smileyOnPress = False
    for button in app.levelThreeButtons:
        if button.contains(mouseX, mouseY):
            action = button.action
            button.isPressed(False)
            if action == 'startScreen':
                setActiveScreen('startScreen')
            elif action == 'reset':
                resetBoardThree(app)
            elif action == 'playSong':
                if app.gameWin:
                    app.lastSong.play()
                    print('playing song')
            
def levelThree_onMouseMove(app, mouseX, mouseY):
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        if app.cellSelection == selectedCell:
            return None
        else:
            app.cellSelection = selectedCell
    else:
        app.cellSelection = None

        
def checkGameWinThree(app):
    if app.gameWin or app.gameOver:
        return
    
    rows, cols = len(app.internalBoard), len(app.internalBoard[0])
    for row in range(rows):
        for col in range(cols):
            thisCell = app.internalBoard[row][col]
            if not thisCell.revealed and not thisCell.bomb:
                return
                
    app.gameWin = True
    app.musicalWins += 1
    app.bombRemain = 0
    thisGameNotes = tuple(app.songNotes)
    app.lastSong = Sequencer(thisGameNotes, instrument='piano', volume=0.6)
    
### FLAGGING GAME THREE###

def levelThree_onKeyPress(app, key):
    if app.gameOver or app.gameWin:
        return
    
    if key == 'f':
        selectRow, selectCol = app.cellSelection
        thisCell = app.internalBoard[selectRow][selectCol]
        if not thisCell.revealed:
            thisCell.flagCell()
        
        countRemaining(app)
    
    #FOR DEMO PURPOSES
    elif key == '!':
        rows, cols = len(app.internalBoard), len(app.internalBoard[0])
        for row in range(rows):
            for col in range(cols):
                thisCell = app.internalBoard[row][col]
                if thisCell.bomb:
                    thisCell.flagCell()
                else:
                    thisCell.reveal()
                    
                checkGameWinThree(app)
        
    
### FLOOD FILL ###

# modified heavily from notes
# and everybody thank my CS major friend, Clayon Yu for his help walking me through it

def floodFill(app, row, col):
    thisCell = app.internalBoard[row][col]
    floodFillHelper(app.internalBoard, row, col)

def floodFillHelper(board, row, col):
    rows, cols = len(board), len(board[0])
    if ((row < 0) or (row >= rows) or
        (col < 0) or (col >= cols)):
        return
    
    thisCell = board[row][col]
    
    if thisCell.revealed:
        return
    
    thisCell.reveal()
        
    if (thisCell.bombCount != 0):
        return
    else:
        if thisCell.flagged:
            thisCell.flagCell()
        floodFillHelper(board, row-1, col-1)
        floodFillHelper(board, row-1, col)
        floodFillHelper(board, row-1, col+1)
        floodFillHelper(board, row, col-1)
        floodFillHelper(board, row, col+1)
        floodFillHelper(board, row+1, col-1)
        floodFillHelper(board, row+1, col)
        floodFillHelper(board, row+1, col+1)
        
        
### FLOOD FILL TWO ###

def floodFillTwo(app, row, col):
    thisCell = app.internalBoard[row][col]
    floodFillHelperTwo(app, app.internalBoard, row, col)

def floodFillHelperTwo(app, board, row, col):
    rows, cols = len(board), len(board[0])
    if ((row < 0) or (row >= rows) or
        (col < 0) or (col >= cols)):
        return
    
    thisCell = board[row][col]
    
    if thisCell.revealed:
        return
    
    thisCell.reveal()
    app.points += (thisCell.bombCount)*2 + 3
        
    if (thisCell.bombCount != 0):
        return
    else:
        if thisCell.flagged:
            thisCell.flagCell()
        floodFillHelper(board, row-1, col-1)
        floodFillHelper(board, row-1, col)
        floodFillHelper(board, row-1, col+1)
        floodFillHelper(board, row, col-1)
        floodFillHelper(board, row, col+1)
        floodFillHelper(board, row+1, col-1)
        floodFillHelper(board, row+1, col)
        floodFillHelper(board, row+1, col+1)
        

### SURROUND FILL ###

def surroundFill(app, row, col):
    thisCell = app.internalBoard[row][col]
    correctFlags = 0
    wrongFlags = 0
    
    for drow in [-1, 0, +1]:
        for dcol in [-1, 0, +1]:
            nextRow = row + drow
            nextCol = col + dcol
            if ((0 <= nextRow < app.rows) and
               (0 <= nextCol < app.cols) and
               ((drow, dcol) != (0,0))):
               cell = app.internalBoard[nextRow][nextCol]
               if cell.bomb and cell.flagged:
                   correctFlags += 1
               elif cell.flagged and not cell.bomb:
                   wrongFlags += 1
                   
    if correctFlags == thisCell.bombCount:
        surroundReveal(app, row, col)
    elif correctFlags + wrongFlags == thisCell.bombCount:
        app.gameOver = True
    else:
        return
    
def surroundReveal(app, row, col):
    thisCell = app.internalBoard[row][col]
    
    for drow in [-1, 0, +1]:
        for dcol in [-1, 0, +1]:
            nextRow = row + drow
            nextCol = col + dcol
            if ((0 <= nextRow < app.rows) and
               (0 <= nextCol < app.cols) and
               ((drow, dcol) != (0,0))):
               cell = app.internalBoard[nextRow][nextCol]
               if (not cell.revealed) and (not cell.bomb):
                    floodFill(app, nextRow, nextCol)
                    
### FLOOD FILL THREE ###

def floodFillMusic(app, row, col):
    thisCell = app.internalBoard[row][col]
    floodFillHelperMusic(app, app.internalBoard, row, col)

def floodFillHelperMusic(app, board, row, col):
    rows, cols = len(board), len(board[0])
    if ((row < 0) or (row >= rows) or
        (col < 0) or (col >= cols)):
        return
    
    thisCell = board[row][col]
    
    if thisCell.revealed:
        return
    
    thisCell.reveal()
    
    if app.songNotes == []:
        note = app.noteDict[thisCell.bombCount]
        app.songNotes.append(Note(note, 4, 1/8))
    else:
        lastNote = app.songNotes[-1]
        upOrDown = random.randrange(1, 3)
        if upOrDown == 2:
            interval = thisCell.bombCount % 9
        elif upOrDown == 1:
            interval = -thisCell.bombCount
        newNote = lastNote.getNote(interval)
        app.songNotes.append(newNote)
        
    if (thisCell.bombCount != 0):
        return
    else:
        if thisCell.flagged:
            thisCell.flagCell()
        floodFillHelper(board, row-1, col-1)
        floodFillHelper(board, row-1, col)
        floodFillHelper(board, row-1, col+1)
        floodFillHelper(board, row, col-1)
        floodFillHelper(board, row, col+1)
        floodFillHelper(board, row+1, col-1)
        floodFillHelper(board, row+1, col)
        floodFillHelper(board, row+1, col+1)
        

### SURROUND FILL THREE ###

def surroundFillMusic(app, row, col):
    thisCell = app.internalBoard[row][col]
    correctFlags = 0
    wrongFlags = 0
    
    for drow in [-1, 0, +1]:
        for dcol in [-1, 0, +1]:
            nextRow = row + drow
            nextCol = col + dcol
            if ((0 <= nextRow < app.rows) and
               (0 <= nextCol < app.cols) and
               ((drow, dcol) != (0,0))):
               cell = app.internalBoard[nextRow][nextCol]
               if cell.bomb and cell.flagged:
                   correctFlags += 1
               elif cell.flagged and not cell.bomb:
                   wrongFlags += 1
                   
    if correctFlags == thisCell.bombCount:
        surroundRevealMusic(app, row, col)
    elif correctFlags + wrongFlags == thisCell.bombCount:
        app.gameOver = True
    else:
        return
    
def surroundRevealMusic(app, row, col):
    thisCell = app.internalBoard[row][col]
    
    for drow in [-1, 0, +1]:
        for dcol in [-1, 0, +1]:
            nextRow = row + drow
            nextCol = col + dcol
            if ((0 <= nextRow < app.rows) and
               (0 <= nextCol < app.cols) and
               ((drow, dcol) != (0,0))):
               cell = app.internalBoard[nextRow][nextCol]
               if (not cell.revealed) and (not cell.bomb):
                    floodFillMusic(app, nextRow, nextCol)

### INSTRUCTIONS ###

    ####NORMAL####
    
def howNormal_redrawAll(app):
    if not app.compLocked:
        app.normalNext.draw(app)
        
    themeName = app.unlockedThemes[app.selectedTheme]
    
    app.goBack.draw(app)
    
    #title
    drawImage(f'{app.baseUrl}/howNormal.png', app.width/2, app.height/2, align='center')
    
    #instructions
    drawLabel('- Click cells to reveal them!', app.width/2, 180, size=18, fill='white', font=app.font)
    drawLabel('- Numbers show how many', app.width/2, 210, size=18, fill='white', font=app.font)
    drawLabel('  bombs are nearby', app.width/2, 230, size=18, fill='white', font=app.font)
    drawLabel('- Press F to flag suspected bombs', app.width/2, 260, size=18, fill='white', font=app.font)
    drawLabel('- Avoid all bombs to win!', app.width/2, 290, size=18, fill='white', font=app.font)
    drawLabel('- Click revealed numbers to auto-reveal', app.width/2, 320, size=18, fill='white', font=app.font)
    drawLabel('  surrounding safe cells', app.width/2, 340, size=18, fill='white', font=app.font)
    
    #drawSquares
    theme = app.unlockedThemes[app.selectedTheme]
    themeList = app.imageBoard[theme]
    bomb, cover, flagged, wrongFlag = 9, 10, 11, 12
    
    numberImg = themeList[1]
    drawImage(numberImg, 120, 400, width=40, height=40)
    
    bombImg = themeList[bomb]
    drawImage(bombImg, 160, 400, width=40, height=40)
    
    coverImg = themeList[cover]
    drawImage(coverImg, 200, 400, width=40, height=40)
    
    flaggedImg = themeList[flagged]
    drawImage(flaggedImg, 240, 400, width=40, height=40)
    
def howNormal_onMouseRelease(app, mouseX, mouseY):
    if not app.compLocked:
        if app.normalNext.contains(mouseX, mouseY):
            app.normalNext.isPressed(False)
            setActiveScreen('howComp')
    
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(False)
        setActiveScreen('startScreen')

def howNormal_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    if not app.compLocked:
        if app.normalNext.contains(mouseX, mouseY):
            app.normalNext.isPressed(True)
            
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(True)
            
def howNormal_onMouseDrag(app, mouseX, mouseY):
    if not app.compLocked:
        if app.normalNext.contains(mouseX, mouseY):
            app.normalNext.isPressed(True)
        else:
            app.normalNext.isPressed(False)
            
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(True)
    else:
        app.goBack.isPressed(False)
        
   ####COMP####
    
def howComp_redrawAll(app):
    if not app.musicLocked:
        app.compNext.draw(app)
    
    app.compBack.draw(app)
        
    themeName = app.unlockedThemes[app.selectedTheme]
    
    app.goBack.draw(app)
    
    #title
    drawImage(f'{app.baseUrl}/howComp.png', app.width/2, app.height/2, align='center')
    
    #instructions
    drawLabel('- Race against the clock!', app.width/2, 180, size=18, fill='white', font=app.font)
    drawLabel('- Earn points for each', app.width/2, 210, size=18, fill='white', font=app.font)
    drawLabel('  cell revealed', app.width/2, 230, size=18, fill='white', font=app.font)
    drawLabel('- Hit a bomb? Lose 10 points', app.width/2, 260, size=18, fill='white', font=app.font)
    drawLabel('  and freeze for 3 seconds', app.width/2, 280, size=18, fill='white', font=app.font)
    drawLabel('- Finish before the timer runs out', app.width/2, 310, size=18, fill='white', font=app.font)
    drawLabel('- Use points to buy themes!', app.width/2, 340, size=18, fill='white', font=app.font)
    
    #drawSquares
    theme = app.unlockedThemes[app.selectedTheme]
    themeList = app.imageBoard[theme]
    bomb, cover, flagged, wrongFlag = 9, 10, 11, 12
    
    numberImg = themeList[1]
    drawImage(numberImg, 120, 400, width=40, height=40)
    
    bombImg = themeList[bomb]
    drawImage(bombImg, 160, 400, width=40, height=40)
    
    coverImg = themeList[cover]
    drawImage(coverImg, 200, 400, width=40, height=40)
    
    flaggedImg = themeList[flagged]
    drawImage(flaggedImg, 240, 400, width=40, height=40)
    
def howComp_onMouseRelease(app, mouseX, mouseY):
    if not app.musicLocked:
        if app.compNext.contains(mouseX, mouseY):
            app.compNext.isPressed(False)
            setActiveScreen('howMusical')
            
    if app.compBack.contains(mouseX, mouseY):
        app.compBack.isPressed(False)
        setActiveScreen('howNormal')
    
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(False)
        setActiveScreen('startScreen')

def howComp_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    if not app.musicLocked:
        if app.compNext.contains(mouseX, mouseY):
            app.compNext.isPressed(True)
    
    if app.compBack.contains(mouseX, mouseY):
        app.compBack.isPressed(True)
        
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(True)
            
def howComp_onMouseDrag(app, mouseX, mouseY):
    if not app.compLocked:
        if app.compNext.contains(mouseX, mouseY):
            app.compNext.isPressed(True)
        else:
            app.compNext.isPressed(False)
            
    if app.compBack.contains(mouseX, mouseY):
        app.compBack.isPressed(True)
    else:
        app.compBack.isPressed(False)
        
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(True)
    else:
        app.goBack.isPressed(False)
        
    ####MUSICAL####
    
def howMusical_redrawAll(app):
    app.musicalBack.draw(app)
        
    themeName = app.unlockedThemes[app.selectedTheme]
    
    app.goBack.draw(app)
    
    #title
    drawImage(f'{app.baseUrl}/howMusical.png', app.width/2, app.height/2, align='center')
    
    #instructions
    drawLabel('- Play like Normal Mode', app.width/2, 180, size=18, fill='white', font=app.font)
    drawLabel('- Each cell you reveal', app.width/2, 210, size=18, fill='white', font=app.font)
    drawLabel('  creates a musical note', app.width/2, 230, size=18, fill='white', font=app.font)
    drawLabel('- Win the game to unlock', app.width/2, 260, size=18, fill='white', font=app.font)
    drawLabel('  your unique song!', app.width/2, 280, size=18, fill='white', font=app.font)
    drawLabel('- Press play to hear your melody', app.width/2, 310, size=18, fill='white', font=app.font)
    
    #drawSquares
    theme = app.unlockedThemes[app.selectedTheme]
    themeList = app.imageBoard[theme]
    bomb, cover, flagged, wrongFlag = 9, 10, 11, 12
    
    numberImg = themeList[1]
    drawImage(numberImg, 120, 400, width=40, height=40)
    
    bombImg = themeList[bomb]
    drawImage(bombImg, 160, 400, width=40, height=40)
    
    coverImg = themeList[cover]
    drawImage(coverImg, 200, 400, width=40, height=40)
    
    flaggedImg = themeList[flagged]
    drawImage(flaggedImg, 240, 400, width=40, height=40)
    
def howMusical_onMouseRelease(app, mouseX, mouseY):
    if app.musicalBack.contains(mouseX, mouseY):
        app.musicalBack.isPressed(False)
        setActiveScreen('howComp')
    
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(False)
        setActiveScreen('startScreen')

def howMusical_onMousePress(app, mouseX, mouseY):
    if not app.muted: app.buttonSound.play()
    if app.musicalBack.contains(mouseX, mouseY):
        app.musicalBack.isPressed(True)
            
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(True)
            
def howMusical_onMouseDrag(app, mouseX, mouseY):
    if app.musicalBack.contains(mouseX, mouseY):
        app.musicalBack.isPressed(True)
    else:
        app.musicalBack.isPressed(False)
            
    if app.goBack.contains(mouseX, mouseY):
        app.goBack.isPressed(True)
    else:
        app.goBack.isPressed(False)

### FOR DEMO ###

def startScreen_onKeyPress(app, key):
    if key == 'c':
        app.compLocked = not app.compLocked
    elif key == 'm':
        app.musicLocked = not app.musicLocked
    elif key == '0':
        app.totalPoints += 500
        

def main():
    runAppWithScreens(initialScreen='startScreen')

main()