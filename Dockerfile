FROM python:3.14-slim-bookworm

WORKDIR Petit_RAG

COPY src .
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
