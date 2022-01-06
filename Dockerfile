FROM ubuntu:bionic

RUN apt-get update && apt-get install -y python3.7 python3-pip
RUN python3.7 -m pip install discord

COPY Bot.py /Bot.py

CMD python3.7 Bot.py
