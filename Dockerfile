FROM hub.ix.ai/docker/alpine:latest
LABEL ai.ix.maintainer="docker@ix.ai"

RUN pip3 install coinbase

ENV LOGLEVEL=INFO

COPY coinbase-exporter.py /

EXPOSE 9308

ENTRYPOINT ["python3", "/coinbase-exporter.py"]
