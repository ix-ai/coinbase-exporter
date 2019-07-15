FROM hub.ix.ai/docker/alpine:latest
LABEL ai.ix.maintainer="docker@ix.ai"
ARG PORT

RUN pip3 install --no-cache-dir coinbase

ENV LOGLEVEL=INFO FIAT=EUR PORT=${PORT}

COPY src/coinbase-exporter.py /

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/coinbase-exporter.py"]
