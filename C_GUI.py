import socket
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from queue import Queue

def validate_input(prompt, response):
    """驗證輸入是否有效"""
    if not response:
        return False
    if "Enter a username:" in prompt or "Enter a password:" in prompt:
        return response.isalnum() and len(response) > 0
    return True


class ClientGUI:
    def __init__(self, master, server_ip):
        self.master = master
        self.master.title("終極密碼")
        
        # Set the window size
        self.master.geometry("600x400")

        self.server_ip = server_ip
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.prompt_message = ""

        # 設定兩個隊列：一個用來處理遊戲訊息，另一個用來處理聊天訊息
        self.game_queue = Queue()
        self.chat_queue = Queue()

        # Connect to server
        try:
            self.client.connect((server_ip, 8888))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Unable to connect to server: {e}")
            sys.exit(1)
        
        # 建立 UI
        self.create_main_menu()

    def create_main_menu(self):
        """主選單：登入與註冊按鈕"""
        self.clear_window()

        tk.Label(self.master, text="Welcome! Please Login or Register.", font=("Arial", 16)).pack(pady=20)

        # 增加按鈕大小
        tk.Button(self.master, text="Login", command=self.login, width=20, height=2, font=("Arial", 14)).pack(pady=10)
        tk.Button(self.master, text="Register", command=self.register, width=20, height=2, font=("Arial", 14)).pack(pady=10)
        
    def wait_for_other_player(self):
        """等待其他玩家連線的畫面"""
        self.clear_window()

        tk.Label(self.master, text="Login Successful!", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.master, text="Waiting for another player to join...", font=("Arial", 14)).pack(pady=20)
        
    def wait_for_game_start(self):
        """等待遊戲開始的訊息"""
        while True:
            message = self.client.recv(1024).decode()
            if "The game is starting." in message:
                self.enter_chat()  # 切換到遊戲畫面
                break

    def login(self):
        """切換到登入介面"""
        self.clear_window()
        #self.client.send(f"L".encode())
        tk.Label(self.master, text="Login", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.master, text="Username:").pack()
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        tk.Label(self.master, text="Password:").pack()
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()

        # 放大提交按鈕
        tk.Button(self.master, text="Submit", command=self.submit_login, width=20, height=2, font=("Arial", 14)).pack(pady=10)
        tk.Button(self.master, text="Back", command=self.create_main_menu, width=20, height=2, font=("Arial", 14)).pack(pady=5)

    def register(self):
        """切換到註冊介面"""
        self.clear_window()
        #self.client.send(f"R".encode())
        tk.Label(self.master, text="Register", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.master, text="Username:").pack()
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        tk.Label(self.master, text="Password:").pack()
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()

        # 放大提交按鈕
        tk.Button(self.master, text="Submit", command=self.submit_register, width=20, height=2, font=("Arial", 14)).pack(pady=10)
        tk.Button(self.master, text="Back", command=self.create_main_menu, width=20, height=2, font=("Arial", 14)).pack(pady=5)

    def submit_login(self):
        """處理登入邏輯"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if validate_input("Enter a username:", username) and validate_input("Enter a password:", password):
            #self.client.send(f"[LOGIN]{username}:{password}".encode())
            login_data = f"L|{username}|{password}"
            print(f"Sending login data: {login_data}")  # 輸出發送的資料，以便調試
            self.client.send(login_data.encode())

            #接收帳密結果
            response = self.client.recv(1024).decode()
            #if response == "LOGIN_SUCCESS":
            #    self.enter_chat()
            if response.startswith("[INFO] Login successful!"):
                self.wait_for_other_player()  # 顯示等待畫面
                threading.Thread(target=self.wait_for_game_start, daemon=True).start()
            else:
                messagebox.showerror("Login Failed", response)
        else:
            messagebox.showerror("Invalid Input", "Username or password is invalid.")

    def submit_register(self):
        """處理註冊邏輯"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if validate_input("Enter a username:", username) and validate_input("Enter a password:", password):
            #self.client.send(f"[REGISTER]{username}:{password}".encode())
            # self.client.send("R".encode())  # 告诉服务器这是注册请求
            # self.client.send(username.encode())  # 单独发送用户名
            # self.client.send(password.encode())  # 单独发送密码
            # 用 | 分隔註冊請求的不同部分
            register_data = f"R|{username}|{password}"
            self.client.send(register_data.encode())
            print(f"Sending login data: {register_data}")  # 輸出發送的資料，以便調試
            response = self.client.recv(1024).decode()
            if response.startswith("[INFO] Registration successful!"):
                messagebox.showinfo("Registration Successful", "You can now log in!")
                self.create_main_menu()
            else:
                messagebox.showerror("Registration Failed", response)
        else:
            messagebox.showerror("Invalid Input", "Username or password is invalid.")

    def enter_chat(self):
        """進入遊玩介面"""
        self.clear_window()
        
        # 主框架，用於左右佈局
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左邊遊戲框
        game_frame = tk.Frame(main_frame)
        game_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(game_frame, text="Game Messages", font=("Arial", 14)).pack(anchor="nw", padx=5, pady=5)

        self.game_display = scrolledtext.ScrolledText(game_frame, wrap=tk.WORD, state='disabled', height=20, width=30)
        self.game_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.game_input = tk.Entry(game_frame, width=20)
        self.game_input.pack(pady=5)

        tk.Button(game_frame, text="Send Number" , command=self.send_game_messages, width=20, height=2, font=("Arial", 12)).pack(pady=5)

    
        # 右邊聊天訊息框
        chat_frame = tk.Frame(main_frame)
        chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(chat_frame, text="Chat", font=("Arial", 14)).pack(anchor="nw", padx=5, pady=5)

        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state='disabled', height=20, width=30)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.chat_input = tk.Entry(chat_frame, width=20)
        self.chat_input.pack(pady=5)

        tk.Button(chat_frame, text="Send Chat", command=self.send_chat_message, width=20, height=2, font=("Arial", 12)).pack(pady=5)

        self.running = True
        threading.Thread(target=self.receive_messages, daemon=True).start()  # 單一線程負責接收所有訊息
        threading.Thread(target=self.process_game_queue, daemon=True).start()  # 處理遊戲訊息的隊列
        threading.Thread(target=self.process_chat_queue, daemon=True).start()  # 處理聊天訊息的隊列

    def send_game_messages(self):
        """發送遊戲訊息"""
        response = self.game_input.get().strip()  # 使用 game_input
        if response:
            self.client.send(response.encode())
            self.game_input.delete(0, tk.END)  # 清除 game_input

    def send_chat_message(self):
        """發送聊天訊息"""
        chat_message = self.chat_input.get().strip()  # 使用 chat_input
        if chat_message:
            self.client.send(f"[CHAT]{chat_message}".encode())
            self.chat_input.delete(0, tk.END)  # 清除 chat_input

    def receive_messages(self):
        """統一接收訊息，並分派到不同的隊列"""
        try:
            while self.running:
                message = self.client.recv(1024).decode()
                if not message:
                    break
                
                # 根據訊息類型將訊息放入不同的隊列
                if message.startswith("[CHAT]"):
                    self.chat_queue.put(message[2:].strip())  # 聊天訊息
                elif "[PROMPT] Do you want to play again?" in message:
                    self.append_message(message.strip())
                    response = messagebox.askyesno("Game Over", "Do you want to play again?")
                    self.client.send("yes".encode() if response else "no".encode())
                elif "[GAME END]" in message:  # 檢查是否收到遊戲結束訊息
                    self.append_message(message.strip())
                    self.reset_to_main_menu()  # 返回主選單
                    break  # 結束接收循環
                else:
                    self.game_queue.put(message.strip())  # 遊戲訊息

        except Exception as e:
            self.append_message(f"[ERROR] {e}")
        finally:
            self.running = False
            self.client.close()
            self.append_message("[DISCONNECTED] Server disconnected.")
            self.reset_to_main_menu()
            
    def reset_to_main_menu(self):
        """返回到主選單"""
        self.clear_window()  # 清除當前視圖
        self.create_main_menu()  # 重新建立主選單


    def process_game_queue(self):
        """處理遊戲訊息"""
        while self.running:
            message = self.game_queue.get()
            self.append_message(message)

    def process_chat_queue(self):
        """處理聊天訊息"""
        while self.running:
            message = self.chat_queue.get()
            self.append_chat_message(message)

    def append_message(self, message):
        """將訊息附加到遊戲訊息接收區域"""
        self.game_display.config(state='normal')
        self.game_display.insert(tk.END, message + '\n')
        self.game_display.config(state='disabled')
        self.game_display.see(tk.END)

    def append_chat_message(self, message):
        """將訊息附加到聊天訊息接收區域"""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + '\n')
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def clear_window(self):
        """清除視窗內容"""
        for widget in self.master.winfo_children():
            widget.destroy()

    def on_close(self):
        """當 GUI 關閉時執行的操作"""
        self.running = False
        self.master.destroy()
        self.client.close()


def start_client_gui():
    if len(sys.argv) != 2:
        print("Usage: python c.py <server_ip>")
        sys.exit(1)

    server_ip = sys.argv[1]

    root = tk.Tk()
    client_gui = ClientGUI(root, server_ip)
    root.protocol("WM_DELETE_WINDOW", client_gui.on_close)
    root.mainloop()


if __name__ == "__main__":
    start_client_gui()
