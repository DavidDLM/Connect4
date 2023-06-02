from socketIO_client import SocketIO
import random
import numpy as np
import sys
import math

ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 0
AI = 1
OPPONENT = 2
PLAYER_PIECE = 1
AI_PIECE = 2
CHUNK_LENGTH = 4
EMPTY = 0
server_url = "http://10.100.2.41:4000"
server_port = 4000

socketIO = SocketIO(server_url, server_port)


def draw_board(board, row, col, piece):
    board[row][col] = piece


def accept(board, col):
    return board[ROW_COUNT - 1][col] == 0


def openRow(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def printBoard(board):
    print(np.flip(board, 0))


def check_winning_move(board, piece):
    row_count = len(board)
    column_count = len(board[0])

    # Check horizontal locations
    for r in range(row_count):
        for c in range(column_count - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Check vertical locations
    for c in range(column_count):
        for r in range(row_count - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Check positive sloped diagonals
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Check negative sloped diagonals
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            if all(board[r + 3 - i][c + i] == piece for i in range(4)):
                return True

    return False


def scoreDistribution(chunk, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    if chunk.count(piece) == 4:
        score += 1000
    elif chunk.count(piece) == 3 and chunk.count(EMPTY) == 1:
        score += 100
    elif chunk.count(piece) == 2 and chunk.count(EMPTY) == 2:
        score += 10

    if chunk.count(opp_piece) == 3 and chunk.count(EMPTY) == 1:
        score -= 25
    return score


def determineScore(board, piece):
    score = 0
    row_count = len(board)
    column_count = len(board[0])

    center_array = [int(i) for i in list(zip(*board))[column_count // 2]]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Horizontal
    for r in range(row_count):
        row_array = board[r]
        for c in range(column_count - 3):
            chunk = row_array[c: c + CHUNK_LENGTH]
            score += scoreDistribution(chunk, piece)

    # Vertical
    for c in range(column_count):
        col_array = [board[r][c] for r in range(row_count)]
        for r in range(row_count - 3):
            chunk = col_array[r: r + CHUNK_LENGTH]
            score += scoreDistribution(chunk, piece)

    # Diagonal (positive sloped)
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            chunk = [board[r + i][c + i] for i in range(CHUNK_LENGTH)]
            score += scoreDistribution(chunk, piece)

    # Diagonal (negative sloped)
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            chunk = [board[r + 3 - i][c + i] for i in range(CHUNK_LENGTH)]
            score += scoreDistribution(chunk, piece)

    return score


def is_terminal_node(board):
    return check_winning_move(board, PLAYER_PIECE) or check_winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maxPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if check_winning_move(board, AI_PIECE):
                return (None, 10000000)
            elif check_winning_move(board, PLAYER_PIECE):
                return (None, -10000000)
            else:  # Game over
                return (None, 0)
        else:
            return (None, determineScore(board, AI_PIECE))
    if maxPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = openRow(board, col)
            b_copy = board.copy()
            draw_board(b_copy, row, col, AI_PIECE)
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
            row = openRow(board, col)
            b_copy = board.copy()
            draw_board(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if accept(board, col)]


def on_connect():
    print("Connected to server")
    socketIO.emit('signin', {'user_name': "David",
                  'tournament_id': 142857, 'user_role': 'player'})


def on_ok_signin():
    print("Login")


def on_finish(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    winner_turn_id = data['winner_turn_id']
    board = data['board']

    print("Winner:", winner_turn_id)
    print(board)

    # Indicate to the server that the player is ready to play again
    socketIO.emit('player_ready', {
                  'tournament_id': 142857, 'player_turn_id': player_turn_id, 'game_id': game_id})


def on_ready(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    board = data['board']
    print("I'm player:", player_turn_id)
    print(board)

    if player_turn_id == 1:
        AI = 1
        OPPONENT = 2
    else:
        AI = 2
        OPPONENT = 1

    # Start the game
    play_game(game_id, player_turn_id, AI, OPPONENT, board)


def play_game(game_id, player_id, ai_id, opponent, board):
    game_over = False

    while not game_over:
        if player_id == ai_id:
            # AI player's turn
            col, _ = minimax(board, 6, -math.inf, math.inf, True)
            if accept(board, col):
                row = openRow(board, col)
                draw_board(board, row, col, AI)
                if check_winning_move(board, AI):
                    print("David wins!")
                    game_over = True
                printBoard(board)
                socketIO.emit('play', {'tournament_id': 142857, 'player_turn_id': player_id,
                              'game_id': game_id, 'movement': col, 'board': board})
        else:
            # Opponent player's turn
            print("Waiting for opponent's move...")
            # Receive the updated board from the opponent in the 'on_ready' event

        # Perform any necessary cleanup or actions when the game ends
        if check_winning_move(board, opponent):
            print("Opponent wins!")
            game_over = True

    # Print the final board state or perform any cleanup tasks
    print("Final board:")
    printBoard(board)


socketIO.on('connect', on_connect)
socketIO.on('ok_signin', on_ok_signin)
socketIO.on('ready', on_ready)
socketIO.on('finish', on_finish)

socketIO.wait()
