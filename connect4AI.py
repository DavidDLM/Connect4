import random
import numpy as np
import pygame
import sys
import math

ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 0
AI = 1
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4
EMPTY = 0


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
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


def winning_move(board, piece):
    row_count = len(board)
    column_count = len(board[0])

    # Check horizontal locations
    for r in range(row_count):
        for c in range(column_count - 3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True

    # Check vertical locations
    for c in range(column_count):
        for r in range(row_count - 3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True

    # Check positive sloped diagonals
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True

    # Check negative sloped diagonals
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            if all(board[r+3-i][c+i] == piece for i in range(4)):
                return True

    return False


def eval_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    if window.count(piece) == 4:
        score += 1000
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 100
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 10

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 25
    return score


def score_position(board, piece):
    score = 0
    row_count = len(board)
    column_count = len(board[0])

    center_array = [int(i) for i in list(board[:, column_count//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Horizontal
    for r in range(row_count):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(column_count - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += eval_window(window, piece)

    # Vertical
    for c in range(column_count):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(row_count - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += eval_window(window, piece)

    # Diagonal (positive sloped)
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += eval_window(window, piece)

    # Diagonal (negative sloped)
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += eval_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maxPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 10000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000)
            else:  # Game over
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))
    if maxPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Min player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, (0, 0, 255), (c*SQUARESIZE,
                             r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(
                screen, (0, 0, 0), (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(
                    screen, (255, 0, 0), (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(
                    screen, (255, 255, 0), (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()


board = create_board()
print_board(board)
game_over = False
#turn = 0

pygame.init()
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)
screen = pygame.display.set_mode(size)
RADIUS = int(SQUARESIZE/2 - 5)
draw_board(board)
pygame.display.update()
font = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)


while not game_over:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            sys.exit()

    # Player 1 input
    if turn == PLAYER and not game_over:
        col, _ = minimax(board, 6, -math.inf, math.inf, True)
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, PLAYER_PIECE)
            if winning_move(board, PLAYER_PIECE):
                label = font.render("Player 1 wins!", 1, (255, 0, 0))
                screen.blit(label, (40, 10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    # Player 2 input
    if turn == AI and not game_over:
        col, _ = minimax(board, 6, -math.inf, math.inf, True)
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            if winning_move(board, AI_PIECE):
                label = font.render("Player 2 wins!", 1, (255, 255, 0))
                screen.blit(label, (40, 10))
                game_over = True
            print_board(board)
            draw_board(board)
            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
