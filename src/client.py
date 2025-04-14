import socket
import json
import time

class Client:

    def __init__(self):
        self.server_ip = "127.0.0.1"
        self.server_port = 8080
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.server_ip, self.server_port))
        

    def register_with_server(self):

        message = {
            "message_code" : 210,
            "message_comment" : "Register"
        }

        msg = json.dumps(message)

        self.conn.send(msg.encode("utf-8"))

        response = self.conn.recv(1024)
        data = json.loads(response)

        print(data)

        if data["message_type"] == 621:
            return 
        elif data["message_type"] == 721:
            raise(data["message_comment"])
        
    def request_chunks(self, chunks : dict):

        req_chunks = json.dumps(chunks)

        message = {
            "message_code" : 310,
            "message_comment" : "Request Chunk",
            "chunk_request" : req_chunks
        }

        msg = json.dumps(message)

        self.conn.send(msg.encode("utf-8"))

        #TODO Receive entire message
        response = self.conn.recv(1024)
        data = json.loads(response)

        print(data)

        if data["message_type"] == 631:
            return data["peers"]
        elif data["message_type"] == 731:
            return None

if __name__ == "__main__":
    client = Client()
    client.register_with_server()

    request = {
        "video" : "v2",
        "chunk_range_start" : 2,
        "chunk_range_end" : 4
    }

    print(client.request_chunks(request))

    client.conn.close()
