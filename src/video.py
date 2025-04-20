
class Video: 
    def __init__(self, name, total_chunks):
        self.name = name
        self.total_chunks = total_chunks

        self.data = {}

    def load_chunk(self, chunk_id, data):
        if chunk_id < self.total_chunks:
            self.data[chunk_id] = data
        else:
            print("WARNING: Invalid Chunk ID")
            
    def get_chunk(self, chunk_id):
        if chunk_id < self.total_chunks:
            return self.data[chunk_id]
        else:
            return "Invalid Chunk ID"