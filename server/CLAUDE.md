# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

rAthena Deploy: a deployment toolkit that cross-compiles the rAthena Ragnarok Online server on macOS (via Docker buildx for linux/amd64) and deploys it to a Linux VPS (AWS Lightsail or similar). Written entirely in shell scripts with Docker.

## Architecture

**Two-phase workflow:**
1. **Build phase** (macOS): `build.sh` uses a multi-stage Dockerfile to compile rAthena from source for linux/amd64, then exports the image as `rathena-server.tar`.
2. **Deploy phase** (macOS → VPS): `deploy.sh` SCPs the tar to the VPS, loads it into Docker, uploads `docker-compose.yml` + `.env`, and starts the stack.

**Docker stack (docker-compose.yml):**
- `rathena` container: runs login-server (6900), char-server (6121), map-server (5121) — all three processes managed by `scripts/entrypoint.sh` with trap-based graceful shutdown.
- `db` container: MariaDB 10.11 with healthcheck. rAthena waits for DB readiness via retry loop in entrypoint.

**entrypoint.sh responsibilities:**
- Waits for MariaDB, auto-initializes schema on first run (`sql-files/main.sql`, `sql-files/logs.sql`)
- Generates `conf/import/*.txt` config files from environment variables
- `pincode_enabled: no` (PIN code disabled for private server)
- Applies custom config/NPC overrides from `/rathena-custom/` volume mount
- Starts all three server processes and monitors with `wait -n`

**Configuration flow:** `.env` → `docker-compose.yml` env vars → `entrypoint.sh` generates `conf/import/` files at runtime.

## Project Structure

```
ro-synology/
├── .gitignore
├── TODO.md                        # 進度追蹤
├── rathena-nas-deploy/
│   ├── CLAUDE.md                  # 本文件
│   ├── .env.example               # 設定檔範本
│   ├── .env                       # 你的設定（git ignored）
│   ├── Dockerfile                 # 多階段建置：編譯 + 精簡運行映像
│   ├── docker-compose.yml         # VPS 部署用
│   ├── docker-compose.local.yml   # 本地測試用
│   ├── build.sh                   # macOS 建置腳本
│   ├── deploy.sh                  # 上傳並部署到 VPS
│   ├── update.sh                  # 重建 + 重新部署
│   ├── setup-vps.sh               # VPS 首次設定（Docker + 防火牆 + swap）
│   ├── scripts/
│   │   └── entrypoint.sh          # 容器啟動腳本
│   └── README.md
└── client/
    ├── 2022-04-06_Ragexe_1648707856_patched.exe  # NEMO patched client
    └── clientinfo.xml                             # Server connection config
```

## Commands

```bash
# Setup (first time)
cp .env.example .env   # then edit SERVER_IP, SERVER_USER

# Build Docker image (requires Docker Desktop running)
./build.sh             # outputs rathena-server.tar

# Deploy to VPS
./deploy.sh            # uploads image + config, starts services

# Rebuild + redeploy in one step
./update.sh

# Local testing with docker-compose
docker compose -f docker-compose.local.yml up -d

# VPS-side management (SSH into VPS first)
cd /opt/rathena
docker compose logs -f rathena    # live logs
docker compose restart rathena    # restart game server
docker compose down               # stop everything
docker compose up -d              # start everything
```

## Key Configuration

All configuration lives in `.env`. Critical variables:
- `SERVER_IP` — VPS public IP or domain (e.g. `ro.rabbit3hole.cc`); also used as `CHAR_PUBLIC_IP` and `MAP_PUBLIC_IP`
- `BUILD_MODE` — `re` (Renewal) or `pre-re` (Pre-Renewal classic)
- `PACKETVER` — client packet version (currently `20220406`), must match the kRO client
- Rate multipliers: `BASE_EXP_RATE`, `JOB_EXP_RATE`, `DROP_RATE`, `CARD_DROP_RATE` (100 = 1x official)

## Client Setup

Patched Ragexe is in `client/` directory (NEMO 5 patches applied):
1. Disable 1rag1 type parameters
2. Disable Ragexe Filename Check
3. Read Data Folder First
4. Disable Game Guard (NProtect)
5. Disable packets id encryption

**Windows usage:**
1. Extract `kRO_FullClient_20230404.zip`
2. Copy patched exe into kRO directory
3. Copy `clientinfo.xml` into kRO `data/` folder (edit `<address>` for your server IP)
4. Run patched exe

**macOS Wine:** Unstable — DirectDraw crash on Apple Silicon. Has worked once (Wine Stable 11.0 + ~/.wine prefix) but not reproducible.

## Dockerfile Build Args

- `RATHENA_BRANCH` — git branch to clone (default: `master`)
- `PACKETVER` — packet version for `./configure`
- `BUILD_MODE` — `re` or `pre-re`; controls `--enable-prere` flag

## Network Ports

| Port | Service       |
|------|---------------|
| 6900 | Login Server  |
| 6121 | Char Server   |
| 5121 | Map Server    |
| 3306 | MariaDB (configurable via `DB_PORT_EXPOSE`) |

## Deploy Options

| 方案 | 月費 | 延遲 (TW) | 備註 |
|------|------|-----------|------|
| Tailscale (本機 Docker) | $0 | 0ms | 朋友需裝 Tailscale，加拿大 ~180ms |
| AWS Lightsail Tokyo | $5 | 25-35ms | 腳本已就緒，加拿大 ~150ms |
| AWS Lightsail 美西 | $5 | ~130ms | 台灣+加拿大折衷點 |
| Oracle Cloud Free (ARM) | $0 | 30-60ms | 需改 Dockerfile 為 arm64 |
