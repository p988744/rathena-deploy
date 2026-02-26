#!/bin/bash
# ============================================================
# deploy.sh — 部署 rAthena 映像到 Linux VPS
# ============================================================
# 前提：
#   - 已執行 build.sh 產生 rathena-server.tar
#   - VPS 已執行 setup-vps.sh（安裝 Docker）
#   - VPS 已啟用 SSH
# 用法：./deploy.sh
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 載入設定
if [ -f .env ]; then
    source .env
else
    echo "❌ 找不到 .env 檔案！"
    echo "   請先執行: cp .env.example .env 並修改設定"
    exit 1
fi

# 變數
SERVER_IP="${SERVER_IP:?請在 .env 中設定 SERVER_IP}"
SERVER_USER="${SERVER_USER:-ubuntu}"
SERVER_SSH_PORT="${SERVER_SSH_PORT:-22}"
REMOTE_DIR="${REMOTE_DIR:-/opt/rathena}"
TAR_FILE="rathena-server.tar"
IMAGE_NAME="rathena-server"
IMAGE_TAG="latest"

echo "============================================"
echo "  🚀 部署 rAthena 到 VPS"
echo "============================================"
echo "  Server : ${SERVER_IP}"
echo "  User   : ${SERVER_USER}"
echo "  SSH    : ${SERVER_SSH_PORT}"
echo "  Dir    : ${REMOTE_DIR}"
echo "============================================"
echo ""

# 檢查 tar 檔是否存在
if [ ! -f "${TAR_FILE}" ]; then
    echo "❌ 找不到 ${TAR_FILE}！請先執行 ./build.sh"
    exit 1
fi

TAR_SIZE=$(du -h "${TAR_FILE}" | cut -f1)

# ------ Step 1: 在 VPS 上建立目錄結構 ------
echo "📁 Step 1: 在 VPS 上建立目錄結構..."
ssh -p "${SERVER_SSH_PORT}" "${SERVER_USER}@${SERVER_IP}" \
    "sudo mkdir -p ${REMOTE_DIR}/{custom/conf,custom/npc}"
echo "✅ 目錄已建立"

# ------ Step 2: 上傳映像檔 ------
echo ""
echo "📤 Step 2: 上傳映像到 VPS (${TAR_SIZE})..."
echo "   可能需要幾分鐘，取決於網路速度..."

scp -P "${SERVER_SSH_PORT}" "${TAR_FILE}" \
    "${SERVER_USER}@${SERVER_IP}:/tmp/${TAR_FILE}"

echo "✅ 上傳完成！"

# ------ Step 3: 載入映像到 Docker ------
echo ""
echo "📥 Step 3: 在 VPS 上載入 Docker 映像..."

ssh -p "${SERVER_SSH_PORT}" "${SERVER_USER}@${SERVER_IP}" << REMOTE_LOAD
docker load -i /tmp/${TAR_FILE}
rm /tmp/${TAR_FILE}
echo "映像載入完成"
docker images | grep ${IMAGE_NAME}
REMOTE_LOAD

echo "✅ 映像已載入！"

# ------ Step 4: 上傳 docker-compose 和 .env ------
echo ""
echo "📤 Step 4: 上傳部署設定檔..."

scp -P "${SERVER_SSH_PORT}" \
    docker-compose.yml .env \
    "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"

echo "✅ 設定檔已上傳"

# ------ Step 5: 啟動服務 ------
echo ""
echo "🚀 Step 5: 啟動伺服器..."

ssh -p "${SERVER_SSH_PORT}" "${SERVER_USER}@${SERVER_IP}" << REMOTE_START
cd ${REMOTE_DIR}

# 如果有舊的容器，先停止
docker compose down 2>/dev/null || true

# 啟動
docker compose up -d

echo ""
echo "等待 30 秒讓服務完全啟動..."
sleep 30

# 顯示狀態
docker compose ps
echo ""
echo "=== rAthena Server Logs (最近 20 行) ==="
docker compose logs --tail=20 rathena
REMOTE_START

echo ""
echo "============================================"
echo "  ✅ 部署完成！"
echo "============================================"
echo ""
echo "  🎮 連線資訊："
echo "  Server : ${SERVER_IP}"
echo "  Port   : 6900"
echo "  帳號   : 輸入 名稱_M 或 名稱_F 自動建立"
echo ""
echo "  📋 管理指令（SSH 到 VPS 後）："
echo "  cd ${REMOTE_DIR}"
echo "  docker compose logs -f rathena  # 查看即時日誌"
echo "  docker compose restart rathena  # 重啟伺服器"
echo "  docker compose down             # 停止全部"
echo "  docker compose up -d            # 啟動全部"
echo "============================================"
