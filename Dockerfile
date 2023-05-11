FROM node:14
RUN apt-get update
RUN apt-get install -y libnotify-bin
RUN mkdir /src
VOLUME /src
WORKDIR /src
