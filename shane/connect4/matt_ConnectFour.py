# File: ConnecrFour.py
# Author: Matthew Harrelson
# Last Update Date: 2024-07-05
# Description: This contains several function for playing connect 4

#TODO: I think I can make the colorDicts an object or something
#TODO: Maybe I should be avoiding the for each loops for the colors

import random

#define constants
ROWS = 6
COLS = 7
BLANK_CHAR = '.'
COLOR_LIST = [{'colorName':'Red', 'defaultChar':'r', 'highlightChar':'R', 'bitmap':0}, {'colorName':'Yellow', 'defaultChar':'y', 'highlightChar':'Y', 'bitmap':0}]

#Creates a list of colors, each color is a dict mapping several variables to values
def createGame():
	#create color list
	colorList = COLOR_LIST

	#Get the Player Types
	for color in colorList:
		colorName = color['colorName']
		print(f'\nPlease Input the Type of Player for the {colorName} Player')
		print('r = Random Moves, h = Human, c = Computer, a = AI')
		while(True):
			userInput = input('')
			userInput = userInput.lower()

			match userInput:
				case 'r':
					color['playerType'] = 'random'
					print(f'{colorName} Player Type set to Random')
					break
				case 'h':
					color['playerType'] = 'human'
					print(f'{colorName} Player Type set to Human')
					break
				case 'c':
					color['playerType'] = 'computer'
					print(f'{colorName} Player Type set to Computer')
					break
				case 'a':
					color['playerType'] = 'ai'
					print('AI player not implemented, Try Again')
				case _:
					print('Invalid Player Type, Try Again')
					print('r = Random, h = Human, c = Computer, a = AI')
	
	return colorList


#function that prints out the current board state
def printBoard(colorList):
	currentBit = 1 << (ROWS * (COLS + 1))

	for i in range(ROWS):
		for j in range(COLS):
			currentBit >>= 1

			if currentBit & colorList[0]['bitmap']:
				print(colorList[0]['defaultChar'], end = ' ')
			elif currentBit & colorList[1]['bitmap']:
				print(colorList[1]['defaultChar'], end = ' ')
			else:
				print(BLANK_CHAR, end = ' ')
		currentBit >>= 1
		print()
	print()

#function that prints out the winning board state, returns the winDirection
def printWinningBoard(colorList, endConditions):
	winningBitmap = 0
	currentBit = endConditions[1]

	match endConditions[2]:
			case '-':
				for i in range(4):
					winningBitmap |= currentBit
					currentBit >>= 1
				winDirection = 'horizontal'
			case '|':
				for i in range(4):
					winningBitmap |= currentBit
					currentBit >>= (COLS+1)
				winDirection = 'vertical'
			case '\\':
				for i in range(4):
					winningBitmap |= currentBit
					currentBit >>= (COLS+2)
				winDirection = 'diagonal'
			case '/':
				for i in range(4):
					winningBitmap |= currentBit
					currentBit >>= COLS
				winDirection = 'diagonal'
	
	currentBit = 1 << (ROWS * (COLS + 1))

	for i in range(ROWS):
		for j in range(COLS):
			currentBit >>= 1
			if currentBit & winningBitmap:
				print(colorList[endConditions[0]]['highlightChar'], end = ' ')
			elif currentBit & colorList[0]['bitmap']:
				print(colorList[0]['defaultChar'], end = ' ')
			elif currentBit & colorList[1]['bitmap']:
				print(colorList[1]['defaultChar'], end = ' ')
			else:
				print(BLANK_CHAR, end = ' ')
		currentBit >>= 1
		print()
	print()
	return winDirection

#Returns a bitmap that contains every pieces, and not just pieces of one color
def getJoinedBitmap(colorList):
	joinedBitmap = 0
	for color in colorList:
		joinedBitmap |= color['bitmap']
	return joinedBitmap

#Function that changes the board by adding a piece in the lowest open space in the specified column
#Returns False if the column is invalid or full, otherwise returns true, assumes the column given is an int
def makeMove(colorList, colorIndex, column):
	#Make sure a valid column was provided
	if column < 0 or column >= COLS: return False

	#Find the lowest open space
	joinedBitmap = getJoinedBitmap(colorList)
	currentBit = 1 << (COLS - column)

	while currentBit & joinedBitmap:
		currentBit <<= (COLS+1)
		if currentBit > (1 << ((ROWS * (COLS + 1)) - 1)): 
			return False
	
	#Add piece of specified color
	colorList[colorIndex]['bitmap'] |= currentBit
	return True


