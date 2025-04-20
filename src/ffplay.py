import subprocess
import time
import shutil
import video


def wait_for_chunk(chunk_dict, chunk_name):
    print(f"[Player] Waiting for {chunk_name}...")
    print(chunk_name not in chunk_dict)
    while chunk_name not in chunk_dict.keys():
        time.sleep(0.5)
    print(f"[Player] {chunk_name} received!")
    return chunk_dict[chunk_name]

def play_all_chunks(TOTAL_CHUNKS, chunk_dict):
    print("[Player] Starting stream-like playback...")

    if not shutil.which('ffplay'):
        print("[Player] ffplay is not installed. Please install it to play video chunks.")
        return

    # Start ffplay process with stdin pipe
    player = subprocess.Popen(
        ["ffplay", "-i", "pipe:0", "-fflags", "nobuffer", "-flags", "low_delay", "-loglevel", "quiet"],
        stdin=subprocess.PIPE
    )
    try:
        # print(TOTAL_CHUNKS)
        for i in range(0, TOTAL_CHUNKS):
            chunk_name = i
            binary_data = wait_for_chunk(chunk_dict, chunk_name)
            player.stdin.write(binary_data)
            time.sleep(0.5)
            print(f"played chunk{i}")
    finally:
        player.stdin.close()
        player.wait()
        print("[Player] All chunks played. Exiting.")

if __name__ == "__main__":
    # video_file = video.VideoChunker("stream.ts", chunk_size = 4096)
    # chunks = video_file.chunkify()
    # TOTAL_CHUNKS = video_file.get_total_chunks()
    # # print(f"[Player] Total chunks: {TOTAL_CHUNKS}")
    # print(f"[Player] Chunks: {chunks.keys()}")


    # play_all_chunks(TOTAL_CHUNKS, video_file.chunks)
    print()