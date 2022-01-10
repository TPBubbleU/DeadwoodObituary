FROM ubuntu:bionic

RUN apt update
RUN apt install -y ffmpeg tzdata
RUN apt install -y git software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install -y python3.9 python3-pip python3.9-distutils

RUN python3.9 -m pip install -U pip setuptools
RUN git clone https://github.com/Pycord-Development/pycord
RUN cd pycord
RUN python3.9 -m pip install -U .[voice]
RUN cd ..

COPY TheGoodtheBadandtheUgly.mp3 /TheGoodtheBadandtheUgly.mp3
COPY Bot.py /Bot.py

CMD ["python3.9","-u","Bot.py"]
