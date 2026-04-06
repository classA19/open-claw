# OpenClaw VPS Stack

This folder is a starter deployment scaffold for a safe OpenClaw VPS.

## Goal

Run OpenClaw on a single Ubuntu VPS with:

- Docker Compose
- Caddy TLS termination
- host-level backups and snapshots
- minimal public surface area

## Starter shape

- `docker-compose.yml`: OpenClaw plus Caddy
- `.env.example`: environment placeholders
- `Caddyfile`: reverse proxy and TLS

## Recommended host

- Ubuntu `24.04 LTS`
- `8 GB RAM`
- `4 vCPU`
- `80-160 GB SSD`

## Folder layout on the VPS

```text
/opt/openclaw/
  .env
  docker-compose.yml
  Caddyfile
  config/
  workspace/
  caddy-data/
  caddy-config/
```

## Safe bootstrap checklist

1. Create the VPS with `Ubuntu 24.04 LTS`.
2. Add your SSH key during provisioning.
3. Enable provider firewall rules before opening the box to the internet.
4. Install Docker Engine and Docker Compose plugin.
5. Copy this folder to `/opt/openclaw/`.
6. Duplicate `.env.example` to `.env` and fill in secrets.
7. Point your domain at the VPS.
8. Start the stack with `docker compose up -d`.
9. Verify Caddy gets TLS and OpenClaw health checks stay green.

## Firewall baseline

- allow `22/tcp` only from your IP if possible
- allow `80/tcp` from anywhere
- allow `443/tcp` from anywhere
- deny everything else

## Deployment notes

- The OpenClaw gateway is published only to `127.0.0.1` on the host.
- Public traffic should hit Caddy on `80/443`, not OpenClaw directly.
- Keep backups enabled at the VPS provider layer.
- Take a manual snapshot before version upgrades or adding risky skills.

## OpenClaw layout suggestions

Start with two agents:

- `Personal Assistant`
- `VoltX Ops`

Keep them separate by:

- prompt
- model choice
- channel bindings
- skill allowlist
- secrets where practical

## First-run sanity checks

```bash
docker compose ps
docker compose logs --tail=100 openclaw-gateway
curl -I https://your-domain.example
```

## Important caution

OpenClaw can execute tools and skills that are powerful enough to damage the host or leak data if misconfigured. Treat every added skill as production code with access implications.
