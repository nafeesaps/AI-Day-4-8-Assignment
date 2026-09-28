import os
import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Groq client
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Embedding model
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Chroma
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_collection(name="company_documents")


def search_documents(question, n_results=3):
    """Retrieve the top 3 relevant document chunks."""

    query_embedding = model.encode([question]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results["documents"][0], results["metadatas"][0]


def answer_without_retrieval(question):
    """Ask the LLM directly without company documents."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant working for the company. "
                    "Answer briefly and clearly. "
                    "If you are unsure, say 'I don't know'."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response.choices[0].message.content


def answer_with_retrieval(question):
    """Retrieve documents and answer using only the retrieved context."""

    documents, metadatas = search_documents(question, n_results=3)

    context_parts = []

    for i in range(len(documents)):
        source = metadatas[i]["source"]

        context_parts.append(
            f"Source file: {source}\n"
            f"Content:\n{documents[i]}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
Answer the user's question using ONLY the context below.

Rules:
1. Answer only from the provided context.
2. Do not use outside knowledge.
3. Do not invent information.
4. Name the file used for the answer.
5. If the answer is not present in the context, say:
   "I don't know based on the available company documents."
6. If the user asks for private, confidential, or unrelated information that is not provided in the context, do not reveal or invent anything. Clearly refuse the request.

Context:
{context}

User question:
{question}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a company document assistant. "
                    "Use only the provided context."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    # Get unique source filenames
    sources = []

    for metadata in metadatas:
        source = metadata["source"]

        if source not in sources:
            sources.append(source)

    return answer, sources


if __name__ == "__main__":
    question = input("Enter your question: ")

    answer, sources = answer_with_retrieval(question)

    print("\nAnswer:")
    print(answer)

    print("\nFiles cited/retrieved:")
    for source in sources:
        print("-", source)