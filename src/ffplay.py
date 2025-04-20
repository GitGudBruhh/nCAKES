import subprocess
import time
import shutil

from video import Video


def wait_for_chunk(chunk_dict, chunk_name):

    while chunk_name not in chunk_dict.keys():
        print(f"[Player] Waiting for {chunk_name}...")
        time.sleep(0.5)
    print(f"[Player] {chunk_name} received!")
    return chunk_dict[chunk_name]

def play_all_chunks(TOTAL_CHUNKS, chunk_dict):
    print("[PLAYER] Starting to play video...")

    if not shutil.which('ffplay'):
        print("[PLAYER] ffplay is not installed. Please install it to play video chunks.")
        return

    # Start ffplay process with stdin pipe
    player = subprocess.Popen(
        ["ffplay", "-i", "pipe:0", "-fflags", "nobuffer", "-flags", "low_delay", "-loglevel", "quiet"],
        stdin=subprocess.PIPE
    )
    try:
        for i in range(0, TOTAL_CHUNKS):
            chunk_name = i
            binary_data = wait_for_chunk(chunk_dict, chunk_name)
            player.stdin.write(binary_data)
            print(f"[PLAYER] played chunk {i}")

    finally:
        player.stdin.close()
        print("test")
        player.wait()
        print("[PLAYER] All chunks played. Exiting.")


# if __name__ == "__main__":
#     video_file = video.VideoChunker("stream.ts", chunk_size = 4096)
#     chunks = video_file.chunkify()
#     TOTAL_CHUNKS = video_file.get_total_chunks()
#     # print(f"[Player] Total chunks: {TOTAL_CHUNKS}")
#     print(f"[Player] Chunks: {chunks.keys()}")


#     play_all_chunks(TOTAL_CHUNKS, video_file.chunks)
#     print()