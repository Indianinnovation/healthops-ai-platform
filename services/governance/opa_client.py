import httpx
import os

OPA_BASE_URL = os.getenv("OPA_URL", "http://localhost:8181")


async def evaluate_policy(package: str, input_data: dict) -> dict:
    """Evaluate an OPA policy and return the decision."""
    url = f"{OPA_BASE_URL}/v1/data/{package.replace('.', '/')}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"input": input_data}, timeout=5)
        return response.json().get("result", {})
