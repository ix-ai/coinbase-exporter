# coinbase-exporter
Prometheus exporter for [Coinbase](https://coinbase.com).

## Usage
```
docker run --rm -it -p 9999:9999 \
  -e LOGLEVEL=DEBUG \
  -e API_KEY="your_api_key" \
  -e API_SECRET="your_api_secret" \
  -e FIAT="USD" \
  -e PORT=9999
  --name coinbase-exporter \
  registry.gitlab.com/ix.ai/coinbase-exporter:latest
```

## Supported variables
* `API_KEY` (no default - **mandatory**) - set this to your Coinbase API key
* `API_SECRET` (no default - **mandatory**) - set this to your Coinbase API secret
* `FIAT` (default: `EUR`) - the fiat currency for which to calculate the total transaction amount
* `GELF_HOST` (no default) - if set, the exporter will also log to this [GELF](https://docs.graylog.org/en/3.0/pages/gelf.html) capable host on UDP
* `GELF_PORT` (defaults to `12201`) - the port to use for GELF logging
* `PORT` (defaults to `9308`) - the listen port for the exporter
* `LOGLEVEL` (defaults to `INFO`)
