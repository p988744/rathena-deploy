# 活動 NPC 與自訂道具設計 — 規劃文件

> 建立日期：2026-02-26

## 一、NPC 腳本語法速查

### 1.1 NPC 腳本標頭格式

```
地圖名,X座標,Y座標,面向方向	script	NPC名稱	精靈ID,{
    // 腳本內容
}
```

面向方向: 0=無方向, 1=西北, 2=北, 3=東北, 4=西, 5=中間, 6=東, 7=西南, 8=南

### 1.2 變數類型

| 前綴 | 類型 | 範圍 | 持久性 |
|------|------|------|--------|
| `name` | 整數 | 角色 | 永久 |
| `name$` | 字串 | 角色 | 永久 |
| `@name` | 整數 | 角色 | 暫時(登出消失) |
| `@name$` | 字串 | 角色 | 暫時 |
| `$name` | 整數 | 全域 | 永久 |
| `.name` | 整數 | NPC | 永久(NPC重載消失) |
| `.@name` | 整數 | 函式範圍 | 暫時 |
| `#name` | 整數 | 帳號 | 永久 |
| `##name` | 整數 | 全域帳號 | 永久 |

### 1.3 常用指令

| 指令 | 說明 |
|------|------|
| `mes "文字";` | 顯示訊息 |
| `next;` | 等待玩家按下一步 |
| `close;` | 關閉對話 |
| `end;` | 結束腳本 |
| `menu "選項1",L_Label1,"選項2",L_Label2;` | 選單 |
| `select("選項1","選項2","選項3")` | 選擇(回傳 1~N) |
| `getitem <id>,<數量>;` | 給予道具 |
| `delitem <id>,<數量>;` | 刪除道具 |
| `countitem(<id>)` | 計算道具數量 |
| `Zeny += 1000;` | 增減 Zeny |
| `percentheal 100,100;` | HP/SP 全恢復 |
| `sc_start <type>,<duration_ms>,<level>;` | 施加狀態 |
| `warp "地圖",X,Y;` | 傳送 |
| `resetstatus;` | 重置屬性 |
| `resetskill;` | 重置技能 |
| `announce "訊息",bc_all;` | 全服廣播 |
| `rand(N)` | 隨機數 0~N-1 |
| `BaseLevel` | 角色基本等級 |
| `strcharinfo(0)` | 角色名稱 |

### 1.4 特殊事件標籤

- `OnInit:` — 伺服器啟動時執行
- `OnClock<HHMM>:` — 每日定時觸發
- `OnPCLoginEvent:` — 玩家登入時
- `OnPCDieEvent:` — 玩家死亡時
- `OnTouch:` — 玩家靠近 NPC 時

## 二、重大技術發現：entrypoint.sh 的 NPC 載入缺陷

### 問題

目前 `entrypoint.sh` 只將 NPC 檔案複製到 `npc/custom/`，但 rAthena **不會自動載入**該目錄下的腳本。每個 NPC 檔案必須在 `npc/scripts_custom.conf` 中註冊才會被載入。

### 解決方案

修改 `entrypoint.sh`，在複製 NPC 檔案後自動掃描並註冊：

```bash
if [ -d "/rathena-custom/npc" ]; then
    echo "   發現自訂 NPC 腳本，正在套用..."
    cp -rf /rathena-custom/npc/* /rathena/npc/custom/ 2>/dev/null || true

    # 自動註冊自訂 NPC 到 scripts_custom.conf
    for f in /rathena/npc/custom/*.txt; do
        if [ -f "$f" ]; then
            SCRIPT_NAME=$(basename "$f")
            if ! grep -q "npc/custom/${SCRIPT_NAME}" /rathena/npc/scripts_custom.conf; then
                echo "npc: npc/custom/${SCRIPT_NAME}" >> /rathena/npc/scripts_custom.conf
                echo "   → 已註冊: ${SCRIPT_NAME}"
            fi
        fi
    done
fi
```

