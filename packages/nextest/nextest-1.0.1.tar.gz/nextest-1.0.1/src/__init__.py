import socket

def send_hello(ip: str, port: int):
    try:
        # 创建 TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 设置超时时间，防止长时间卡住
            print(f"[*] Connecting to {ip}:{port} ...")
            s.connect((ip, port))
            
            # 发送消息
            message = "hello"
            s.sendall(message.encode())
            print(f"[+] Sent: {message}")
            
            # 可选：接收对方回复（如果有）
            try:
                response = s.recv(1024)
                if response:
                    print(f"[<] Received: {response.decode(errors='ignore')}")
            except socket.timeout:
                print("[!] No response (timeout)")
            
            print("[*] Closing connection.")
    except Exception as e:
        print(f"[x] Error: {e}")

if __name__ == "__main__":
    # 修改为你想连接的 IP 和端口
    target_ip = "83.229.126.93"
    target_port = 8080
    send_hello(target_ip, target_port)

