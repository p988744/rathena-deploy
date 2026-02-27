# 繁體中文化客戶端 — 規劃文件

> 建立日期：2026-02-26

## 1. 現況分析

### 1.1 客戶端基本資訊
- **kRO Full Client**: 2022-07-21
- **Ragexe**: 2022-04-06 (NEMO patched, 12 patches)
- **PACKETVER**: 20220406
- **langtype**: 0 (Korean)
- **DATA.INI**: rdata.grf > data.grf
- **已啟用 patch**: "Read Data Folder First" — data/ 資料夾優先於 GRF

### 1.2 目前已有的翻譯檔案

| 檔案 | 行數 | 語言 | 來源 |
|------|------|------|------|
| `data/msgstringtable.txt` | 4,022 | 英文 | ROenglishRE |
| `data/cardprefixnametable.txt` | 1,604 | 英文 | ROenglishRE |
| `data/mapnametable.txt` | 1,344 | 英文 | ROenglishRE |
| `data/questid2display.txt` | 33,475 | 英文 | ROenglishRE |

### 1.3 GRF 內尚未覆蓋的關鍵 Lua 檔案（韓文原版）

| 檔案 | 大小 | 說明 |
|------|------|------|
| `System/itemInfo_true.lub` | 7.2MB | 道具名稱與描述 (compiled bytecode) |
| `System/tipbox.lub` | 955KB | 提示框文字 |
| `System/achievement_list.lub` | 142KB | 成就列表 |
| GRF 內 `skillinfoz/` | 多檔 | 技能名稱、描述、技能樹 |
| GRF 內 `datainfo/` | 多檔 | 職業名、飾品名、寵物資訊 |

## 2. 現有翻譯資源

### 2.1 可用的中文資源

