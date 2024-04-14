FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY . .

RUN playwright install chromium

RUN playwright install-deps

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=7860"]