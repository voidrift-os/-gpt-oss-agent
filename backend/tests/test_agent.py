import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_agent_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/agent/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}



@pytest.mark.asyncio
async def test_gpt_oss_agent(monkeypatch):
    async def mock_generate_text(prompt: str) -> str:
        return f"Echo: {prompt}"

    from app.api.api_v1.endpoints import agent
    monkeypatch.setattr(agent, "generate_text", mock_generate_text)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Normal prompt
        resp = await ac.post("/api/v1/agent/gpt-oss", json={"prompt": "hello"})
        assert resp.status_code == 200
        assert resp.json() == {"text": "Echo: hello"}

        # Empty prompt
        resp = await ac.post("/api/v1/agent/gpt-oss", json={"prompt": ""})
        assert resp.status_code == 200
        assert resp.json() == {"text": "Echo: "}

        # Prompt too long (should fail)
        long_prompt = "a" * 2048
        resp = await ac.post("/api/v1/agent/gpt-oss", json={"prompt": long_prompt})
        assert resp.status_code == 400
        assert "Prompt too long" in resp.json()["detail"]

        # X-Forwarded-For header (should use header IP for rate limiting)
        for _ in range(5):
            resp = await ac.post(
                "/api/v1/agent/gpt-oss",
                json={"prompt": "test"},
                headers={"X-Forwarded-For": "203.0.113.1"}
            )
            assert resp.status_code == 200
        # 6th request should be rate limited
        resp = await ac.post(
            "/api/v1/agent/gpt-oss",
            json={"prompt": "test"},
            headers={"X-Forwarded-For": "203.0.113.1"}
        )
        assert resp.status_code == 429
        assert "Rate limit exceeded" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_gpt_oss_agent_error(monkeypatch):
    async def mock_generate_text(prompt: str) -> str:
        raise Exception("Agent error!")

    from app.api.api_v1.endpoints import agent
    monkeypatch.setattr(agent, "generate_text", mock_generate_text)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/agent/gpt-oss", json={"prompt": "fail"})
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Internal Server Error"
