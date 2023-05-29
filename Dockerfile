FROM python:3.11

RUN apt-get update && apt-get install -y netcat

WORKDIR /url-short

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

RUN chmod +x scripts/entrypoint.sh
