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

### 更新自訂 NPC（不需重新編譯）

修改 `server/custom-npc/` 下的 NPC 檔案後，上傳並重啟即可生效：

```bash
# 上傳指定 NPC 檔案（以 ep_shops.txt 為例）
scp server/custom-npc/ep_shops.txt ubuntu@52.196.22.227:/opt/rathena/custom/npc/ep_shops.txt

# 重啟伺服器
ssh ubuntu@52.196.22.227 "cd /opt/rathena && sudo docker compose restart rathena"

# 驗證 NPC 載入
ssh ubuntu@52.196.22.227 "sudo docker logs rathena-server 2>&1 | grep '已啟用'"
```

| 檔案 | 說明 | 部署指令 |
|------|------|----------|
| `ep_shops.txt` | EP 裝備商店（izlude） | `scp server/custom-npc/ep_shops.txt ubuntu@52.196.22.227:/opt/rathena/custom/npc/ep_shops.txt` |
| `healer.txt` | 補血 + Buff NPC | `scp server/custom-npc/healer.txt ubuntu@52.196.22.227:/opt/rathena/custom/npc/healer.txt` |
| `illu_mobs.txt` | 幻影地下城怪物 spawn | `scp server/custom-npc/illu_mobs.txt ubuntu@52.196.22.227:/opt/rathena/custom/npc/illu_mobs.txt` |

> 上傳任何檔案後都需要 `docker compose restart rathena` 才會生效。

### 需要重新編譯的修改

- 更改 `PACKETVER`
- 更改 `BUILD_MODE`（re ↔ pre-re）
- 更改 `RATHENA_BRANCH`
- 修改 Dockerfile 中的編譯選項

## 發布流程

### Server 發布

Server 有三種更新方式，依變更範圍選擇：

| 變更類型 | 方式 | 停機時間 | 指令 |
|---------|------|---------|------|
| NPC 腳本 | 熱更新 | ~30s 重啟 | `git push`（CI 自動部署）或手動 `scp` + `restart` |
| 倍率/設定 | 改 .env + 重啟 | ~30s 重啟 | `scp .env` → `restart` |
| rAthena 版本/編譯選項 | 完整重建 | ~20min build + ~5min deploy | `git tag v*` + `git push --tags`（CI）或手動 `update.sh` |

```
                        ┌─────────────────────────────┐
                        │     改了什麼？               │
                        └─────────┬───────────────────┘
                ┌─────────────────┼─────────────────┐
                ▼                 ▼                  ▼
        NPC 腳本            .env 設定          Dockerfile/
     custom-npc/*.txt    （倍率、名稱）     PACKETVER/分支
                │                │                  │
                ▼                ▼                  ▼
          git push 到       scp .env →         git tag v* →
          main 分支         restart             push tags
                │                │                  │
                ▼                ▼                  ▼
        CI: deploy-npc      手動 SSH          CI: deploy-full
        自動 scp+restart    重啟即可          build→scp→restart
```

#### 手動指令

```bash
# --- NPC 熱更新 ---
scp server/custom-npc/*.txt ubuntu@52.196.22.227:/opt/rathena/custom/npc/
ssh ubuntu@52.196.22.227 "cd /opt/rathena && sudo docker compose restart rathena"

# --- 改設定 ---
scp server/.env ubuntu@52.196.22.227:/opt/rathena/.env
ssh ubuntu@52.196.22.227 "cd /opt/rathena && sudo docker compose restart rathena"

# --- 完整重建部署 ---
cd server/
./update.sh              # = build.sh + deploy.sh
```

#### CI/CD（GitHub Actions）

| Workflow | 觸發條件 | 做什麼 |
|----------|---------|--------|
| `deploy-npc.yml` | push main + `server/custom-npc/**` 有變更 | scp NPC → restart |
| `deploy-full.yml` | push `v*` tag | build image → scp → deploy |

```bash
# 觸發 NPC 自動部署
git add server/custom-npc/
git commit -m "npc: ..."
git push

# 觸發完整部署
git tag v1.5.0
git push --tags
```

### Client 發布

Client 透過 `gws`（Google Workspace CLI）上傳到 Google Drive 分享：

```bash
cd client/
./release.sh 1.5.0
```

流程：打包 zip (~3.8GB) → 上傳 Google Drive「RO」資料夾 → 設定公開分享 → 輸出下載連結

> 前提：已安裝 `gws`（`npm i -g @googleworkspace/cli`）並完成 `gws auth login`

#### 已發布版本

| 版本 | 大小 | 主要變更 |
|------|------|---------|
| v1.0 | 3.8GB | 基礎客戶端 |
| v1.1 | 3.8GB | 繁體中文化 Phase 1 |
| v1.4.1 | 3.8GB | 繁體中文道具+技能名稱 |

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
