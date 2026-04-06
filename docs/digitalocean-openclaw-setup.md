# DigitalOcean OpenClaw Setup

## Recommended droplet

For your use case, create this exact starter box:

- Provider: `DigitalOcean`
- Region: `ATL1` if you want lower latency from the US South, otherwise `NYC3`
- OS: `Ubuntu 24.04 LTS x64`
- Plan: `Basic`
- CPU option: `Premium AMD`
- Size: `8 GB RAM / 4 vCPU / 160 GB SSD`
- Price checked April 5, 2026: `$48/month`

## Why this exact choice

- `Basic 8 GB / 4 vCPU` is much more comfortable than the bare minimum for OpenClaw
- it gives room for Docker, logs, uploaded files, multiple agents, and some growth
- `Premium AMD` is the sweet spot for feeling fast without jumping to much pricier dedicated-CPU plans
- `160 GB` means you do not start life fighting disk pressure immediately

## What not to choose

- not `4 GB / 2 vCPU` unless you are okay with tighter headroom
- not `CPU-Optimized` yet, because it doubles the monthly cost too early
- not the cheapest 1-2 GB droplets for production use

## Estimated monthly cost

- Droplet: `$48/month`
- Daily backups on a Basic plan: about `30%` extra, so about `$14.40/month`
- Manual snapshots: `$0.06/GB-month`

Practical budget:

- normal safe setup: about `$62-70/month`

## Create it in the dashboard

In DigitalOcean, use these choices:

1. Click `Create` -> `Droplets`
2. Choose `Ubuntu 24.04 LTS x64`
3. Choose a datacenter region:
   - `ATL1` if it is available in your account and you want good central/eastern US performance
   - otherwise `NYC3`
4. Under plan, choose `Basic`
5. Under CPU options, choose `Premium AMD`
6. Choose `8 GB / 4 vCPU / 160 GB SSD`
7. Turn on `Monitoring`
8. Turn on `Daily Backups`
9. Add your SSH key during creation
10. Do not enable password authentication if the UI gives that option
11. Use a hostname like `openclaw-core-01`
12. Create exactly `1` droplet

## Firewall to create immediately

Create a cloud firewall and attach it to the droplet right away.

Inbound:

- `SSH` port `22` from `your home/work public IP only`
- `HTTP` port `80` from `0.0.0.0/0` and `::/0`
- `HTTPS` port `443` from `0.0.0.0/0` and `::/0`

Outbound:

- allow all outbound for now

Do not expose any OpenClaw internal ports publicly.

## Safe naming

- Firewall: `fw-openclaw-core`
- Droplet: `openclaw-core-01`
- Project: `openclaw`

## After the droplet is created

Run this checklist in order:

1. SSH in as `root` using your key
2. Create a non-root sudo user
3. Disable password SSH login
4. Install Docker Engine and Docker Compose plugin
5. Copy [`ops/openclaw`](/C:/Users/class/receipt-pwa/ops/openclaw) to `/opt/openclaw/`
6. Fill in `.env`
7. Point your domain to the droplet IP
8. Start the stack
9. Verify HTTPS works
10. Take a manual baseline snapshot

## What I recommend as the next implementation step

Build the host from this repo using the deployment scaffold already added:

- [README.md](/C:/Users/class/receipt-pwa/ops/openclaw/README.md)
- [docker-compose.yml](/C:/Users/class/receipt-pwa/ops/openclaw/docker-compose.yml)
- [.env.example](/C:/Users/class/receipt-pwa/ops/openclaw/.env.example)
- [Caddyfile](/C:/Users/class/receipt-pwa/ops/openclaw/Caddyfile)

## Sources

- [DigitalOcean Droplet pricing](https://www.digitalocean.com/pricing/droplets)
- [DigitalOcean Droplet plan types](https://docs.digitalocean.com/products/droplets/concepts/choosing-a-plan/)
- [DigitalOcean Droplet features](https://docs.digitalocean.com/products/droplets/details/features/)
- [DigitalOcean firewalls quickstart](https://docs.digitalocean.com/products/networking/firewalls/getting-started/quickstart/)
- [DigitalOcean create firewalls](https://docs.digitalocean.com/products/networking/firewalls/how-to/create/)
- [DigitalOcean backups details](https://docs.digitalocean.com/products/backups/details/)
- [DigitalOcean backups pricing](https://docs.digitalocean.com/products/backups/details/pricing/)
- [DigitalOcean enable backups](https://docs.digitalocean.com/products/backups/how-to/enable/)
- [DigitalOcean snapshot droplets](https://docs.digitalocean.com/products/snapshots/how-to/snapshot-droplets/)
- [DigitalOcean snapshot pricing](https://docs.digitalocean.com/products/snapshots/details/)
