import os

# Absolute path to the folder holding the source documents
DOCS_PATH = "./documents"

# Chunking parameters for splitting documents into sections for embedding and retrieval
CHUNK_SIZE = 400        
MAX_CHUNK_SIZE = 800    
CHUNK_OVERLAP = 60   
MIN_CHUNK_LENGTH = 50   
