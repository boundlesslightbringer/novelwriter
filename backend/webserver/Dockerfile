# stage 1: don't need build-essential at runtime
FROM python:3.12-slim-bookworm AS build

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/* 

COPY pyproject.toml .

RUN pip install --no-cache-dir --user .  

# stage 2: copy over the installed dependencies from the build stage
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=build /root/.local /root/.local

ENV PATH="/root/.local/bin:$PATH"

COPY . .

EXPOSE 7000

CMD ["fastapi", "run", "main.py", "--proxy-headers", "--port", "7000", "--host", "0.0.0.0"]
