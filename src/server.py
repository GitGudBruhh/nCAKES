import socket
import threading
import os
import json

peers = []

manifest = {
    'v1': {
        'p1': [1, 2, 3, 4, 5]
    },
    'v2': {
        'p1': [1, 2, 4, 5],
        'p2': [1, 2, 3, 4, 5]
    },
    'v3': {
        'p2': [1, 2, 4, 5]
    }
}

def get_peers_info():
    return peers


def get_chunk_info(conn, address, chunk_request):

    chunk_request_dict = json.loads(chunk_request)

    # chunk_request_dict = {
    #     "video": "v1",
    #     "chunk_range_start": 1,
    #     "chunk_range_end": 5
    # }

    vid = chunk_request_dict['video']
    chunk_range_start = chunk_request_dict['chunk_range_start']
    chunk_range_end = chunk_request_dict['chunk_range_end']

    peers_having_chunk = []

    for vid in manifest:
        for peer in vid:
            chunks = manifest[vid][peer]['chunks']
            chunk_peer_has = []

            for chunk in chunks:
                if chunk_range_start <= chunk <= chunk_range_end:
                    chunk_peer_has.append(chunk)

            if len(chunk_peer_has) > 0:
                peers_having_chunk.append((peer, chunk_peer_has))

    return peers_having_chunk


def update_manifest(uploader_info, vid_name):
    uploader_info_dict = json.loads(uploader_info)

    # uploader_info_dict = {
    #     'p1' : {
    #         'chunks' : [4, 5]
    #     },
    #     'p2' : {
    #         'chunks' : [1, 2, 4, 5]
    #     }
    # }

    for peer in uploader_info_dict:

        if peer not in manifest:
            manifest[peer] = {}

        if vid_name not in manifest[peer]:
            manifest[peer][vid_name] = {'chunks': []}

        for chunk in uploader_info_dict[peer]['chunks']:
            if chunk not in manifest[peer][vid_name]['chunks']:
                manifest[peer][vid_name]['chunks'].append(chunk)


def register_new_peer(client, address):
    peers.append((client, address))

def handle_peer(conn, address):
    while True :
        action = conn.recv(1024).decode("utf-8")
        if not action:
            break

        if action == "chunk request" :
            chunk_request = conn.recv(1024).decode("utf-8")
            response = get_chunk_info(conn, address, chunk_request)
            response = json.dumps(response)
            conn.send(f"peers {response}".encode("utf-8"))

        elif action == "upload" :
            vid_name = conn.recv(1024).decode("utf-8")
            response = get_peers_info()
            response = json.dumps(response)
            conn.send(response.encode("utf-8"))
            uploader_info = conn.recv(1024).decode("utf-8")
            update_manifest(uploader_info, vid_name)

        # elif action == "share chunk" :
        #     share_chunk_info = conn.recv(1024).decode("utf-8")
        #     share_chunk(conn, address, share_chunk_info)

        elif action == "exit" :
            break

    return

def start_tracker():
    print("Starting tracker...")
    tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker.bind(('127.0.0.1', 8080))
    tracker.listen(10)
    print("Tracker started...")

    try:
        while True:
            conn, address = tracker.accept()
            print(f"Connection from {address} has been established.")
            client_handler = threading.Thread(target=handle_peer, args=(conn, address))
            register_new_peer(conn, address)
            client_handler.start()
    except KeyboardInterrupt:
        print("Shutting down tracker server...")
    finally:
        tracker.close()
        print("Tracker closed.")

start_tracker()