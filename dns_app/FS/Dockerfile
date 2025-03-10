FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install requests

COPY FS.py .
COPY test_register.py .

EXPOSE 9090

CMD ["python", "FS.py"] 