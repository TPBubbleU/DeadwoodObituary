
FROM ubuntu:bionic

COPY bot.py /bot.py
COPY quotes.json /quotes.json

RUN apt-get update && apt-get install -y python3.7 python3-pip
RUN python3.7 -m pip install discord
CMD python3.7 bot.py
