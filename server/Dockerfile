# @see: https://docs.astral.sh/uv/guides/integration/docker/
# @see: https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile

# Build the application in /app directory
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Use a final image without uv
FROM python:3.13-slim-bookworm

# Install Tippecanoe build dependencies
RUN apt-get update && \
    apt-get -y install gcc g++ make libsqlite3-dev zlib1g-dev git gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Build Tippecanoe from source
WORKDIR /tmp
RUN git clone https://github.com/felt/tippecanoe.git && \
    cd tippecanoe && \
    make && \
    make install && \
    cp tippecanoe /usr/local/bin/ && \
    rm -rf /tmp/tippecanoe

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
