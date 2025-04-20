import socket
import json
import time
import threading

class ServerConnection:

    def __init__(self, server_ip, server_port):

        self.server_ip = server_ip
        self.server_port = server_port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.server_ip, self.server_port))

        # Threading stuff
        self.conn_lock = threading.Lock()
        

    def send_msg_len(self, msg):
        msg_len = len(msg)
        length = msg_len.to_bytes(4, byteorder='big')
        self.conn.send(length)

    def register_with_server(self):

        message = {
            "message_code" : 210,
            "message_comment" : "Register"
        }


        msg = json.dumps(message)
        
        self.send_msg_len(msg)
        self.conn.send(msg.encode("utf-8"))

        response = self.conn.recv(1024)
        data = json.loads(response)

        print(data)

        if data["message_type"] == 621:
            return 
        elif data["message_type"] == 721:
            raise(data["message_comment"])
        
    def request_chunks(self, request : dict):

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

            #TODO Receive entire message
            response = self.conn.recv(1024)

        data = json.loads(response)
        print(data)

        if data["message_type"] == 631:
            return data["peers"]
        elif data["message_type"] == 731:
            return None

    def update_chunks(self, vid_name, avail_chunks):

        message = {
            "message_code" : 410,
            "message_comment" : "Update Chunks",
            "vid_name" : vid_name,
            "avail_chunks" : avail_chunks
        }

        msg = json.dumps(message)

        self.send_msg_len(msg)
        print(len(msg))
        print(msg)
        self.conn.send(msg.encode("utf-8"))

        response = self.conn.recv(1024)
        data = json.loads(response)

        print(data)

        if data["message_type"] == 641:
            pass
        elif data["message_type"] == 741:
            pass
    
    def send_alive_to_server(self):

        message = {
            "message_code" : 101,
            "message_comment" : "Alive"
        }

        msg = json.dumps(message)

        self.send_msg_len(msg)
        self.conn.send(msg.encode("utf-8"))

        response = self.conn.recv(1024)
        data = json.loads(response)

        print(data)

        if data["message_type"] == 611:
            return None
