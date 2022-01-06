FROM ubuntu:bionic

RUN apt-get update && apt-get install -y python3.7 python3-pip
RUN python3.7 -m pip install -U "discord.py[voice]"

COPY "The Good the Bad and the Ugly.mp3" /"The Good the Bad and the Ugly.mp3"
COPY Bot.py /Bot.py

CMD python3.7 Bot.py
