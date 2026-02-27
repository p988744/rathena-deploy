# 伺服器設定管理與打包工具 TUI — 規劃文件

> 建立日期：2026-02-26

## 1. 現狀分析

### 1.1 目前架構

目前的管理流程完全是手動的：

```
macOS (開發機)                       AWS Lightsail VPS
 .env (手動編輯)                      /opt/rathena/
 build.sh (手動執行)      ─ SCP ─>    docker-compose.yml
 deploy.sh (手動執行)     ─ SSH ─>    docker compose up -d
```

**設定流程**：`.env` → `docker-compose.yml` 環境變數 → `entrypoint.sh` 生成 `conf/import/*.txt`

**痛點**：
- 修改倍率需手動編輯 `.env`，然後 `scp` + `ssh restart`
- 帳號管理需 SSH 進伺服器再手動執行 MySQL 指令
- 查看伺服器狀態需要開 SSH
- 沒有統一的管理介面

### 1.2 .env 設定結構

| 分類 | 變數 | 修改後行為 |
|------|------|------------|
| VPS 連線 | `SERVER_IP`, `SERVER_USER`, `SERVER_SSH_PORT`, `REMOTE_DIR` | 變更部署目標 |
| 伺服器名稱 | `SERVER_NAME` | 重啟生效 |
| 遊戲倍率 | `BASE_EXP_RATE`, `JOB_EXP_RATE`, `DROP_RATE`, `CARD_DROP_RATE` | 重啟生效，無需重新編譯 |
| 資料庫 | `DB_USER`, `DB_PASS`, `DB_NAME`, `DB_ROOT_PASS`, `DB_PORT_EXPOSE` | 重啟生效 |
| 建置 | `RATHENA_BRANCH`, `PACKETVER`, `BUILD_MODE` | 需要重新編譯 |

### 1.3 rAthena 帳號資料庫結構

rAthena 使用 MariaDB，帳號存在 `login` table：
- `account_id` — 帳號 ID
- `userid` — 帳號名稱
- `user_pass` — 密碼（明文，因為 `use_MD5_passwords: no`）
- `sex` — 性別 (M/F/S)
- `group_id` — 權限等級（0=玩家, 1=初級GM, 99=管理員）

存取方式：透過 SSH 到 VPS 後 `docker compose exec db mysql -u ragnarok -pragnarok ragnarok`

### 1.4 現有腳本的功能映射

| 腳本 | 功能 | TUI 對應操作 |
|------|------|-------------|
| `build.sh` | 建置 Docker image | "重新編譯" |
| `deploy.sh` | 上傳 + 部署 + 啟動 | "部署到伺服器" |
| `update.sh` | build + deploy | "更新伺服器" |
| `setup-vps.sh` | VPS 初始設定 | 首次設定向導 |

## 2. 技術選型

### 2.1 候選框架比較

| 維度 | Python + Textual | Go + Bubbletea | Rust + Ratatui | Shell + dialog |
|------|:---:|:---:|:---:|:---:|
| 開發速度 | 5/5 | 3/5 | 2/5 | 4/5 |
| TUI 品質 | 5/5 | 4/5 | 4/5 | 2/5 |
| 維護成本 | 3/5 | 5/5 | 4/5 | 2/5 |
| macOS 相容 | 5/5 | 5/5 | 5/5 | 4/5 |
| SSH/DB 整合 | 5/5 | 4/5 | 3/5 | 5/5 |
| 分發難度 | 3/5 | 5/5 | 5/5 | 4/5 |

### 2.2 推薦：Python + Textual

**理由**：
1. **開發效率最高**：個人/小團隊工具，速度是第一優先
2. **功能匹配度最高**：表格（帳號列表）、表單（設定編輯）、即時日誌串流、diff 顯示 — Textual 原生支持
3. **整合自然**：`python-dotenv` 讀寫 `.env`、`paramiko` SSH、`pymysql` 資料庫、subprocess 調用現有 shell 腳本
4. **分發方案**：用 `uv` 管理，`uv run ro-admin` 即可啟動

