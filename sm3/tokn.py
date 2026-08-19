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
prompt1 = "hello"
prompt2 = "explain newton's laws of motion in simple terms"
prompt3 = "describe gojo satoru's cursed technique in jujutsu kaisen"   

for prompt in [prompt1, prompt2, prompt3]:
    messages = [
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model=selected_model,
        messages=messages,
        max_tokens=300
    )
    usage = response.usage
    print(f"Prompt: {prompt}")
    print(
        f"Tokens used: {usage.prompt_tokens}, "
        f"completion tokens: {usage.completion_tokens}, "
        f"total tokens: {usage.total_tokens}, "
        f"finish reason: {response.choices[0].finish_reason}"
    )
#     print("##################")
#     answer = response.choices[0].message.content
#     print(answer)


