import socket
import random

def start_game():
    # 隨機生成一個 0 到 100 之間的數字
    secret_number = random.randint(0, 100)
    print(secret_number)
    print("Server has selected a number between 0 and 100.")
    
    # 創建一個 TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(2)  # 等待2位客戶端連接
    
    print("Waiting for players to connect...")
    
    # 接受兩位客戶端連接
    client1, addr1 = server_socket.accept()
    print(f"Player 1 connected from {addr1}")
    client2, addr2 = server_socket.accept()
    print(f"Player 2 connected from {addr2}")
    
    players = [client1, client2]
    player_turn = 0  # 玩家1先猜
    game_over = False
    
    while not game_over:
        current_player = players[player_turn]
        other_player = players[1 - player_turn]
        
        current_player.sendall(b"Your turn to guess. Please enter a number between 0 and 100: ")
        
        # 等待玩家猜數字
        guess = int(current_player.recv(1024).decode())
        print(f"Player {player_turn + 1} guessed: {guess}")
        
        if guess < secret_number:
            current_player.sendall(f"Too low! Try again. The number is between {guess} and 100.".encode())
            other_player.sendall(f"Player {player_turn + 1} guessed too low. The number is between {guess} and 100.".encode())
        elif guess > secret_number:
            current_player.sendall(f"Too high! Try again. The number is between 0 and {guess}.".encode())
            other_player.sendall(f"Player {player_turn + 1} guessed too high. The number is between 0 and {guess}.".encode())
        else:
            current_player.sendall(b"Congratulations! You guessed the correct number!")
            other_player.sendall(b"Game over! Player has guessed the correct number.")
            game_over = True
        
        # 換下一位玩家的回合
        player_turn = 1 - player_turn
    
    # 關閉所有連接
    client1.close()
    client2.close()
    server_socket.close()

if __name__ == "__main__":
    start_game()
