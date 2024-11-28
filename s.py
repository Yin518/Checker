import socket
from threading import Thread
from logic import UltimatePasswordGame

def handle_client(client_socket, addr, game, clients):
    """
    处理每个客户端的连接和交互。
    """
    try:
        # 发送欢迎消息并请求用户名
        client_socket.sendall(b"Welcome! Please enter your game name: ")
        name = client_socket.recv(1024).decode().strip()

        # 注册玩家
        success, message = game.add_player(name)
        client_socket.sendall(message.encode())

        if not success:
            client_socket.close()
            return

        print(f"Player '{name}' connected from {addr}.")

        # 添加到已连接的客户端列表
        clients.append((client_socket, name))

        # 等待所有玩家加入
        while len(clients) < 2:
            client_socket.sendall(b"Waiting for another player to join...\n")
            client_socket.recv(1024)  # 简单地等待，防止阻塞

        # 通知所有玩家游戏已准备好
        if len(clients) == 2:
            for client, _ in clients:
                client.sendall(b"The game is ready to start!\n")

        # 让第一位玩家设置范围
        if name == game.players[0]:
            client_socket.sendall(b"Please set the range (e.g., 10 100): ")
            while True:
                try:
                    range_input = client_socket.recv(1024).decode().strip()
                    lower, upper = map(int, range_input.split())
                    success, message = game.set_range(lower, upper, name)
                    client_socket.sendall(message.encode())
                    if success:
                        # 通知所有玩家範圍已設定
                        for c, _ in clients:
                            c.sendall(f"The range has been set to {lower}~{upper}.\n".encode())
                        break
                except ValueError:
                    client_socket.sendall(b"Invalid input. Please enter two integers separated by a space.\n")
                except Exception as e:
                    client_socket.sendall(f"An error occurred: {str(e)}\n".encode())

        # 游戏进行循环
        while True:
            current_turn = game.current_turn
            current_player_socket, current_player_name = clients[current_turn]

            # 询问当前玩家进行猜测
            current_player_socket.sendall(b"Your turn to guess. Please enter a number: ")

            try:
                guess_input = current_player_socket.recv(1024).decode().strip()
                guess = int(guess_input)
                success, message = game.guess_number(guess, current_player_name)

                # 发送结果给当前玩家
                current_player_socket.sendall(message.encode())

                # 发送结果给另一位玩家
                other_player_index = 1 - current_turn
                other_player_socket, other_player_name = clients[other_player_index]
                other_player_socket.sendall(message.encode())

                if success:
                    # 游戏结束
                    current_player_socket.sendall(b"Game over! Thanks for playing.\n")
                    other_player_socket.sendall(b"Game over! Thanks for playing.\n")
                    break

            except ValueError:
                current_player_socket.sendall(b"Invalid guess. Please enter a valid number.\n")
            except Exception as e:
                current_player_socket.sendall(f"An error occurred: {str(e)}\n".encode())

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()
        print(f"Connection with {addr} closed.")

def start_server(host='localhost', port=12345):
    """
    启动服务器并处理客户端连接。
    """
    game = UltimatePasswordGame()
    clients = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # 等待2位玩家连接

    print(f"Server is running on {host}:{port}... Waiting for players to connect.")

    try:
        while len(clients) < 2:
            client_socket, addr = server_socket.accept()
            print(f"Player connected from {addr}")
            client_thread = Thread(target=handle_client, args=(client_socket, addr, game, clients))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
