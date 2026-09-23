import os
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("API key loaded:", bool(api_key))

# Create Groq client
client = Groq(api_key=api_key)

# Send question to the LLM
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    temperature=1,
    messages=[
        {
            "role": "system",
            "content": (
                "You are an assistant working for the company. "
                "Answer questions briefly and clearly. "
                "If you are unsure about an answer, say 'I don't know'."
            )
        },
        {
            "role": "user",
            "content": "How many days of annual leave are employees entitled to each year?"
        }
    ]
)

# Display answer
print("\nAnswer:")
print(response.choices[0].message.content)

# Display token usage
print("\nToken Usage:")
print("Prompt tokens:", response.usage.prompt_tokens)
print("Completion tokens:", response.usage.completion_tokens)
print("Total tokens:", response.usage.total_tokens)