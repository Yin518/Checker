import socket
import sys

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

    last_message = ""  # 用於追蹤最後一條訊息，避免重複處理

    while True:
        try:
            message = client.recv(1024).decode()
            if not message:
                break  # 連線中斷

            # 確保訊息完整性
            if message == last_message:
                continue  # 跳過重複訊息

            last_message = message  # 更新最後一條訊息
            
            if "[PROMPT]" in message:
                print(message.replace("[PROMPT]", ""), end="")
                response = input().strip()
                client.send(response.encode())
            else:
                print(message)
        except ConnectionResetError:
            print("[DISCONNECTED] Server disconnected.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            break

    client.close()

if __name__ == "__main__":
    start_client()
