#!/bin/bash
# ============================================================
# remote-build.sh — 直接在 VPS 上建置並重啟 rAthena
# ============================================================
# 不需要本機 Docker，不需要上傳大型 tar 檔
# VPS 直接 clone rAthena source 並編譯（原生 linux/amd64）
# 用法：./remote-build.sh
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 載入設定
if [ -f .env ]; then
    source .env
else
    echo "❌ 找不到 .env 檔案！"
    exit 1
fi

SERVER_IP="${SERVER_IP:?請在 .env 中設定 SERVER_IP}"
SERVER_USER="${SERVER_USER:-ubuntu}"
SERVER_SSH_PORT="${SERVER_SSH_PORT:-22}"
REMOTE_DIR="${REMOTE_DIR:-/opt/rathena}"
RATHENA_BRANCH="${RATHENA_BRANCH:-master}"
PACKETVER="${PACKETVER:-20220406}"
BUILD_MODE="${BUILD_MODE:-re}"

SSH="ssh -p ${SERVER_SSH_PORT} ${SERVER_USER}@${SERVER_IP}"
SCP="scp -P ${SERVER_SSH_PORT}"

echo "============================================"
echo "  🔨 VPS 遠端建置 rAthena"
echo "============================================"
echo "  VPS       : ${SERVER_IP}"
echo "  Branch    : ${RATHENA_BRANCH}"
echo "  PacketVer : ${PACKETVER}"
echo "  Mode      : ${BUILD_MODE}"
echo "============================================"
echo ""

# ------ Step 1: 在 VPS 建立目錄 ------
echo "📁 Step 1: 建立 VPS 目錄..."
$SSH "sudo mkdir -p ${REMOTE_DIR}/{custom/conf,custom/npc} && \
      sudo chown -R ${SERVER_USER}:${SERVER_USER} ${REMOTE_DIR}"
echo "✅ 目錄就緒"

# ------ Step 2: 上傳建置所需檔案 ------
echo ""
echo "📤 Step 2: 上傳 Dockerfile、scripts、設定檔..."

# 建立遠端 scripts 目錄
$SSH "mkdir -p ${REMOTE_DIR}/scripts"

# 上傳各檔案
$SCP Dockerfile                    "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/Dockerfile"
$SCP scripts/entrypoint.sh         "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/scripts/entrypoint.sh"
$SCP docker-compose.yml            "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/docker-compose.yml"
$SCP .env                          "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/.env"

echo "✅ 檔案上傳完成"

# ------ Step 3: 在 VPS 上建置 ------
echo ""
echo "🔨 Step 3: 在 VPS 上建置 Docker Image..."
echo "   (clone rAthena + 編譯，約 5-15 分鐘)"
echo ""

$SSH "cd ${REMOTE_DIR} && \
    sudo docker build \
        --build-arg RATHENA_BRANCH=${RATHENA_BRANCH} \
        --build-arg PACKETVER=${PACKETVER} \
        --build-arg BUILD_MODE=${BUILD_MODE} \
        --tag rathena-server:latest \
        . && \
    echo '✅ 映像建置完成' && \
    sudo docker images | grep rathena-server"

# ------ Step 4: 重啟服務 ------
echo ""
echo "🚀 Step 4: 重啟服務..."

$SSH "cd ${REMOTE_DIR} && \
    sudo docker compose down 2>/dev/null || true && \
    sudo docker compose up -d && \
    echo '' && \
    echo '等待 30 秒讓服務完全啟動...' && \
    sleep 30 && \
    sudo docker compose ps && \
    echo '' && \
    echo '=== rAthena Logs (最近 20 行) ===' && \
    sudo docker compose logs --tail=20 rathena"

echo ""
echo "============================================"
echo "  ✅ 遠端建置並部署完成！"
echo "============================================"
echo "  Server : ${SERVER_IP}"
echo "  Port   : 6900"
echo "============================================"
