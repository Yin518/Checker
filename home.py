import pygame
import sys

# 初始化 pygame
pygame.init()

# 畫面設定
screen_width, screen_height = 600, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("登入與註冊介面")

# 顏色設定
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 100, 200)
light_blue = (100, 180, 255)
green = (0, 150, 0)
light_green = (100, 255, 100)
gray = (200, 200, 200)
red = (200, 0, 0)
light_red = (255, 100, 100)

# 按鈕設定
button_width, button_height = 200, 50
login_button = pygame.Rect((screen_width // 2 - button_width // 2, 120), (button_width, button_height))
register_button = pygame.Rect((screen_width // 2 - button_width // 2, 200), (button_width, button_height))
back_button = pygame.Rect(10, screen_height - 60, 100, 40)  # 返回按鈕的位置與大小

# 字型設定
font = pygame.font.SysFont('Arial', 28)
input_font = pygame.font.SysFont('Arial', 22)

# 載入背景圖片
try:
    background_image = pygame.image.load("image/background.jpg")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))  # 縮放至畫面大小
except pygame.error:
    print("無法載入背景圖片，請確認路徑是否正確。")
    sys.exit()

# 文字繪製函數
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)


# 嘗試載入登入頁面的背景圖片
try:
    login_background_image = pygame.image.load("image/LoginAndRegister.jpg")
    login_background_image = pygame.transform.scale(login_background_image, (screen_width, screen_height))  # 縮放至畫面大小
except pygame.error:
    print("無法載入登入頁面的背景圖片，請確認路徑是否正確。")
    sys.exit()

# 輸入帳號與密碼
def input_screen(title):
    input_box1 = pygame.Rect(screen_width // 2 - 150, 150, 300, 40)
    input_box2 = pygame.Rect(screen_width // 2 - 150, 230, 300, 40)
    active_box = None
    color_inactive = gray
    color_active = black
    color1 = color_inactive
    color2 = color_inactive
    username = ""
    password = ""
    running = True

    while running:
        screen.fill(white)
        # 繪製背景圖片
        screen.blit(login_background_image, (0, 0))
        draw_text(title, font, black, screen, screen_width // 2, 80)

        # 繪製輸入框與內容
        pygame.draw.rect(screen, color1, input_box1, 2)
        pygame.draw.rect(screen, color2, input_box2, 2)

        draw_text(username, input_font, black, screen, input_box1.centerx, input_box1.centery)
        draw_text("*" * len(password), input_font, black, screen, input_box2.centerx, input_box2.centery)

        draw_text("Input name", font, black, screen, screen_width // 2, 125)
        draw_text("Input password", font, black, screen, screen_width // 2, 210)

        # 繪製返回按鈕
        back_color = light_red if back_button.collidepoint(pygame.mouse.get_pos()) else red
        pygame.draw.rect(screen, back_color, back_button)
        draw_text("Back", font, white, screen, back_button.centerx, back_button.centery)

        # 事件處理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 檢查是否點擊返回按鈕
                if back_button.collidepoint(event.pos):
                    running = False
                # 檢查是否點擊輸入框
                elif input_box1.collidepoint(event.pos):
                    active_box = input_box1
                elif input_box2.collidepoint(event.pos):
                    active_box = input_box2
                else:
                    active_box = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 檢查點擊是否在輸入框內
                if input_box1.collidepoint(event.pos):
                    active_box = input_box1
                elif input_box2.collidepoint(event.pos):
                    active_box = input_box2
                else:
                    active_box = None
            elif event.type == pygame.KEYDOWN:
                if active_box == input_box1:
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode
                elif active_box == input_box2:
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    else:
                        password += event.unicode
                elif event.key == pygame.K_RETURN:  # 按下 Enter 完成輸入
                    print(f"name: {username}, password: {password}")
                    running = False

        # 更新輸入框顏色
        color1 = color_active if active_box == input_box1 else color_inactive
        color2 = color_active if active_box == input_box2 else color_inactive

        # 更新畫面
        pygame.display.flip()

# 主程式迴圈
running = True
while running:
    # 繪製背景圖片
    screen.blit(background_image, (0, 0))

    # 獲取滑鼠位置
    mouse_pos = pygame.mouse.get_pos()

    # 檢查滑鼠是否在按鈕上
    login_color = light_blue if login_button.collidepoint(mouse_pos) else blue
    register_color = light_green if register_button.collidepoint(mouse_pos) else green

    # 畫按鈕
    pygame.draw.rect(screen, login_color, login_button)
    pygame.draw.rect(screen, register_color, register_button)

    # 繪製文字
    draw_text("Login", font, white, screen, login_button.centerx, login_button.centery)
    draw_text("Register", font, white, screen, register_button.centerx, register_button.centery)

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if login_button.collidepoint(mouse_pos):
                print("登入按鈕被點擊")
                input_screen("Login")
            elif register_button.collidepoint(mouse_pos):
                print("註冊按鈕被點擊")
                input_screen("Register")

    # 更新畫面
    pygame.display.flip()

# 結束 pygame
pygame.quit()
