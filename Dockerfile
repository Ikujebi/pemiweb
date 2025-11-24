# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Flask will run on port 5000
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
