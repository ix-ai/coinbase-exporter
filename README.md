# coinbase-exporter

[![Pipeline Status](https://gitlab.com/ix.ai/coinbase-exporter/badges/master/pipeline.svg)](https://gitlab.com/ix.ai/coinbase-exporter/)
[![Docker Stars](https://img.shields.io/docker/stars/ixdotai/coinbase-exporter.svg)](https://hub.docker.com/r/ixdotai/coinbase-exporter/)
[![Docker Pulls](https://img.shields.io/docker/pulls/ixdotai/coinbase-exporter.svg)](https://hub.docker.com/r/ixdotai/coinbase-exporter/)
[![Gitlab Project](https://img.shields.io/badge/GitLab-Project-554488.svg)](https://gitlab.com/ix.ai/coinbase-exporter/)

Prometheus exporter for [Coinbase](https://coinbase.com).

> **Warning** Since Coinbase deprecated their [python library](https://github.com/coinbase/coinbase-python), I can't guarantee the maintainability of this project.

## Usage
```sh
docker run --rm -it -p 9999:9999 \
  -e LOGLEVEL=DEBUG \
  -e API_KEY="your_api_key" \
  -e API_SECRET="your_api_secret" \
  -e FIAT="USD" \
  -e PORT=9999
  --name coinbase-exporter \
  ixdotai/coinbase-exporter:latest
```

## Supported variables
| **Variable**  | **Default** | **Mandatory** | **Description**                                                                                                        |
|:--------------|:-----------:|:-------------:|:-----------------------------------------------------------------------------------------------------------------------|
| `API_KEY`     | -           | **YES**       | set this to your Coinbase API key                                                                                      |
| `API_SECRET`  | -           | **YES**       | set this to your Coinbase API secret                                                                                   |
| `FIAT`        | `EUR`       | NO            | the fiat currency for which to calculate the total transaction amount                                                  |
| `LOGLEVEL`    | `INFO`      | NO            | [Logging Level](https://docs.python.org/3/library/logging.html#levels)                                                 |
| `GELF_HOST`   | -           | NO            | if set, the exporter will also log to this [GELF](https://docs.graylog.org/en/3.0/pages/gelf.html) capable host on UDP |
| `GELF_PORT`   | `12201`     | NO            | Ignored, if `GELF_HOST` is unset. The UDP port for GELF logging                                                        |
| `PORT`        | `9308`      | NO            | The port for prometheus metrics                                                                                        |

## Tags and Arch

Starting with version 0.4.2, the images are multi-arch, with builds for amd64, arm64, armv7 and armv6.
* `vN.N.N` - for example v0.4.1
* `latest` - always pointing to the latest version
* `dev-branch` - the last build on a feature/development branch
* `dev-master` - the last build on the master branch

## Resources:
* GitLab: https://gitlab.com/ix.ai/coinbase-exporter
* GitHub: https://github.com/ix-ai/coinbase-exporter
* Docker Hub: https://hub.docker.com/r/ixdotai/coinbase-exporter

See also [ix.ai/crypto-exporter](https://gitlab.com/ix.ai/crypto-exporter) for more usage examples, including Prometheus configuration
