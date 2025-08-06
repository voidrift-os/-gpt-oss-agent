import os
import random
import asyncio
import logging
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from app.ai_client import generate_text
from app.core.rate_limiter import RateLimiter

logger = logging.getLogger("agent")
router = APIRouter()

MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", 1024))
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))
RATE_PERIOD = int(os.getenv("RATE_PERIOD", 60))  # seconds
rate_limiter = RateLimiter("gpt-oss-agent", RATE_LIMIT, RATE_PERIOD)

class AgentRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    text: str

def get_client_ip(request: Request) -> str:
    # Respect X-Forwarded-For header if behind proxies/load balancers
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # Can be a comma separated list, take the first IP
        ip = x_forwarded_for.split(",")[0].strip()
        logger.debug(f"Using X-Forwarded-For IP: {ip}")
        return ip
    return request.client.host

@router.post("/agent/gpt-oss", response_model=AgentResponse)
async def gpt_oss_agent_endpoint(
    request: Request,
    body: AgentRequest
):
    if len(body.prompt) > MAX_PROMPT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prompt too long (max {MAX_PROMPT_LENGTH} characters)"
        )

    identifier = get_client_ip(request)
    allowed = await rate_limiter.allow_request(identifier)
    if not allowed:
        logger.warning(f"Rate limit exceeded for IP: {identifier}")
        # Add random jitter delay 100-300ms before responding
        await asyncio.sleep(random.uniform(0.1, 0.3))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {RATE_LIMIT} requests per {RATE_PERIOD} seconds"
        )

    try:
        text = await generate_text(body.prompt)
        return {"text": text}
    except Exception as e:
        logger.error(f"Error generating text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/agent/health")
async def agent_health():
    return {"status": "ok"}
