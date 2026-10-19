import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def route_question(question: str) -> str:
    """
    Classifies the user's question into one of three routes:
    - 'ticket': If the user wants to create a support ticket.
    - 'order': If the user is asking about an order status.
    - 'rag': For general company document / policy questions or security attacks.
    """
    question_lower = question.lower()
    
    # Pre-emptively route potential prompt injections or security attacks to rag
    attack_keywords = ["ignore", "disregard", "dan", "override", "secret", "credentials", "password=", ".env"]
    if any(keyword in question_lower for keyword in attack_keywords):
        return "rag"

    prompt = f"""
Classify the following user question into exactly one of these three categories:
1. "ticket" (if the user wants to submit, create, or log a support ticket or issue)
2. "order" (if the user asks about the status or tracking of an order number)
3. "rag" (for general company policy, HR, benefits, IT security, or other document queries)

Return ONLY the category name ("ticket", "order", or "rag") with no extra text.

User question: {question}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a precise intent classifier. Output only the category name."},
            {"role": "user", "content": prompt}
        ]
    )

    intent = response.choices[0].message.content.strip().lower()
    
    # Fallback to rag if classification is unclear
    if intent not in ["ticket", "order", "rag"]:
        return "rag"
        
    return intent