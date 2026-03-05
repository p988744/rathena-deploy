#!/usr/bin/env bash
# release.sh — 打包 client 並上傳到 Google Drive
# 用法: ./release.sh <version>
# 範例: ./release.sh 1.5.0
set -euo pipefail

# --- Config ---
DRIVE_FOLDER_ID="1mjRD5xRZZzcwhOJ9y3coNpD_2ixHGhiI"  # Google Drive "RO" folder
CLIENT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$CLIENT_DIR")"

# --- Args ---
VERSION="${1:?用法: ./release.sh <version>  (例: 1.5.0)}"
ZIP_NAME="ro-client-v${VERSION}.zip"
ZIP_PATH="/tmp/${ZIP_NAME}"

echo "=== RO Client Release v${VERSION} ==="

# --- Step 1: Package ---
echo ""
echo "[1/4] 打包 client/ → ${ZIP_NAME} ..."
echo "      (排除: savedata/, .DS_Store, *.megatmp*)"

cd "$CLIENT_DIR"
rm -f "$ZIP_PATH"

# zip 整個 client 資料夾，排除不需要的檔案
zip -r -q "$ZIP_PATH" . \
    -x "savedata/*" \
    -x "*.DS_Store" \
    -x "*.megatmp*" \
    -x "release.sh" \
    -x "db/*" \
    -x "server/*"

ZIP_SIZE=$(du -h "$ZIP_PATH" | cut -f1)
echo "      完成: ${ZIP_SIZE}"

# --- Step 2: Upload ---
echo ""
echo "[2/4] 上傳到 Google Drive ..."

UPLOAD_RESULT=$(gws drive files create \
    --json "{\"name\": \"${ZIP_NAME}\", \"parents\": [\"${DRIVE_FOLDER_ID}\"]}" \
    --upload "$ZIP_PATH" 2>&1)

FILE_ID=$(echo "$UPLOAD_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$FILE_ID" ]; then
    echo "      上傳失敗!"
    echo "$UPLOAD_RESULT"
    exit 1
fi

echo "      File ID: ${FILE_ID}"

# --- Step 3: Set sharing (anyone with link can download) ---
echo ""
echo "[3/4] 設定分享權限（任何人可下載）..."

gws drive permissions create \
    --params "{\"fileId\": \"${FILE_ID}\"}" \
    --json '{"role": "reader", "type": "anyone"}' > /dev/null 2>&1

# --- Step 4: Get download link ---
echo ""
echo "[4/4] 產生下載連結 ..."

VIEW_LINK="https://drive.google.com/file/d/${FILE_ID}/view?usp=sharing"
DIRECT_LINK="https://drive.google.com/uc?export=download&id=${FILE_ID}"

echo ""
echo "========================================"
echo "  RO Client v${VERSION} 發布完成!"
echo "========================================"
echo ""
echo "  分享連結: ${VIEW_LINK}"
echo "  直接下載: ${DIRECT_LINK}"
echo "  檔案大小: ${ZIP_SIZE}"
echo "  Drive ID: ${FILE_ID}"
echo ""

# --- Cleanup ---
rm -f "$ZIP_PATH"
echo "已清除暫存檔 ${ZIP_PATH}"
