FROM ghcr.io/astral-sh/uv:python3.13-trixie

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 \
    PATH="/app/.venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN uv sync --frozen --group dev

CMD ["/bin/bash"]
