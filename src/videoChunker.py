class VideoChunker:
    def __init__(self, file_path, chunk_size=1024 * 1024):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.chunks = {}
        self.total_chunks = 0

    def chunkify(self):
        with open(self.file_path, 'rb') as f:
            chunk_id = 0
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                self.chunks[str(chunk_id)] =  chunk
                chunk_id += 1
        
        self.total_chunks = len(self.chunks)
        print(f"[Chunker] Split into {self.total_chunks} chunks.")
        return self.chunks

    def get_total_chunks(self):
        return self.total_chunks
