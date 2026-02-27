# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ragnarok Online private server ("最粗的感動") based on rAthena, deployed to AWS Lightsail via Docker. The project has three main parts: server deployment scripts, a kRO game client with NEMO patches, and a Python TUI admin panel.

## Architecture

```
ro/
├── server/          # Docker-based rAthena server (shell scripts)
├── client/          # kRO game client + English localization + patched exe
├── nemo/            # NEMO Patcher tool + original/patched Ragexe binaries
├── admin/           # Python TUI admin panel (Textual framework)
└── docs/            # Planning documents
```

**Server deployment is a two-phase workflow:**
1. **Build** (macOS): `server/build.sh` cross-compiles rAthena for linux/amd64 via Docker buildx → exports `rathena-server.tar`
2. **Deploy** (macOS→VPS): `server/deploy.sh` SCPs the image to VPS, loads it, starts the Docker stack

**Configuration flow:** `server/.env` → `docker-compose.yml` env vars → `entrypoint.sh` generates `conf/import/*.txt` at container startup.

**Docker stack:** Two containers — `rathena` (login/char/map servers on ports 6900/6121/5121, network_mode: host) and `db` (MariaDB 10.11).

## Commands

```bash
# Server build & deploy (run from server/)
cd server/
./build.sh              # Build Docker image (~5-15 min, needs Docker Desktop)
./deploy.sh             # Deploy to VPS
./update.sh             # Rebuild + redeploy in one step

# Local testing
cd server/
docker compose -f docker-compose.local.yml up -d

# VPS management (SSH in first)
ssh ubuntu@52.196.22.227
cd /opt/rathena
sudo docker compose logs -f rathena
sudo docker compose restart rathena
sudo docker compose down && sudo docker compose up -d

# Change rates without rebuild — edit server/.env, then:
scp server/.env ubuntu@52.196.22.227:/opt/rathena/.env
ssh ubuntu@52.196.22.227 "cd /opt/rathena && sudo docker compose restart rathena"

# Re-patch client exe (macOS)
cd nemo/
wine NEMO.exe

# Admin panel
cd admin/
uv run python -m ro_admin.app
```

## Critical Version Bindings

PACKETVER, Ragexe, and kRO client versions are tightly coupled. Mismatches cause silent connection failures.

| Component | Current Value | Rule |
|-----------|--------------|------|
| PACKETVER | `20220406` | Must exactly match Ragexe date |
| Ragexe | `2022-04-06_Ragexe_1648707856` | Patched with 12 NEMO patches |
| kRO Client | `2022-07-21` | Date must be ≥ Ragexe date |
| Packet Obfuscation | Disabled both sides | Server: `#undef PACKET_OBFUSCATION` in Dockerfile; Client: NEMO "Disable packets id encryption" |
| Password | Plaintext (0x0064) | Server: `use_MD5_passwords: no`; Client: NEMO "Restore old login packet" |

**Changes requiring server rebuild:** PACKETVER, BUILD_MODE (re/pre-re), RATHENA_BRANCH, Dockerfile compile options.
**Changes NOT requiring rebuild:** Rates, server name, DB credentials (just restart container).

## Server .env Key Variables

- `SERVER_IP` — VPS public IP, used for client connections and char/map public IP
- `PACKETVER` — Must match Ragexe exe date exactly (e.g., `20220406`)
- `BUILD_MODE` — `re` (Renewal) or `pre-re` (Pre-Renewal)
- `BASE_EXP_RATE` / `JOB_EXP_RATE` / `DROP_RATE` / `CARD_DROP_RATE` — 100 = 1x official

## Client Configuration

- `client/data/clientinfo.xml` — Server connection IP/port (EUC-KR encoded XML)
- `client/data/msgstringtable.txt` — English UI translations (from ROenglishRE)
- `client/Ragexe_patched.exe` — The only tracked exe; all other binaries are gitignored

## Admin Panel (admin/)

Python TUI using Textual, connects to VPS via SSH tunnel for DB access. Dependencies managed with `uv` (see `admin/pyproject.toml`). Key deps: textual, paramiko, pymysql, sshtunnel, python-dotenv. Reads config from `server/.env`.

## Git Conventions

- Large binaries (GRF, DLL, most EXE) are gitignored — only `client/Ragexe_patched.exe` and specific NEMO files are tracked
- Release archives (`*.tar`, `*.zip`, `*.tar.gz`) are gitignored
- Language: Documentation is in Traditional Chinese; code comments may be mixed Chinese/English
