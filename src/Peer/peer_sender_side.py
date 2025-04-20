import socket
import json
import time
import threading

# TODO:
# 1. change message_code : 631 to something else while sending the chunk

class PeerSenderSide:
    def __init__(self):
        pass
    
    def send_requested_chunk(self, data, conn):
        """
        Sends requested chunk

        :param data: json object containing the video and chunk info
        :param conn: connection socket between requesting and sending peer
        :return: None
        """
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

    def handle_peer(self, conn, parent = None):
        """
        Addresses other peers' chunk requests

        :param conn: connection socket between requesting and sending peer
        :param parent: the parent's 'self' object
        :return: None
        """
        global json_message
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
                else:
                    print(message)
            except json.JSONDecodeError:
                response = json.dumps({"message_comment": "Invalid JSON",
                                        "message_type": 799})
                response_len = len(response).to_bytes(4, 'big')
                conn.send(response_len)
                conn.send(response.encode("utf-8"))
                print(response)
            except Exception as e:
                response = json.dumps({"sender side error": str(e)})
                response_len = len(response).to_bytes(4, 'big')
                conn.send(response_len)
                conn.send(response.encode("utf-8"))