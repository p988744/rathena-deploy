#!/bin/bash
# ============================================================
# setup-vps.sh — VPS 首次設定（在 VPS 上執行）
# ============================================================
# 功能：安裝 Docker、設定防火牆、建立 swap
# 適用：AWS Lightsail / 任何 Ubuntu 22.04+ VPS
#
# 用法：
#   1. SSH 進入 VPS
#   2. 上傳此腳本：scp setup-vps.sh user@VPS_IP:~/
#   3. 執行：chmod +x setup-vps.sh && sudo ./setup-vps.sh
# ============================================================

set -e

# 檢查 root 權限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 請使用 sudo 執行此腳本"
    echo "   sudo ./setup-vps.sh"
    exit 1
fi

echo "============================================"
echo "  🔧 rAthena VPS 初始設定"
echo "============================================"
echo ""

# ------ Step 1: 系統更新 ------
echo "📦 Step 1: 更新系統套件..."
apt-get update -qq
apt-get upgrade -y -qq
echo "✅ 系統已更新"

# ------ Step 2: 安裝 Docker ------
echo ""
echo "🐳 Step 2: 安裝 Docker..."

if command -v docker &>/dev/null; then
    echo "✅ Docker 已安裝，跳過"
else
    # 安裝必要套件
    apt-get install -y -qq ca-certificates curl gnupg lsb-release

    # 加入 Docker GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # 加入 Docker apt 來源
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null

    # 安裝 Docker
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # 啟動 Docker
    systemctl enable docker
    systemctl start docker

    echo "✅ Docker 安裝完成"
fi

# 將目前使用者加入 docker 群組（不需 sudo 執行 docker）
CURRENT_USER="${SUDO_USER:-$USER}"
if [ "$CURRENT_USER" != "root" ]; then
    usermod -aG docker "$CURRENT_USER"
    echo "✅ 已將 ${CURRENT_USER} 加入 docker 群組"
    echo "   ⚠ 需重新登入 SSH 才會生效"
fi

# ------ Step 3: 建立部署目錄 ------
echo ""
echo "📁 Step 3: 建立部署目錄..."
DEPLOY_DIR="/opt/rathena"
mkdir -p "${DEPLOY_DIR}"/{custom/conf,custom/npc}

# 設定擁有者
if [ "$CURRENT_USER" != "root" ]; then
    chown -R "$CURRENT_USER":"$CURRENT_USER" "${DEPLOY_DIR}"
fi

echo "✅ 部署目錄已建立: ${DEPLOY_DIR}"

# ------ Step 4: 設定防火牆 ------
echo ""
echo "🔒 Step 4: 設定防火牆..."

if command -v ufw &>/dev/null; then
    # 允許 SSH
    ufw allow 22/tcp comment 'SSH'

    # 允許 rAthena 遊戲 Port
    ufw allow 6900/tcp comment 'rAthena Login Server'
    ufw allow 6121/tcp comment 'rAthena Char Server'
    ufw allow 5121/tcp comment 'rAthena Map Server'

    # 啟用防火牆（如果尚未啟用）
    echo "y" | ufw enable 2>/dev/null || true
    ufw reload

    echo "✅ UFW 防火牆已設定"
    ufw status numbered
else
    echo "⚠️  UFW 未安裝，請手動設定防火牆"
    echo "   需要開放 Port: 22, 6900, 6121, 5121"
fi

# ------ Step 5: 安裝 fail2ban ------
echo ""
echo "🛡️ Step 5: 安裝 fail2ban（SSH 防暴力破解）..."

if command -v fail2ban-server &>/dev/null; then
    echo "✅ fail2ban 已安裝，跳過"
else
    apt-get install -y -qq fail2ban

    # 建立本地設定（不會被更新覆蓋）
    cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

    systemctl enable fail2ban
    systemctl restart fail2ban
    echo "✅ fail2ban 已安裝並啟動"
fi

# ------ Step 6: 建立 Swap ------
echo ""
echo "💾 Step 6: 檢查 Swap..."

SWAP_SIZE=$(free -m | awk '/Swap:/ {print $2}')
if [ "${SWAP_SIZE}" -lt 100 ]; then
    echo "   建立 1GB Swap（低記憶體 VPS 需要）..."
    fallocate -l 1G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile

    # 加入 fstab（重開機自動掛載）
    if ! grep -q "/swapfile" /etc/fstab; then
        echo "/swapfile none swap sw 0 0" >> /etc/fstab
    fi

    # 調整 swappiness（只在記憶體不足時使用 swap）
    sysctl vm.swappiness=10
    echo "vm.swappiness=10" >> /etc/sysctl.conf

    echo "✅ 1GB Swap 已建立"
else
    echo "✅ Swap 已存在 (${SWAP_SIZE}MB)，跳過"
fi

# ------ 完成 ------
echo ""
echo "============================================"
echo "  ✅ VPS 設定完成！"
echo "============================================"
echo ""
echo "  部署目錄 : ${DEPLOY_DIR}"
echo "  Docker   : $(docker --version)"
echo "  Compose  : $(docker compose version)"
echo ""
echo "  防火牆已開放："
echo "    Port 22   — SSH"
echo "    Port 6900 — Login Server"
echo "    Port 6121 — Char Server"
echo "    Port 5121 — Map Server"
echo ""
echo "  下一步："
echo "  1. 重新登入 SSH（讓 docker 群組生效）"
echo "  2. 回到 macOS 執行 ./deploy.sh"
echo "============================================"
