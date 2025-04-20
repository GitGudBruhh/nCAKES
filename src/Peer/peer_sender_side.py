import socket
import json
import time
import threading

from video import Video


class PeerSenderSide:
    def __init__(self):
        # init method for peer sender side; no initialization needed for now
        pass
    
    def send_requested_chunk(self, data, conn, videos: dict[str, Video]):
        """
        Sends the requested video chunk.

        :param data: json object containing the video name and chunk info; expected keys: "video_name", "chunk_number"
        :param conn: connection socket between requesting and sending peer
        :param videos: dictionary mapping video names to Video objects
        :return: None
        """
        # read video name and chunk number from the received json data
        video_name = data.get("video_name")
        chunk_number = data.get("chunk_number")

        # retrieve the binary chunk from the corresponding video object
        binary_chunk = videos[video_name].get_chunk(chunk_number)
        response = {
            "message_comment": "Chunk request fulfilled",
            "message_code": 632,
            "video_len": len(binary_chunk),
            "video_name": video_name,
            "chunk_number": chunk_number
        }
        # convert the response to json format
        response = json.dumps(response)
        response_size = len(response)
        # send the length of the json response as a 4-byte integer in big-endian format
        conn.send(response_size.to_bytes(4, "big"))
        # send the actual json response encoded in utf-8
        conn.send(response.encode("utf-8"))
        # send the binary video chunk
        conn.send(binary_chunk)

    def handle_peer(self, conn, videos, parent=None):
        """
        Addresses chunk requests from other peers.

        :param conn: connection socket between the requesting and sending peer
        :param videos: dictionary mapping video names to Video objects
        :param parent: the parent's 'self' object (optional, not used in current implementation)
        :return: None
        """
        json_message = ""
        # run a loop to continuously listen for requests from the peer
        while True:
            try:
                # receive the length of the json message (4 bytes)
                message_bytes = conn.recv(4)
                if not message_bytes:
                    # break if no data received
                    break
                message_bytes = int.from_bytes(message_bytes, byteorder='big')

                # receive the complete json message using the specified length
                while message_bytes > 0:
                    message = conn.recv(message_bytes).decode("utf-8")
                    json_message += message
                    message_bytes -= len(message)

                # parse the json message into a dictionary
                data = json.loads(json_message)
                # reset json_message for the next iteration
                json_message = ""
                message_code = data.get("message_code")
                
                if message_code == 320:
                    # assuming peer is requesting one chunk at a time,
                    # call the method to send the requested chunk
                    self.send_requested_chunk(data, conn, videos)
                else:
                    # print unexpected or error message
                    print(message)

            except json.JSONDecodeError:
                # handle invalid json and notify the peer
                response = json.dumps({"message_comment": "Invalid JSON", "message_type": 799})
                response_len = len(response).to_bytes(4, 'big')
                conn.send(response_len)
                conn.send(response.encode("utf-8"))
                # print the error response for debugging
                print(response)
            except Exception as e:
                # handle any other exceptions and notify the peer of the error
                response = json.dumps({"sender side error": str(e)})
                response_len = len(response).to_bytes(4, 'big')
                conn.send(response_len)
                conn.send(response.encode("utf-8"))
