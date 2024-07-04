import socket
import threading
import pygame

# Set up the client socket
CLIENT_HOST = 'localhost'
CLIENT_PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (CLIENT_HOST, CLIENT_PORT)
client_socket.connect(server_address)

# Pygame initialization
pygame.init()

WIDTH, HEIGHT = 900, 900
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe!")

BOARD = pygame.image.load("assets/Board.png")
X_IMG = pygame.image.load("assets/X.png")
O_IMG = pygame.image.load("assets/O.png")

BG_COLOR = (214, 201, 227)

board = [[None, None, None], [None, None, None], [None, None, None]]
graphical_board = [[[None, None], [None, None], [None, None]],
                   [[None, None], [None, None], [None, None]],
                   [[None, None], [None, None], [None, None]]]

player_symbol = None

def receive_updates():
    global board, graphical_board, player_symbol

    while True:
        data = client_socket.recv(1024).decode()

        if data == 'X' or data == 'O':
            player_symbol = data
        elif data == 'DRAW':
            print("It's a draw!")
            reset_board()
        elif data in ['X', 'O']:
            print(f"Player {data} wins!")
            reset_board()
        else:
            # Update the board based on the received data
            for i in range(3):
                for j in range(3):
                    cell = data[i * 3 + j]
                    if cell != '-':
                        board[i][j] = cell
                        if cell == 'X':
                            graphical_board[i][j][0] = X_IMG
                            graphical_board[i][j][1] = X_IMG.get_rect(center=(j * 300 + 150, i * 300 + 150))
                        else:
                            graphical_board[i][j][0] = O_IMG
                            graphical_board[i][j][1] = O_IMG.get_rect(center=(j * 300 + 150, i * 300 + 150))

def reset_board():
    global board, graphical_board
    board = [[None, None, None], [None, None, None], [None, None, None]]
    graphical_board = [[[None, None], [None, None], [None, None]],
                       [[None, None], [None, None], [None, None]],
                       [[None, None], [None, None], [None, None]]]

def render_board():
    SCREEN.fill(BG_COLOR)
    SCREEN.blit(BOARD, (64, 64))

    for i in range(3):
        for j in range(3):
            if graphical_board[i][j][0] is not None:
                SCREEN.blit(graphical_board[i][j][0], graphical_board[i][j][1])

    pygame.display.update()

def send_move(row, col):
    if board[row][col] is None:
        move = f"{row},{col}"
        client_socket.sendall(move.encode())

# Start the thread to receive updates from the server
receive_thread = threading.Thread(target=receive_updates)
receive_thread.start()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            client_socket.close()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            converted_x = (event.pos[0] - 65) // 300
            converted_y = event.pos[1] // 300
            send_move(converted_y, converted_x)

    render_board()