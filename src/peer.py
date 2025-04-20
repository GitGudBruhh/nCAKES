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
        self.server_handle_interval = 40

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
                time.sleep(1)
                for video in self.videos.keys():
                    self.server_conn.update_chunks(self.videos[video])


                #TODO Send Alive pings once in a while
                # self.server_conn.send_alive_to_server()

            time.sleep(self.server_handle_interval)

    def start_sender_side(self):

        print("[SENDER_SIDE] Starting sender-side of this peer...")
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sender.bind((self.ip_address, 9090))
        sender.listen(10)

        print("[SENDER_SIDE] Sender-side started...")

        try:
            while True:
                conn, address = sender.accept()
                print(f"[SENDER_SIDE] Connection from {address} has been established.")
                client_handler = threading.Thread(target=self.sender_side.handle_peer,
                                                    args=(conn, self.videos), #args should be a tuple
                                                    kwargs = {'parent': self})
                client_handler.start()

        except KeyboardInterrupt:
            print("[SENDER_SIDE] Shutting down sender-side of this peer...")
        finally:
            sender.close()
            print("[SENDER_SIDE] Sender-side of this peer closed.")

    def start_receiver_side(self):
        # connect to tracker - done in server_conn
        # request video chunk info
        video_name = "amogh.mp4"
        request = {
            "video" : video_name
        }

        chunks, peer_info = self.server_conn.request_chunks(request)

        video_len = chunks["metadata"]["vid_len"]
        self.videos[video_name] = Video(request["video"], video_len)

        video_player = threading.Thread(target=play_all_chunks, args=(video_len, self.videos[video_name].data))
        video_player.start()

        total_peers = len(peer_info)

        while len(self.videos[video_name].avail_chunks) < video_len:
            for chunk_num in (set(range(video_len)) - self.videos[video_name].avail_chunks):
                
                cur_peer = peer_info[chunk_num % total_peers]
        for chunk_num in range(video_len):

            cur_peer = chunk_num % total_peers

            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((peer_info[cur_peer]["peer_1"]["ip_addr"], 9090))

            video_player = threading.Thread(target=self.receiver_side.handle_peer,
                                            args=(conn, self.videos[video_name], chunk_num))
            video_player.start()

        # connect to peers -> call handle_peer()

        #TODO Remove this later, but keep it for now or else client will bombard server with requests
        # time.sleep(10)

if __name__ == "__main__":

    peer = Peer()

    tracker_side = threading.Thread(target=peer.handle_server, daemon=True)
    tracker_side.start()

    sender_side = threading.Thread(target=peer.start_sender_side, daemon=True)
    sender_side.start()

    video = Video("amogh.mp4", 0)
    video.load_video("./videos/stream.ts", 1048576)     # Chunk size of 1MB

    peer.videos = {
        "amogh.mp4" : video
    }

    # peer.start_receiver_side()
<<<<<<< HEAD
=======

    try:
        while True:
            pass
    except KeyboardInterrupt:
        response = {
            "message_comment": "Deregister",
            "message_code": 220
        }

        response = json.dumps(response).encode('utf-8')
        msg_len = len(response)
        peer.server_conn.conn.send(msg_len.to_bytes(4, byteorder="big"))
        peer.server_conn.conn.send(response)

        msg_len = peer.server_conn.conn.recv(4)
        msg = peer.server_conn.conn.recv(int.from_bytes(msg_len))
        exit(0)
>>>>>>> 641d8e49bb107180c9771bc006d5519320badf56


    peer.server_conn.conn.close()