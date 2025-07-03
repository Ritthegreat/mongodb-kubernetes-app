FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY app.py .

RUN pip install flask pymongo

EXPOSE 5000

CMD ["python", "app.py"] 