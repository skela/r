FROM ubuntu:24.10

ENV DEBIAN_FRONTEND="noninteractive"
ENV TZ=Europe/London

RUN apt update --yes
RUN apt install --yes curl wget unzip lcov sed git bash xz-utils sudo python3 python3-pip python3-venv build-essential zip imagemagick inkscape gimp
RUN rm -rf /var/lib/{apt,dpkg,cache,log}

WORKDIR /rod

ADD https://astral.sh/uv/0.4.18/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.cargo/bin/:$PATH"

COPY .python-version .
COPY uv.lock .
COPY pyproject.toml .
RUN uv sync

COPY rplatform/ /rod/rplatform

COPY *.py /rod/

COPY setup.json /rod/

RUN echo '#!/usr/bin/env bash\n/rod/.venv/bin/python3 /rod/rod.py "$@"' >> /rod/rod

RUN chown -R ubuntu: /rod

RUN mkdir /res
RUN chown ubuntu: /res

USER ubuntu

RUN chmod +x /rod/rod

ENV PATH="/rod/:${PATH}"

WORKDIR /res

# ARG USER_ID
# ARG GROUP_ID

# RUN addgroup --gid $GROUP_ID user
# RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user


# USER user
