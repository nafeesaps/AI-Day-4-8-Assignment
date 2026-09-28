import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = "chroma_db"

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_collection(
    name="company_documents"
)


def search_documents(question, expected_source, n_results=3):
    # Convert question into an embedding
    query_embedding = model.encode([question]).tolist()[0]

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    print("\n" + "=" * 70)
    print("Question:", question)
    print("Expected source:", expected_source)
    print("=" * 70)

    # Print top 3 results
    for i in range(len(results["documents"][0])):
        source = results["metadatas"][0][i]["source"]
        distance = results["distances"][0][i]
        document = results["documents"][0][i]

        print(f"\nResult {i + 1}")
        print("Distance:", distance)
        print("Source:", source)
        print("Content:", document)
        print("-" * 60)

    # Check whether the correct document came first
    first_source = results["metadatas"][0][0]["source"]

    if first_source == expected_source:
        print("Correct document first: YES")
    else:
        print("Correct document first: NO")


# Five test questions
questions = [
    (
        "How many annual leave days are employees entitled to each year?",
        "leave_policy.txt"
    ),
    (
        "How long is the standard refund period after purchasing a product?",
        "refund_policy.txt"
    ),
    (
        "What should employees do if they receive a suspicious email?",
        "it_password_policy.txt"
    ),
    (
        "What are the company's standard working hours?",
        "working_hours_holidays.txt"
    ),
    (
        "How can customers check the status of their order?",
        "product_faq.txt"
    )
]


# Run all five tests
for question, expected_source in questions:
    search_documents(question, expected_source)