#Makes a computer move
def makeComputerMove(colorList, colorIndex):
	import min_connect4 as comp
	column = comp.get_move(colorList, colorIndex)
	if makeMove(colorList, colorIndex, column):
		colorName = colorList[colorIndex]['colorName']
		print(f'{colorName} Played in Column {column+1}')
	else:
		print('ERROR', 'illegal computer move', column)
		exit(-1)
	return


#Makes a random valid move
def makeRandomMove(colorList, colorIndex):
	while True:
		column = random.randrange(0,COLS)
		if makeMove(colorList, colorIndex, column):
			colorName = colorList[colorIndex]['colorName']
			print(f'{colorName} Played in Column {column+1}')
			break

#Queries the player for their desiered move and makes it
#if an invalid colomn is given, asks again
def makeHumanMove(colorList, colorIndex):
	colorName = colorList[colorIndex]['colorName']
	print(f'{colorName} Player, Enter Column')
	while True:
		column = int(input()) - 1
		if makeMove(colorList, colorIndex, column):
			print(f'{colorName} Played in Column {column+1}')
			break
		print(f'Invalid Column, Pick a column from 1-{COLS} that is not full')

	return

#Makes a move based on the currentColor
def nextMove(colorList, currentColorIndex):
	match colorList[currentColorIndex]['playerType']:
		case 'computer':
			makeComputerMove(colorList, currentColorIndex)
		case 'random':
			makeRandomMove(colorList, currentColorIndex)
		case 'human':
			makeHumanMove(colorList, currentColorIndex)

#Takes the log base 2 of an int
def log2(num):
	result = -1
	while num != 0:
		num >>= 1
		result += 1
	return result

#Takes the position of a piece in the bitmapping and converts it to a row and column 
def findPosition(bit):
	bitwisePosition = log2(bit)
	column = COLS - (bitwisePosition % (COLS + 1))
	row = (bitwisePosition // (COLS + 1))
	return [column, row]

#Checks if a specific color has won
def checkWin(color):
	#Get bitmap
	bitmap = color['bitmap']

	#Check Horizontal Win
	current = bitmap & bitmap << 1
	current = current & current << (1*2)
	if current != 0:
		return [current, '-']
	
	#Check Vertical Win
	current = bitmap & bitmap << (COLS+1)
	current = current & current << ((COLS+1)*2)
	if current != 0:
		position = findPosition(log2(current))
		return [current, '|']
	
	#Check Right Diagonal Win
	current = bitmap & bitmap << (COLS+2)
	current = current & current << ((COLS+2)*2)
	if current != 0:
		position = findPosition(log2(current))
		return [current, '\\']
	
	#Check Left Diagonal Win
	current = bitmap & bitmap << COLS
	current = current & current << (COLS*2)
	if current != 0:
		position = findPosition(log2(current))
		return [current, '/']

	return

#Checks to see if the game should end
#Returns a list if a player has won in the form [colorIndex, bitmapPosition, direction]
#bitmapPosition will corespond to the top left piece in the winning line (or top right for diagonals)
#If the board is full (and thus the game ties) returns a list containing only -1
#Otherwise returns None
def checkEndConditions(colorList):
	for colorIndex, color in enumerate(colorList):
		result = checkWin(color)
		if result != None:
			return [colorIndex] + result
	
	joinedBitmap = getJoinedBitmap(colorList)
	currentBit = 1 << (ROWS * (COLS + 1))

	for i in range(COLS):
		currentBit >>= 1
		if not (currentBit & joinedBitmap):
			return
	return [-1]

#main function
def main():
	#Welcome User
	print('Welcome to ConenctFour')
	
	#Create Board
	colorList = createGame()
	print()

	#Select Fisrt Player
	currentColor = 0 if random.choice([True, False]) else 1
	colorName = colorList[currentColor]['colorName']
	print(f'{colorName} Player randomly selected to go first')
	print()

	#Enter Main Game Loop
	while(True):
		printBoard(colorList)

		nextMove(colorList, currentColor)
		currentColor = (currentColor + 1) % 2

		endConditions = checkEndConditions(colorList)
		if endConditions != None:
			break
	
	#Print The end of game board
	if endConditions[0] == -1:
		printBoard(colorList)
		print('Game Ended in Tie')

	else:	
		winDirection = printWinningBoard(colorList, endConditions)
		winPosition = findPosition(endConditions[1])
		colorName = colorList[endConditions[0]]['colorName']
		print(f'{colorName} won with a {winDirection} four in a row starting at ({winPosition[0]+1},{winPosition[1]+1})')

main()
