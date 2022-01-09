FROM ubuntu:bionic

RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg
#RUN python3 -m pip install -U "discord.py[voice]"
RUN python3 -m pip install -U "py-cord[voice]"

COPY TheGoodtheBadandtheUgly.mp3 /TheGoodtheBadandtheUgly.mp3
COPY Bot.py /Bot.py

CMD ["python3","-u","Bot.py"]
