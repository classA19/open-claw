# OpenClaw VPS Plan

## What we are optimizing for

- Frictionless day-to-day performance
- Good isolation from your personal machine
- Enough headroom for both personal and business agents
- A setup that stays understandable for a solo operator

## Context that shapes the hosting choice

Your business context points to an always-available agent platform that will likely grow into:

- multiple channels
- multiple agents
- a mix of trusted and semi-trusted skills
- persistent logs, memory, and uploaded files
- occasional admin and automation tasks that must feel responsive

OpenClaw's official requirements are modest, but production usage grows fast once you add active skills, channels, logs, and sandboxing. The docs list `4 GB RAM`, `2+ CPU cores`, and `Docker v24+` as the practical recommendation for moderate production traffic. For this project, that is the floor, not the target.

## Recommendation

### Best overall pick for this project: DigitalOcean

Why:

- easiest beginner experience
- clean docs and console
- free stateful cloud firewall
- good snapshot/backup support
- predictable business-friendly experience

Recommended starting size:

- `Basic Premium AMD` or `General Purpose`
- minimum comfortable start: `4 GB / 2 vCPU`
- preferred for low-friction business use: `8 GB / 4 vCPU`

When to choose it:

- you want the smoothest first deployment
- you care more about reliability and simplicity than absolute lowest cost

### Best price/performance: Hetzner Cloud

Why:

- outstanding price/performance
- free stateful firewalls
- strong dedicated-vCPU value
- US regions available

Recommended starting sizes:

- value start: `CPX31` in US, `4 vCPU / 8 GB / 160 GB`
- stronger dedicated option: `CCX13` in US, `2 dedicated vCPU / 8 GB / 80 GB`

When to choose it:

- you want more machine for the money
- you are okay with a slightly less beginner-polished buying experience

### Good premium alternative: Vultr

Why:

- many regions
- strong networking reputation
- good firewall/snapshot tooling

Recommended starting size:

- `High Performance` cloud compute
- `4 GB / 2 vCPU` minimum, `8 GB / 4 vCPU` preferred

When to choose it:

- region flexibility matters
- you want a platform that is more premium than budget-focused

## Current pricing notes checked on April 5, 2026

### DigitalOcean

- `Basic 4 GB / 2 vCPU`: `$24/mo`
- `CPU-Optimized 4 GB / 2 vCPU`: `$42/mo`
- snapshots: `$0.06/GB per month`
- backups: percentage-based or usage-based plans

### Hetzner

- US `CPX31`: `$24.99/mo` after Hetzner's April 1, 2026 adjustment
- US `CCX13`: `$19.99/mo` after Hetzner's April 1, 2026 adjustment
- firewalls: free
- primary IPv4: extra cost

### Vultr

- `High Performance 4 GB / 2 vCPU`: `$72/mo`
- `Regular Performance 4 GB / 2 vCPU`: `$60/mo`
- snapshots: `$0.05/GB per month`

## My recommendation for you

If you want the safest beginner-friendly answer, start with:

- `DigitalOcean`
- `Basic Premium AMD 8 GB RAM / 4 vCPU / 160 GB SSD`
- `Ubuntu 24.04 LTS`
- daily backups enabled
- weekly manual snapshot before major changes

Beginner-specific walkthrough:

- [digitalocean-openclaw-setup.md](/C:/Users/class/receipt-pwa/docs/digitalocean-openclaw-setup.md)

If you want the best value without getting reckless, start with:

- `Hetzner CPX31` in `Ashburn` or `Hillsboro`
- `Ubuntu 24.04 LTS`
- backups enabled
- one protected baseline snapshot after hardening

## Safe architecture

### Phase 1

One VPS, one OpenClaw stack, two agents:

- `Personal Assistant`
- `VoltX Ops`

Both live on one host, but with:

- separate API keys where possible
- separate channel bindings
- a reviewed skill allowlist
- Docker sandboxing for risky skills

### Phase 2

Split risky work from core control:

- `openclaw-core`: UI, gateway, config, approved skills
- `openclaw-worker`: disposable worker host or container path for browser/shell-heavy jobs

That split is worth doing once tool usage gets more aggressive.

## Security baseline

- Ubuntu `24.04 LTS`
- SSH key auth only
- disable password login
- cloud firewall on day one
- expose only `80/443` publicly, and `22` only from your IP if possible
- keep OpenClaw bound behind a reverse proxy
- enable Docker sandboxing only for skills you trust enough to run at all
- use separate provider keys for personal and business automations
- never upload your main browser profile, password vault export, or local machine secrets

## Resource target

This is the starter target I would deploy for you right now:

- `8 GB RAM`
- `4 vCPU`
- `80-160 GB SSD`
- daily backups
- Docker-based deployment
- Caddy reverse proxy

That gives enough room for a responsive OpenClaw instance, two serious agents, logs, files, and growth without feeling cramped immediately.

## Immediate next build steps

1. Choose `DigitalOcean` or `Hetzner`.
2. Provision `Ubuntu 24.04 LTS`.
3. Apply the hardened Docker/Caddy stack in [`ops/openclaw/README.md`](/C:/Users/class/receipt-pwa/ops/openclaw/README.md).
4. Stand up a single OpenClaw instance first.
5. Create two agents: personal and business.
6. Add channels and skills gradually, not all at once.

## Sources

- [OpenClaw system requirements](https://openclawdoc.com/docs/getting-started/requirements/)
- [OpenClaw installation](https://openclawdoc.com/docs/getting-started/installation/)
- [OpenClaw intro](https://openclawdoc.com/docs/intro/)
- [OpenClaw models overview](https://openclawdoc.com/docs/models/overview/)
- [OpenClaw built-in tools warning](https://openclawdoc.com/docs/agents/tools/)
- [OpenClaw Docker Compose in GitHub](https://github.com/openclaw/openclaw/blob/main/docker-compose.yml)
- [DigitalOcean Droplet pricing](https://www.digitalocean.com/pricing/droplets)
- [DigitalOcean firewalls](https://docs.digitalocean.com/docs/networking/firewalls)
- [DigitalOcean snapshots](https://docs.digitalocean.com/products/snapshots/)
- [Hetzner price adjustment, effective April 1, 2026](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)
- [Hetzner Cloud general purpose](https://www.hetzner.com/cloud/general-purpose)
- [Hetzner cloud firewalls overview](https://docs.hetzner.com/cloud/firewalls/overview)
- [Hetzner backups and snapshots overview](https://docs.hetzner.com/cloud/servers/backups-snapshots/overview)
- [Vultr pricing](https://www.vultr.com/pricing/)
- [Vultr firewall groups](https://docs.vultr.com/products/network/firewall/management/groups)
- [Vultr snapshots FAQ](https://docs.vultr.com/products/orchestration/snapshots/faq)
