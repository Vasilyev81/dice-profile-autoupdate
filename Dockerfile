FROM python:3.11-slim-bookworm
WORKDIR /app
COPY requirements.txt requirements
RUN pyp3 install -r requirements

COPY . .

CMD ["python3", "main.py", "p"]