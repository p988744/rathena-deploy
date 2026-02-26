# FAQ — 常見問題

## 版本相容性（重要）

### Q: 客戶端與伺服器的版本對應關係是什麼？

這是最關鍵的相容性問題。三個版本必須互相匹配：

| 項目 | 目前使用版本 | 說明 |
|------|------------|------|
| **kRO Full Client** | 2022-07-21 | GRF 資料檔來源，包含地圖、模型、音效等遊戲資料 |
| **Ragexe.exe** | 2022-04-06 (unpacked) | 遊戲執行檔，從 nemo.herc.ws 取得的未加殼版本 |
| **PACKETVER** | 20220406 | 伺服器編譯參數，必須與 Ragexe 日期匹配 |

**規則：**
- `PACKETVER` 必須與 `Ragexe.exe` 的日期一致
- `kRO Full Client` 的日期需大於或等於 `Ragexe.exe` 的日期
- 更換任何一個版本都可能導致不相容

### Q: 為什麼不用最新的 kRO 客戶端？

2023 年之後的 kRO Ragexe.exe 使用了 WinLicense 加殼保護，NEMO Patcher 無法 patch。
2022-04-06 是社群推薦且已驗證穩定的版本。

### Q: 可以換成其他 PACKETVER 嗎？

可以，但需要：
1. 從 nemo.herc.ws 下載對應日期的 unpacked Ragexe
2. 修改 `.env` 的 `PACKETVER`
3. 重新編譯伺服器（`./build.sh` + `./deploy.sh`）
4. 用 NEMO 重新 patch 該 Ragexe

---

## 連線問題

### Q: 客戶端顯示 "Please wait..." 然後連不上

檢查項目：
1. **VPS 防火牆**：確認 6900、6121、5121 port 已開放
2. **clientinfo.xml**：`<address>` 是否為正確的伺服器 IP
3. **伺服器狀態**：SSH 進 VPS 執行 `sudo docker compose logs -f rathena` 確認三個 server 都在運行
4. **Windows 防火牆**：可能需要新增 Ragexe_patched.exe 的防火牆規則

### Q: 客戶端顯示 "NO MSG"

所有 UI 文字都是 "NO MSG" → `data/msgstringtable.txt` 缺失或損壞，從 client patch 重新複製。

只有特定訊息是 "NO MSG" → 伺服器回傳的錯誤碼在 msgstringtable 中沒有對應文字，通常是帳號/密碼問題。

### Q: 伺服器 log 顯示 "Closed connection" 但沒有認證結果

可能原因：
- Packet Obfuscation 不匹配：確認 Dockerfile 有 `#undef PACKET_OBFUSCATION`
- 客戶端缺少 "Disable packets id encryption" patch
- PACKETVER 與 Ragexe 版本不匹配

### Q: 帳號密碼輸入後顯示 "Please enter at least X characters"

rAthena 預設帳號和密碼都要 6 個字元以上。使用較長的帳號密碼。

---

## 帳號問題

### Q: 如何註冊帳號？

自動註冊已開啟。在登入畫面：
- 帳號輸入：`你的帳號_M`（男）或 `你的帳號_F`（女）
- 密碼：6 字元以上
- 首次登入自動建立帳號

### Q: 如何建立 GM 帳號？

SSH 進伺服器，直接操作資料庫：

```bash
sudo docker compose exec db mysql -u ragnarok -pragnarok ragnarok \
  -e "INSERT INTO login (account_id, userid, user_pass, sex, group_id) \
      VALUES (2000001, 'mygm', 'mypassword', 'M', 99);"
```

`group_id` 等級：0=玩家, 1=初級GM, 99=管理員

### Q: 忘記密碼怎麼辦？

```bash
sudo docker compose exec db mysql -u ragnarok -pragnarok ragnarok \
  -e "UPDATE login SET user_pass='newpassword' WHERE userid='帳號名';"
```

---

## NEMO Patch 問題

### Q: 目前用了哪些 patches？

