FROM ubuntu:21.04

ENV DEBIAN_FRONTEND="noninteractive"
ENV TZ=Europe/London
RUN apt update --yes
RUN apt install --yes curl wget unzip lcov sed git bash xz-utils sudo python3 python3-pip build-essential zip imagemagick inkscape gimp
RUN rm -rf /var/lib/{apt,dpkg,cache,log}

WORKDIR /rod
COPY Pipfile .

RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python3 -m pip install -r Pipfile 

RUN mkdir res

COPY rplatform/ /rod/rplatform

COPY *.py /rod/

RUN echo "python3 /rod/rod.py" >> /rod/rod

RUN chmod +x /rod/rod

ENV PATH="/rod/:${PATH}"

WORKDIR /res

RUN rod -h
