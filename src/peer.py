import socket
import json
import time
import threading
from ffplay import play_all_chunks

from Peer.server_con import ServerConnection
from Peer.peer_receiver_side import PeerReceiverSide
from Peer.peer_sender_side import PeerSenderSide

from video import Video

class Peer:

    def __init__(self):
        
        # self.ip_address = '127.0.0.1'
        self.ip_address = "0.0.0.0"

        # Peer to Server Connection
        self.server_conn = ServerConnection("192.168.0.110", 8080)
        self.server_handle_interval = 5

        # Peer to Peer Server (For sending data)
        self.sender_side = PeerSenderSide()

        # Peer to Peer client (For requesting and receiving data)
        self.receiver_side = PeerReceiverSide()

        self.videos : dict[str, Video] = {}

    def handle_server(self):
        with self.server_conn.conn_lock:
            self.server_conn.register_with_server()

        while True:
            # Get lock corresponding to socket connecting to the server
            with self.server_conn.conn_lock:

                # Update this clients available chunks to the server periodically
                for video in self.videos.keys():
                    self.server_conn.update_chunks(video, list(self.videos[video].avail_chunks))


        #         #TODO Send Alive pings once in a while
        #         # self.server_conn.send_alive_to_server()

            time.sleep(self.server_handle_interval + 1000)

    def start_sender_side(self):

        print("Starting sender-side of this peer...")
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((self.ip_address, 9090))
        sender.listen(10)

        print("Sender-side started...")

        try:
            while True:
                conn, address = sender.accept()
                print(f"Connection from {address} has been established.")
                client_handler = threading.Thread(target=self.sender_side.handle_peer, 
                                                    args=(conn,), #args should be a tuple
                                                    kwargs = {'parent': self}) 
                client_handler.start()

        except KeyboardInterrupt:
            print("Shutting down sender-side of this peer...")
        finally:
            sender.close()
            print("Sender-side of this peer closed.")   

    def start_receiver_side(self):
        # connect to tracker - done in server_conn
        while True:
            # request video chunk info
            request = {
                "video" : "amogh.mp4",
                "chunk_range_start" : 0,
                "chunk_range_end" : 3
            }

            data = self.server_conn.request_chunks(request)
            
            print("[RECEIVER]", data)
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((data[0], 9090))
            req = {
                "message_code" : 320,
                "video_name" : "amogh.mp4",
                "chunk_number": 0
            }
            req = json.dumps(req)
            conn.send(len(req).to_bytes(4, "big"))
            conn.send(req.encode("utf-8"))
            videoss = self.receiver_side.handle_peer(conn, parent=self)
            play_all_chunks(1, videoss)
            # parse tracker's reply. extract peer info
            # connect to peers -> call handle_peer()

            #TODO Remove this later, but keep it for now or else client will bombard server with requests
            time.sleep(10)

if __name__ == "__main__":

    peer = Peer()

    tracker_side = threading.Thread(target=peer.handle_server, daemon=True)
    tracker_side.start()

    video = Video("amogh.mp4", 10)
    video.avail_chunks = set((0, 1, 2, 3, 4, 5))

    peer.videos = {
        "amogh.mp4" : video
    }

    sender_side = threading.Thread(target=peer.start_sender_side, daemon=True)
    sender_side.start()

    peer.start_receiver_side()
    
    while True:
        pass

    peer.server_conn.conn.close()