import socket
import sys

def validate_input(prompt, response):
    """驗證輸入是否有效"""
    if not response:
        return False
    if "Do you want to register or login?" in prompt:
        return response.upper() in ["R", "L"]
    if "Enter a username:" in prompt or "Enter a password:" in prompt:
        return response.isalnum() and len(response) > 0
    if "make a guess" in prompt:
        return response.isdigit()
    if "Enter the lower bound:" in prompt or "Enter the upper bound:" in prompt:
        return response.isdigit()
    return True


def start_client():
    if len(sys.argv) != 2:
        print("Usage: python c.py <server_ip>")
        sys.exit(1)
        
    server_ip = sys.argv[1]
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((server_ip, 8888))
    except Exception as e:
        print(f"[ERROR] Unable to connect to server: {e}")
        sys.exit(1)

    while True:
        try:
            message = client.recv(1024).decode()
            if not message:
                break

            if "[PROMPT]" in message:
                prompt = message.replace("[PROMPT]", "").strip()
                print(prompt, end="")

                # 持續要求用戶輸入直到通過驗證
                while True:
                    response = input().strip()
                    if validate_input(prompt, response):
                        break
                    else:
                        print("[ERROR] Invalid input. Please try again:", end=" ")

                client.send(response.encode())
            else:
                print(message.strip())  # 處理非 [PROMPT] 的訊息
        except ConnectionResetError:
            print("[DISCONNECTED] Server disconnected.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            break

    client.close()


if __name__ == "__main__":
    start_client()
