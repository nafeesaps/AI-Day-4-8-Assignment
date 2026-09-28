from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer


# Paths
DOCS_DIR = Path("docs")
CHROMA_DIR = Path("chroma_db")


# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


# Create Chroma database
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name="company_documents"
)


def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks


# Read documents and create chunks
documents = []
metadatas = []
ids = []

chunk_id = 0

for file_path in DOCS_DIR.glob("*.txt"):
    text = file_path.read_text(encoding="utf-8")

    chunks = chunk_text(text)

    print(f"{file_path.name}: {len(chunks)} chunks")

    for chunk in chunks:
        documents.append(chunk)

        metadatas.append({
            "source": file_path.name
        })

        ids.append(f"chunk_{chunk_id}")

        chunk_id += 1


# Create embeddings
print("\nCreating embeddings...")

embeddings = model.encode(documents).tolist()


# Store documents and embeddings in Chroma
collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)


print("\nIndexing complete.")
print("Total chunks stored:", len(documents))