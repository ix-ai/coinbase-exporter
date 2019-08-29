FROM alpine:latest
LABEL maintainer="docker@ix.ai"

ARG PORT=9308
ARG LOGLEVEL=INFO
ARG FIAT=EUR

WORKDIR /app

COPY src/ /app

RUN apk --no-cache upgrade && \
    apk --no-cache add python3 gcc musl-dev && \
    pip3 install --no-cache-dir -r requirements.txt

ENV LOGLEVEL=${LOGLEVEL} FIAT=${FIAT} PORT=${PORT}

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/app/coinbase-exporter.py"]
