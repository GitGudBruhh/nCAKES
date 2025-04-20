import socket
import json
import time
import threading

from Peer.server_con import ServerConnection
from Peer.peer_receiver_side import PeerReceiverSide
from Peer.peer_sender_side import PeerSenderSide

class Peer:

    def __init__(self, sender_side):
        self.ip_address = '10.200.244.162'
        # Peer to Server Connection
        self.server_conn = ServerConnection("127.0.0.1", 8080)
        self.server_handle_interval = 5

        # Peer to Peer Server (For sending data)
        self.sender_side = PeerSenderSide()

        # Peer to Peer client (For requesting and receiving data)
        self.receiver_side = None

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
                client_handler = threading.Thread(target=self.server.handle_peer, 
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
                "video_name" : "1",
                "chunk_range_start" : 0,
                "chunk_range_end" : 5
            }

            self.server_conn.request_chunks(request)
            
            # receive chunk info
            message_bytes = self.server_conn.conn.recv(4)
            if not message_bytes:
                break
            message_bytes = int.from_bytes(message_bytes, byteorder='big')

            while message_bytes > 0:
                    message = self.server_conn.conn.recv(message_bytes).decode("utf-8")
                    json_message += message
                    message_bytes -= len(message)

            # parse tracker's reply. extract peer info
            # connect to peers -> call handle_peer()

if __name__ == "__main__":

    peer = Peer()

    tracker_side = threading.Thread(target=peer.handle_server, daemon=True)
    tracker_side.start()
    sender_side = threading.Thread(target=peer.start_sender_side, daemon=True)
    sender_side.start()
    
    peer.start_receiver_side()

    request = {
        "video" : "video_2",
        "chunk_range_start" : 2,
        "chunk_range_end" : 4
    }

    print(peer.server_conn.request_chunks(request))

    peer.videos["amogh.mp4"] = [0, 1, 2, 3, 4, 5, 6, 7]

    time.sleep(5)
    peer.server_conn.conn.close()