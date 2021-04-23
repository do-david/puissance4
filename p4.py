import numpy as np
import random
import pygame
import sys
import math

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def game_over(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def evaluate(board, piece):
	score = 0

	## Score center column
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	## Score Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(board):
	return game_over(board, PLAYER_PIECE) or game_over(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if game_over(board, AI_PIECE):
				return (None, 100000000000000)
			elif game_over(board, PLAYER_PIECE):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, evaluate(board, AI_PIECE))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):

	valid_locations = get_valid_locations(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = evaluate(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def game_intro():
    #retourne nb_player et le palier de difficulté
    res = []
    intro = True
    startClicked = False
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if width/2 <= mouse[0] <= width/2+150 and (height/2) <= mouse[1] <= (height/2)+150:
                    print('start button clicked')
                    startClicked = True
                    continue
                if width/5 <= mouse[0] <= width/5+100 and (height/4) <= mouse[1] <= (height*3/4)+100 and startClicked:
                    print('this is easy')
                    res.append(random.randint(1,2))
                    intro = False
                if width/2 <= mouse[0] <= width/2+100 and (height*3/4) <= mouse[1] <= (height*3/4)+100 and startClicked:
                    print('this is medium')
                    res.append(random.randint(3,4))
                    intro = False
                if width*4/5 <= mouse[0] <= width*4/5+100 and (height/4) <= mouse[1] <= (height*3/4)+100 and startClicked:
                    print('this is hard')
                    res.append(random.randint(5,6))
                    intro = False
        if(startClicked):
            smallText = pygame.font.Font('freesansbold.ttf',35)
            Text1Surf, Text1Rect = text_objects("Easy", smallText)
            Text2Surf, Text2Rect = text_objects("Medium", smallText)
            Text3Surf, Text3Rect = text_objects("Hard", smallText)
            Text1Rect.center = ((width/5),(height*3/4))
            Text2Rect.center = ((width/2),(height*3/4))
            Text3Rect.center = ((width*4/5),(height*3/4))
            screen.blit(Text1Surf, Text1Rect)
            screen.blit(Text2Surf, Text2Rect)
            screen.blit(Text3Surf, Text3Rect)
        pygame.display.update()
        mouse = pygame.mouse.get_pos()
        screen.fill(white)
        largeText = pygame.font.Font('freesansbold.ttf',115)
        mediumText = pygame.font.Font('freesansbold.ttf',65)
        TextSurf, TextRect = text_objects("Puissance 4", largeText)
        TextRect.center = ((width/2),(height/4))
        screen.blit(TextSurf, TextRect)
        ButtonSurf, ButtonRect = text_objects("Start", mediumText)
        ButtonRect.center = ((width/2),(height/2))
        screen.blit(ButtonSurf, ButtonRect)
    return res
        
pygame.display.set_caption('Puissance 4')
black = (0,0,0)
white = (255,255,255)
board = create_board()
print_board(board)
gameIsOver = False
pygame.init()
#lvl = -1
nb_player = -1
#0: AI vs AI || 1: Player vs AI || 2: Player vs Player
while nb_player < 0 or nb_player > 2:
	nb_player = int(input("Nombre de joueur :"))
#Choix du niveau
# while lvl < 1 or lvl > 6:
# 	lvl = int(input("Choix du niveau de difficulte (1-6):"))

#Implémentation graphique
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)
screen = pygame.display.set_mode(size)
res = game_intro()
lvl = res[0]
print('lvl = ',lvl)
draw_board(board)
pygame.display.update()
myfont = pygame.font.SysFont("monospace", 75)
# clock = pygame.time.Clock()
#utilisation du random pour savoir qui commence
turn = random.randint(PLAYER, AI)
#Lancement du jeu
while not gameIsOver:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == PLAYER:
				if nb_player >= 1:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))
				else :
					col, minimax_score = minimax(board, lvl, -math.inf, math.inf, True)

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)

					if game_over(board, PLAYER_PIECE):
						label = myfont.render("Player 1 wins!!", 1, RED)
						screen.blit(label, (40,10))
						gameIsOver = True

					turn += 1
					turn = turn % 2

					print_board(board)
					draw_board(board)


			# # Ask for Player 2 Input
			else:				
				#col = random.randint(0, COLUMN_COUNT-1)
				#col = pick_best_move(board, AI_PIECE)
				if nb_player > 1:
						posx = event.pos[0]
						col = int(math.floor(posx/SQUARESIZE))
				else :
					col, minimax_score = minimax(board, lvl, -math.inf, math.inf, True)
				if is_valid_location(board, col):
					#pygame.time.wait(500)
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, AI_PIECE)

					if game_over(board, AI_PIECE):
						label = myfont.render("Player 2 wins!!", 1, YELLOW)
						screen.blit(label, (40,10))
						gameIsOver = True

					print_board(board)
					draw_board(board)

					turn += 1
					turn = turn % 2

	if gameIsOver:
		pygame.time.wait(3000)