from socket import *
import threading
import json


# global variables
video_dir = "../Frontend/videos/"

class Peer:
    def __init__(self):
        self.ip_address = '10.200.244.162'

    def handle_peer(self, conn):
        i = 0
        global json_size
        global bytes_received
        global json_message
        json_size = 0
        bytes_received = 0
        json_message = ""
        while True:
            try:
                # Receive the JSON message
                message_bytes = conn.recv(4)
                message_bytes = int.from_bytes(message_bytes, byteorder='big')
                if not message:
                    break
                print(i , message)
                i+=1
                while message_bytes > 0:
                        message = conn.recv(message_bytes).decode("utf-8")
                        json_message += message
                        message_bytes -= len(message)

                # Parse the JSON message
                data = json.loads(json_message)
                json_message = ""
                message_code = data.get("message_type")
                print(message_code)
                
                if message_code == 310:
                    # assuming peer is requesting 1 chunk at a time
                    video_name = data.get("video_name")
                    chunk_number = data.get("chunk_number")
                    with open(f'{video_dir}video_{video_name}_{chunk_number}.mp4', 'rb') as f:
                        binary_chunk = f.read()
                    response = {
                            "message_comment": "Request action fulfilled",
                            "message_type": 631,
                            "video": binary_chunk,
                            "video_name": video_name,
                            "chunk_number": chunk_number
                        }
                    response_size = {
                                "message_size":len((str)(response)),
                                "message_type": 139
                                    }
                    response_size = json.dumps(response_size)
                    conn.send(response_size.encode("utf-8"))
                    response = json.dumps(response)
                    conn.send(response.encode("utf-8"))
                
                elif message_code == 631: #receiving chunk
                    video_name = data.get("video_name")
                    chunk_number = data.get("chunk_number")
                    video = data.get("video").decode("utf-8")
                    with open(f"{video_dir}video_{video_name}_{chunk_number}.mp4", "wb") as f:
                        f.write(video)
                    # TODO:report updated chunk collection to tracker
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

    def start_serverSide(self):
        print("Starting server-side of this peer...")
        server = socket(AF_INET, SOCK_STREAM)
        server.bind((self.ip_address, 8080))
        server.listen(10)
        print("Server-side started...")

        try:
            while True:
                conn, address = server.accept()
                print(f"Connection from {address} has been established.")
                client_handler = threading.Thread(target=self.handle_peer, args=(conn,)) #args should be a tuple
                client_handler.start()
        except KeyboardInterrupt:
            print("Shutting down server-side of this peer...")
        finally:
            server.close()
            print("Tracker closed.")

    def start_clientSide():
        # connect to tracker
        tracker_ip = '127.0.0.1'
        tracker_port = 8080
        client = socket(AF_INET, SOCK_STREAM)
        client.connect((tracker_ip, tracker_port))
        # request video chunk info
        request = {
            "message_type" : 000,
            "video_name" : "v1",
            "chunk_range" : "0",
            "chunk_range_end" : "0"
        }
        
        # response_size = json.dumps(response_size)
        # client.send(response_size.encode("utf-8"))
        request = json.dumps(request)
        client.send(request.encode("utf-8"))
        
        # receive chunk info
        chunk_info = client.recv(1024)
        # connect to peers -> handle_peer() call only if not in self.receivers
        
        pass


peer_instance = Peer()
peer_instance.start_serverSide()
