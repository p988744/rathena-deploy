# 🏰 rAthena VPS Deploy

在 macOS 上建置 Ragnarok Online 私服 Docker 映像，一鍵部署到 AWS Lightsail（或任何 Linux VPS）。

---

## 📋 流程總覽

```
macOS (開發機)                         AWS Lightsail VPS
┌──────────────────┐                  ┌──────────────────────┐
│  1. ./build.sh   │                  │                      │
│     ↓            │   scp 上傳       │  Docker Compose      │
│  Dockerfile      │ ──────────────→  │  ┌────────────────┐  │
│  + rAthena 原始碼 │                  │  │ rathena-server │  │
│     ↓            │                  │  │  Login Server   │  │
│  docker buildx   │                  │  │  Char Server    │  │
│  --platform      │                  │  │  Map Server     │  │
│  linux/amd64     │                  │  └────────────────┘  │
│     ↓            │                  │  ┌────────────────┐  │
│  rathena-server  │   docker compose │  │   MariaDB      │  │
│  .tar (映像檔)   │ ──────────────→  │  │   (資料庫)     │  │
│                  │                  │  └────────────────┘  │
│  2. ./deploy.sh  │                  │                      │
└──────────────────┘                  └──────────────────────┘
                                               ↑
                                     ro.rabbit3hole.cc
                                        ┌──────────────┐
                                        │  Windows PC   │
                                        │  RO 客戶端    │
                                        └──────────────┘
```

---

## 🔧 前提需求

### macOS 端
- [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) — 必須安裝
- SSH 客戶端（macOS 內建）

### VPS 端
- AWS Lightsail $5/mo（東京，1 vCPU / 1 GB RAM）或任何 Linux VPS
- Ubuntu 22.04 LTS
- 開放 Port: 22 (SSH), 6900, 6121, 5121

### DNS（可選）
- Domain 指向 VPS 的 Static IP（例如 `ro.rabbit3hole.cc`）

---

## 🚀 快速開始

### Step 1：建立 VPS

**AWS Lightsail：**
1. 登入 [AWS Lightsail Console](https://lightsail.aws.amazon.com/)
2. Create instance → Linux → Ubuntu 22.04 LTS
3. Plan: $5/mo（東京 ap-northeast-1）
4. 建立後到 Networking tab → 開放 TCP 6900, 6121, 5121
5. 建立 Static IP 並綁定到實例
6. 將 Domain DNS A record 指向 Static IP

### Step 2：設定 VPS

```bash
# 上傳設定腳本
scp setup-vps.sh ubuntu@YOUR_VPS_IP:/tmp/

# SSH 進入 VPS
ssh ubuntu@YOUR_VPS_IP

# 執行設定（安裝 Docker、防火牆、swap）
chmod +x /tmp/setup-vps.sh && sudo /tmp/setup-vps.sh

# 重新登入讓 docker group 生效
exit
ssh ubuntu@YOUR_VPS_IP
```

### Step 3：設定本地環境

```bash
cd rathena-nas-deploy

# 複製設定檔
cp .env.example .env

# 編輯設定 — 修改 SERVER_IP
nano .env
```

**.env 中必須修改的項目：**
```env
SERVER_IP=ro.rabbit3hole.cc   # ← 你的 VPS IP 或 Domain
SERVER_USER=ubuntu             # ← VPS SSH 使用者
```

### Step 4：建置

```bash
chmod +x build.sh deploy.sh update.sh setup-vps.sh
./build.sh
```

首次建置需要 5-15 分鐘（下載 + 編譯），會產生 `rathena-server.tar` 映像檔。

### Step 5：部署

```bash
./deploy.sh
```

會自動上傳映像到 VPS、建立目錄、啟動服務。完成後即可遊玩！

---

## 🎮 連線遊戲

1. **準備客戶端**（在 Windows 上）
   - 安裝 kRO 完整客戶端
   - 用 WARP/NEMO Patcher 處理 Ragexe

2. **修改 clientinfo.xml**
   ```xml
   <connection>
     <display>TestRO</display>
     <address>ro.rabbit3hole.cc</address>
     <port>6900</port>
     <version>55</version>
     <langtype>0</langtype>
   </connection>
   ```

3. **建立帳號**
   - 帳號欄位輸入 `yourname_M`（男）或 `yourname_F`（女）
   - 自動建立帳號，第一個帳號 = GM 帳號

---

## 📁 專案結構

```
rathena-nas-deploy/
├── .env.example          # 設定檔範本
├── .env                  # 你的設定（git ignore）
├── Dockerfile            # 多階段建置：編譯 + 精簡運行映像
├── docker-compose.yml    # VPS 部署用 Compose 設定
├── docker-compose.local.yml  # 本地測試用
├── build.sh              # macOS 建置腳本
├── deploy.sh             # 上傳並部署到 VPS
├── update.sh             # 重建 + 重新部署（一鍵更新）
├── setup-vps.sh          # VPS 首次設定腳本
├── scripts/
│   └── entrypoint.sh     # 容器啟動腳本（自動設定 + 啟動）
├── client-package/       # 客戶端安裝包
│   ├── clientinfo.xml
│   ├── 安裝說明.txt
│   ├── data/
│   ├── System/
│   └── Setup/
└── README.md             # 本文件
```

---

## ⚙️ 自訂設定

### 修改倍率
直接改 `.env`，然後重新部署：
```bash
./deploy.sh    # 會自動重啟服務套用新設定
```

### 進階自訂（設定檔覆蓋）
在 VPS 的 `/opt/rathena/custom/conf/` 放入自訂設定檔，
會自動覆蓋容器內的 `conf/import/` 目錄。

NPC 腳本放在 `/opt/rathena/custom/npc/`。

### 切換 Pre-Renewal（經典版本）
```env
BUILD_MODE=pre-re    # 在 .env 中修改
```
然後執行 `./update.sh` 重建映像。

---

## 🔄 更新 rAthena

```bash
# 一鍵更新（重新建置 + 部署）
./update.sh
```

或手動分步驟：
```bash
./build.sh     # 只重建映像
./deploy.sh    # 只重新部署
```

---

## 🐛 疑難排解

### 查看日誌
```bash
# SSH 到 VPS 後
cd /opt/rathena
docker compose logs -f rathena     # 即時日誌
docker compose logs -f db          # 資料庫日誌
```

### Apple Silicon Mac 建置失敗
確保 Docker Desktop 設定中：
- **Settings → General → Use Rosetta for x86_64/amd64 emulation** — 如果建置卡住，**取消勾選**此選項

### 客戶端無法連線
- 確認 DNS `ro.rabbit3hole.cc` 指向正確的 VPS IP
- 確認 VPS 防火牆開放 6900/6121/5121
- 確認 AWS Lightsail Networking 也開放了這些 Port
- `docker compose ps` 確認容器正在運行

### 資料庫連線失敗
```bash
docker compose ps
docker compose logs db
```

---

## ⚠️ 注意事項

- 本專案僅供個人學習與懷舊用途
- rAthena 以 GPL 授權釋出，遊戲素材屬於 GRAVITY Co., Ltd.
- 請勿用於商業營利
