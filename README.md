# RO Private Server

個人用 Ragnarok Online 私服，基於 rAthena 部署在 AWS Lightsail。

## 目錄結構

```
ro/
├── server/              # 伺服器設定與部署腳本
│   ├── .env             # 環境變數（IP、倍率、DB 密碼）
│   ├── Dockerfile       # rAthena 編譯用 multi-stage Dockerfile
│   ├── docker-compose.yml
│   ├── scripts/
│   │   └── entrypoint.sh  # 容器啟動腳本
│   ├── build.sh         # 建置 Docker image
│   ├── deploy.sh        # 部署到 VPS
│   └── update.sh        # 重建 + 重新部署
├── client/              # 完整遊戲客戶端（kRO + patch）
│   ├── Ragexe_patched.exe  # NEMO patched 執行檔
│   ├── data/
│   │   ├── clientinfo.xml     # 伺服器連線設定
│   │   ├── msgstringtable.txt # 英文 UI 翻譯
│   │   └── ...
│   ├── SystemEN/
│   │   └── Navi_Data.lub
│   ├── data.grf         # kRO 遊戲資料 (3.3GB)
│   └── rdata.grf        # kRO 遊戲資料 (276MB)
├── nemo/                # NEMO Patcher 工具
│   ├── NEMO.exe         # Patcher 程式（Wine 可執行）
│   ├── 2022-04-06_Ragexe_1648707856.exe  # 原始未 patch 的 exe
│   └── 2022-04-06_Ragexe_1648707856_patched.exe.log  # Patch 記錄
├── VERSION
├── CHANGELOG.md
└── README.md
```

## 快速開始

### 伺服器部署

```bash
# 1. 設定環境變數
cd server/
cp .env.example .env  # 編輯 .env 設定 SERVER_IP 等

# 2. 建置 Docker image（需要 Docker Desktop）
./build.sh

# 3. 部署到 VPS（需要 SSH 存取）
./deploy.sh

# 4. 一鍵重建 + 部署
./update.sh
```

### 客戶端使用

1. 取得完整客戶端（`ro-client-v1.0.zip` 或從本 repo 的 `client/` 複製）
2. 修改 `data/clientinfo.xml` 中的 `<address>` 為伺服器 IP
3. 執行 `Ragexe_patched.exe`
4. 帳號：6 字元以上，首次登入自動註冊（帳號名加 `_M` 或 `_F` 後綴）

### 重新 Patch 客戶端

如果需要重新 patch（例如加減 NEMO patches）：

```bash
cd nemo/
wine NEMO.exe  # macOS 用 Wine 執行
```

1. Load client → 選 `2022-04-06_Ragexe_1648707856.exe`
2. 手動勾選需要的 patches（見 CHANGELOG.md）
3. Apply → 產生新的 `_patched.exe`
4. 複製到 `client/` 覆蓋

## 伺服器管理

### SSH 連線

```bash
ssh ubuntu@52.196.22.227
cd /opt/rathena
```

### 常用指令

```bash
# 查看即時 log
sudo docker compose logs -f rathena

# 重啟遊戲伺服器
sudo docker compose restart rathena

# 停止所有服務
sudo docker compose down

# 啟動所有服務
sudo docker compose up -d
```

### 修改倍率（不需重新編譯）

1. 編輯 `server/.env` 中的倍率設定
2. 上傳：`scp server/.env ubuntu@52.196.22.227:/opt/rathena/.env`
3. 重啟：`ssh ubuntu@52.196.22.227 "cd /opt/rathena && sudo docker compose restart rathena"`

### 需要重新編譯的修改

- 更改 `PACKETVER`
- 更改 `BUILD_MODE`（re ↔ pre-re）
- 更改 `RATHENA_BRANCH`
- 修改 Dockerfile 中的編譯選項

## 網路設定

| Port | 服務 | 說明 |
|------|------|------|
| 6900 | Login Server | 登入認證 |
| 6121 | Char Server | 角色管理 |
| 5121 | Map Server | 遊戲地圖 |
| 3306 | MariaDB | 資料庫（僅內部） |

VPS 防火牆需開放 6900、6121、5121 的 TCP 連線。

## GM 指令速查

```
@baselvl 200         # 基本等級
@joblvl 60           # 職業等級
@job <id>            # 轉職（見 FAQ）
@allskill            # 全技能
@str/agi/vit/int/dex/luk 130  # 素質點
@item <id> <num>     # 取得道具
@warp <map>          # 傳送
@heal                # 回滿 HP/SP
@speed 0             # 最快移速
@autoloot 100        # 自動撿取
@monster <id>        # 召喚怪物
@go 0                # 傳送主城
```

## 技術細節

| 項目 | 值 |
|------|-----|
| Server | rAthena master (Renewal) |
| PACKETVER | 20220406 |
| Client Exe | 2022-04-06_Ragexe_1648707856 |
| kRO Data | kRO Full Client 2022-07-21 |
| Packet Obfuscation | Disabled |
| Password | Plaintext (packet 0x0064) |
| Docker | network_mode: host |
| DB | MariaDB 10.11 |
