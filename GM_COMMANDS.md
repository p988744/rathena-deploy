# GM 指令速查表

## 角色培養

```
@baselvl <lv>              # 設定基本等級（最高 200）
@joblvl <lv>               # 設定職業等級（最高 60）
@job <id>                  # 轉職（見下方 ID 表）
@allskill                  # 學會全部技能
@stpoint <num>             # 給予屬性點數
@skpoint <num>             # 給予技能點數
@str <val>                 # 設定 STR（最高 130）
@agi <val>                 # 設定 AGI
@vit <val>                 # 設定 VIT
@int <val>                 # 設定 INT
@dex <val>                 # 設定 DEX
@luk <val>                 # 設定 LUK
@pow <val>                 # 四轉特性值 Power
@sta <val>                 # 四轉特性值 Stamina
@wis <val>                 # 四轉特性值 Wisdom
@spl <val>                 # 四轉特性值 Spell
@con <val>                 # 四轉特性值 Concentration
@crt <val>                 # 四轉特性值 Creative
@reset                     # 重置屬性 + 技能
@statreset                 # 只重置屬性
@skillreset                # 只重置技能
```

### 一鍵滿等

```
@baselvl 200
@joblvl 60
@allskill
@str 130
@agi 130
@vit 130
@int 130
@dex 130
@luk 130
```

## 道具

```
@item <id> <數量>          # 取得道具
@item2 <id> <數量> <identified> <refine> <attribute> <card1> <card2> <card3> <card4>
@delitem <id> <數量>       # 刪除道具
@itemreset                 # 清空背包
@storage                   # 開啟倉庫
@guildstorage              # 開啟公會倉庫
@autoloot <rate>           # 自動撿取（0~100%）
@alootid <id>              # 自動撿取指定道具
@alootid reset             # 清除自動撿取清單
```

### 常用道具 ID

| ID | 道具 | ID | 道具 |
|----|------|----|------|
| 501 | 紅色藥水 | 607 | 伊吉拉神之果實 |
| 502 | 橙色藥水 | 608 | 伊吉拉聖水 |
| 503 | 黃色藥水 | 12210 | 泡泡糖 (經驗+50%) |
| 504 | 白色藥水 | 12211 | 戰鬥手冊 (經驗+50%) |
| 505 | 藍色藥水 | 7621 | 古木樹枝 (召喚 MVP) |
| 506 | 綠色藥水 | 7227 | 死神樹枝 (召喚一般怪) |
| 601 | 蒼蠅翅膀 | 6635 | 豐饒之角 |
| 602 | 蝴蝶翅膀 | 14003 | 十字軍轉職證書 |
| 604 | 萬能藥 | 4001-4999 | 卡片區間 |

## 移動與傳送

```
@warp <地圖> <x> <y>      # 傳送到指定地圖座標
@go <number>               # 傳送到主城
@jump                      # 隨機跳轉同地圖
@load                      # 回存檔點
@save                      # 儲存目前位置為存檔點
@memo <slot>               # 記憶傳送點（0~2）
@where                     # 顯示目前座標
@mapinfo                   # 顯示地圖資訊
```

### @go 城市列表

| # | 城市 | # | 城市 |
|---|------|---|------|
| 0 | Prontera 普隆德拉 | 8 | Comodo 乙梅多 |
| 1 | Morocc 摩洛哥 | 9 | Yuno 朱諾 |
| 2 | Geffen 吉芬 | 10 | Amatsu 天津 |
| 3 | Payon 斐揚 | 11 | Gonryun 崑崙 |
| 4 | Alberta 亞爾乙特 | 12 | Umbala |
| 5 | Izlude 伊茲魯德 | 13 | Niflheim 乙芙乙海姆 |
| 6 | Al De Baran 乙德巴朗 | 14 | Louyang 洛陽 |
| 7 | Lutie 魯提耶 | 15 | Novice Ground |

### 常用地圖名

```
prontera     # 普隆德拉
morocc       # 摩洛哥
geffen       # 吉芬
payon        # 斐揚
alberta      # 亞爾乙特
izlude       # 伊茲魯德
aldebaran    # 乙德巴朗
yuno         # 朱諾
rachel       # 雷契爾
veins        # 維因斯
hugel        # 休乙爾
lighthalzen  # 利希特城
einbroch     # 乙音布雷希
malangdo     # 貓咪島
eclage       # 乙克拉久
mora         # 墨拉
lasagna      # 拉薩那
prt_fild08   # 普隆德拉南方
pay_dun00    # 斐揚洞穴 1F
gef_dun00    # 吉芬地下城 1F
moc_pryd01   # 摩洛哥金字塔 1F
```

## 怪物

```
@monster <id>              # 召喚 1 隻怪物
@monster <id> <數量>       # 召喚多隻
@summon <id> <秒>          # 召喚跟隨怪物
@killmonster               # 殺死地圖上所有怪物
@mobsearch <id>            # 搜尋地圖上的怪物
@whereis <id>              # 查詢怪物出沒地圖
@mobinfo <id>              # 查詢怪物詳細資訊
```

### 常用怪物 ID

