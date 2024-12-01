import socket
import threading
import random
import time

# Game Configuration
users = {}  # Dictionary to store username and password
player_queue = []  # Queue to store connected players
lock = threading.Lock()
logged_in_users = set()  # 用於追蹤已登入的使用者
# 用來記錄已登入的帳號和客戶端連線的字典
active_connections = {}
# 用來存儲註冊用戶的資料 (帳號: 密碼)

def register_or_login(client_socket):
    while True:
        try:
            # Receive and split the initial data
            data = client_socket.recv(1024).decode()
            if data:
                parts = data.split("|")
                choice = parts[0]  # 'R' for register or 'L' for login
                username = parts[1]  # Username
                password = parts[2]  # Password

                if choice == 'R':  # Registration process
                    if username in users:
                        client_socket.send("[ERROR] Username already exists. Try logging in.\n".encode())
                        continue

                    with lock:
                        users[username] = password
                    client_socket.send("[INFO] Registration successful! You can now log in.\n".encode())

                elif choice == 'L':  # Login process
                    if username not in users:
                        client_socket.send("[ERROR] Username does not exist. Please register first.\n".encode())
                        continue

                    if users.get(username) == password:
                        # Ensure the user isn't already logged in
                        with lock:
                            if username in logged_in_users:
                                client_socket.send("[ERROR] This account is already logged in.\n".encode())
                                continue

                            logged_in_users.add(username)
                        client_socket.send("[INFO] Login successful! Please wait for another player to join.\n".encode())
                        return username
                    else:
                        client_socket.send("[ERROR] Invalid username or password. Try again.\n".encode())

                else:
                    client_socket.send("[ERROR] Invalid choice. Please enter 'R' to register or 'L' to login.\n".encode())

        except ConnectionResetError:
            print("[INFO] Client disconnected unexpectedly.")
            client_socket.close()
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            client_socket.close()
            return None


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

def handle_chat(player_sockets):
    """處理玩家之間的聊天功能"""
    while True:
        for sock in player_sockets:
            try:
                message = sock.recv(1024).decode()
                if message.startswith("[CHAT]"):
                    # 廣播聊天訊息給所有玩家
                    chat_message = message[len("[CHAT]"):].strip()
                    broadcast(player_sockets, f"[CHAT] {chat_message}\n")
            except Exception as e:
                print(f"[ERROR] Chat handling error: {e}")
                return
            
def handle_game(player1_socket, player2_socket,player1_name, player2_name):
    try:
        # 啟動聊天執行緒
        chat_thread = threading.Thread(target=handle_chat, args=([player1_socket, player2_socket],))
        chat_thread.daemon = True
        chat_thread.start()
        
        while True:  # 增加循環以支持多輪遊戲
            target_number, lower, upper = intial_game(player1_socket, player2_socket)
            current_player = 0  # 0 for Player 1, 1 for Player 2
            players = [(player1_socket, "Player 1"), (player2_socket, "Player 2")]
            last_guess = None  # 用於記錄上一位玩家的猜測

            while True:
                player_socket, player_name = players[current_player]
                other_player_socket, other_player_name = players[1 - current_player]

                # 檢測玩家是否斷線
                if player_socket._closed or other_player_socket._closed:
                    broadcast([player1_socket, player2_socket], f"[GAME END] {other_player_name} has disconnected. The game has ended.\n")
                    return

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
                    except (ValueError, ConnectionResetError):
                        broadcast([player1_socket, player2_socket], f"[GAME END] {player_name} has disconnected. The game has ended.\n")
                        return

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

            # 遊戲結束，詢問玩家是否繼續
            player1_socket.send("[PROMPT] Do you want to play again? (yes/no): ".encode())
            player2_socket.send("[PROMPT] Do you want to play again? (yes/no): ".encode())

            response1 = player1_socket.recv(1024).decode().strip().lower()
            response2 = player2_socket.recv(1024).decode().strip().lower()

            if response1 == "yes" and response2 == "yes":
                broadcast([player1_socket, player2_socket], "[INFO] Both players agreed to play again. Starting a new game...\n")
                continue  # 重新開始遊戲
            else:
                broadcast([player1_socket, player2_socket], "[GAME END] One or both players chose to exit. The game has ended.\n")
                break

    except ConnectionResetError as e:
        print(f"[ERROR] ConnectionResetError: {e}")
        broadcast([player1_socket, player2_socket], "[GAME END] One player has disconnected. Game over.\n")
        if player1_name in active_connections:
            del active_connections[player1_name]
        if player2_name in active_connections:
            del active_connections[player2_name]
    finally:
        for sock, _ in players:
            sock.close()



def broadcast(sockets, message):
    for sock in sockets:
        try:
            sock.send(message.encode())
        except Exception as e:
            print(f"[ERROR] Unable to send message to {sock}: {e}")

def handle_client(client_socket, address):
    global player_queue, logged_in_users
    print(f"[NEW CONNECTION] {address} connected.")

    username = register_or_login(client_socket)
    if username is None:
        # If registration or login fails, return early
        return

    with lock:

        # Add the logged-in user to the queue and track in the set
        logged_in_users.add(username)
        player_queue.append((username, client_socket))
        print(f"[INFO] {username} logged in successfully. Current queue: {[p[0] for p in player_queue]}")
        active_connections[username] = client_socket
        

    try:
        # 處理客戶端邏輯
        try:
            while True:
                with lock:
                    if len(player_queue) == 2:
                        player1_socket = player_queue[0][1]
                        player2_socket = player_queue[1][1]
                        print("[INFO] Two players connected. Starting the game...")
                        for i in active_connections:
                            if active_connections[i] == player1_socket:
                                name1 = i
                                break
                        for i in active_connections:
                            if active_connections[i] == player2_socket:
                                name2 = i
                                break

                        threading.Thread(target=handle_game, args=(player1_socket, player2_socket,name1,name2)).start()
                        player_queue.clear()
                        break
        except (socket.error, ConnectionResetError):
            print(f"[GAME END] Player {username} disconnected unexpectedly.")
            handle_disconnection(username, client_socket)

    finally:
        # 連線結束時，從活躍連線中移除
        if username in active_connections:
            del active_connections[username]

def handle_disconnection(username, client_socket):
    """Handle player disconnection and clean up resources"""
    global player_queue, logged_in_users
    with lock:
        # Remove from the queue if present
        player_queue = [p for p in player_queue if p[0] != username]
        logged_in_users.discard(username)
        print(f"[GAME END] {username} has been removed from the game queue.")
        if username in active_connections:
            del active_connections[username]
        client_socket.close()
        print(f"[INFO] {username} has been removed from the game queue.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(5)
    print("[LISTENING] Server is listening on port 8888")

    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        print(f"Current active connections: {active_connections}")
if __name__ == "__main__":
    start_server()
