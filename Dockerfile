FROM ubuntu:24.04

RUN apt update && apt install -y python3 python3-pip ffmpeg

WORKDIR /home
COPY ./ .


ENV PYTHONPATH='/home'
RUN pip3 install -r requirements.txt --break-system-packages
