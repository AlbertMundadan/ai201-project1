import os
from dotenv import load_dotenv

load_dotenv()

DOCS_PATH = "./documents"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"


EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_COLLECTION = "UConnHousing"
CHROMA_PATH = "./chroma_db"

# Chunking parameters for splitting documents into sections for embedding and retrieval
CHUNK_SIZE = 400        
MAX_CHUNK_SIZE = 800    
CHUNK_OVERLAP = 60   
MIN_CHUNK_LENGTH = 50   

# Retrieval parameters
N_RESULTS = 4