## 3. 架構設計

### 3.1 目錄結構

```
~/ro/admin/                        # TUI 工具根目錄
├── pyproject.toml                 # uv 管理
├── src/
│   └── ro_admin/
│       ├── __init__.py
│       ├── app.py                 # Textual App 入口
│       ├── config.py              # .env 讀寫 + 設定管理
│       ├── ssh.py                 # SSH 連線管理
│       ├── db.py                  # 資料庫操作（透過 SSH tunnel）
│       ├── docker.py              # Docker compose 操作包裝
│       ├── client.py              # 客戶端打包邏輯
│       ├── screens/
│       │   ├── dashboard.py       # 主儀表板（伺服器狀態）
│       │   ├── settings.py        # 設定管理畫面
│       │   ├── accounts.py        # 帳號管理畫面
│       │   ├── server_ops.py      # 伺服器操作畫面
│       │   ├── logs.py            # 日誌查看畫面
│       │   └── packaging.py       # 打包與分發畫面
│       └── widgets/
│           ├── rate_editor.py     # 倍率編輯器
│           ├── env_diff.py        # .env 變更 diff 顯示
│           └── status_bar.py      # 伺服器狀態列
```

### 3.2 設定讀寫策略

直接修改 `~/ro/server/.env`（唯一設定來源）：
1. 啟動時讀取 `.env`
2. 用戶在 TUI 中修改設定值
3. 顯示 diff（舊值 → 新值）
4. 確認後寫入 `.env`（保留原始格式和註解）
5. 依據修改類型決定：僅倍率/名稱 → restart；PACKETVER/BUILD_MODE → rebuild

### 3.3 SSH 連線策略

```
TUI (macOS)
  ├── SSH Connection (paramiko)
  │     ├── 遠端命令：docker compose ps/restart/logs
  │     ├── 遠端檔案上傳：scp .env, docker-compose.yml
  │     └── SSH Tunnel (port forward 3306)
  │           └── pymysql → MariaDB
  └── 本地命令：subprocess → build.sh / deploy.sh
```

### 3.4 帳號管理

透過 SSH tunnel 連接 MariaDB 的 `login` table：
- 建立帳號（INSERT INTO login）
- 帳號列表（SELECT FROM login）
- 設定 GM 等級（UPDATE group_id: 0=玩家, 1=初級GM, 99=管理員）
- 封鎖/解封帳號（UPDATE state）
- 線上玩家（SELECT FROM char WHERE online=1）

## 4. UI 設計

### 4.1 主畫面

```
┌─────────────────────────────────────────────────────────┐
│  RO Admin - 最粗的感動  │  52.196.22.227  │  ● Online  │
├──────────┬──────────────────────────────────────────────┤
│ [1] 儀表板│  Server Status                              │
│ [2] 設定  │  ├── Login Server  : ● Running              │
│ [3] 帳號  │  ├── Char Server   : ● Running              │
│ [4] 操作  │  └── Map Server    : ● Running              │
│ [5] 日誌  │                                              │
│ [6] 打包  │  Current Rates                               │
│           │  ├── Base EXP : 50x                          │
│ [q] 離開  │  ├── Job EXP  : 50x                          │
│           │  ├── Drop     : 50x                          │
│           │  └── Card     : 50x                          │
│           │                                              │
│           │  Players Online: 0                           │
└──────────┴──────────────────────────────────────────────┘
```

### 4.2 設定畫面

