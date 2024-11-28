import socket
import threading
import random

# Game Configuration
users = {}  # Dictionary to store username and password
player_queue = []  # Queue to store connected players
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

def intial_game(player1_socket, player2_socket):
    players = [player1_socket, player2_socket]
    broadcast(players, "Both players have joined. The game is starting.\n")

    # Player 1 設定範圍
    player1_socket.send("[PROMPT] You are Player 1. Please set the game range.\n".encode())

    # Lower bound
    lower = None
    while lower is None:
        player1_socket.send("[PROMPT] Enter the lower bound: ".encode())
        try:
            lower = int(player1_socket.recv(1024).decode().strip())
        except ValueError:
            player1_socket.send("[ERROR] Invalid input. Please enter an integer for the lower bound.\n".encode())

    # Upper bound
    upper = None
    while upper is None:
        player1_socket.send("[PROMPT] Enter the upper bound: ".encode())
        try:
            upper = int(player1_socket.recv(1024).decode().strip())
            if upper > lower:
                break
            else:
                player1_socket.send("[ERROR] Upper bound must be greater than the lower bound.\n".encode())
                upper = None
        except ValueError:
            player1_socket.send("[ERROR] Invalid input. Please enter an integer for the upper bound.\n".encode())

    # 隨機產生目標數字
    target_number = random.randint(lower, upper)

    # 廣播範圍
    broadcast(players, f"The range is {lower} ~ {upper}\nGAME START !!!\n")
    return target_number, lower, upper

def handle_game(player1_socket, player2_socket):
    target_number, lower, upper = intial_game(player1_socket, player2_socket)
    current_player = 0  # 0 for Player 1, 1 for Player 2
    players = [(player1_socket, "Player 1"), (player2_socket, "Player 2")]
    last_guess = None  # 用於記錄上一位玩家的猜測

    while True:
        player_socket, player_name = players[current_player]
        other_player_socket, other_player_name = players[1 - current_player]

        # 如果範圍縮小到唯一值，直接宣告獲勝
        if lower == upper:
            if lower == target_number:
                broadcast([player1_socket, player2_socket], f"[INFO] The target number is {lower}.\n")
                player_socket.send("[SUCCESS] The remaining range equals the target number! You've won the game!\n".encode())
                other_player_socket.send(f"[INFO] {player_name} won the game because the remaining range equals the target number.\n".encode())
            else:
                broadcast([player1_socket, player2_socket], f"[ERROR] Unexpected state: lower != target_number.\n")
            break

        # 向當前玩家提供範圍訊息，並告知上一位玩家的猜測
        
        if last_guess is not None:
            player_socket.send(f"[INFO] {other_player_name} guessed {last_guess}.\n".encode())
            
        broadcast([player1_socket, player2_socket], f"It's {player_name}'s turn.\n")

        player_socket.send(f"[INFO] The current range is {lower} to {upper}.\n".encode())

        # 獲取當前玩家的猜測
        valid_guess = False
        while not valid_guess:
            player_socket.send(f"[PROMPT] {player_name}, make a guess: ".encode())
            try:
                guess = int(player_socket.recv(1024).decode().strip())
                if lower <= guess <= upper:
                    valid_guess = True  # 有效猜測
                    last_guess = guess  # 更新上一位玩家的猜測
                else:
                    player_socket.send(f"[ERROR] Invalid guess. Enter a number within {lower} and {upper}.\n".encode())
            except ValueError:
                player_socket.send("[ERROR] Invalid input. Please enter a valid number.\n".encode())

        # 判斷猜測結果
        if guess == target_number:
            player_socket.send("[SUCCESS] Correct! You've won the game!\n".encode())
            other_player_socket.send(f"[INFO] {player_name} guessed the target number ({target_number}). You lose.\n".encode())
            break
        elif guess < target_number:
            lower = max(lower, guess + 1)
            player_socket.send("[INFO] Too low! Try again.\n".encode())
        else:
            upper = min(upper, guess - 1)
            player_socket.send("[INFO] Too high! Try again.\n".encode())

        # 廣播更新範圍給所有玩家
        broadcast([player1_socket, player2_socket], f"[INFO] Updated range is {lower} to {upper}.\n")

        # 切換回合
        current_player = 1 - current_player

    # 遊戲結束，關閉連線
    for sock, _ in players:
        sock.send("[INFO] The game has ended. Closing connection.\n".encode())
        sock.close()


def broadcast(sockets, message):
    for sock in sockets:
        try:
            sock.send(message.encode())
        except Exception as e:
            print(f"[ERROR] Unable to send message to {sock}: {e}")

def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")
    username = register_or_login(client_socket)

    with lock:
        player_queue.append((username, client_socket))

        if len(player_queue) == 2:
            player1_socket = player_queue[0][1]
            player2_socket = player_queue[1][1]
            threading.Thread(target=handle_game, args=(player1_socket, player2_socket)).start()
            player_queue.clear()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(5)
    print("[LISTENING] Server is listening on port 8888")

    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
