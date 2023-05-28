FROM python:3.11

RUN apt-get update && apt-get install -y netcat

WORKDIR /src

COPY ./requirements.txt .

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

ADD ./scripts /scripts/

RUN chmod +x /scripts/entrypoint.sh

EXPOSE 8000
