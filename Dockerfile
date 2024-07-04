FROM ubuntu:23.04

ENV DEBIAN_FRONTEND="noninteractive"
ENV TZ=Europe/London
RUN apt update --yes
RUN apt install --yes curl wget unzip lcov sed git bash xz-utils sudo python3 python3-pip python3-venv build-essential zip imagemagick inkscape gimp
RUN rm -rf /var/lib/{apt,dpkg,cache,log}

WORKDIR /rod
COPY Pipfile .

RUN python3 -m pip install -r Pipfile --break-system-packages

RUN mkdir res

COPY rplatform/ /rod/rplatform

COPY *.py /rod/

COPY setup.json /rod/

RUN echo "python3 /rod/rod.py" >> /rod/rod

RUN chmod +x /rod/rod

ENV PATH="/rod/:${PATH}"

WORKDIR /res

RUN rod -h