| 資源 | 語言 | 可用性 |
|------|------|--------|
| [kukuasir1/RO-client-side-chinese-translation](https://github.com/kukuasir1/RO-client-side-chinese-translation) | **簡體中文** | 含 itemInfo, skilldescript, msgstringtable 等，需簡繁轉換 |
| [OpenKore twRO tables](https://github.com/OpenKore/openkore/tree/master/tables/twRO) | **繁體中文** | twRO 的部分對照表，非完整客戶端翻譯 |
| [scriptord3/Ragnarok-Client-Scripts](https://github.com/scriptord3/Ragnarok-Client-Scripts) | 韓文原始碼 | 反編譯的 kRO Lua，可作為翻譯源檔案 |
| [PandasWS/Pandas](https://github.com/PandasWS/Pandas) | 簡繁中文 | 基於 rAthena 的中文模擬器，有 UTF-8 支援 |

**結論**：不存在直接可用的完整繁體中文翻譯。最接近的是 kukuasir1 簡體中文 + OpenCC 簡繁轉換。

## 3. 需翻譯的檔案清單（按優先度）

### 第一層：data/ 文字檔（最安全）

| 檔案 | 行數 | 優先度 |
|------|------|--------|
| `msgstringtable.txt` | 4,022 | 最高 |
| `cardprefixnametable.txt` | 1,604 | 高 |
| `mapnametable.txt` | 1,344 | 高 |
| `questid2display.txt` | 33,475 | 中 |

### 第二層：System/ lub 檔案（需反編譯）

| 檔案 | 大小 | 優先度 |
|------|------|--------|
| `itemInfo_true.lub` | 7.2MB | 最高 |

### 第三層：GRF 內 Lua 檔案（需提取）

| 目錄 | 檔案 | 優先度 |
|------|------|--------|
| `skillinfoz/` | skilldescript.lua, skillinfolist.lua | 最高 |
| `datainfo/` | jobname.lua, accname.lua, petinfo.lua | 高 |
| `stateicon/` | stateiconinfo.lua | 中 |

### 第四層：exe 內嵌文字

- TranslateClient patch + 繁中版 TranslateClient.txt
- 風險較高，建議最後處理

### 第五層：NPC 對話（伺服器端）

- 約 38 萬條文字，工作量巨大
- 建議保留英文或跳過

## 4. NEMO 需新增的 Patches

在現有 12 個 patch 基礎上：

| Patch | 設定值 | 用途 |
|-------|--------|------|
| **SetFontCharset** | 136 (CHINESEBIG5_CHARSET) | **必要** — 否則無法渲染繁中字元 |
| **UseCustomFont / SetFontName** | "Microsoft JhengHei" | 替換韓文字型為繁中字型 |
| **IgnoreLuaErrors** | — | 防護翻譯期間的 Lua 錯誤 |
| FixCharsetForFonts | — | 可能需要，修正字型 charset 映射 |

### 字型處理

目前 `System/font/` 有 SCDream4.otf, SCDream6.otf — 韓文字型，**不支援繁中**。

建議方案：用 NEMO SetFontName patch 指定系統字型（如 Microsoft JhengHei），不需修改字型檔。

## 5. LLM 翻譯可行性

| 檔案類型 | 可行性 | 預估工時 | 策略 |
|---------|--------|---------|------|
| msgstringtable.txt | **高** | 2-4h | 分批 500 行，保留 %d/%s/^色碼 |
| cardprefix/mapname | **高** | 2-4h | 簡單逐行翻譯 |
| itemInfo (lua) | **中高** | 8-16h | 反編譯 → 提取字串 → 分批翻譯 → 回填 |
| skilldescript/info | **中高** | 4-8h | 結構化 table，提取字串翻譯 |
| TranslateClient.txt | **中** | 4-8h | 需 Big5 hex 編碼轉換 |
| NPC 對話 | **低** | 不建議 | 38 萬條，工作量過大 |
| **合計** | | **34-68h** | |

**最佳策略**：kukuasir1 簡體中文 + OpenCC 簡繁轉換 + LLM 校對/補充

## 6. 技術方案

### 6.1 檔案覆蓋機制

已啟用 "Read Data Folder First"：
```
優先順序: data/ 資料夾 > rdata.grf > data.grf
```

只需將翻譯後的檔案放在 `client/data/` 或 `client/System/`，不需修改 GRF。

### 6.2 編碼策略

- **建議使用 Big5 編碼**（配合 SetFontCharset=136）
- 原生支援，不需額外 patch
- 如需 UTF-8，可參考 PandasWS/Pandas 的方案

### 6.3 關鍵技術決策

| 決策 | 建議 | 理由 |
|------|------|------|
| 文字編碼 | Big5 | 原生支援，不需額外 patch |
| 字型方案 | NEMO 指定系統字型 | 簡單，無需打包字型 |
| itemInfo 基底 | kukuasir1 簡體版 + OpenCC | 省時省力 |
| 翻譯引擎 | LLM + 人工校對 | 效率最高 |
| TranslateClient | 先不啟用 | 風險較高 |
| NPC 對話 | 保留英文 | 工作量過大 |

## 7. 實施計畫

### Phase 1：msgstringtable.txt + 字型 patch (Day 1)
1. 備份現有 `client/data/`
2. LLM 翻譯 msgstringtable.txt（英→繁中）
3. NEMO 新增 SetFontCharset=136 + SetFontName
4. 測試繁中文字顯示

### Phase 2：其他文字檔 (Day 2)
1. 翻譯 cardprefixnametable.txt, mapnametable.txt
2. 測試驗證

### Phase 3：GRF Lua 提取 (Day 3)
1. 用 GRF Editor 或 zextractor 提取 lua 檔案
2. 用 unluac 反編譯 itemInfo_true.lub

### Phase 4：itemInfo 翻譯 (Day 4-6)
1. kukuasir1 簡體版 → OpenCC 簡繁轉換
2. LLM 校對 + 補充缺失項目
3. 測試道具名稱與描述

### Phase 5：技能/職業翻譯 (Day 7-9)
1. skilldescript.lua, skillinfolist.lua 翻譯
2. jobname.lua, accname.lua 翻譯
3. 逐檔測試（避免 Lua 錯誤）

### Phase 6：整合測試 (Day 10)
1. 完整功能測試
2. 修正亂碼/Lua 錯誤

## 8. 風險與回退

### 風險

| 風險 | 影響 | 緩解 |
|------|------|------|
| Lua 語法錯誤 | 崩潰/功能異常 | IgnoreLuaErrors patch + 逐檔測試 |
| itemInfo 版本不匹配 | 道具圖片錯誤 | 只翻譯 text 欄位，不改 resource 欄位 |
| 字型 charset 不匹配 | 亂碼 | 正確設定 charset=136 + 測試不同字型 |
| lub 反編譯失敗 | 無法翻譯 itemInfo | 多種工具嘗試 + kukuasir1 版本作備案 |

### 回退方案

- 每個 Phase 獨立可回退
- 刪除 `data/luafiles514/` 即可恢復 GRF 原版
- 完整回退：從 `ro-client-v1.0.zip` 還原

## 9. 版本管理

- 分支：`feature/localization-zhtw`
- 每個 phase 完成後 commit
- 翻譯檔案放在 `client/data/` 和 `client/System/`
- 確認 `.gitignore` 不排除 `data/luafiles514/` 路徑

## 10. 參考資源

- [kukuasir1 簡體中文翻譯](https://github.com/kukuasir1/RO-client-side-chinese-translation)
- [OpenKore twRO tables](https://github.com/OpenKore/openkore/tree/master/tables/twRO)
- [ROenglishRE](https://github.com/llchrisll/ROenglishRE)
- [scriptord3 Ragnarok Client Scripts](https://github.com/scriptord3/Ragnarok-Client-Scripts)
- [PandasWS/Pandas](https://github.com/PandasWS/Pandas)
- [GRF Editor](https://rathena.org/board/files/file/2766-grf-editor/)
- [unluac](https://sourceforge.net/projects/unluac/)
- [NEMO Patcher](http://nemo.herc.ws/patches/)