同樣，支援自訂道具資料庫：
```bash
if [ -d "/rathena-custom/db" ]; then
    echo "   發現自訂資料庫，正在套用..."
    cp -rf /rathena-custom/db/* /rathena/db/ 2>/dev/null || true
fi
```

## 三、5 個 NPC 設計方案

### 方案 1：每日簽到 NPC

**位置**：`custom/npc/daily_checkin.txt`

```
prontera,155,185,4	script	每日簽到員	4_F_KAFRA1,{
    mes "[每日簽到員]";
    mes "歡迎來到每日簽到！";
    mes "累計簽到天數: " + checkin_count;
    next;

    .@today = gettime(7)*10000 + gettime(6)*100 + gettime(3);
    if (checkin_lastday == .@today) {
        mes "[每日簽到員]";
        mes "你今天已經簽到過了喔！明天再來吧～";
        close;
    }

    checkin_lastday = .@today;
    checkin_count++;

    getitem 7227,5;  // 死神樹枝 x5
    Zeny += 50000;

    mes "[每日簽到員]";
    mes "簽到成功！獲得:";
    mes "- 50,000 Zeny";
    mes "- 死神樹枝 x5";

    if (checkin_count % 7 == 0) {
        getitem 7621,1;  // 古木樹枝(MVP召喚)
        mes "^FF0000[七日獎勵] 古木樹枝 x1！^000000";
    }
    if (checkin_count == 30) {
        getitem 12210,10; // 泡泡糖 x10
        mes "^0000FF[30日里程碑] 泡泡糖 x10！^000000";
    }
    close;
}
```

### 方案 2：轉蛋機 NPC

**位置**：`custom/npc/gacha_machine.txt`

```
prontera,160,185,4	script	神秘轉蛋機	1_ETC_04,{
    mes "[神秘轉蛋機]";
    mes "每次抽取費用: ^FF0000500,000 Zeny^000000";
    next;

    if (select("投入 500,000 Zeny 抽獎:離開") == 2) close;
    if (Zeny < 500000) { mes "Zeny 不足！"; close; }
    Zeny -= 500000;

    .@roll = rand(10000);

    if (.@roll < 100) {          // 1% SSR
        .@prize = callfunc("F_Rand",4302,4305,4365,4367);
        announce strcharinfo(0) + " 從轉蛋機抽到了 SSR 獎品！",bc_all;
    } else if (.@roll < 500) {   // 4% SR
        .@prize = callfunc("F_Rand",2357,2358,2514,2515);
    } else if (.@roll < 2000) {  // 15% R
        .@prize = callfunc("F_Rand",607,608,12210,12211);
    } else {                     // 80% N
        .@prize = callfunc("F_Rand",501,502,503,504,505,506);
    }

    getitem .@prize,1;
    mes "[神秘轉蛋機]";
    mes "恭喜！抽到獎品了！";
    close;
}
```

### 方案 3：支援祭司 NPC（Buff & 回復）

**位置**：`custom/npc/buff_healer.txt`

```
prontera,150,185,4	script	支援祭司	4_F_PRIEST,{
    mes "[支援祭司]";
    mes "需要什麼服務呢？";
    next;

    switch(select("全回復 + Buff:僅回復:僅 Buff:移除負面狀態:離開")) {
    case 1:
        percentheal 100,100;
        callsub S_Buff;
        mes "[支援祭司]"; mes "已回復並施加全套增益效果！"; close;
    case 2:
        percentheal 100,100;
        mes "[支援祭司]"; mes "HP/SP 已完全回復！"; close;
    case 3:
        callsub S_Buff;
        mes "[支援祭司]"; mes "增益效果已施加！"; close;
    case 4:
        callsub S_Debuff;
        mes "[支援祭司]"; mes "負面狀態已全部移除！"; close;
    case 5: close;
    }

S_Buff:
    sc_start SC_BLESSING,1800000,10;
    sc_start SC_INC_AGI,1800000,10;
    sc_start SC_ASSUMPTIO,1800000,5;
    sc_start SC_GLORIA,1800000,5;
    sc_start SC_MAGNIFICAT,1800000,5;
    sc_start SC_IMPOSITIO,1800000,5;
    return;

S_Debuff:
    sc_end SC_POISON; sc_end SC_CURSE; sc_end SC_SILENCE;
    sc_end SC_CONFUSION; sc_end SC_BLIND; sc_end SC_BLEEDING;
    sc_end SC_STONE; sc_end SC_FREEZE; sc_end SC_STUN;
    return;
}
```

