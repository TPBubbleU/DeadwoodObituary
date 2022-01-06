FROM ubuntu:bionic

RUN apt-get update && apt-get install -y python3.7 python3-pip
RUN apt-get install ffmpeg
RUN python3 -m pip install -U "discord.py[voice]"

COPY TheGoodtheBadandtheUgly.mp3 /TheGoodtheBadandtheUgly.mp3
COPY Bot.py /Bot.py

CMD ["python3","-u","Bot.py"]
