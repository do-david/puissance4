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

def text_title(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def text_objects(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()

#affichage du menu qui retourne nb_player et le palier de difficult??
def game_intro():
    res = []
    np = 0
    lvl = 0
    intro = True
    startButton = False
    playersButton = False
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            #tous les blocks de buttons o?? l'utilisateur clique
            if event.type == pygame.MOUSEBUTTONDOWN:
                if width/2-75 <= mouse[0] <= width/2+75 and (height/2)-40 <= mouse[1] <= (height/2)+40:
                    startButton = True
                    continue
                if (width/5)-50 <= mouse[0] <= (width/5)+50 and (height*5/8)-20 <= mouse[1] <= (height*5/8)+20 and startButton:
                    playersButton = True
                    np = 0
                    continue
                if (width/2)-70 <= mouse[0] <= (width/2)+70 and (height*5/8)-20 <= mouse[1] <= (height*5/8)+20 and startButton:
                    playersButton = True
                    np = 1
                    continue
                if (width*4/5)-100 <= mouse[0] <= (width*4/5)+100 and (height*5/8)-20 <= mouse[1] <= (height*5/8)+20 and startButton:
                    intro = False
                    np = 2
                    break
                if (width/5)-50 <= mouse[0] <= (width/5)+50 and (height*3/4)-25 <= mouse[1] <= (height*3/4)+25 and startButton and playersButton:
                    lvl = random.randint(1,2)
                    intro = False
                if (width/2)-70 <= mouse[0] <= width/2+70 and (height*3/4)-25 <= mouse[1] <= (height*3/4)+25 and startButton and playersButton:
                    lvl = random.randint(3,4)
                    intro = False
                if (width*4/5)-50 <= mouse[0] <= (width*4/5)+50 and (height*3/4)-25 <= mouse[1] <= (height*3/4)+25 and startButton and playersButton:
                    lvl = random.randint(5,6)
                    intro = False
        #afficher la ligne des adversaires apr??s avoir cliqu?? sur start
        if(startButton):
            #affichage des rectangles pour les buttons
            if (width/5)-50 <= mouse[0] <= (width/5)+50 and (height*5/8)-20  <= mouse[1] <= (height*5/8)+20:
                pygame.draw.rect(screen,color_light,[(width/5)-50,(height*5/8)-20,100,40])
            else:
                pygame.draw.rect(screen,color_dark,[(width/5)-50,(height*5/8)-20,100,40])
            if (width/2)-70 <= mouse[0] <= (width/2)+70 and  (height*5/8)-20 <= mouse[1] <= (height*5/8)+20:
                pygame.draw.rect(screen,color_light,[(width/2)-70,(height*5/8)-20,140,40])
            else:
                pygame.draw.rect(screen,color_dark,[(width/2)-70,(height*5/8)-20,140,40])
            if (width*4/5)-100 <= mouse[0] <= (width*4/5)+100 and  (height*5/8)-20 <= mouse[1] <= (height*5/8)+20:
                pygame.draw.rect(screen,color_light,[(width*4/5)-100,(height*5/8)-20,200,40])
            else:
                pygame.draw.rect(screen,color_dark,[(width*4/5)-100,(height*5/8)-20,200,40])
            #affichage du textes dans les buttons
            vrSmallText = pygame.font.Font('freesansbold.ttf',20)
            Text1Surf, Text1Rect = text_objects("AI vs AI", vrSmallText)
            Text2Surf, Text2Rect = text_objects("Player vs AI", vrSmallText)
            Text3Surf, Text3Rect = text_objects("Player 1 vs Player 2", vrSmallText)
            Text1Rect.center = ((width/5),(height*5/8))
            Text2Rect.center = ((width/2),(height*5/8))
            Text3Rect.center = ((width*4/5),(height*5/8))
            screen.blit(Text1Surf, Text1Rect)
            screen.blit(Text2Surf, Text2Rect)
            screen.blit(Text3Surf, Text3Rect)
            #affichage de la ligne des diff??rentes difficult??s de l'IA
            if(playersButton):
                #affichage des rectangles pour les buttons
                if (width/5)-50 <= mouse[0] <= (width/5)+50 and (height*3/4)-25  <= mouse[1] <= (height*3/4)+25:
                    pygame.draw.rect(screen,color_light,[(width/5)-50,(height*3/4)-25,100,50])
                else:
                    pygame.draw.rect(screen,color_dark,[(width/5)-50,(height*3/4)-25,100,50])
                if (width/2)-70 <= mouse[0] <= (width/2)+70 and  (height*3/4)-25<= mouse[1] <= (height*3/4)+25:
                    pygame.draw.rect(screen,color_light,[(width/2)-70,(height*3/4)-25,140,50])
                else:
                    pygame.draw.rect(screen,color_dark,[(width/2)-70,(height*3/4)-25,140,50])
                if (width*4/5)-50 <= mouse[0] <= (width*4/5)+50 and  (height*3/4)-25 <= mouse[1] <= (height*3/4)+25:
                    pygame.draw.rect(screen,color_light,[(width*4/5)-50,(height*3/4)-25,100,50])
                else:
                    pygame.draw.rect(screen,color_dark,[(width*4/5)-50,(height*3/4)-25,100,50])
                #affichage des textes dans les buttons
                smallText = pygame.font.Font('freesansbold.ttf',35)
                Text4Surf, Text4Rect = text_objects("Easy", smallText)
                Text5Surf, Text5Rect = text_objects("Medium", smallText)
                Text6Surf, Text6Rect = text_objects("Hard", smallText)
                Text4Rect.center = ((width/5),(height*3/4))
                Text5Rect.center = ((width/2),(height*3/4))
                Text6Rect.center = ((width*4/5),(height*3/4))
                screen.blit(Text4Surf, Text4Rect)
                screen.blit(Text5Surf, Text5Rect)
                screen.blit(Text6Surf, Text6Rect)
        pygame.display.update()
        mouse = pygame.mouse.get_pos()
        screen.fill(white)
        #affichage du titre
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_title("Puissance 4", largeText)
        TextRect.center = ((width/2),(height/4))
        screen.blit(TextSurf, TextRect)
        #affichage du button start
        if width/2-70 <= mouse[0] <= width/2+70 and (height/2)-40 <= mouse[1] <= (height/2)+40:
            pygame.draw.rect(screen,color_light,[(width/2)-75,(height/2)-40,150,80])
        else:
            pygame.draw.rect(screen,color_dark,[(width/2)-75,(height/2)-40,150,80])
        mediumText = pygame.font.Font('freesansbold.ttf',65)
        ButtonSurf, ButtonRect = text_objects("Start", mediumText)
        ButtonRect.center = ((width/2),(height/2))
        screen.blit(ButtonSurf, ButtonRect)
    if(not lvl):
        res.append(np)
        return res
    else:
        res.append(np)
        res.append(lvl)
        return res
        
pygame.display.set_caption('Puissance 4')
black = (0,0,0)
white = (255,255,255)
color_light = (170,170,170)
color_dark = (100,100,100)
board = create_board()
print_board(board)
gameIsOver = False
pygame.init()

#Impl??mentation graphique
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)
screen = pygame.display.set_mode(size)
res = game_intro()
if(len(res) <2 and res[0] == 2):
    nb_player = res[0]
else:
    nb_player = res[0]
    lvl = res[1]
draw_board(board)
pygame.display.update()
myfont = pygame.font.SysFont("monospace", 75)
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


			# Ask for Player 2 Input
			else:				
				if nb_player > 1:
						posx = event.pos[0]
						col = int(math.floor(posx/SQUARESIZE))
				else :
					col, minimax_score = minimax(board, lvl, -math.inf, math.inf, True)
				if is_valid_location(board, col):
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