### 方案 4：挑戰競技場 NPC

**位置**：`custom/npc/challenge_arena.txt`

使用 `guild_vs1` ~ `guild_vs3` 地圖，選擇難度後傳送進入並召喚 MVP。擊敗後回管理員處領獎。

- 初級 (Lv50+)：Orc Lord
- 中級 (Lv99+)：Baphomet
- 高級 (Lv150+)：Beelzebub

### 方案 5：萬能管理員 NPC

**位置**：`custom/npc/utility_npc.txt`

整合城鎮/迷宮傳送、重置屬性技能、修理裝備等功能到一個 NPC。

## 四、自訂道具

### 4.1 YAML 格式 (`custom/db/import/item_db.yml`)

```yaml
Header:
  Type: ITEM_DB
  Version: 3

Body:
  - Id: 40000
    AegisName: Custom_Ticket
    Name: Activity Ticket
    Type: Etc
    Buy: 0
    Weight: 0

  - Id: 40001
    AegisName: Custom_Exp_Potion
    Name: Super Exp Potion
    Type: Usable
    Buy: 0
    Weight: 10
    Script: |
      sc_start SC_EXPBOOST,3600000,100;
      percentheal 100,100;
```

### 4.2 ID 範圍

- 官方道具：1~29999
- **自訂道具建議使用 40000+**，避免與未來官方更新衝突

## 五、目錄結構

```
ro/server/custom/
├── npc/
│   ├── daily_checkin.txt
│   ├── gacha_machine.txt
│   ├── buff_healer.txt
│   ├── challenge_arena.txt
│   └── utility_npc.txt
├── conf/
│   └── (optional overrides)
└── db/
    └── import/
        └── item_db.yml
```

## 六、實施順序

### Phase 1：基礎設施
1. 修改 `entrypoint.sh` 添加 NPC 自動註冊邏輯
2. 修改 `entrypoint.sh` 添加自訂資料庫複製邏輯

### Phase 2：必備 NPC（先部署最實用的）
1. `buff_healer.txt` — 支援祭司
2. `utility_npc.txt` — 萬能管理員
3. 重啟容器驗證

### Phase 3：活動 NPC
1. `daily_checkin.txt` — 每日簽到
2. `gacha_machine.txt` — 轉蛋機

### Phase 4：進階內容
1. `challenge_arena.txt` — 競技場
2. 自訂道具 `item_db.yml`

## 七、測試與除錯

```
@reloadscript       # 重載所有 NPC 腳本(不需重啟)
@reloaditemdb       # 重載道具資料庫(不需重啟)
@npc <NPC名稱>     # 直接開啟 NPC 對話測試
@loadnpc npc/custom/xxx.txt  # 臨時載入單一腳本測試
```

## 八、注意事項

1. **entrypoint.sh 是最關鍵的修改** — 不修改它，NPC 檔案放進去也不會被載入
2. **一次只加一個 NPC** — 語法錯誤會導致 map-server 載入失敗
3. **變數命名** — 永久角色變數一旦建立就存入資料庫，命名要有前綴避免衝突
4. **50x 倍率經濟平衡** — Zeny 獲取快，轉蛋機定價需 50 萬以上才有意義
5. **精靈 ID** — 使用內建 NPC 精靈（如 `4_F_KAFRA1`）通常不會有問題
