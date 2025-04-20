import socket
import json
import time
import threading

class PeerReceiverSide:
    def __init__(self):
        pass

    def receive_chunk(self, data, conn):
        """
        Saves chunks received from other peers

        :param data: json object containing the video and chunk info
        :param conn: connection socket between requesting and sending peer
        :return: None
        """
        video_len = data.get("video_len")
        video_chunk = b''

        while video_len > 0:
            video_sub_chunk = conn.recv(video_len)
            video_chunk += video_sub_chunk
            video_len -= len(video_sub_chunk)
            
        video_name = data.get("video_name")
        chunk_number = data.get("chunk_number")

        videoss = {chunk_number : video_chunk}

        return videoss


    def handle_peer(self, conn):
        """
        Addresses video chunks sent by other peers

        :param conn: connection socket between requesting and sending peer
        :param parent: the parent's 'self' object
        :return: None
        """
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
                message_code = data.get("message_code")
                
                if message_code == 632: #receiving chunk
                    video_chunk = self.receive_chunk(data, conn)
                    video_name = data.get("video_name")
                    chunk_number = data.get("chunk_number")
                    return video_chunk

                else:
                    print(message)

            except json.JSONDecodeError:
                response = json.dumps({"message_comment": "Invalid JSON",
                                        "message_type": 799})
                response_len = len(response).to_bytes(4, 'big')
                conn.send(response_len)
                conn.send(response.encode("utf-8"))

            except Exception as e:
                response = json.dumps({"receiver side error": str(e)})
                response_len = len(response).to_bytes(4, 'big')
                conn.send(response_len)
                conn.send(response.encode("utf-8"))