| ID | 怪物 | 備註 |
|----|------|------|
| 1002 | Poring 波利 | |
| 1038 | Osiris 歐西里斯 | MVP |
| 1039 | Baphomet 巴風特 | MVP |
| 1046 | Doppelganger | MVP |
| 1059 | Mistress 蜂后 | MVP |
| 1086 | Golden Thief Bug 黃金蟲 | MVP |
| 1087 | Orc Hero 獸人英雄 | MVP |
| 1088 | Orc Lord 獸人酋長 | MVP |
| 1089 | Maya 螳螂女王 | MVP |
| 1112 | Drake 乘風破浪 | MVP |
| 1115 | Eddga 虎王 | MVP |
| 1147 | Maya 瑪雅 | MVP |
| 1150 | Moonlight 月夜花 | MVP |
| 1159 | Phreeoni | MVP |
| 1252 | Turtle General 龜將軍 | MVP |
| 1272 | Dark Lord 暗黑之王 | MVP |
| 1312 | Thanatos | MVP |
| 1373 | Lord of the Dead | MVP |
| 1418 | Beelzebub 蒼蠅之王 | MVP |
| 1492 | Ifrit 伊弗利特 | MVP |
| 1583 | Tao Gunka 大長老 | MVP |
| 1708 | Nidhoggur Shadow | MVP |
| 1785 | Atroce 暴虐之徒 | MVP |
| 2068 | Naght Sieger | MVP |
| 20611 | 巴基力英格麗 | MVP |

## 戰鬥與狀態

```
@heal                      # 回滿 HP/SP
@alive                     # 復活自己
@speed <val>               # 移動速度（0=最快, 400=預設）
@killable                  # 切換可被攻擊狀態
@invincible                # 切換無敵狀態
@hide                      # 隱身
@disguise <mob_id>         # 變身成怪物
@undisguise                # 解除變身
@size <0-2>                # 改變大小（0=小, 1=中, 2=大）
```

## 對其他玩家

```
@recall <name>             # 召喚玩家到身邊
@recallall                 # 召喚所有玩家
@kick <name>               # 踢出玩家
@ban <time> <name>         # 封鎖玩家（例: @ban 7d player1）
@unban <name>              # 解封
@mute <min> <name>         # 禁言
@unmute <name>             # 解除禁言
@jail <name>               # 關入監獄
@unjail <name>             # 釋放
@charbaselvl <lv> <name>   # 設定他人等級
@charjoblvl <lv> <name>    # 設定他人職業等級
```

## 伺服器管理

```
@reloadscript              # 重新載入 NPC 腳本
@reloadbattleconf          # 重新載入戰鬥設定
@reloaditemdb              # 重新載入道具資料庫
@reloadmobdb               # 重新載入怪物資料庫
@reloadskilldb             # 重新載入技能資料庫
@who                       # 線上玩家列表
@uptime                    # 伺服器運行時間
@rates                     # 顯示目前倍率
@npc <npc_name>            # 開啟 NPC 對話
```

## 活動用

```
@pvpon                     # 開啟 PVP
@pvpoff                    # 關閉 PVP
@gvgon                     # 開啟 GVG
@gvgoff                    # 關閉 GVG
@agitstart                 # 開始攻城戰
@agitend                   # 結束攻城戰
@night                     # 設定為夜晚
@day                       # 設定為白天
@weather <0-4>             # 天氣（0=晴, 1=雪, 2=霧, 3=櫻花, 4=落葉）
@effect <id>               # 播放效果
@skillon                   # 允許使用技能
@skilloff                  # 禁止使用技能
```

## 轉職 ID 對照表

### 一般職業

| ID | 職業 | ID | 職業 |
|----|------|----|------|
| 0 | Novice 初心者 | 7 | Knight 騎士 |
| 1 | Swordman 劍士 | 8 | Priest 祭司 |
| 2 | Mage 魔法師 | 9 | Wizard 巫師 |
| 3 | Archer 弓箭手 | 10 | Blacksmith 鐵匠 |
| 4 | Acolyte 服事 | 11 | Hunter 獵人 |
| 5 | Merchant 商人 | 12 | Assassin 刺客 |
| 6 | Thief 盜賊 | 23 | Super Novice |

### 轉生

| ID | 職業 | ID | 職業 |
|----|------|----|------|
| 4001 | High Novice | 4008 | Lord Knight |
| 4002 | High Swordman | 4009 | High Priest |
| 4003 | High Mage | 4010 | High Wizard |
| 4004 | High Archer | 4011 | Whitesmith |
| 4005 | High Acolyte | 4012 | Sniper |
| 4006 | High Merchant | 4013 | Assassin Cross |
| 4007 | High Thief | 4014 | Paladin |
|  |  | 4015 | Champion |
|  |  | 4016 | Professor |
|  |  | 4017 | Stalker |
|  |  | 4018 | Creator |
|  |  | 4019 | Clown |
|  |  | 4020 | Gypsy |

### 三轉

| ID | 職業 | ID | 職業 |
|----|------|----|------|
| 4054 | Rune Knight | 4066 | Royal Guard |
| 4055 | Warlock | 4067 | Sorcerer |
| 4056 | Ranger | 4068 | Minstrel |
| 4057 | Arch Bishop | 4069 | Wanderer |
| 4058 | Mechanic | 4070 | Sura |
| 4059 | Guillotine Cross | 4071 | Genetic |
|  |  | 4072 | Shadow Chaser |

### 四轉

| ID | 職業 | ID | 職業 |
|----|------|----|------|
| 4252 | Dragon Knight | 4258 | Imperial Guard |
| 4253 | Meister | 4259 | Biolo |
| 4254 | Shadow Cross | 4260 | Abyss Chaser |
| 4255 | Arch Mage | 4261 | Elemental Master |
| 4256 | Cardinal | 4262 | Inquisitor |
| 4257 | Windhawk | 4279 | Hyper Novice |

### 特殊職業

| ID | 職業 | ID | 職業 |
|----|------|----|------|
| 23 | Super Novice | 4190 | Expanded SN |
| 24 | Gunslinger | 4211 | Rebellion |
| 25 | Ninja | 4212 | Kagerou |
| 4046 | Taekwon | 4213 | Oboro |
| 4047 | Star Gladiator | 4215 | Star Emperor |
| 4049 | Soul Linker | 4216 | Soul Reaper |
| 4218 | Summoner 喵族 | 4279 | Hyper Novice |
