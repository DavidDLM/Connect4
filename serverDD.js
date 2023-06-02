// From Python to JS
const io = require('socket.io-client');
const serverUrl = "http://192.168.1.104:4000";
const socket = io(serverUrl);

const INF = Infinity;
const ROW_COUNT = 6
const COLUMN_COUNT = 7
const PLAYER = 0
const AI = 1
const OPPONENT = 2
const PLAYER_PIECE = 1
const AI_PIECE = 2
const CHUNK_LENGTH = 4
const EMPTY = 0

/*
def on_connect():
    print("Connected to server")
    socketIO.emit('signin', {
        'user_name': "David",
        'tournament_id': 142857,
        'user_role': 'player'
    })
*/
socket.on('connect', () => {
  console.log("Connected to server");
  socket.emit('signin', {
    user_name: "David",
    tournament_id: 142857,
    user_role: 'player'
  });
});

/* 
def on_ok_signin():
    print("Login")
*/
socket.on('ok_signin', () => {
  console.log("Login");
});

socket.on('ready', play_game);
socket.on('finish', on_finish);
/*
def play_game(game_id, player_id, ai_id, opponent, board):
    game_over = False

    while not game_over:
        if player_id == ai_id:
            # AI player's turn
            col, _ = minimax(board, 6, -math.inf, math.inf, True)
            if accept(board, col):
                row = openRow(board, col)
                AIMovement(board, row, col, AI)
                if winCheck(board, AI):
                    print("David wins!")
                    game_over = True
                printBoard(board)
                socketIO.emit('play', {
                    'tournament_id': 142857,
                    'player_turn_id': player_id,
                    'game_id': game_id,
                    'movement': col,
                    'board': board  # Send the updated board to the opponent
                })
        else:
            # Opponent player's turn
            print("Waiting for opponent's move...")
            # Receive the updated board from the opponent in the 'on_ready' event

        # Perform any necessary cleanup or actions when the game ends
        if winCheck(board, opponent):
            print("Opponent wins!")
            game_over = True

    # Print the final board state or perform any cleanup tasks
    print("Final board:")
    printBoard(board)
*/
function play_game(data) {
  // Variables
  const game_id = data.game_id;
  const player_turn_id = data.player_turn_id;
  const board = data.board;
  // Processing variables according to Minimax algorithm
  const alpha = -INF;
  const beta = INF;
  const board_copy = draw_board(board);
  const depth = 6;
  // Player to maximize
  const maxPlayer = player_turn_id;
  // Get best move
  const result = minimax(board_copy, depth, alpha, beta, maxPlayer);
  // AI player's turn
  const col = get_best_move(board_copy, result, maxPlayer);

  socket.emit('play', {
    tournament_id: 142857,
    player_turn_id: player_turn_id,
    game_id: game_id,
    board: board_copy, // Send the updated board to the opponent
    movement: col
  });
}
/*
def on_finish(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    winner_turn_id = data['winner_turn_id']
    board = data['board']

    print("Winner:", winner_turn_id)
    print(board)

    # Indicate to the server that the player is ready to play again
    socketIO.emit('player_ready', {
        'tournament_id': 142857,
        'player_turn_id': player_turn_id,
        'game_id': game_id
    })
*/
function on_finish(data) {
  const game_id = data.game_id;
  const player_turn_id = data.player_turn_id;
  const winnerTurnID = data.winner_turn_id;
  const board = data.board;
  // Print the final board state or perform any cleanup tasks
  console.log("Winner: ", winnerTurnID);
  console.log(board);
  // Perform any necessary cleanup or actions when the game ends
  socket.emit('player_ready', {
    tournament_id: 142857,
    player_turn_id: player_turn_id,
    game_id: game_id
  });
}
/*
def minimax(board, depth, alpha, beta, maxPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = isTerminal(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winCheck(board, AI_PIECE):
                return (None, 10000000)
            elif winCheck(board, PLAYER_PIECE):
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
            AIMovement(b_copy, row, col, AI_PIECE)
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
            AIMovement(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value
*/
function minimax(board, depth, alpha, beta, maxPlayer) {
  if (depth === 0 || is_terminal_node(board)) {
    return determine_score(board);
  }

  if (maxPlayer) { // Max player
    let value = -INF;
    for (let column = 0; column < COLUMN_COUNT; column++) {
      if (is_valid_move(board, column)) {
        const b_copy = make_ai_move(board, column, 1);
        const new_score = minimax(b_copy, depth - 1, alpha, beta, false);
        value = Math.max(value, new_score);
        alpha = Math.max(alpha, value);
        if (beta <= alpha) {
          break;
        }
      }
    }
    return value;
  } else { // Min player
    let value = INF;
    for (let column = 0; column < COLUMN_COUNT; column++) {
      if (is_valid_move(board, column)) {
        const b_copy = make_ai_move(board, column, 2);
        const new_score = minimax(b_copy, depth - 1, alpha, beta, true);
        value = Math.min(value, new_score);
        beta = Math.min(beta, value);
        if (beta <= alpha) {
          break;
        }
      }
    }
    return value;
  }
}

