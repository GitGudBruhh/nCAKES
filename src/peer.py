import socket
import json
import time
import threading

from Peer.server_con import ServerConnection

class Peer:

    def __init__(self, sender_side):
        self.ip_address = '10.200.244.162'
        
        # Peer to Server Connection
        self.server_conn = ServerConnection("127.0.0.1", 8080)
        self.server_handle_interval = 5

        # Peer to Peer Server (For sending data)
        self.server = sender_side

        # Peer to Peer client (For requesting and receiving data)
        self.client = None

        self.videos = {}

    def handle_server(self):
        with self.server_conn.conn_lock:
            self.server_conn.register_with_server()

        while True:
            # Get lock corresponding to socket connecting to the server
            with self.server_conn.conn_lock:
                
                # Update this clients available chunks to the server periodically
                for video in self.videos.keys():
                    self.server_conn.update_chunks(video, self.videos[video])


                #TODO Send Alive pings once in a while
                # self.server_conn.send_alive_to_server()

            time.sleep(self.server_handle_interval)

class PeerSenderSide:
    def __init__(self):
        self.video_dir = "../Frontend/videos/"
        pass
    def send_requested_chunk(self, data, conn):
        video_name = data.get("video_name")
        chunk_number = data.get("chunk_number")
        with open(f'{self.video_dir}video_{video_name}_{chunk_number}.mp4', 'rb') as f:
            binary_chunk = f.read()
        response = {
                "message_comment": "Request action fulfilled",
                "message_code": 631,
                "video_len": len(binary_chunk),
                "video_name": video_name,
                "chunk_number": chunk_number
            }
        response = json.dumps(response)
        response_size = len(response)
        conn.send(response_size.to_bytes(4, "big"))
        conn.send(response.encode("utf-8"))
        conn.send(binary_chunk)

    def receive_chunk(self, data, conn):
        video_len = data.get("video_len")
        video_chunk = b''
        while video_len > 0:
            video_sub_chunk = conn.recv(video_len).decode("utf-8")
            video_chunk += video_sub_chunk
            video_len -= len(video_sub_chunk)
        video_name = data.get("video_name")
        chunk_number = data.get("chunk_number")
        with open(f"{self.video_dir}video_{video_name}_{chunk_number}.mp4", "wb") as f:
            f.write(video_chunk)

    def handle_peer(self, conn):
        global json_size
        global json_message
        json_size = 0
        json_message = ""
        while True:
            try:
                # Receive the JSON message length
                message_bytes = conn.recv(4)
                if not message_bytes:
                    break
                message_bytes = int.from_bytes(message_bytes, byteorder='big')

                while message_bytes > 0:
                        message = conn.recv(message_bytes).decode("utf-8")
                        json_message += message
                        message_bytes -= len(message)

                # Parse the JSON message
                data = json.loads(json_message)
                json_message = ""
                message_code = data.get("message_code")
                print(message_code)
                
                if message_code == 310:
                    # assuming peer is requesting 1 chunk at a time
                    self.send_requested_chunk(data, conn)
                    
                
                elif message_code == 631: #receiving chunk
                    self.receive_chunk(data, conn)
                    # TODO:report updated chunk collection to tracker
                else:
                    print(message)
            except json.JSONDecodeError:
                response = json.dumps({"message_comment": "Invalid JSON",
                                        "message_type": 799})
                response_len = len(response).to_bytes(4, 'big')
                conn.send(response_len)
                conn.send(response.encode("utf-8"))
            except Exception as e:
                response = json.dumps({"Server error": str(e)})
                response_len = len(response).to_bytes(4, 'big')
                conn.send(response_len)
                conn.send(response.encode("utf-8"))
    def start_sender_side(self):
        print("Starting sender-side of this peer...")
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender.bind((self.ip_address, 8080))
        sender.listen(10)
        print("Sender-side started...")

        try:
            while True:
                conn, address = sender.accept()
                print(f"Connection from {address} has been established.")
                client_handler = threading.Thread(target=self.handle_peer, args=(conn,)) #args should be a tuple
                client_handler.start()
        except KeyboardInterrupt:
            print("Shutting down sender-side of this peer...")
        finally:
            sender.close()
            print("Sender-side of this peer closed.")

if __name__ == "__main__":

    sender_side = PeerSenderSide()
    peer = Peer(sender_side)

    tracker_side = threading.Thread(target=peer.handle_server, daemon=True)
    tracker_side.start()

    request = {
        "video" : "v2",
        "chunk_range_start" : 2,
        "chunk_range_end" : 4
    }

    print(peer.server_conn.request_chunks(request))

    peer.videos["amogh.mp4"] = [0, 1, 2, 3, 4, 5, 6, 7]

    time.sleep(5)
    peer.server_conn.conn.close()