import socket

def start_client():
    SERVER_HOST = 'localhost'  # 修改为目标服务器 IP
    SERVER_PORT = 12345

    # 连接到服务器
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    try:
        while True:
            # 接收提示并显示
            message = client_socket.recv(1024).decode()
            print(message, end='')  # 使用 end='' 以避免重复换行

            if "Please enter your game name" in message:
                name = input()
                client_socket.sendall(name.encode())
            elif "Please enter your password" in message:
                password = input()
                client_socket.sendall(password.encode())
            elif "等待另一位玩家加入" in message or "Waiting for another player to join" in message:
                continue  # 继续等待
            elif "Please set the range" in message:
                while True:
                    try:
                        low = int(input("請輸入範圍的最低值："))
                        high = int(input("請輸入範圍的最高值："))
                        range_input = f"{low} {high}"
                        client_socket.sendall(range_input.encode())  # 发送范围
                        response = client_socket.recv(1024).decode()
                        print(response)
                        if "範圍設定成功" in response or "Range has been set" in response:
                            break
                    except ValueError:
                        print("請輸入有效的整數！")
            elif "Your turn to guess" in message or "你的回合" in message:
                while True:
                    try:
                        guess = int(input("請輸入你的猜測："))
                        client_socket.sendall(str(guess).encode())
                        response = client_socket.recv(1024).decode()
                        print(response)
                        if "恭喜" in response or "Game over" in response:
                            return
                        break
                    except ValueError:
                        print("請輸入有效的整數！")
            elif "Game over" in message or "恭喜" in message:
                break

    finally:
        print("遊戲結束，關閉連接。")
        client_socket.close()

if __name__ == "__main__":
    start_client()
