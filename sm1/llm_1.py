import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

client = Groq(api_key=my_api_key)


selected_model = "openai/gpt-oss-120b"


prompt = "name of hitsugaya toshiro's bankai in bleach?"
messages = [
    {"role": "user", "content": prompt}
]


response = client.chat.completions.create(
    model=selected_model,
    messages=messages
)

print("##################")
answer = response.choices[0].message.content
print(answer)