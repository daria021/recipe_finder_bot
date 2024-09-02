FROM python:3.12

RUN apt-get update && \
    apt-get -y install libzbar0

RUN mkdir /recipes_bot

WORKDIR /recipes_bot

RUN mkdir bills

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY .. .
