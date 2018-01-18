FROM ubuntu:12.04
FROM python:2.7

COPY /. /.

RUN pip install -r requirements.txt

RUN \
  apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10 && \
  apt-get update && \
  apt-get install emacs24 -y && \
  apt-get install lsof -y

EXPOSE 8000
