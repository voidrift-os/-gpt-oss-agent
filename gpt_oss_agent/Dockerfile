FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gpt_oss_agent.py .

EXPOSE 5000

CMD ["uvicorn", "gpt_oss_agent:app", "--host", "0.0.0.0", "--port", "5000"]
