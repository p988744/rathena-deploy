#!/bin/bash
set -e

echo "============================================"
echo "  🏰 rAthena Server"
echo "============================================"
echo "  Server Name : ${SERVER_NAME}"
echo "  Char IP     : ${CHAR_PUBLIC_IP}"
echo "  Map IP      : ${MAP_PUBLIC_IP}"
echo "  DB Host     : ${DB_HOST}:${DB_PORT}"
echo "  EXP Rate    : ${BASE_EXP_RATE}x / ${JOB_EXP_RATE}x"
echo "  Drop Rate   : ${DROP_RATE}x (Card: ${CARD_DROP_RATE}x)"
echo "============================================"

# ------ 等待資料庫就緒 ------
echo "[1/4] 等待資料庫連線..."
MAX_RETRIES=30
RETRY=0
until mysql -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASS}" -e "SELECT 1" &>/dev/null; do
    RETRY=$((RETRY + 1))
    if [ $RETRY -ge $MAX_RETRIES ]; then
        echo "❌ 資料庫連線超時！請確認 MariaDB 容器是否正常運行。"
        exit 1
    fi
    echo "   等待中... ($RETRY/$MAX_RETRIES)"
    sleep 3
done
echo "✅ 資料庫已就緒！"

# ------ 初始化資料庫（僅首次） ------
echo "[2/4] 檢查資料庫是否需要初始化..."
TABLE_COUNT=$(mysql -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASS}" -N -e \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${DB_NAME}';" 2>/dev/null || echo "0")

if [ "${TABLE_COUNT}" -lt "10" ]; then
    echo "   首次啟動，匯入資料庫結構..."
    mysql -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" < /rathena/sql-files/main.sql
    mysql -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" < /rathena/sql-files/logs.sql
    echo "✅ 資料庫初始化完成！"
else
    echo "✅ 資料庫已存在 (${TABLE_COUNT} 張表)，跳過初始化。"
fi

# ------ 生成設定檔 ------
echo "[3/4] 生成伺服器設定..."

# 確保 import 資料夾存在
mkdir -p /rathena/conf/import

# 資料庫連線（必須覆蓋全域 + 各伺服器個別的 DB 設定）
cat > /rathena/conf/import/inter_conf.txt << EOF
// Login Server DB
login_server_ip: ${DB_HOST}
login_server_port: ${DB_PORT}
login_server_id: ${DB_USER}
login_server_pw: ${DB_PASS}
login_server_db: ${DB_NAME}

// IP Ban DB
ipban_db_ip: ${DB_HOST}
ipban_db_port: ${DB_PORT}
ipban_db_id: ${DB_USER}
ipban_db_pw: ${DB_PASS}
ipban_db_db: ${DB_NAME}

// Char Server DB
char_server_ip: ${DB_HOST}
char_server_port: ${DB_PORT}
char_server_id: ${DB_USER}
char_server_pw: ${DB_PASS}
char_server_db: ${DB_NAME}

// Map Server DB
map_server_ip: ${DB_HOST}
map_server_port: ${DB_PORT}
map_server_id: ${DB_USER}
map_server_pw: ${DB_PASS}
map_server_db: ${DB_NAME}

// Web Server DB
web_server_ip: ${DB_HOST}
web_server_port: ${DB_PORT}
web_server_id: ${DB_USER}
web_server_pw: ${DB_PASS}
web_server_db: ${DB_NAME}

// Log DB
log_db_ip: ${DB_HOST}
log_db_port: ${DB_PORT}
log_db_id: ${DB_USER}
log_db_pw: ${DB_PASS}
log_db_db: ${DB_NAME}
EOF

# Char Server
cat > /rathena/conf/import/char_conf.txt << EOF
server_name: ${SERVER_NAME}
char_ip: ${CHAR_PUBLIC_IP}
login_ip: 127.0.0.1
login_port: ${LOGIN_PORT:-6900}
char_port: ${CHAR_PORT:-6121}
// 允許自動建立帳號
new_account: yes
// 關閉安全密碼（PIN碼）
pincode_enabled: no
// 新角色出生點：伊斯魯得島
start_point: izlude,128,114
start_point_pre: izlude,128,114
start_point_doram: izlude,128,114
// 新角色初始金額：2億
start_zeny: 200000000
EOF

