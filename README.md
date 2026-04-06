# OpenClaw Infra

Infrastructure and deployment files for a safe OpenClaw VPS setup.

## What is here

- `docs/`: provider choice and setup runbooks
- `ops/openclaw/`: Docker Compose and Caddy deployment scaffold

## Current target

- provider: DigitalOcean
- OS: Ubuntu 24.04 LTS
- size: 8 GB RAM / 4 vCPU / 160 GB SSD
- reverse proxy: Caddy
- runtime: Docker Compose

## Important

Do not commit real secrets, session cookies, or production `.env` files.
