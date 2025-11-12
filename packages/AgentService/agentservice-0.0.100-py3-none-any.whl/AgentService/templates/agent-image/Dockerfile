FROM python:3.11-slim

WORKDIR /app

RUN pip install AgentService==0.0.99

COPY . .

CMD ["python", "manage.py", "start"]