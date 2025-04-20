import socket
import threading
import os
import json


class Tracker:
    """
    Tracker class for managing peers and chunk manifest
    """
    UID = 0

    def __init__(self):
        """
        Initializes the Tracker with peers, manifest, and peer info.
        """
        self.peers = []
        self.manifest = {
            'video_1': {
                'peer_1': {
                    'chunks': {1, 2, 3, 4, 5}
                }
            },
            'video_2': {
                'peer_1': {
                    'chunks': {1, 5}
                },
                'peer_2': {
                    'chunks': {1, 2, 3, 4, 5}
                }
            },
            'video_3': {
                'peer_2': {
                    'chunks': {1, 2, 4, 5}
                }
            }
        }

        self.peer_info = {
            'peer_1': {
                'ip_addr': '127.0.0.1'
            },
            'peer_2': {
                'ip_addr': '127.0.0.1'
            },
            'peer_3': {
                'ip_addr': '127.0.0.1'
            },
        }

    def get_peers_info(self):
        """
        Returns a list of registered peers.

        :return: List of peers
        """
        return self.peers

    def get_chunk_info(self, conn, address, chunk_request):
        """
        Retrieves chunk information based on a request.

        :param conn: Connection object
        :param address: Address tuple of the peer
        :param chunk_request: JSON-encoded chunk request string
        :return: Tuple (peers list, is_all_available boolean)
        """
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
        is_all_available = (chunks_covered == requested)

        return (peers_containing_range, is_all_available)

    def update_manifest(self, uploader_info, vid_name, conn, address):
        """
        Updates the manifest with new chunk information.

        :param uploader_info: uploader info (chunk list)
        :param vid_name: Video name as a string
        :param conn: Connection object
        :param address: Address tuple of the uploader
        :return: None
        """
        chunks = uploader_info
        ip_client = address[0]
        message_code = 641
        message_comment = "Updated Chunks Successfully!"
        peer_identifier = None

        for peer_id, info in self.peer_info.items():
            if info["ip_addr"] == ip_client:
                peer_identifier = peer_id
                break

        if peer_identifier is None:
            print("Unknown peer IP:", ip_client)
            message_comment = "Failed to update chunks!"
            message_code = 741

        response = {
            "message_comment": message_comment,
            "message_code": message_code,
        }

        if message_code == 741:
            response = json.dumps(response).encode('utf-8')
            msg_len = len(response)
            conn.send(msg_len.to_bytes(4, byteorder="big"))
            conn.send(response)
            return

        if vid_name not in self.manifest:
            self.manifest[vid_name] = {}

        if peer_identifier not in self.manifest[vid_name]:
            self.manifest[vid_name][peer_identifier] = {'chunks': set()}

        for chunk in chunks:
            self.manifest[vid_name][peer_identifier]['chunks'].add(chunk)

        response = json.dumps(response).encode('utf-8')
        msg_len = len(response)
        conn.send(msg_len.to_bytes(4, byteorder="big"))
        conn.send(response)

    def register_new_peer(self, client, address):
        """
        Registers a new peer.

        :param client: Connection object for the peer
        :param address: Address tuple of the peer
        :return: None
        """
        if (client, address) not in self.peers:
            self.peers.append((client, address))
            message_comment = "Registration Successful!"
        else:
            message_comment = "The peer has already registered!"

        response = {
            "message_comment": message_comment,
            "message_code": 621
        }

        response = json.dumps(response).encode('utf-8')
        msg_len = len(response)
        client.send(msg_len.to_bytes(4, byteorder="big"))
        client.send(response)

    def deregister_peer(self, client, address):
        """
        Deregisters an existing peer.

        :param client: Connection object for the peer
        :param address: Address tuple of the peer
        :return: None
        """
        peer = (client, address)
        ip_client = address[0]
        peer_identifier = None
    
        if peer in self.peers:
            # update the manifest i.e delete the chunks that had deregistering peer had.
            for peer_id, info in self.peer_info.items():
                if info["ip_addr"] == ip_client:
                    peer_identifier = peer_id
                    break
            
            for video_id in list(self.manifest.keys()):
                if peer_identifier in self.manifest[video_id]:
                    del self.manifest[video_id][peer_identifier]
                
                # remove the video from manifest if it does not have any peer.
                if not self.manifest[video_id]:
                    del self.manifest[video_id]

            self.peers.remove(peer)
            message_code = 651
            message_comment = "Successfully Deregistered!"
        else:
            message_code = 751
            message_comment = "Peer not found in the register!"

        response = {
            "message_comment": message_comment,
            "message_code": message_code
        }

        response = json.dumps(response).encode('utf-8')
        msg_len = len(response)
        client.send(msg_len.to_bytes(4, byteorder="big"))
        client.send(response)

    def handle_peer(self, conn, address):
        """
        Handles communication with a peer.

        :param conn: Connection object
        :param address: Address tuple of the peer
        :return: None
        """
        while True:
            try:
                # Receive the first 4 bytes for message length
                raw_msg_len = conn.recv(4)
                if not raw_msg_len:
                    break

                msg_len = int.from_bytes(raw_msg_len, byteorder="big")

                # Receive the JSON message
                read_len = 0
                remaining_len = msg_len
                message = b''
                while read_len < msg_len:
                    partial_msg = conn.recv(remaining_len)
                    message += partial_msg
                    remaining_len -= len(partial_msg)
                    read_len += len(partial_msg)

                message = message.decode('utf-8')

                # Parse the JSON message
                data = json.loads(message)
                message_code = data.get("message_code")
                message_comment = data.get("message_comment")

                print(f"Received {message_code}: {message_comment}")

                if message_code == 210:  # 210 Register
                    self.register_new_peer(conn, address)

                elif message_code == 220:  # 220 Deregister
                    self.deregister_peer(conn, address)

                elif message_code == 310:  # 310 Request Chunk
                    chunk_request = data.get("chunk_request")

                    peers_containing_range, is_all_available = self.get_chunk_info(conn, address, chunk_request)

                    if is_all_available:
                        response = {
                            "message_comment": "Chunk request fulfilled",
                            "message_code": 631,
                            "peers": peers_containing_range
                        }
                    else:
                        response = {
                            "message_comment": "Request cannot be fulfilled",
                            "message_code": 731,
                            "peers": peers_containing_range
                        }

                    response = json.dumps(response).encode('utf-8')
                    msg_len = len(response)
                    conn.send(msg_len.to_bytes(4, byteorder="big"))
                    conn.send(response)

                elif message_code == 410:  # 410 Update chunks
                    vid_name = data.get("vid_name")
                    uploader_info = data.get("avail_chunks")
                    self.update_manifest(uploader_info, vid_name, conn, address)

                else:  # 799 Invalid message code/Structure
                    response = {
                        "message_comment": "Invalid message code",
                        "message_code": 799}

                    response = json.dumps(response).encode('utf-8')
                    msg_len = len(response)
                    conn.send(msg_len.to_bytes(4, byteorder="big"))
                    conn.send(response)

            except json.JSONDecodeError:
                response = {
                    "message_comment": "Invalid JSON",
                    "message_code": 799}

                response = json.dumps(response).encode('utf-8')
                msg_len = len(response)
                conn.send(msg_len.to_bytes(4, byteorder="big"))
                conn.send(response)

            except Exception as e:
                response = {"Tracker error": str(e)}
                response = json.dumps(response).encode('utf-8')
                msg_len = len(response)
                conn.send(msg_len.to_bytes(4, byteorder="big"))
                conn.send(response)

        return

    def start_tracker(self):
        """
        Starts the tracker server.

        :return: None
        """
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
