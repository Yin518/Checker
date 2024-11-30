import socket
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext


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
            # self.client.send("L".encode())  # 告诉服务器这是登录请求
            # self.client.send(username.encode())  # 单独发送用户名
            # self.client.send(password.encode())  # 单独发送密码

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

        self.chat_display = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, state='disabled', height=20, width=50)
        self.chat_display.pack(padx=10, pady=10)

        self.user_input = tk.Entry(self.master, width=40)
        self.user_input.pack(pady=5)

        tk.Button(self.master, text="Send", command=self.send_response, width=20, height=2, font=("Arial", 14)).pack(pady=5)

        self.running = True
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def send_response(self):
        """發送聊天訊息"""
        response = self.user_input.get().strip()
        if response:
            self.client.send(response.encode())
            self.user_input.delete(0, tk.END)

    def receive_messages(self):
        """接收聊天訊息"""
        try:
            while self.running:
                message = self.client.recv(1024).decode()
                if not message:
                    break

                if "[PROMPT] Do you want to play again?" in message:
                    self.append_message(message.strip())
                    response = messagebox.askyesno("Game Over", "Do you want to play again?")
                    self.client.send("yes".encode() if response else "no".encode())
                else:
                    self.append_message(message.strip())
        except Exception as e:
            self.append_message(f"[ERROR] {e}")
        finally:
            self.running = False
            self.client.close()
            self.append_message("[DISCONNECTED] Server disconnected.")

    def append_message(self, message):
        """將訊息附加到聊天區域"""
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
