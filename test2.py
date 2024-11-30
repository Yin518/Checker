import pygame
import sys

# 初始化pygame
pygame.init()

# 設定畫面大小
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("登入界面")

# 顏色設定
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 255)

# 字型設定
font = pygame.font.Font(None, 36)

# 輸入框設定
input_box = pygame.Rect(200, 150, 140, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
clock = pygame.time.Clock()

# 處理登入邏輯
def submit_login(username):
    print(f"Username: {username}")
    # 這裡可以加上發送登入請求的邏輯

# 主循環
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:  # 按下回車時，提交登入
                    submit_login(text)
                    text = ''  # 重置輸入框
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]  # 刪除最後一個字
                else:
                    text += event.unicode  # 增加文字

    # 顯示輸入框
    txt_surface = font.render(text, True, color)
    width = max(200, txt_surface.get_width()+10)  # 動態調整輸入框寬度
    input_box.w = width
    screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
    pygame.draw.rect(screen, color, input_box, 2)  # 畫出輸入框

    # 更新畫面
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