# Map Server
cat > /rathena/conf/import/map_conf.txt << EOF
map_ip: ${MAP_PUBLIC_IP}
char_ip: 127.0.0.1
char_port: ${CHAR_PORT:-6121}
map_port: ${MAP_PORT:-5121}
EOF

# Login Server
cat > /rathena/conf/import/login_conf.txt << EOF
login_port: ${LOGIN_PORT:-6900}
new_account: yes
use_MD5_passwords: no
client_hash_check: off
EOF

# 遊戲倍率設定
cat > /rathena/conf/import/battle_conf.txt << EOF
base_exp_rate: ${BASE_EXP_RATE}
job_exp_rate: ${JOB_EXP_RATE}
item_rate_common: ${DROP_RATE}
item_rate_common_boss: ${DROP_RATE}
item_rate_heal: ${DROP_RATE}
item_rate_heal_boss: ${DROP_RATE}
item_rate_use: ${DROP_RATE}
item_rate_use_boss: ${DROP_RATE}
item_rate_equip: ${DROP_RATE}
item_rate_equip_boss: ${DROP_RATE}
item_rate_card: ${CARD_DROP_RATE}
item_rate_card_boss: ${CARD_DROP_RATE}
item_rate_mvp: ${DROP_RATE}
EOF

# 如果有外掛設定檔（從 volume mount 進來），覆蓋
if [ -d "/rathena-custom/conf" ]; then
    echo "   發現自訂設定，正在套用..."
    cp -rf /rathena-custom/conf/* /rathena/conf/import/ 2>/dev/null || true
fi

if [ -d "/rathena-custom/npc" ]; then
    echo "   發現自訂 NPC 腳本，正在套用..."
    cp -rf /rathena-custom/npc/* /rathena/npc/custom/ 2>/dev/null || true
fi

# overlay: 直接覆蓋 rAthena 原始檔案（conf/battle、conf/groups、db/re 等）
# 目錄結構對應 /rathena/，例：
#   custom/overlay/conf/battle/battle.conf → /rathena/conf/battle/battle.conf
#   custom/overlay/conf/groups.yml         → /rathena/conf/groups.yml
#   custom/overlay/db/re/item_db_usable.yml → /rathena/db/re/item_db_usable.yml
if [ -d "/rathena-overlay" ]; then
    echo "   發現 overlay 檔案，正在覆蓋..."
    cp -rf /rathena-overlay/* /rathena/ 2>/dev/null || true
    echo "   overlay 套用完成"
fi

# Replace NPC_ skills with compatible player skills to prevent map server crashes.
# Applied to both db/re/ (built-in) and db/import/ (custom overlay).
# Pattern: @NPC_SKILLNAME,<state>,<skill_id>, → @REPLACEMENT,<state>,<new_id>,
# Any remaining NPC_ lines are deleted as a catch-all.
# Replace NPC_ skills known to crash map-server:
#   NPC_SPLASHATTACK (174) — AoE NULL-pointer crash in rAthena skill handler
#   NPC_COMBOATTACK  (171) — combo state-machine crash on monster units
# All other NPC_ skills are safe (client + server both know them).
# The catch-all on the official DB is kept as a safety net for unknown monsters.
_replace_npc_skills() {
  local f="$1"
  local catchall="${2:-no}"   # pass "catchall" to also delete remaining NPC_ lines
  [ -f "$f" ] || return
  # ── Confirmed crash-causing skills ───────────────────────────────────────
  sed -i 's|@NPC_COMBOATTACK,\([^,]*\),171,|@MO_COMBOFINISH,\1,273,|g'      "$f"
  sed -i 's|@NPC_SPLASHATTACK,\([^,]*\),174,|@KN_BOWLINGBASH,\1,62,|g'      "$f"
  # ── NPC_CHEAL: replace so self-target logic applies correctly ────────────
  sed -i 's|@NPC_CHEAL,\([^,]*\),729,|@AL_HEAL,\1,28,|g'                    "$f"
  # ── Fix buff skills: change target→self so monsters don't buff players ───
  # 28=AL_HEAL 34=AL_BLESSING 60=KN_TWOHANDQUICKEN 249=CR_AUTOGUARD 361=HP_ASSUMPTIO 687=NPC_ALLHEAL
  for _sid in 28 34 60 249 361 687; do
    sed -i "/,${_sid},/ s/,target,/,self,/g" "$f"
  done
  # ── Catch-all: official DB only, guards against other dangerous NPC_ skills
  if [ "$catchall" = "catchall" ]; then
    sed -i '/@NPC_/d' "$f"
  fi
}
# Official DB: replace known crashes + catch-all
_replace_npc_skills /rathena/db/re/mob_skill_db.txt catchall
# Custom DB: replace known crashes only — all other NPC_ skills preserved as-is
_replace_npc_skills /rathena/db/import/mob_skill_db.txt
echo "   Replaced NPC_COMBOATTACK/NPC_SPLASHATTACK; all other NPC_ skills preserved"

# 啟用 custom warper（含幻影地圖傳送）
sed -i 's|//npc: npc/custom/warper.txt|npc: npc/custom/warper.txt|' /rathena/npc/scripts_custom.conf
echo "   已啟用自訂 Warper NPC"

# 啟用幻影地下城開放世界怪物 spawn
if [ -f "/rathena/npc/custom/illu_mobs.txt" ]; then
    if ! grep -q 'illu_mobs.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/illu_mobs.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用幻影地下城怪物 spawn"
fi

# 啟用生態圈 spawn
if [ -f "/rathena/npc/custom/eco_mobs.txt" ]; then
    if ! grep -q 'eco_mobs.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/eco_mobs.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用生態圈怪物 spawn"
fi

# 啟用重置npc spawn
if [ -f "/rathena/npc/custom/reset_npc.txt" ]; then
    if ! grep -q 'reset_npc.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/reset_npc.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用重置npc spawn"
fi

# 啟用健身房大師
if [ -f "/rathena/npc/custom/gympass.txt" ]; then
    if ! grep -q 'gympass.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/gympass.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用健身房大師"
fi

# 啟用野怪金幣及服飾（擊殺給 Zeny和機率掉服飾）
if [ -f "/rathena/npc/custom/zeny_mob.txt" ]; then
    if ! grep -q 'zeny_mob.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/zeny_mob.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用野怪金幣及服飾 spawn"
fi

# 啟用金幣精靈（全野外 + 地穴，擊殺給 Zeny）
if [ -f "/rathena/npc/custom/zeny_mob.txt" ]; then
    if ! grep -q 'zeny_mob.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/zeny_mob.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用金幣精靈 spawn"
fi

# 啟用 EP 裝備商店 NPC（EP1-13 到 EP19，共 7 個商店）
if [ -f "/rathena/npc/custom/ep_shops.txt" ]; then
    if ! grep -q 'ep_shops.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/ep_shops.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用 EP 裝備商店 NPC"
fi

# 啟用安全精煉師 NPC（+9 / +13）
if [ -f "/rathena/npc/custom/safe_refiner.txt" ]; then
    if ! grep -q 'safe_refiner.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/safe_refiner.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用安全精煉師 NPC"
fi

# 啟用卡片給予 NPC
if [ -f "/rathena/npc/custom/card_giver.txt" ]; then
    if ! grep -q 'card_giver.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/card_giver.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用卡片給予 NPC"
fi

# 啟用升階 NPC + Etel 材料商人
if [ -f "/rathena/npc/custom/grade_enhancer.txt" ]; then
    if ! grep -q 'grade_enhancer.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/grade_enhancer.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用升階 NPC + Etel 材料商人"
fi

# 統合附魔師 NPC（英文版，EP17.2 全自動 / EP18 灰狼 / EP19 雪花・冰晶）
# enchant_master.txt 為繁體中文備用版，不載入
if [ -f "/rathena/npc/custom/enchant_master_en.txt" ]; then
    if ! grep -q 'enchant_master_en.txt' /rathena/npc/scripts_custom.conf; then
        echo 'npc: npc/custom/enchant_master_en.txt' >> /rathena/npc/scripts_custom.conf
    fi
    echo "   已啟用統合附魔師 NPC (EN)"
fi

# 啟用基本服務 NPC（轉職、重置、補血等）
for npc in jobmaster resetnpc platinum_skills healer breeder card_seller itemmall stylist card_remover item_signer; do
    sed -i "s|//npc: npc/custom/${npc}.txt|npc: npc/custom/${npc}.txt|" /rathena/npc/scripts_custom.conf
done
echo "   已啟用轉職、重置、基本服務 NPC"

# 自訂：重置免費
sed -i 's|setarray .@Reset, 5000, 5000, 9000, 0;|setarray .@Reset, 0, 0, 0, 0;|' /rathena/npc/custom/resetnpc.txt

# 自訂：降低轉職等級要求
sed -i 's|setarray .Req_First\[0\],1,10;|setarray .Req_First[0],1,1;|' /rathena/npc/custom/jobmaster.txt
sed -i 's|setarray .Req_Second\[0\],1,40;|setarray .Req_Second[0],1,1;|' /rathena/npc/custom/jobmaster.txt
sed -i 's|setarray .Req_Rebirth\[0\],99,50;|setarray .Req_Rebirth[0],80,40;|' /rathena/npc/custom/jobmaster.txt
sed -i 's|setarray .Req_Third\[0\],99,50;|setarray .Req_Third[0],80,40;|' /rathena/npc/custom/jobmaster.txt
sed -i 's|setarray .Req_Fourth\[0\],200,70;|setarray .Req_Fourth[0],180,60;|' /rathena/npc/custom/jobmaster.txt
sed -i 's|setarray .Req_Exp_NJ_GS\[0\],99,70;|setarray .Req_Exp_NJ_GS[0],80,40;|' /rathena/npc/custom/jobmaster.txt
sed -i 's|setarray .Req_Exp_SNOVI\[0\],99,99;|setarray .Req_Exp_SNOVI[0],80,80;|' /rathena/npc/custom/jobmaster.txt
sed -i 's|.SkillPointCheck = true;|.SkillPointCheck = false;|' /rathena/npc/custom/jobmaster.txt

echo "✅ 設定檔生成完成！"

# ------ 啟動伺服器 ------
echo "[4/4] 啟動伺服器..."

cd /rathena

echo "   → 啟動 Login Server (Port ${LOGIN_PORT:-6900})..."
./login-server &
LOGIN_PID=$!
sleep 3

echo "   → 啟動 Char Server (Port ${CHAR_PORT:-6121})..."
./char-server &
CHAR_PID=$!
sleep 3

echo "   → 啟動 Map Server (Port ${MAP_PORT:-5121})..."
./map-server &
MAP_PID=$!
sleep 3

echo ""
echo "============================================"
echo "  ✅ rAthena 伺服器已全部啟動！"
echo "============================================"
echo "  Login Server : PID ${LOGIN_PID}"
echo "  Char Server  : PID ${CHAR_PID}"
echo "  Map Server   : PID ${MAP_PID}"
echo ""
echo "  客戶端連線 IP: ${CHAR_PUBLIC_IP}"
echo "  登入 Port    : ${LOGIN_PORT:-6900}"
echo ""
echo "  建立帳號方式："
echo "  帳號輸入 yourname_M (男) 或 yourname_F (女)"
echo "  第一個帳號自動成為 GM！"
echo "============================================"

# 優雅關閉處理
trap_handler() {
    echo ""
    echo "⚠️  收到停止訊號，正在關閉伺服器..."
    kill $MAP_PID 2>/dev/null
    sleep 1
    kill $CHAR_PID 2>/dev/null
    sleep 1
    kill $LOGIN_PID 2>/dev/null
    echo "✅ 伺服器已安全關閉。"
    exit 0
}

trap trap_handler SIGTERM SIGINT

# 等待任一 process 結束
wait -n $LOGIN_PID $CHAR_PID $MAP_PID
EXIT_CODE=$?
echo "⚠️  某個伺服器 process 已退出 (exit code: ${EXIT_CODE})"

# 清理其他 process
kill $LOGIN_PID $CHAR_PID $MAP_PID 2>/dev/null
exit $EXIT_CODE