```
┌──────────────────────────────────────────────────────────┐
│  Settings                                    [Save] [↩]  │
├──────────────────────────────────────────────────────────┤
│  ── Game Rates ──────────────────────────────────        │
│  Base EXP Rate   [  5000  ] (50x)                        │
│  Job EXP Rate    [  5000  ] (50x)                        │
│  Drop Rate       [  5000  ] (50x)                        │
│  Card Drop Rate  [  5000  ] (50x)                        │
│                                                          │
│  ── Build Config (requires rebuild) ─────────────        │
│  PACKETVER       [ 20220406    ]  ⚠ rebuild needed       │
│  Build Mode      [ re         ]  ⚠ rebuild needed        │
│                                                          │
│  ── Changes Preview ─────────────────────────────        │
│  BASE_EXP_RATE: 5000 → 10000  (restart only)            │
└──────────────────────────────────────────────────────────┘
```

### 4.3 帳號管理畫面

```
┌──────────────────────────────────────────────────────────┐
│  Accounts                          [New Account] [↩]     │
├──────────────────────────────────────────────────────────┤
│  ┌────────┬────────────┬─────┬──────────┬────────────┐  │
│  │ ID     │ Account    │ Sex │ GM Level │ Status     │  │
│  ├────────┼────────────┼─────┼──────────┼────────────┤  │
│  │ 2000000│ admin      │ M   │ 99 (Admin)│ Active    │  │
│  │ 2000001│ player1    │ F   │ 0 (Player)│ Active    │  │
│  └────────┴────────────┴─────┴──────────┴────────────┘  │
│  Actions: [E]dit  [G]M Level  [B]an  [U]nban            │
└──────────────────────────────────────────────────────────┘
```

## 5. 實作計劃

### Phase 1: 核心基礎 (2-3 天)
- 初始化 Python 專案（uv init, pyproject.toml）
- `config.py` — `.env` 讀寫，變數分類
- `ssh.py` — SSH 連線管理
- `docker.py` — 包裝 docker compose 遠端命令
- Textual App 骨架 + 主導航
- Dashboard 畫面

**依賴**：textual >= 0.50, paramiko >= 3.0, python-dotenv >= 1.0, pymysql >= 1.1, sshtunnel >= 0.4

### Phase 2: 設定管理 (1-2 天)
- 設定編輯表單
- 倍率友善顯示（5000 → 50x）
- 變更 diff 預覽
- Apply 動作（寫 .env → SCP → restart/rebuild）

### Phase 3: 帳號管理 (1-2 天)
- SSH tunnel + pymysql 連線
- 帳號列表（DataTable widget）
- 建立帳號、GM 權限、封鎖/解封

### Phase 4: 伺服器操作 (1 天)
- 一鍵重啟/重新編譯+部署
- 日誌即時串流
- 資料庫備份

### Phase 5: 打包與分發 (1 天)
- 客戶端打包（更新 clientinfo.xml IP，zip 壓縮）
- 版本號管理
- Changelog 生成

## 6. 與現有腳本的整合

**原則**：TUI 不取代現有 shell 腳本，而是包裝它們。

```
ro-admin TUI
  ├── 設定管理 → 直接讀寫 ~/ro/server/.env
  ├── 伺服器操作
  │     ├── 重啟 → SSH: docker compose restart rathena
  │     ├── 編譯 → subprocess: ~/ro/server/build.sh
  │     └── 部署 → subprocess: ~/ro/server/deploy.sh
  ├── 帳號管理 → SSH tunnel → MariaDB
  └── 客戶端打包 → Python zipfile + clientinfo.xml 模板
```

## 7. 潛在挑戰

| 挑戰 | 解決方案 |
|------|---------|
| SSH 連線斷線 | paramiko keepalive + 自動重連 + 狀態列顯示 |
| 並發操作 | Textual Worker 非同步 + 危險操作確認對話框 |
| .env 寫入安全性 | 僅替換值部分保留註解格式 + `.env.bak` 備份 |
| DB 直接操作風險 | Transaction + 二次確認 + 只做簡單 INSERT/UPDATE |

## 8. 執行方式

```bash
cd ~/ro/admin
uv run ro-admin              # 開發/日常使用

# 或安裝到 PATH
uv tool install -e .
ro-admin                     # 全域可用
```