/*
def is_terminal_node(board):
    return winCheck(board, PLAYER_PIECE) or winCheck(board, AI_PIECE) or len(get_valid_locations(board)) == 0
*/

function is_terminal_node(board) {
  if (check_winning_move(board, 1) || check_winning_move(board, 2)) {
    return true;
  }

  return !board.flat().includes(0);
}
/*
def winCheck(board, piece):
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
 */
function check_winning_move(board, player) {
  const rows = board.length;
  const cols = board[0].length;

  // Check horizontal locations
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols - 3; col++) {
      if (
        board[row][col] === player &&
        board[row][col + 1] === player &&
        board[row][col + 2] === player &&
        board[row][col + 3] === player
      ) {
        return true;
      }
    }
  }

  // Check vertical locations
  for (let col = 0; col < cols; col++) {
    for (let row = 0; row < rows - 3; row++) {
      if (
        board[row][col] === player &&
        board[row + 1][col] === player &&
        board[row + 2][col] === player &&
        board[row + 3][col] === player
      ) {
        return true;
      }
    }
  }

  // Check positive sloped diagonals
  for (let row = 0; row < rows - 3; row++) {
    for (let col = 0; col < cols - 3; col++) {
      if (
        board[row][col] === player &&
        board[row + 1][col + 1] === player &&
        board[row + 2][col + 2] === player &&
        board[row + 3][col + 3] === player
      ) {
        return true;
      }
    }
  }

  // Check negative sloped diagonals
  for (let row = 3; row < rows; row++) {
    for (let col = 0; col < cols - 3; col++) {
      if (
        board[row][col] === player &&
        board[row - 1][col + 1] === player &&
        board[row - 2][col + 2] === player &&
        board[row - 3][col + 3] === player
      ) {
        return true;
      }
    }
  }

  return false;
}

/*
def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if accept(board, col)]
*/

function is_valid_move(board, column) {
  return board[0][column] === 0;
}

function make_ai_move(board, column, player) {
  const b_copy = draw_board(board);
  for (let row = 5; row >= 0; row--) {
    if (b_copy[row][column] === 0) {
      b_copy[row][column] = player;
      break;
    }
  }
  return b_copy;
}
/*
def determine_score(board, piece):
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
            chunk = row_array[c:c+CHUNK_LENGTH]
            score += scoreDistribution(chunk, piece)

    # Vertical
    for c in range(column_count):
        col_array = [board[r][c] for r in range(row_count)]
        for r in range(row_count - 3):
            chunk = col_array[r:r+CHUNK_LENGTH]
            score += scoreDistribution(chunk, piece)

    # Diagonal (positive sloped)
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            chunk = [board[r+i][c+i] for i in range(CHUNK_LENGTH)]
            score += scoreDistribution(chunk, piece)

    # Diagonal (negative sloped)
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            chunk = [board[r+3-i][c+i] for i in range(CHUNK_LENGTH)]
            score += scoreDistribution(chunk, piece)

    return score

*/
function determine_score(board) {
  // Evaluation logic to assign a score to a board state
  // Returns a positive score if player 1 (AI) is winning, negative if player 2 (opponent) is winning, or 0 for a draw
  // Assign different weights to different positions on the board or consider other factors
  const scores = {
    '1': 1,
    '2': -1,
    '0': 0
  };

  const this_board = board.flat();
  const score = this_board.reduce((total, cell) => total + scores[cell], 0);

  return score;
}

function get_best_move(board, result, maxPlayer) {
  const valid_moves = get_valid_locations(board);
  const best_valid_move = valid_moves.reduce((best, move) => {
    const b_copy = make_ai_move(board, move, maxPlayer);
    const new_score = result === determine_score(b_copy);
    if (new_score > best.new_score) {
      return { move, new_score };
    }
    return best;
  }, { move: -1, new_score: -INF });

  return best_valid_move.move;
}

/*
def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if accept(board, col)]
*/

function get_valid_locations(board) {
  const valid_moves = [];
  for (let col = 0; col < COLUMN_COUNT; col++) {
    if (is_valid_move(board, col)) {
      valid_moves.push(col);
    }
  }
  return valid_moves;
}

/*
def draw_board(board, row, col, piece):
    board[row][col] = piece
*/

function draw_board(board) {
  return board.map(row => [...row]);
}
