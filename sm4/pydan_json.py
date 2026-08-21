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

# structured prompt for the model
from pydantic import BaseModel
class ticket(BaseModel):
    name: str
    special_ability: str
    special_attack: str
 
schema = ticket.model_json_schema()

response_format={
    "type": "json_object",
}
system_prompt = f""" extract the following information from the user prompt and return it in a json format that matches the following schema: {schema}"""

message_system = {"role": "system", 
                  "content": system_prompt}

text = "my name is uzumaki naruto, my special ability is shadow clone jutsu, and my special attack is rasengan, i was trained by jiraiya and kakashi, i am a ninja from konoha, i have a pet frog named gamabunta, and my favorite food is ramen"

prompt = f""" this is a warpower detail, extraxt information from this.
 {text} """

message_user = {"role": "user", 
                "content": prompt}
messages = [
    message_system,
    message_user
]


response = client.chat.completions.create(
    model=selected_model,
    messages=messages,
    response_format=response_format 
)

print("##################")
answer = response.choices[0].message.content
print(answer)


import json
raw_json = answer
data = json.loads(raw_json)
Ticket = ticket(**data)

print(Ticket.name)
print(Ticket.special_ability)
print(Ticket.special_attack)