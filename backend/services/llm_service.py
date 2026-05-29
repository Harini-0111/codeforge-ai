import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL_NAME = "meta-llama/llama-3.1-70b-instruct"

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def review_code(code: str) -> str:
    """Send code to the LLM and return a single review string."""
    if not os.getenv("OPENROUTER_API_KEY"):
        raise ValueError("OPENROUTER_API_KEY is not set")

    prompt = (
        "Review the following code.\n\n"
        "Rules:\n"
        "- Only mention real issues present in the code\n"
        "- Avoid generic advice\n"
        "- Keep feedback proportional to snippet size\n"
        "- Do not mention testing, security, or scalability unless directly relevant\n"
        "- Be concise and practical\n\n"
        "Return sections:\n"
        "Issues\n"
        "Improvements\n"
        "Best Practices\n\n"
        f"Code:\n{code}"
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a senior code reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or ""
