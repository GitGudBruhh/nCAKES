import socket
import json
import time
import threading

from Peer.server_con import ServerConnection

class Peer:

    def __init__(self):

        self.server_conn = ServerConnection("127.0.0.1", 8080, 5)


if __name__ == "__main__":

    peer = Peer()

    server_side = threading.Thread(target=peer.server_conn.handle_server, daemon=True)
    server_side.start()

    request = {
        "video" : "v2",
        "chunk_range_start" : 2,
        "chunk_range_end" : 4
    }

    print(peer.server_conn.request_chunks(request))

    peer.server_conn.avail_chunks["amogh.mp4"] = [0, 1, 2, 3, 4, 5, 6, 7]

    time.sleep(20)
    peer.server_conn.conn.close()