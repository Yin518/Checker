import socket
import threading
import random

# Game Configuration
users = {}  # Dictionary to store username and password
active_players = []  # To track active players
lock = threading.Lock()

def register_or_login(client_socket):
    while True:
        client_socket.send("[PROMPT] Do you want to register or login? (R/L): ".encode())
        choice = client_socket.recv(1024).decode().strip().upper()

        if choice == 'R':
            client_socket.send("[PROMPT] Enter a username: ".encode())
            username = client_socket.recv(1024).decode().strip()

            if username in users:
                client_socket.send("[ERROR] Username already exists. Try logging in.\n".encode())
                continue

            client_socket.send("[PROMPT] Enter a password: ".encode())
            password = client_socket.recv(1024).decode().strip()

            with lock:
                users[username] = password

            client_socket.send("[INFO] Registration successful! You can now log in.\n".encode())
        elif choice == 'L':
            client_socket.send("[PROMPT] Enter your username: ".encode())
            username = client_socket.recv(1024).decode().strip()

            client_socket.send("[PROMPT] Enter your password: ".encode())
            password = client_socket.recv(1024).decode().strip()

            if users.get(username) == password:
                client_socket.send("[INFO] Login successful! Please wait for another player to join.\n".encode())
                return username
            else:
                client_socket.send("[ERROR] Invalid username or password. Try again.\n".encode())
        else:
            client_socket.send("[ERROR] Invalid choice. Please enter 'R' to register or 'L' to login.\n".encode())
def broadcast(sockets, message):
    for sock in sockets:
        try:
            sock.send(message.encode())
        except Exception as e:
            print(f"[ERROR] Unable to send message to {sock}: {e}")

def handle_game(player1_socket, player2_socket):
    players = [player1_socket, player2_socket]
    broadcast(players, "Both players have joined. The game is starting.\n")

    # Player 1 設定範圍
    player1_socket.send("You are Player 1. Please set the game range.\n".encode())
    
    # Lower bound
    player1_socket.send("[PROMPT] Enter the lower bound: ".encode())
    while True:
        try:
            lower = int(player1_socket.recv(1024).decode())
            break
        except ValueError:
            player1_socket.send("[PROMPT] Invalid input. Please enter an integer for the lower bound: ".encode())
    
    # Upper bound
    player1_socket.send("[PROMPT] Enter the upper bound: ".encode())
    while True:
        try:
            upper = int(player1_socket.recv(1024).decode())
            if upper > lower:
                break
            else:
                player1_socket.send("[PROMPT] Upper bound must be greater than the lower bound. Try again: ".encode())
        except ValueError:
            player1_socket.send("[PROMPT] Invalid input. Please enter an integer for the upper bound: ".encode())

    target_number = random.randint(lower, upper)
    current_player = 0  # 0 for Player 1, 1 for Player 2
    players = [(player1_socket, "Player 1"), (player2_socket, "Player 2")]

    while True:
        player_socket, player_name = players[current_player]
        other_player_socket, _ = players[1 - current_player]

        other_player_socket.send(f"It is {player_name}'s turn.\n".encode())
        player_socket.send(f"The current range is {lower} to {upper}.\n".encode())
        player_socket.send(f"[PROMPT] {player_name}, make a guess: ".encode())

        guess = None
        while guess is None:
            try:
                guess = int(player_socket.recv(1024).decode())
                if lower <= guess <= upper:
                    break
                else:
                    player_socket.send(f"[PROMPT] Invalid guess. Enter a number within {lower} and {upper}: ".encode())
            except ValueError:
                player_socket.send("[PROMPT] Invalid input. Please enter a valid number: ".encode())

        if guess == target_number:
            player_socket.send("Correct! You've won the game!\n".encode())
            other_player_socket.send("The other player guessed correctly. You lose.\n".encode())
            break
        elif guess < target_number:
            lower = max(lower, guess + 1)
            player_socket.send("Too low!\n".encode())
        else:
            upper = min(upper, guess - 1)
            player_socket.send("Too high!\n".encode())

        current_player = 1 - current_player  # Switch turns


def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")
    username = register_or_login(client_socket)

    with lock:
        active_players.append((username, client_socket))

    # Wait for two players to connect
    while True:
        with lock:
            if len(active_players) == 2:
                break

    # Notify both players that the game is starting
    with lock:
        player1_socket = active_players[0][1]
        player2_socket = active_players[1][1]

    # player1_socket.send("[INFO] Both players have joined. The game is starting.\n".encode())
    # player2_socket.send("[INFO] Both players have joined. The game is starting.\n".encode())

    # Start the game
    handle_game(player1_socket, player2_socket)

    # Clean up after the game
    with lock:
        active_players.remove((username, client_socket))
    client_socket.close()
    print(f"[DISCONNECTED] {address} disconnected.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(5)
    print("[LISTENING] Server is listening on port 8888")

    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
