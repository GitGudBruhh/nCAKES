import json
from video import Video

class PeerReceiverSide:
    def __init__(self):
        # init method for peer receiver side; no initialization needed for now
        pass

    def receive_chunk(self, data, conn):
        """
        Receives and saves video chunks sent from other peers.

        :param data: JSON data containing the video length and additional info (expected keys: "video_len")
        :param conn: connection socket between the requesting and sending peer
        :return: video chunk in binary string format
        """
        video_len = data.get("video_len")
        video_chunk = b''

        # read chunks until the complete video data is received
        while video_len > 0:
            video_sub_chunk = conn.recv(video_len)
            video_chunk += video_sub_chunk
            video_len -= len(video_sub_chunk)

        return video_chunk

    def handle_peer(self, conn, video: Video, chunk_req):
        """
        Addresses video chunks sent by other peers.

        :param conn: connection socket between the requesting and sending peer
        :param video: Video object representing the video file
        :param chunk_req: the requested video chunk number
        :return: None
        """
        json_message = ""

        # sending a chunk request to the peer
        req = {
            "message_code": 320,
            "video_name": video.name,
            "chunk_number": chunk_req
        }
        req = json.dumps(req)
        # send the length of the JSON request as a 4-byte integer (big-endian)
        conn.send(len(req).to_bytes(4, "big"))
        # send the actual JSON request encoded in utf-8
        conn.send(req.encode("utf-8"))

        # receiving the response from the peer
        try:
            # receive the length of the JSON message first (4 bytes)
            message_bytes = conn.recv(4)
            message_bytes = int.from_bytes(message_bytes, byteorder='big')

            # receive the complete JSON message based on the provided length
            while message_bytes > 0:
                message = conn.recv(message_bytes).decode("utf-8")
                json_message += message
                message_bytes -= len(message)

            # parse the received JSON message
            data = json.loads(json_message)
            message_code = data.get("message_code")
            
            if message_code == 632:  # code indicating that a video chunk is being sent
                video_chunk = self.receive_chunk(data, conn)
                video_name = data.get("video_name")
                chunk_number = data.get("chunk_number")
                # save the received video chunk in the video object's chunks
                video.put_chunk(chunk_number, video_chunk)
            else:
                # print unexpected or error message
                print(message)

        except json.JSONDecodeError:
            # handle the JSON decoding error by sending an error response
            response = json.dumps({"message_comment": "Invalid JSON", "message_type": 799})
            response_len = len(response).to_bytes(4, 'big')
            conn.send(response_len)
            conn.send(response.encode("utf-8"))

        except Exception as e:
            # handle any generic exceptions and notify the peer of the error
            response = json.dumps({"receiver side error": str(e)})
            response_len = len(response).to_bytes(4, 'big')
            conn.send(response_len)
            conn.send(response.encode("utf-8"))
        
        finally:
            conn.close()
