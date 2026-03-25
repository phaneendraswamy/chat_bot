import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)
load_dotenv(".env.local", override=True)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello in one sentence"}],
)

print(response.choices[0].message.content)
