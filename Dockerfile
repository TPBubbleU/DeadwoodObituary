FROM ubuntu:bionic

RUN apt-get update 
RUN apt-get install -y ffmpeg tzdata
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get install -y python3.9 python3-pip python3.9-distutils
#RUN python3.10 -m pip install -U "discord.py[voice]"
RUN python3.9 -m pip install -U "py-cord[voice]"

COPY TheGoodtheBadandtheUgly.mp3 /TheGoodtheBadandtheUgly.mp3
COPY Bot.py /Bot.py

CMD ["python3.9","-u","Bot.py"]
