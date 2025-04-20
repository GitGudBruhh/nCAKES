import json
from video import Video

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

        return video_chunk


    def handle_peer(self, conn, video : Video, chunk_req):
        """
        Addresses video chunks sent by other peers

        :param conn: connection socket between requesting and sending peer
        :param parent: the parent's 'self' object
        :return: None
        """
        json_message = ""

        # Sending the request to the peer using conn
        req = {
            "message_code" : 320,
            "video_name" : video.name,
            "chunk_number": chunk_req
        }
        req = json.dumps(req)
        conn.send(len(req).to_bytes(4, "big"))
        conn.send(req.encode("utf-8"))

        # Receiving the response/chunk sent by the peer

        try:
            # Receive the JSON message length
            message_bytes = conn.recv(4)
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
                video.put_chunk(chunk_number, video_chunk)

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