import socket
import json
import time

class Client:

    def __init__(self):
        self.server_ip = "127.0.0.1"
        self.server_port = 8080
        self.server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_conn.connect((self.server_ip, self.server_port))

        self.avail_chunks = {}
        

    def register_with_server(self):

        message = {
            "message_code" : 210,
            "message_comment" : "Register"
        }

        msg = json.dumps(message)

        self.server_conn.send(msg.encode("utf-8"))

        response = self.server_conn.recv(1024)
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

        self.server_conn.send(msg.encode("utf-8"))

        #TODO Receive entire message
        response = self.server_conn.recv(1024)
        data = json.loads(response)

        print(data)

        if data["message_type"] == 631:
            return data["peers"]
        elif data["message_type"] == 731:
            return None

    def update_chunks(self, vid_name):

        message = {
            "message_code" : 410,
            "message_comment" : "Update Chunks",
            "vid_name" : vid_name,
            "uploader_info" : None
        }

        msg = json.dumps(message)

        self.server_conn.send(msg.encode("utf-8"))

        #TODO Receive entire message
        response = self.server_conn.recv(1024)
        data = json.loads(response)

        print(data)

        if data["message_type"] == 641:
            pass
        elif data["message_type"] == 741:
            pass
    
    def respond_to_heartbeat(self):

        message = {
            "message_code" : 101,
            "message_comment" : "Alive"
        }

        msg = json.dumps(message)

        self.server_conn.send(msg.encode("utf-8"))

if __name__ == "__main__":
    client = Client()
    client.register_with_server()

    request = {
        "video" : "v2",
        "chunk_range_start" : 2,
        "chunk_range_end" : 4
    }

    print(client.request_chunks(request))

    client.avail_chunks["amogh.mp4"] = [0, 1, 2, 3, 4, 5, 6, 7]


    
    client.server_conn.close()
