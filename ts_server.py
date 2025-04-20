# ts_server.py
import socket
import time

HOST = '127.0.0.1'
PORT = 9999
FILENAME = 'streamable.ts'

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"[+] Waiting for connection on {HOST}:{PORT}")

    conn, addr = server.accept()
    print(f"[+] Client connected: {addr}")

    with open(FILENAME, 'rb') as f:
        count = 0
        while chunk := f.read(4096):
            count += 1
            if count == 400:
                print("sleeping")
                time.sleep(10)
                print("continuing")
            conn.sendall(chunk)

    conn.close()
    print("[+] Done streaming")

if __name__ == "__main__":
    main()
