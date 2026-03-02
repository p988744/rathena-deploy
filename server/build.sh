#!/bin/bash
# ============================================================
# build.sh — 在 macOS 上建置 rAthena Docker 映像
# ============================================================
# 前提：已安裝 Docker Desktop for Mac
# 用法：./build.sh
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 載入設定
if [ -f .env ]; then
    source .env
else
    echo "⚠️  找不到 .env 檔案，將使用預設值。"
    echo "   建議先執行: cp .env.example .env 並修改設定"
fi

# 預設值
RATHENA_BRANCH="${RATHENA_BRANCH:-master}"
RATHENA_COMMIT="${RATHENA_COMMIT:-}"
PACKETVER="${PACKETVER:-20220406}"
BUILD_MODE="${BUILD_MODE:-re}"
IMAGE_NAME="rathena-server"
IMAGE_TAG="latest"
TAR_FILE="rathena-server.tar"

echo "============================================"
echo "  🔨 rAthena Docker Image Builder"
echo "============================================"
echo "  Branch    : ${RATHENA_BRANCH}"
echo "  Commit    : ${RATHENA_COMMIT:-latest}"
echo "  PacketVer : ${PACKETVER}"
echo "  Mode      : ${BUILD_MODE}"
echo "  Platform  : linux/amd64 (for Linux VPS)"
echo "============================================"
echo ""

# 檢查 Docker 是否運行
if ! docker info &>/dev/null; then
    echo "❌ Docker 未運行！請先啟動 Docker Desktop。"
    exit 1
fi

# 確保 entrypoint.sh 有執行權限
chmod +x scripts/entrypoint.sh

# ------ Step 1: 建置映像 ------
echo "📦 Step 1: 建置 Docker 映像 (linux/amd64)..."
echo "   這可能需要 5-15 分鐘（取決於網路和 CPU）..."
echo ""

docker buildx build \
    --platform linux/amd64 \
    --build-arg RATHENA_BRANCH="${RATHENA_BRANCH}" \
    --build-arg RATHENA_COMMIT="${RATHENA_COMMIT}" \
    --build-arg PACKETVER="${PACKETVER}" \
    --build-arg BUILD_MODE="${BUILD_MODE}" \
    --build-arg CACHEBUST="$(date +%s)" \
    --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
    --load \
    .

echo ""
echo "✅ 映像建置完成！"

# ------ Step 2: 匯出為 tar 檔 ------
echo ""
echo "📦 Step 2: 匯出映像為 ${TAR_FILE}..."

docker save "${IMAGE_NAME}:${IMAGE_TAG}" -o "${TAR_FILE}"

# 顯示檔案大小
TAR_SIZE=$(du -h "${TAR_FILE}" | cut -f1)
echo "✅ 匯出完成！檔案大小: ${TAR_SIZE}"

echo ""
echo "============================================"
echo "  ✅ 建置完成！"
echo "============================================"
echo ""
echo "  映像: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  檔案: ${TAR_FILE} (${TAR_SIZE})"
echo ""
echo "  下一步："
echo "  1. 修改 .env 中的 SERVER_IP 和其他設定"
echo "  2. 執行 ./deploy.sh 部署到 VPS"
echo "============================================"
