FROM ubuntu:bionic

RUN apt-get update 
RUN apt-get install -y ffmpeg tzdata
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get install -y python3.10 python3-pip 
#RUN python3.10 -m pip install -U "discord.py[voice]"
RUN python3.10 -m pip install -U setuptools
RUN python3.10 -m pip install -U "py-cord[voice]"

COPY TheGoodtheBadandtheUgly.mp3 /TheGoodtheBadandtheUgly.mp3
COPY Bot.py /Bot.py

CMD ["python3.10","-u","Bot.py"]
