import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)
DEPLOYMENT = os.getenv("OPENAI_DEPLOYMENT", "gpt-4o-mini")

def suggest_test_steps(requirement_text: str) -> str:
    prompt = f"""
    You are a senior QA automation engineer.
    Given this requirement, propose concise, executable UI+API test steps (ordered list):
    {requirement_text}
    """
    r = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return r.choices[0].message.content
