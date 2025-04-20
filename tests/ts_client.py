# ts_client.py
import socket
import subprocess

HOST = '127.0.0.1'
PORT = 9999

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    # Start ffplay to read from stdin
    player = subprocess.Popen(
        ["ffplay", "-i", "pipe:0", "-fflags", "nobuffer", "-flags", "low_delay"],
        stdin=subprocess.PIPE
    )

    while True:
        data = s.recv(4096)
        if not data:
            break
        player.stdin.write(data)

    s.close()
    player.stdin.close()
    print("[+] Finished")

if __name__ == "__main__":
    main()
