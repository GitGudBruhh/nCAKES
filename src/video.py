import os

class Video: 
    def __init__(self, name : str, total_chunks : int):
        self.name = name
        self.total_chunks = total_chunks

        self.avail_chunks = set()
        self.data : dict = {}

    def put_chunk(self, chunk_id, data):
        if chunk_id < self.total_chunks:
            self.data[chunk_id] = data
            self.avail_chunks.add(chunk_id)
        else:
            print("WARNING: Invalid Chunk ID")
            
    def get_chunk(self, chunk_id : int):
        if chunk_id in self.avail_chunks:  
            if chunk_id < self.total_chunks:
                return self.data[chunk_id]
            else:
                return "Invalid Chunk ID"
        else:
            # Chunk is not yet available, but it is valid
            return None
    
    def save_video(self, path):

        # Make sure the video is ready to be saved (all chunks available)
        if len(self.avail_chunks) == self.total_chunks:
            
            file_path = os.path.join(path, f"{self.name}.ts") 
            
            with open(file_path, 'wb') as video_file:
                for chunk_id in range(self.total_chunks):
                    if chunk_id in self.avail_chunks:
                        video_file.write(self.data[chunk_id])
            
            print(f"Video '{self.name}' has been saved to {file_path}")

        else:
            print("ERROR: Not all chunks are available. Unable to save video.")

    def load_video(self, path, chunk_size):
        
        if not os.path.exists(path):
            print(f"ERROR: File '{path}' not found.")
            return

        with open(path, 'rb') as video_file:
            chunk_id = 0
            while True:
                chunk_data = video_file.read(chunk_size)
                if not chunk_data:
                    break
                self.data[chunk_id] = chunk_data
                self.avail_chunks.add(chunk_id)
                chunk_id += 1

        self.total_chunks = chunk_id
        print(f"Video '{self.name}' loaded from {path} with {chunk_id} chunks.")
