# coinbase-exporter
Prometheus exporter for [Coinbase](https://coinbase.com).

## Usage
```
docker run --rm -it -p 9308:9308 \
  -e LOGLEVEL=DEBUG \
  -e API_KEY="your_api_key" \
  -e API_SECRET="your_api_secret" \
  -e FIAT="USD" \
  --name coinbase-exporter \
  hub.ix.ai/docker/coinbase-exporter:latest
```

## Supported variables
* `API_KEY` (no default) - set this to your Coinbase API key
* `API_SECRET` (no default) - set this to your Coinbase API secret
* `FIAT` (default: `EUR`) - the fiat currency for which to calculate the total transaction amount
* `LOGLEVEL` (defaults to `INFO`)
