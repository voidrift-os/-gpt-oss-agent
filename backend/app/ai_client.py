import os
import httpx
import logging

GPT_AGENT_URL = os.getenv("GPT_AGENT_URL", "http://gpt-oss-agent:5000/generate")
logging.basicConfig(level=logging.INFO)

async def generate_text(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                GPT_AGENT_URL,
                json={"prompt": prompt},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("text", "")
        except Exception as e:
            logging.error(f"Error calling GPT OSS agent: {e}")
            raise
