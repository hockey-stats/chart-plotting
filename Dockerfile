FROM ubuntu:24.04

RUN apt update && apt install -y python3 python3-pip

WORKDIR /home
COPY ./ .


ENV PYTHONPATH='/home'
RUN pip3 install -r requirements.txt --break-system-packages

CMD ["panel", "serve", "dashboard/fantasy_fa.py", "--port=80", "--address=0.0.0.0", "--allow-websocket-origin=*"]