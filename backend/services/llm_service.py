import json
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


def review_project_map(project_map: dict) -> str:
    """Send a project map to the LLM and return a review string."""
    if not os.getenv("OPENROUTER_API_KEY"):
        raise ValueError("OPENROUTER_API_KEY is not set")

    payload = json.dumps(project_map, ensure_ascii=True, indent=2)
    prompt = (
        "You are a senior software architect reviewing a project map.\n\n"
        "Hard constraints (must follow):\n"
        "- Every statement must be backed by explicit Project Map evidence.\n"
        "- Do not infer facts not present in the map.\n"
        "- Do not estimate developer skill, team size, project maturity, or business goals.\n"
        "- Do not recommend technologies or practices not present in the map.\n"
        "- Do not describe architecture patterns (e.g., microservices) unless explicitly supported.\n"
        "- If information is missing, say: 'Not enough information available from the project map.'\n\n"
        "Output format (strict JSON only, no markdown):\n"
        "{\n"
        "  \"overview\": [\n"
        "    {\"statement\": \"...\", \"evidence\": [\"field=value\", ...]}\n"
        "  ],\n"
        "  \"architecture_notes\": [\n"
        "    {\"statement\": \"...\", \"evidence\": [\"field=value\", ...]}\n"
        "  ],\n"
        "  \"risks\": [\n"
        "    {\"statement\": \"...\", \"evidence\": [\"field=value\", ...]}\n"
        "  ],\n"
        "  \"opportunities\": [\n"
        "    {\"statement\": \"...\", \"evidence\": [\"field=value\", ...]}\n"
        "  ]\n"
        "}\n\n"
        "Evidence rules:\n"
        "- Evidence must cite exact fields from the map: frameworks, languages, entry_points, "
        "important_files, file_counts, directory_summary, database_signals, package_managers.\n"
        "- If a statement cannot be supported, replace it with the missing-info sentence.\n\n"
        "Return JSON only. Do not wrap in markdown or code fences.\n\n"
        f"Project Map:\n{payload}"
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a senior software architect."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    content = response.choices[0].message.content or ""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        fallback = {
            "overview": [
                {
                    "statement": "Not enough information available from the project map.",
                    "evidence": [],
                }
            ],
            "architecture_notes": [],
            "risks": [],
            "opportunities": [],
            "meta": {
                "warning": "LLM output was not valid JSON; returned fallback response.",
            },
        }
        return json.dumps(fallback, ensure_ascii=True, indent=2)

    return json.dumps(parsed, ensure_ascii=True, indent=2)
