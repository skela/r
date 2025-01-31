FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

ENV LIBRARY_PATH=/lib:/usr/lib
ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=uv.lock,target=uv.lock \
	--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
	uv sync --frozen --no-install-project --no-dev

RUN uv venv --relocatable

ADD pyproject.toml /app
ADD uv.lock /app
ADD .python-version /app

RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --frozen --no-dev

FROM ubuntu:24.10

COPY --from=builder --chown=ubuntup:ubuntu /app /app
COPY --chown=ubuntu:ubuntu --from=builder /app/.venv /app/.venv
COPY --chown=ubuntu:ubuntu --from=builder /opt/uv/python /opt/uv/python

ENV PATH="/app/.venv/bin:$PATH"

ENV DEBIAN_FRONTEND="noninteractive"
ENV TZ=Europe/London

RUN apt update --yes
RUN apt install --yes curl wget unzip lcov sed git bash xz-utils sudo build-essential zip imagemagick inkscape gimp
RUN rm -rf /var/lib/{apt,dpkg,cache,log}

COPY rplatform/ /app/rplatform
COPY *.py /app/
COPY setup.json /app/

RUN chown -R ubuntu: /app
RUN mkdir /res
RUN chown ubuntu: /res
RUN chmod +x /app/rod.py
RUN mv /app/rod.py /app/rod
RUN ln -s /app/rod /usr/local/bin/rod

USER ubuntu

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /res