12 個最小必要 patches（見 CHANGELOG.md）。重點：
- **不要勾 "Translate Client"** — 會導致 SystemEN 路徑錯誤
- **不要勾 "Use Ascii on All LangTypes"** — 影響 Lua 載入
- **不要勾 "Always load Korea ExternalSettings lua file"** — 導致額外錯誤

### Q: 出現 Lua 錯誤怎麼辦？

如果 NEMO patches 只勾了 12 個最小必要 patches，不應該有 Lua 錯誤。
如果出現，可能是 `data/luafiles514/` 資料夾裡有殘留的覆蓋檔案。

**解決方法：**
1. 刪除 `data/luafiles514/` 整個資料夾
2. 只保留 `data/` 裡的文字檔（clientinfo.xml、msgstringtable.txt 等）
3. 保留 `SystemEN/Navi_Data.lub`

### Q: 如何在 macOS 上使用 NEMO？

```bash
brew install --cask wine-stable  # 安裝 Wine
cd nemo/
wine NEMO.exe
```

---

## 伺服器管理

### Q: 修改倍率需要重新編譯嗎？

**不需要。** 修改 `.env` 然後重啟容器即可：

```bash
# 本地修改 .env 後
scp server/.env ubuntu@52.196.22.227:/opt/rathena/.env
ssh ubuntu@52.196.22.227 "cd /opt/rathena && sudo docker compose restart rathena"
```

### Q: 哪些修改需要重新編譯（rebuild）？

| 修改內容 | 需要 rebuild? |
|---------|:---:|
| 倍率 (EXP/Drop) | 否 |
| 伺服器名稱 | 否 |
| 資料庫密碼 | 否 |
| NPC 腳本 | 否（重啟即可） |
| PACKETVER | **是** |
| BUILD_MODE (re/pre-re) | **是** |
| Packet Obfuscation | **是** |
| rAthena 版本更新 | **是** |

### Q: 如何備份資料庫？

```bash
ssh ubuntu@52.196.22.227
cd /opt/rathena
sudo docker compose exec db mysqldump -u ragnarok -pragnarok ragnarok > backup_$(date +%Y%m%d).sql
```

### Q: 如何還原資料庫？

```bash
sudo docker compose exec -T db mysql -u ragnarok -pragnarok ragnarok < backup_20260226.sql
```

---

## 常用 GM 指令

### 轉職 ID 對照表

| ID | 職業 | ID | 職業 |
|----|------|----|------|
| 0 | Novice 初心者 | 4001 | High Novice 轉生初心者 |
| 1 | Swordman 劍士 | 4008 | Lord Knight |
| 2 | Mage 魔法師 | 4009 | High Priest |
| 3 | Archer 弓箭手 | 4010 | High Wizard |
| 4 | Acolyte 服事 | 4011 | Whitesmith |
| 5 | Merchant 商人 | 4012 | Sniper |
| 6 | Thief 盜賊 | 4013 | Assassin Cross |
| 7 | Knight 騎士 | 4054 | Rune Knight (三轉) |
| 8 | Priest 祭司 | 4055 | Warlock |
| 9 | Wizard 巫師 | 4056 | Ranger |
| 10 | Blacksmith 鐵匠 | 4057 | Arch Bishop |
| 11 | Hunter 獵人 | 4058 | Mechanic |
| 12 | Assassin 刺客 | 4059 | Guillotine Cross |
| 23 | Super Novice | 4252 | Dragon Knight (四轉) |
| 14 | Crusader | 4255 | Arch Mage |
| 15 | Monk 武僧 | 4256 | Cardinal |
| 19 | Bard 詩人 | 4279 | Hyper Novice |

### 常用地圖

```
@warp prontera      # 普隆德拉
@warp geffen        # 乙乏菲斯
@warp payon         # 乙弓
@warp morocc        # 摩洛哥
@warp aldebaran     # 乙德巴朗
@warp comodo        # 乙梅多
@warp yuno          # 朱諾
@warp rachel        # 雷乙兒
@warp malangdo      # 貓咪島
```
