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


prompt = "suggest me a name for my website which runs on the theme of waste management?"

message_system = [
    {"role": "system", "content": "You are a genius name rater."}
]
messages = [
    {"role": "user", "content": prompt}
]

#temperature can be added to the request to control the randomness of the output. A higher temperature will result in more random responses, while a lower temperature will result in more deterministic responses.
response = client.chat.completions.create(
    model=selected_model,
    messages=message_system + messages,
    temperature=0.8,
)

print("##################")
answer = response.choices[0].message.content
print(answer)