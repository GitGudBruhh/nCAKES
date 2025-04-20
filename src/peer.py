import socket
import json
import time
import threading

from Peer.server_con import ServerConnection

class Peer:

    def __init__(self):
        
        # Peer to Server Connection
        self.server_conn = ServerConnection("127.0.0.1", 8080)
        self.server_handle_interval = 5

        # Peer to Peer Server (For sending data)
        self.server = None

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

if __name__ == "__main__":

    peer = Peer()

    server_side = threading.Thread(target=peer.handle_server, daemon=True)
    server_side.start()

    request = {
        "video" : "v2",
        "chunk_range_start" : 2,
        "chunk_range_end" : 4
    }

    print(peer.server_conn.request_chunks(request))

    peer.videos["amogh.mp4"] = [0, 1, 2, 3, 4, 5, 6, 7]

    time.sleep(5)
    peer.server_conn.conn.close()