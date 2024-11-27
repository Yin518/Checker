import socket

def start_client():
    # 連接到 Server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    
    while True:
        # 接收提示並顯示
        message = client_socket.recv(1024).decode()
        print(message)
        
        if "Congratulations" in message:  # 遊戲結束
            break
        
        # 用戶輸入猜測數字
        guess = input("Enter your guess: ")
        client_socket.sendall(guess.encode())
    
    client_socket.close()

if __name__ == "__main__":
    start_client()
