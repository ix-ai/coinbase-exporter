FROM alpine:latest
LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/coinbase-exporter"

WORKDIR /app

COPY src/ /app

RUN apk --no-cache upgrade && \
    apk add --no-cache python3 gcc musl-dev && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del --no-cache --purge gcc musl-dev

EXPOSE 9308

ENTRYPOINT ["python3", "/app/coinbase-exporter.py"]
