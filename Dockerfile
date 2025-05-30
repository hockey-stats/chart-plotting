FROM ubuntu:24.04

RUN apt update && apt install -y python3 python3-pip git vim

WORKDIR /home
COPY ./ .

RUN git clone https://github.com/hockey-stats/tweet-posting.git

ENV PYTHONPATH='/home'
RUN pip3 install -r requirements.txt --break-system-packages
RUN pip3 install -r tweet-posting/requirements.txt --break-system-packages
