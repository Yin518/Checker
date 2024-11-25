import socket
import pickle
from game_control import GameControl

class Server:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}...")

        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Connection established with {self.client_address}")

        # 接收客戶端的遊戲模式
        game_mode = self.client_socket.recv(1024).decode()
        print(f"Game mode selected: {game_mode}")

        # 根據遊戲模式初始化GameControl
        if game_mode == "1":
            self.game_control = GameControl(player_color="W", is_computer_opponent=False)
        else:
            self.game_control = GameControl(player_color="W", is_computer_opponent=True)

    def handle_client(self):
        while True:
            # 接收玩家的移動資料
            data = self.client_socket.recv(1024)
            if not data:
                break

            move_data = pickle.loads(data)
            print("Received move data:", move_data)

            # 確認是否是玩家的回合
            if self.game_control.get_turn() == "W":  # 玩家回合 (假設玩家是白棋)
                self.game_control.update_game_state(move_data)

                # 更新遊戲狀態後切換回合
                if self.game_control.get_turn() == "B" and self.game_control.ai_control:
                    self.game_control.move_ai()
            
            # 如果不是玩家的回合，拒絕接受移動並返回錯誤信息
            else:
                print("Error: Move received during AI's turn!")

            # 發送回更新後的遊戲狀態
            self.client_socket.send(pickle.dumps(self.game_control.get_game_state()))


    def close(self):
        self.client_socket.close()

if __name__ == "__main__":
    server = Server()
    server.handle_client()
    server.close()
