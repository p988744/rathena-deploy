# 版本相容性對照表

本文件記錄客戶端與伺服器各組件的版本對應關係。
**更換任何組件前務必確認相容性。**

## 目前穩定版本 (v1.0.0)

```
┌─────────────────────────────────────────────────────┐
│  kRO Full Client    : 2022-07-21                    │
│  Ragexe.exe         : 2022-04-06 (unpacked)         │
│  PACKETVER          : 20220406                      │
│  rAthena Branch     : master                        │
│  BUILD_MODE         : re (Renewal)                  │
│  NEMO Patcher       : 4144/Nemo (gitlab)            │
│  Packet Obfuscation : Disabled                      │
│  Password Encryption: Disabled (plaintext 0x0064)   │
└─────────────────────────────────────────────────────┘
```

## 版本綁定規則

### 1. PACKETVER ↔ Ragexe.exe（強綁定）

PACKETVER 必須與 Ragexe.exe 的日期完全一致。

```
Ragexe: 2022-04-06_Ragexe_1648707856.exe
                    ~~~~~~~~
PACKETVER: 20220406 ← 對應此日期
```

不匹配會導致：登入時伺服器收到封包但無法解析，直接斷線。

### 2. kRO Full Client ↔ Ragexe.exe（需相容）

kRO Client 日期需 **≥** Ragexe 日期，否則 GRF 中可能缺少 Ragexe 需要的資源檔。

```
OK:  kRO 2022-07-21 + Ragexe 2022-04-06  (GRF 較新)
OK:  kRO 2022-04-06 + Ragexe 2022-04-06  (同期)
NG:  kRO 2021-04-06 + Ragexe 2022-04-06  (GRF 太舊)
```

### 3. NEMO Patches ↔ Ragexe.exe（需對應）

NEMO 的 patch pattern 是依照 Ragexe 版本比對的。
不同日期的 Ragexe 可能有些 patch 找不到匹配（顯示紅色圓點）。

### 4. Packet Obfuscation（Server ↔ Client 同步）

| Server | Client NEMO Patch | 結果 |
|--------|-------------------|------|
| `#undef PACKET_OBFUSCATION` | "Disable packets id encryption" ✓ | **OK** |
| 不 undef（預設啟用） | "Disable packets id encryption" ✓ | NG：封包不匹配 |
| `#undef PACKET_OBFUSCATION` | 未勾 "Disable packets id encryption" | NG：封包不匹配 |
| 不 undef（預設啟用） | 未勾 "Disable packets id encryption" | OK（但需要 key 匹配） |

### 5. Password Encryption（Server ↔ Client 同步）

| Server login_conf | Client NEMO Patch | clientinfo.xml | 結果 |
|-------------------|-------------------|----------------|------|
| use_MD5_passwords: no | "Restore old login packet" ✓ | 無 passwordencrypt | **OK（目前）** |
| use_MD5_passwords: yes | "Restore old login packet" ✓ | 無 passwordencrypt | OK |
| use_MD5_passwords: no | 未勾 "Restore old login packet" | 有 passwordencrypt | OK（但 new_account 不可用） |

## 各組件取得來源

| 組件 | 來源 | 備註 |
|------|------|------|
| kRO Full Client | Mega 下載 | `kRO_FullClient_20220721.zip` (3.8GB) |
| Ragexe (unpacked) | nemo.herc.ws | 需用 Python 2 腳本下載 |
| NEMO Patcher | gitlab.com/4144/Nemo | Windows 程式，macOS 用 Wine |
| rAthena | github.com/rathena/rathena | Dockerfile 自動 git clone |
| ROenglishRE | github.com/llchrisll/ROenglishRE | 只用 msgstringtable.txt 等文字檔 |

## 升級注意事項

### 升級 rAthena（不改 PACKETVER）

影響範圍：伺服器端
```bash
# 只需重新 build + deploy
./build.sh && ./deploy.sh
```

### 升級 Ragexe + PACKETVER

影響範圍：伺服器端 + 客戶端
1. 從 nemo.herc.ws 下載新的 unpacked Ragexe
2. 修改 `.env` 中的 `PACKETVER`
3. 重新 build 伺服器
4. 用 NEMO 重新 patch 新 Ragexe
5. 確認 kRO Client GRF 日期 ≥ 新 Ragexe 日期
6. **所有玩家需更新客戶端**

### 升級 kRO Full Client

影響範圍：客戶端
1. 下載新的 kRO Full Client
2. 在新目錄解壓
3. 將 client patch 檔案覆蓋進去
4. 測試確認無 Lua 錯誤
5. **所有玩家需更新客戶端**

### 切換 Renewal ↔ Pre-Renewal

影響範圍：伺服器端
1. 修改 `.env` 的 `BUILD_MODE=pre-re`
2. 重新 build + deploy
3. 清空資料庫（不同模式的資料不通用）
