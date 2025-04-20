import socket
import json
import time
import threading

class PeerReceiverSide:
    def __init__(self):
        pass

    def handle_peer(self, conn, parent = None):
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
                    video_name = data.get("video_name")
                    chunk_number = data.get("chunk_number")
                    parent.videos[video_name].append(chunk_number)
                    # report updated chunk collection to tracker: DONE
                    parent.server_conn.update_chunks(video_name, parent.videos[video_name])
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