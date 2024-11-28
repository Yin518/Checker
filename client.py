import socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 8888))

    while True:
        try:
            message = client.recv(1024).decode()
            if not message:
                break

            if "[PROMPT]" in message:
                print(message.replace("[PROMPT]", "").strip(), end="")
                response = input().strip()
                client.send(response.encode())
            else:
                print(message.strip())  # 不重複輸出
        except ConnectionResetError:
            print("[DISCONNECTED] Server disconnected.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            break

    client.close()


def validate_input(prompt, response):
    if not response:
        return False
    if "Do you want to register or login?" in prompt:
        return response.upper() in ["R", "L"]
    if "Enter a username:" in prompt or "Enter a password:" in prompt:
        return response.isalnum() and len(response) > 0
    if "make a guess" in prompt:
        return response.isdigit()
    return True

if __name__ == "__main__":
    start_client()
