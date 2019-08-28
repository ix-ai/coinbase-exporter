FROM alpine:latest
LABEL maintainer="docker@ix.ai"

ARG PORT=9308
ARG LOGLEVEL=INFO
ARG FIAT=EUR

RUN apk --no-cache upgrade && \
    apk --no-cache add python3 gcc musl-dev && \
    pip3 install --no-cache-dir prometheus_client pygelf coinbase

ENV LOGLEVEL=${LOGLEVEL} FIAT=${FIAT} PORT=${PORT}

COPY src/coinbase-exporter.py /

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/coinbase-exporter.py"]
