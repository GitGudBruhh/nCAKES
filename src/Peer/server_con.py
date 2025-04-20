import socket
import json
import threading

from video import Video

class ServerConnection:

    def __init__(self, server_ip, server_port):
        """
        Initializes the ServerConnection instance.

        :param server_ip: The IP address of the server to connect to.
        :type server_ip: str
        :param server_port: The port number of the server to connect to.
        :type server_port: int
        """

        self.server_ip = server_ip
        self.server_port = server_port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.server_ip, self.server_port))

        # Threading stuff
        self.conn_lock = threading.Lock()


    def send_msg_len(self, msg):
        """
        Sends the length of the message to the server.

        :param msg: The message whose length is to be sent.
        :type msg: str
        """
        msg_len = len(msg)
        length = msg_len.to_bytes(4, byteorder='big')
        self.conn.send(length)

    def register_with_server(self):
        """
        Registers the client with the server.

        :raises Exception: If the server responds with an error message.
        """

        message = {
            "message_code" : 210,
            "message_comment" : "Register"
        }


        msg = json.dumps(message)

        self.send_msg_len(msg)
        self.conn.send(msg.encode("utf-8"))

        # Receive response from server
        raw_res_len = self.conn.recv(4)
        res_len = int.from_bytes(raw_res_len, byteorder="big")
        response = self.conn.recv(res_len).decode("utf-8")


        data = json.loads(response)

        print(data)

        if data["message_code"] == 621:
            return
        elif data["message_code"] == 721:
            raise(data["message_comment"])

    def request_chunks(self, request : dict):
        """
        Requests video chunks from the server.

        :param request: A dictionary containing the chunk request details.
        :type request: dict
        :return: A tuple containing the chunks and peer information if successful,
                 or None if the request was not successful.
        :rtype: tuple or None
        """

        req_chunks = json.dumps(request)

        message = {
            "message_code" : 310,
            "message_comment" : "Request Chunk",
            "chunk_request" : req_chunks
        }

        msg = json.dumps(message)

        with self.conn_lock:
            self.send_msg_len(msg)
            self.conn.send(msg.encode("utf-8"))

            # Receive resposne message
            raw_res_len = self.conn.recv(4)
            res_len = int.from_bytes(raw_res_len, byteorder="big")
            #TODO Make sure we receive full length (in all server conn functions)
            response = self.conn.recv(res_len).decode("utf-8")

        data = json.loads(response)
        print('[SERVER_CONN]', data)

        if data["message_code"] == 631:
            return (data["chunks"], data["peer_info"])
        elif data["message_code"] == 731:
            return None

    def update_chunks(self, vid : Video):
        """
        Updates the server with the available chunks of a video.

        :param vid: The Video object containing the video details.
        :type vid: Video
        """

        message = {
            "message_code" : 410,
            "message_comment" : "Update Chunks",
            "vid_name" : vid.name,
            "vid_len": vid.total_chunks,
            "avail_chunks" : list(vid.avail_chunks),
        }

        msg = json.dumps(message)

        self.send_msg_len(msg)
        self.conn.send(msg.encode("utf-8"))

        # Receive response from server
        raw_res_len = self.conn.recv(4)
        res_len = int.from_bytes(raw_res_len, byteorder="big")
        response = self.conn.recv(res_len).decode("utf-8")


        data = json.loads(response)
        print(data)

        if data["message_code"] == 641:
            pass
        elif data["message_code"] == 741:
            pass

    def send_alive_to_server(self):
        """
        Sends a heartbeat message to the server to indicate that the client is alive.

        :return: None if the server acknowledges the heartbeat.
        :rtype: None
        """
        
        message = {
            "message_code" : 101,
            "message_comment" : "Alive"
        }

        msg = json.dumps(message)

        self.send_msg_len(msg)
        self.conn.send(msg.encode("utf-8"))

        raw_res_len = self.conn.recv(4)
        res_len = int.from_bytes(raw_res_len, byteorder="big")
        response = self.conn.recv(res_len).decode("utf-8")

        data = json.loads(response)

        print(data)

        if data["message_code"] == 611:
            return None
