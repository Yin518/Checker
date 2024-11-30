import socket
import sys
import threading
import pygame
from pygame.locals import *

# Initialize pygame
pygame.init()

def validate_input(prompt, response):
    """驗證輸入是否有效"""
    if not response:
        return False
    if "Enter a username:" in prompt or "Enter a password:" in prompt:
        return response.isalnum() and len(response) > 0
    return True


class ClientGUI:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.prompt_message = ""
        self.running = True
        self.current_screen = "main_menu"

        # Initialize Pygame screen
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("終極密碼")
        
        # Load background image
        self.background = pygame.image.load("image/background.jpg")
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 24)

        # Input boxes for username and password
        self.username = ""
        self.password = ""
        self.active_input = None  # Track which input field is active

        # Connect to server
        try:
            self.client.connect((server_ip, 8888))
        except Exception as e:
            self.show_message(f"Unable to connect to server: {e}")
            sys.exit(1)

    def create_main_menu(self):
        """主選單：登入與註冊按鈕"""
        self.current_screen = "main_menu"
        self.show_main_menu()

    def show_main_menu(self):
        """顯示主選單"""
        self.screen.blit(self.background, (0, 0))
        self.draw_text("Welcome! Please Login or Register.", self.font, (255, 255, 255), (300, 50))

        self.draw_button("Login", 200, 200, self.login)
        self.draw_button("Register", 200, 300, self.register)

        pygame.display.flip()

    def draw_button(self, text, x, y, callback):
        """Draws a button and checks if it is clicked"""
        button_rect = pygame.Rect(x, y, 200, 50)
        pygame.draw.rect(self.screen, (0, 0, 255), button_rect)
        self.draw_text(text, self.small_font, (255, 255, 255), (x + 50, y + 15))

        # Check for click events
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_x, mouse_y):
            if pygame.mouse.get_pressed()[0]:  # Left click
                callback()

    def draw_text(self, text, font, color, position):
        """Draw text to the screen"""
        label = font.render(text, True, color)
        self.screen.blit(label, position)

    def login(self):
        """切換到登入介面"""
        self.current_screen = "login"
        self.username = ""
        self.password = ""
        self.active_input = "username"  # Default to username input being active
        self.show_login_screen()

    def register(self):
        """切換到註冊介面"""
        self.current_screen = "register"
        self.username = ""
        self.password = ""
        self.active_input = "username"  # Default to username input being active
        self.show_register_screen()

    def show_login_screen(self):
        """顯示登入畫面"""
        self.screen.blit(self.background, (0, 0))
        self.draw_text("Login", self.font, (255, 255, 255), (350, 50))

        # Draw input boxes for username and password
        self.draw_input_box(self.username, 100, 150, 400, 40, (255, 255, 255), self.active_input == "username")
        self.draw_input_box("*" * len(self.password), 100, 200, 400, 40, (255, 255, 255), self.active_input == "password")

        self.draw_button("Submit", 100, 300, self.submit_login)
        self.draw_button("Back", 100, 400, self.create_main_menu)

        pygame.display.flip()

    def show_register_screen(self):
        """顯示註冊畫面"""
        self.screen.blit(self.background, (0, 0))
        self.draw_text("Register", self.font, (255, 255, 255), (350, 50))

        # Draw input boxes for username and password
        self.draw_input_box(self.username, 100, 150, 400, 40, (255, 255, 255), self.active_input == "username")
        self.draw_input_box("*" * len(self.password), 100, 200, 400, 40, (255, 255, 255), self.active_input == "password")

        self.draw_button("Submit", 100, 300, self.submit_register)
        self.draw_button("Back", 100, 400, self.create_main_menu)

        pygame.display.flip()

    def draw_input_box(self, text, x, y, w, h, color, active=False):
        """繪製輸入框"""
        box_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, color, box_rect, 2)  # 2 is the border width
        if active:
            pygame.draw.rect(self.screen, (0, 0, 255), box_rect, 4)  # Blue border for active input box
        self.draw_text(text, self.small_font, (255, 255, 255), (x + 5, y + 5))  # Draw text inside box

    def submit_login(self):
        """處理登入邏輯"""
        if validate_input("Enter a username:", self.username) and validate_input("Enter a password:", self.password):
            self.client.send("L".encode())  # 告诉服务器这是登录请求
            self.client.send(self.username.encode())  # 单独发送用户名
            self.client.send(self.password.encode())  # 单独发送密码

            response = self.client.recv(1024).decode()
            if response.startswith("[INFO] Login successful!"):
                self.show_message("Login successful!")
                self.current_screen = "waiting_for_player_2"  # Update screen to waiting screen
                self.show_waiting_for_player_2()  # Show waiting screen
                self.wait_for_other_player()  # Start thread for checking other player
            else:
                self.show_message("Login failed. Please try again.")
        else:
            self.show_message("Invalid input.")

    def submit_register(self):
        """處理註冊邏輯"""
        if validate_input("Enter a username:", self.username) and validate_input("Enter a password:", self.password):
            self.client.send("R".encode())  # 告诉服务器这是注册请求
            self.client.send(self.username.encode())  # 单独发送用户名
            self.client.send(self.password.encode())  # 单独发送密码

            response = self.client.recv(1024).decode()
            if response.startswith("[INFO] Registration successful!"):
                self.show_message("Registration successful!")
                self.create_main_menu()
            else:
                self.show_message("Registration failed. Please try again.")
        else:
            self.show_message("Invalid input.")

    def show_message(self, message):
        """顯示訊息"""
        self.screen.blit(self.background, (0, 0))
        self.draw_text(message, self.font, (255, 255, 255), (100, 100))
        pygame.display.flip()
        pygame.time.wait(2000)  # Show message for 2 seconds

    def show_waiting_for_player_2(self):
        """顯示等待玩家2的畫面"""
        self.screen.blit(self.background, (0, 0))
        self.draw_text("Waiting for Player 2 to join...", self.font, (255, 255, 255), (100, 200))
        pygame.display.flip()

    def wait_for_other_player(self):
        """等待遊戲開始的訊息"""
        while True:
            message = self.client.recv(1024).decode()
            if "The game is starting." in message:
                self.enter_chat()  # 切換到遊戲畫面
                break

    def enter_chat(self):
        """進入聊天界面"""
        self.screen.blit(self.background, (0, 0))
        self.draw_text("Game is starting!", self.font, (255, 255, 255), (100, 100))
        pygame.display.flip()

        # Proceed with chat and game logic...

    def run(self):
        """遊戲主迴圈"""
        while self.running:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                # Handle mouse click to set the active input box
                if event.type == MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.current_screen == "login" or self.current_screen == "register":
                        # Check if the click is inside the username or password box
                        if 100 <= mouse_x <= 500 and 150 <= mouse_y <= 190:
                            self.active_input = "username"
                        elif 100 <= mouse_x <= 500 and 200 <= mouse_y <= 240:
                            self.active_input = "password"

                # Handle keyboard input for username and password
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        if self.active_input == "username" and self.username:
                            self.username = self.username[:-1]
                        elif self.active_input == "password" and self.password:
                            self.password = self.password[:-1]
                    elif event.key == K_RETURN:
                        if self.current_screen == "login":
                            self.submit_login()
                        elif self.current_screen == "register":
                            self.submit_register()
                    else:
                        if self.active_input == "username":
                            self.username += event.unicode
                        elif self.active_input == "password":
                            self.password += event.unicode

            # Redraw the current screen
            if self.current_screen == "main_menu":
                self.show_main_menu()
            elif self.current_screen == "login":
                self.show_login_screen()
            elif self.current_screen == "register":
                self.show_register_screen()
            elif self.current_screen == "waiting_for_player_2":
                self.show_waiting_for_player_2()

            pygame.display.flip()

        pygame.quit()


def start_client_gui():
    if len(sys.argv) != 2:
        print("Usage: python c.py <server_ip>")
        sys.exit(1)

    server_ip = sys.argv[1]
    client_gui = ClientGUI(server_ip)
    client_gui.run()


if __name__ == "__main__":
    start_client_gui()
