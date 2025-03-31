import socket
import threading
import os
import json


class Tracker:

    UID = 0

    def __init__(self):
        self.peers = []
        self.manifest = {
            'v1': {
                'p1': {
                    'chunks': {1, 2, 3, 4, 5}
                }
            },
            'v2': {
                'p1': {
                    'chunks': {1, 2, 4, 5}
                },
                'p2': {
                    'chunks': {1, 2, 3, 4, 5}
                }
            },
            'v3': {
                'p2': {
                    'chunks': {1, 2, 4, 5}
                }
            }
        }

        self.peer_info = {
            'p1': {
                'ip_addr': '127.0.0.1'
            },
            'p2': {
                'ip_addr': '127.0.0.1'
            },
            'p3': {
                'ip_addr': '127.0.0.1'
            },
        }

    def get_peers_info(self):
        return self.peers

    def get_chunk_info(self, conn, address, chunk_request):
        # Retrieve video name
        chunk_request_dict = json.loads(chunk_request)
        vid = chunk_request_dict['video']

        # Retrieve requested chunk range
        chunk_range_start = chunk_request_dict['chunk_range_start']
        chunk_range_end = chunk_request_dict['chunk_range_end']
        requested = {i for i in range(chunk_range_start, chunk_range_end + 1)}

        peers_containing_range = []
        chunks_covered = set()

        # Best effort set cover of requested chunks
        for peer in self.manifest[vid]:
            available = self.manifest[vid][peer]['chunks']
            requested_and_available = available.intersection(requested)

            if len(requested_and_available - chunks_covered) > 0:
                peers_containing_range.append(peer)
                chunks_covered.update(requested_and_available)

        # Check if all requested chunks are available
        # Used to inject video into swarm
        is_all_available = (chunks_covered == requested)

        return (peers_containing_range, is_all_available)

    def update_manifest(self, uploader_info, vid_name):
        # TODO: Change this function
        uploader_info_dict = json.loads(uploader_info)

        for peer in uploader_info_dict:
            if peer not in self.manifest:
                self.manifest[peer] = {}

            if vid_name not in self.manifest[peer]:
                self.manifest[peer][vid_name] = {'chunks': []}

            for chunk in uploader_info_dict[peer]['chunks']:
                if chunk not in self.manifest[peer][vid_name]['chunks']:
                    self.manifest[peer][vid_name]['chunks'].append(chunk)

    def register_new_peer(self, client, address):
        self.peers.append((client, address))

    def handle_peer(self, conn, address):
        while True:
            try:
                # Receive the JSON message
                message = conn.recv(1024).decode("utf-8")
                if not message:
                    break

                # Parse the JSON message
                data = json.loads(message)
                message_code = data.get("message_code")
                message_comment = data.get("message_comment")

                print(f"Received {message_code}: {message_comment}")

                if message_code == 210:  # 210 Register
                    self.register_new_peer(conn, address)

                # TODO: Implement deregister
                # elif message_code == 220:  # 220 Deregister
                #     self.deregister_peer(conn, address)

                elif message_code == 310:  # 310 Request Chunk
                    chunk_request = data.get("chunk_request")

                    peers_containing_range, is_all_available = self.get_chunk_info(conn, address, chunk_request)

                    if is_all_available:
                        response = {
                            "message_comment": "Chunk request fulfilled",
                            "message_type": 631,
                            "peers": peers_containing_range
                        }
                    else:
                        response = {
                            "message_comment": "Request cannot be fulfilled",
                            "message_type": 731,
                            "peers": peers_containing_range
                        }

                    response = json.dumps(response)
                    conn.send(response.encode("utf-8"))

                elif message_code == 410:  # 410 Update chunks
                    vid_name = data.get("vid_name")
                    uploader_info = data.get("uploader_info")

                    self.update_manifest(uploader_info, vid_name)

                    # TODO: response = ?
                    conn.send(response.encode("utf-8"))

                else:  # 799 Invalid message code/Structure
                    response = json.dumps({"message_comment": "Invalid message code",
                                           "message_type": 799})
                    conn.send(response.encode("utf-8"))

            except json.JSONDecodeError:
                response = json.dumps({"message_comment": "Invalid JSON",
                                        "message_type": 799})
                conn.send(response.encode("utf-8"))
            except Exception as e:
                response = json.dumps({"Tracker error": str(e)})
                conn.send(response.encode("utf-8"))

        return

    def start_tracker(self):
        print("Starting tracker...")
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.bind(('127.0.0.1', 8080))
        tracker.listen(10)
        print("Tracker started...")

        try:
            while True:
                conn, address = tracker.accept()
                print(f"Connection from {address} has been established.")
                client_handler = threading.Thread(target=self.handle_peer, args=(conn, address))
                client_handler.start()
        except KeyboardInterrupt:
            print("Shutting down tracker server...")
        finally:
            tracker.close()
            print("Tracker closed.")


# Start the tracker
if __name__ == "__main__":
    tracker_instance = Tracker()
    tracker_instance.start_tracker()
