import socket
import threading

# Set up the server socket
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (SERVER_HOST, SERVER_PORT)
server_socket.bind(server_address)
server_socket.listen(2)  # Listen for up to 2 connections

# Game state
board = [[None, None, None], [None, None, None], [None, None, None]]
players = {}  # Dictionary to store player connections and symbols
player_symbols = ['X', 'O']
current_player = 0  # Index of the current player's turn

def handle_client(conn, player_id):
    global current_player

    while True:
        # Receive the move from the client
        move = conn.recv(1024).decode()
        if not move:
            break

        row, col = map(int, move.split(','))

        # Update the board with the player's move
        if board[row][col] is None:
            board[row][col] = player_symbols[player_id]

            # Check for win or draw
            winner = check_win(board)
            if winner is not None:
                # Send the winner information to both players
                for player_conn in players.keys():
                    player_conn.sendall(winner.encode())
                break

            # Switch to the next player's turn
            current_player = (current_player + 1) % 2

            # Send the updated board to both players
            for player_conn in players.keys():
                player_conn.sendall(encode_board(board).encode())

    # Clean up the connection when the game is over
    conn.close()
    del players[conn]

def accept_connections():
    player_count = 0
    while player_count < 2:
        conn, addr = server_socket.accept()
        player_id = player_count
        players[conn] = player_id
        threading.Thread(target=handle_client, args=(conn, player_id)).start()
        player_count += 1

def check_win(board):
    # Check rows
    for row in board:
        if row.count(row[0]) == len(row) and row[0] is not None:
            return row[0]

    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != None:
            return board[0][col]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != None:
        return board[2][0]

    # Check for a draw
    if all(cell is not None for row in board for cell in row):
        return "DRAW"

    # Game is not over yet
    return None

def encode_board(board):
    encoded_board = ''
    for row in board:
        for cell in row:
            encoded_board += str(cell) if cell is not None else '-'
    return encoded_board

def main():
    accept_connections()
    server_socket.close()

if __name__ == '__main__':
    main()