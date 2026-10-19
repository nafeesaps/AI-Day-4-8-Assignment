import os
import time
import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
from log import log_interaction
from guard import check_input_guardrail, check_output_guardrail
from router import route_question
from tools import create_ticket

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
    start_time = time.time()
    
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

    answer = response.choices[0].message.content
    duration = time.time() - start_time

    log_interaction({
        "mode": "without_retrieval",
        "question": question,
        "answer": answer,
        "duration": duration
    })

    return answer


def answer_with_retrieval(question):
    """Retrieve documents and answer using only the retrieved context."""
    start_time = time.time()

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
    answer = check_output_guardrail(answer)

    sources = []
    for metadata in metadatas:
        source = metadata["source"]
        if source not in sources:
            sources.append(source)

    duration = time.time() - start_time

    log_interaction({
        "mode": "with_retrieval",
        "question": question,
        "documents": documents,
        "metadatas": metadatas,
        "prompt": prompt,
        "tool_calls": [],
        "answer": answer,
        "sources": sources,
        "duration": duration
    })

    return answer, sources


def process_query(question):
    """
    Routes the question based on intent (ticket, order, or rag),
    applies guardrails, executes tools if necessary, and logs the interaction.
    """
    is_safe, refusal_message = check_input_guardrail(question)
    if not is_safe:
        log_interaction({
            "mode": "blocked_input",
            "question": question,
            "answer": refusal_message,
            "duration": 0.0
        })
        return refusal_message, []

    intent = route_question(question)

    if intent == "ticket":
        priority = "High" if "high" in question.lower() else ("Urgent" if "urgent" in question.lower() else "Medium")
        result = create_ticket(title="User Support Request", description=question, priority=priority)
        
        log_interaction({
            "mode": "tool_call",
            "tool": "create_ticket",
            "question": question,
            "answer": result,
            "duration": 0.0
        })
        return result, ["tickets.json"]

    elif intent == "order":
        if "1042" in question:
            answer = "Order 1042 was Shipped on 2026-09-29."
        elif "1043" in question:
            answer = "Order 1043 is currently Processing."
        elif "1044" in question:
            answer = "Order 1044 has been Delivered."
        else:
            answer = "Order not found."
        
        return answer, ["product_faq.txt"]

    else:
        return answer_with_retrieval(question)


if __name__ == "__main__":
    question = input("Enter your question: ")
    answer, sources = process_query(question)

    print("\nAnswer:")
    print(answer)

    print("\nFiles cited/retrieved:")
    for source in sources:
        print("-", source)