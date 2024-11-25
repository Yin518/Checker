import pygame as pg
import socket
import pickle
from game_control import GameControl  # 假設GameControl處理遊戲邏輯

# 其他pygame初始化設定
pg.init()
FPS = 60
fps_clock = pg.time.Clock()

# 設定顯示
DISPLAYSURF = pg.display.set_mode((600, 600))
main_font = pg.font.Font(None, 36)
turn_rect = pg.Rect(10, 10, 200, 40)
winner_rect = pg.Rect(10, 50, 200, 40)

class Client:
    def __init__(self):
        self.server_ip = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
        self.server_port = int(input("Enter server port (default 5555): ") or 5555)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))
        
        # **選擇遊戲模式並檢查輸入**
        while True:
            self.game_mode = input("Select game mode (1 for Player vs Player, 2 for Player vs Computer): ")
            if self.game_mode in ["1", "2"]:
                break
            print("Invalid input. Please enter 1 or 2.")
        self.client_socket.send(self.game_mode.encode())  # 發送遊戲模式到伺服器

        self.game_control = GameControl(player_color="W", is_computer_opponent=self.game_mode == "2")

    def send_move_to_server(self, move_data):
        # 發送玩家的移動到伺服器
        self.client_socket.send(pickle.dumps(move_data))

    def receive_game_state(self):
        # 接收伺服器回傳的遊戲狀態
        data = self.client_socket.recv(1024)
        game_state = pickle.loads(data)
        self.game_control.update_game_state(game_state)
    
    def close(self):
        self.client_socket.close()

def main():
    client = Client()

    while True:
        # GUI
        DISPLAYSURF.fill((255, 255, 255))
        client.game_control.draw_screen(DISPLAYSURF)

        turn_display_text = "White's turn" if client.game_control.get_turn() == "W" else "Black's turn"
        DISPLAYSURF.blit(main_font.render(turn_display_text, True, (0, 0, 0)), turn_rect)

        if client.game_control.get_winner() is not None:
            winner_display_text = "White wins!" if client.game_control.get_winner() == "W" else "Black wins!"
            DISPLAYSURF.blit(main_font.render(winner_display_text, True, (0, 0, 0)), winner_rect)

        # Event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                client.close()
                pg.quit()
                return
            
            if event.type == pg.MOUSEBUTTONDOWN:
                client.game_control.hold_piece(event.pos)
            
            if event.type == pg.MOUSEBUTTONUP:
                move_data = client.game_control.release_piece(event.pos)
                if move_data:
                    # 發送移動資料到伺服器
                    client.send_move_to_server(move_data)
                    # 接收伺服器回傳的遊戲狀態
                    client.receive_game_state()

        pg.display.update()
        fps_clock.tick(FPS)

if __name__ == "__main__":
    main()
