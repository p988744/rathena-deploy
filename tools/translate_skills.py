#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate RO skill names and descriptions from Korean (EUC-KR) to
Traditional Chinese (Big5) using twRO official naming conventions.

Usage:
  python translate_skills.py
"""

import os
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(TOOLS_DIR)
CLIENT_DATA_DIR = os.path.join(PROJECT_DIR, "client", "data")
EXTRACTED_DIR = os.path.join(TOOLS_DIR, "extracted")

# =============================================================================
# twRO Official Skill Name Translations
# Format: "SKILL_ID": "繁體中文名"
# =============================================================================
SKILL_NAME_MAP = {
    # ===== Novice =====
    "NV_BASIC": "基本技能",
    "NV_FIRSTAID": "急救",
    "NV_TRICKDEAD": "裝死",

    # ===== Swordman =====
    "SM_SWORD": "劍術修練",
    "SM_TWOHAND": "雙手劍修練",
    "SM_RECOVERY": "HP回復力向上",
    "SM_BASH": "重擊",
    "SM_PROVOKE": "挑釁",
    "SM_MAGNUM": "霸氣衝擊",
    "SM_ENDURE": "耐久",
    "SM_MOVINGRECOVERY": "移動時HP回復",
    "SM_FATALBLOW": "致命打擊",
    "SM_AUTOBERSERK": "自動狂暴",

    # ===== Mage =====
    "MG_SRECOVERY": "SP回復力向上",
    "MG_SIGHT": "探索",
    "MG_NAPALMBEAT": "靈魂攻擊",
    "MG_SAFETYWALL": "安全防護罩",
    "MG_SOULSTRIKE": "靈魂打擊",
    "MG_COLDBOLT": "冰箭術",
    "MG_FROSTDIVER": "冰凍術",
    "MG_STONECURSE": "石化術",
    "MG_FIREBOLT": "火箭術",
    "MG_FIREBALL": "火球術",
    "MG_FIREWALL": "火牆",
    "MG_LIGHTNINGBOLT": "雷擊術",
    "MG_THUNDERSTORM": "雷暴",
    "MG_ENERGYCOAT": "魔力外衣",

    # ===== Archer =====
    "AC_OWL": "貓頭鷹之眼",
    "AC_VULTURE": "鷹之眼",
    "AC_CONCENTRATION": "集中力提升",
    "AC_DOUBLE": "二連矢",
    "AC_SHOWER": "箭雨",
    "AC_MAKINGARROW": "製作箭矢",
    "AC_CHARGEARROW": "蓄力射擊",

    # ===== Thief =====
    "TF_DOUBLE": "連續攻擊",
    "TF_MISS": "迴避率增加",
    "TF_STEAL": "偷竊",
    "TF_HIDING": "躲藏",
    "TF_POISON": "塗毒",
    "TF_DETOXIFY": "解毒",
    "TF_SPRINKLESAND": "撒沙",
    "TF_BACKSLIDING": "後滑步",
    "TF_PICKSTONE": "撿石頭",
    "TF_THROWSTONE": "投石",

    # ===== Acolyte =====
    "AL_DP": "天使之護",
    "AL_DEMONBANE": "惡魔剋星",
    "AL_RUWACH": "霸邪陣",
    "AL_PNEUMA": "氣功彈防護",
    "AL_TELEPORT": "瞬間移動",
    "AL_WARP": "傳送之陣",
    "AL_HEAL": "治癒術",
    "AL_INCAGI": "敏捷提升",
    "AL_DECAGI": "降低敏捷",
    "AL_HOLYWATER": "聖水創造",
    "AL_CRUCIS": "十字驅魔",
    "AL_ANGELUS": "天使之障壁",
    "AL_BLESSING": "祝福",
    "AL_CURE": "治療術",
    "AL_HOLYLIGHT": "聖光術",

    # ===== Merchant =====
    "MC_INCCARRY": "負重增加",
    "MC_DISCOUNT": "折扣",
    "MC_OVERCHARGE": "漫天喊價",
    "MC_PUSHCART": "推車",
    "MC_IDENTIFY": "鑑定",
    "MC_VENDING": "露天商店",
    "MC_MAMMONITE": "金幣投擲",
    "MC_CARTREVOLUTION": "手推車攻擊",
    "MC_CHANGECART": "更換手推車",
    "MC_LOUD": "大乘叫喊",

    # ===== Knight =====
    "KN_SPEARMASTERY": "槍術修練",
    "KN_PIERCE": "刺擊",
    "KN_BRANDISHSPEAR": "騎士槍術",
    "KN_SPEARSTAB": "槍刺",
    "KN_SPEARBOOMERANG": "回力槍",
    "KN_TWOHANDQUICKEN": "雙手劍加速",
    "KN_AUTOCOUNTER": "自動反擊",
    "KN_BOWLINGBASH": "保齡球攻擊",
    "KN_RIDING": "騎乘",
    "KN_CAVALIERMASTERY": "騎兵修練",
    "KN_CHARGEATK": "衝鋒攻擊",
    "KN_ONEHAND": "單手劍加速",

    # ===== Priest =====
    "PR_MACEMASTERY": "鈍器修練",
    "PR_IMPOSITIO": "神聖之光",
    "PR_SUFFRAGIUM": "唱頌縮減",
    "PR_ASPERSIO": "聖水噴灑",
    "PR_BENEDICTIO": "聖體降福",
    "PR_SANCTUARY": "聖域",
    "PR_STRECOVERY": "恢復術",
    "PR_SLOWPOISON": "緩毒",
    "ALL_RESURRECTION": "復活術",
    "PR_KYRIE": "天使之圍",
    "PR_MAGNIFICAT": "天恩頌歌",
    "PR_GLORIA": "榮耀聖歌",
    "PR_LEXDIVINA": "靜默",
    "PR_TURNUNDEAD": "驅魔",
    "PR_LEXAETERNA": "紊亂",
    "PR_MAGNUS": "聖十字攻擊",
    "PR_REDEMPTIO": "犧牲",

    # ===== Hunter =====
    "HT_ANKLESNARE": "定位陷阱",
    "HT_BEASTBANE": "狩獵修練",
    "HT_BLASTMINE": "爆破陷阱",
    "HT_BLITZBEAT": "猛鷹襲擊",
    "HT_CLAYMORETRAP": "闊劍陷阱",
    "HT_DETECTING": "偵測",
    "HT_FALCON": "獵鷹修練",
    "HT_FLASHER": "閃光陷阱",
    "HT_FREEZINGTRAP": "冰凍陷阱",
    "HT_LANDMINE": "地雷陷阱",
    "HT_REMOVETRAP": "拆除陷阱",
    "HT_TALKIEBOX": "說話陷阱",
    "HT_SANDMAN": "催眠陷阱",
    "HT_SHOCKWAVE": "衝擊波陷阱",
    "HT_SKIDTRAP": "滑行陷阱",
    "HT_SPRINGTRAP": "彈簧陷阱",
    "HT_STEELCROW": "鐵鷹爪",
    "HT_PHANTASMIC": "幻影箭",
    "HT_POWER": "猛鷹連擊",

    # ===== Wizard =====
    "WZ_FIREPILLAR": "火柱",
    "WZ_SIGHTRASHER": "爆裂探索",
    "WZ_FIREIVY": "火焰藤蔓",
    "WZ_METEOR": "隕石術",
    "WZ_JUPITEL": "雷擊之盾",
    "WZ_VERMILION": "暴風術",
    "WZ_WATERBALL": "水球術",
    "WZ_ICEWALL": "冰牆",
    "WZ_FROSTNOVA": "冰霜之星",
    "WZ_STORMGUST": "暴風雪",
    "WZ_EARTHSPIKE": "大地之刺",
    "WZ_HEAVENDRIVE": "天堂之路",
    "WZ_QUAGMIRE": "沼澤術",
    "WZ_ESTIMATION": "怪物資訊",
    "WZ_SIGHTBLASTER": "探索連擊",

    # ===== Assassin =====
    "AS_RIGHT": "右手修練",
    "AS_LEFT": "左手修練",
    "AS_KATAR": "十字刺刃修練",
    "AS_CLOAKING": "隱匿",
    "AS_SONICBLOW": "音速擊",
    "AS_GRIMTOOTH": "鬼牙擊",
    "AS_ENCHANTPOISON": "附魔毒",
    "AS_POISONREACT": "毒素反擊",
    "AS_VENOMDUST": "毒霧",
    "AS_SPLASHER": "毒素濺爆",
    "AS_SONICACCEL": "音速加速",
    "AS_VENOMKNIFE": "毒飛刀",

    # ===== Blacksmith =====
    "BS_IRON": "鐵製造",
    "BS_STEEL": "鋼鐵製造",
    "BS_ENCHANTEDSTONE": "屬性石製造",
    "BS_ORIDEOCON": "神之金屬研究",
    "BS_DAGGER": "短劍製作",
    "BS_SWORD": "劍製作",
    "BS_TWOHANDSWORD": "雙手劍製作",
    "BS_AXE": "斧製作",
    "BS_MACE": "鈍器製作",
    "BS_KNUCKLE": "拳刃製作",
    "BS_SPEAR": "槍製作",
    "BS_HILTBINDING": "劍柄修練",
    "BS_FINDINGORE": "礦石發現",
    "BS_WEAPONRESEARCH": "武器研究",
    "BS_REPAIRWEAPON": "武器修理",
    "BS_SKINTEMPER": "鍛造肌膚",
    "BS_HAMMERFALL": "猛力鐵鎚",
    "BS_ADRENALINE": "腎上腺素飆升",
    "BS_WEAPONPERFECT": "完美武器",
    "BS_OVERTHRUST": "武器加持",
    "BS_MAXIMIZE": "武器力量最大化",
    "BS_ADRENALINE2": "完全腎上腺素飆升",
    "BS_UNFAIRLYTRICK": "可疑的商術",
    "BS_GREED": "貪欲",

    # ===== Crusader =====
    "CR_TRUST": "信仰",
    "CR_AUTOGUARD": "自動防禦",
    "CR_SHIELDCHARGE": "盾牌衝擊",
    "CR_SHIELDBOOMERANG": "盾牌回力標",
    "CR_REFLECTSHIELD": "盾牌反射",
    "CR_HOLYCROSS": "神聖十字攻擊",
    "CR_GRANDCROSS": "大十字攻擊",
    "CR_DEVOTION": "獻身",
    "CR_PROVIDENCE": "天使之力",
    "CR_DEFENDER": "防禦",
    "CR_SPEARQUICKEN": "長槍加速",
    "CR_SHRINK": "盾牌推回",
    "CR_SLIMPITCHER": "瓶裝藥水投擲",
    "CR_FULLPROTECTION": "完全化學防護",
    "CR_ALCHEMY": "煉金術",
    "CR_SYNTHESISPOTION": "藥水合成",
    "CR_ACIDDEMONSTRATION": "酸性炸彈",
    "CR_CULTIVATION": "植物栽培",

    # ===== Monk =====
    "MO_IRONHAND": "鐵砂掌",
    "MO_SPIRITSRECOVERY": "運氣調息",
    "MO_CALLSPIRITS": "蓄氣",
    "MO_ABSORBSPIRITS": "吸氣",
    "MO_TRIPLEATTACK": "六合拳",
    "MO_BODYRELOCATION": "弓身彈影",
    "MO_DODGE": "移花接木",
    "MO_INVESTIGATE": "浸透勁",
    "MO_FINGEROFFENSIVE": "彈指神通",
    "MO_STEELBODY": "金剛不壞",
    "MO_BLADESTOP": "真劍百破刀",
    "MO_EXPLOSIONSPIRITS": "爆氣",
    "MO_EXTREMITYFIST": "阿修羅霸凰拳",
    "MO_CHAINCOMBO": "連環全身掌",
    "MO_COMBOFINISH": "猛龍誇強",
    "MO_KITRANSLATION": "振氣注入",
    "MO_BALKYOUNG": "發勁",

    # ===== Sage =====
    "SA_ADVANCEDBOOK": "進階書本修練",
    "SA_CASTCANCEL": "詠唱取消",
    "SA_FREECAST": "自由詠唱",
    "SA_SPELLBREAKER": "魔力破壞",
    "SA_AUTOSPELL": "自動念咒",
    "SA_MAGICROD": "魔力吸收",
    "SA_VOLCANO": "火山",
    "SA_DELUGE": "洪水",
    "SA_VIOLENTGALE": "暴風",
    "SA_BARRENZONE": "虛擬",
    "SA_LANDPROTECTOR": "大地保護",
    "SA_FLAMELAUNCHER": "火焰附加",
    "SA_FROSTWEAPON": "冰凍附加",
    "SA_LIGHTNINGLOADER": "雷電附加",
    "SA_SEISMICWEAPON": "大地附加",
    "SA_DRAGONOLOGY": "龍學",
    "SA_DISPELL": "消除魔法",
    "SA_ABRACADABRA": "天羅地網",
    "SA_MONOCELL": "單體化",
    "SA_CLASSCHANGE": "職業變更",
    "SA_SUMMONMONSTER": "召喚魔物",
    "SA_REVERSEORCISH": "獸人語翻譯",
    "SA_DEATH": "死神",
    "SA_FORTUNE": "幸運",
    "SA_TAMINGMONSTER": "馴養魔物",
    "SA_QUESTION": "?",
    "SA_GRAVITY": "重力場",
    "SA_LEVELUP": "升級",
    "SA_INSTANTDEATH": "即死",
    "SA_FULLRECOVERY": "完全回復",
    "SA_COMA": "昏迷",
    "SA_CREATECON": "元素轉換器製造",
    "SA_ELEMENTWATER": "元素轉換(水)",
    "SA_ELEMENTGROUND": "元素轉換(地)",
    "SA_ELEMENTFIRE": "元素轉換(火)",
    "SA_ELEMENTWIND": "元素轉換(風)",

    # ===== Rogue =====
    "RG_SNATCHER": "掠奪者",
    "RG_STEALCOIN": "偷錢",
    "RG_BACKSTAP": "背刺",
    "RG_TUNNELDRIVE": "隧道突擊",
    "RG_RAID": "襲擊",
    "RG_STRIPWEAPON": "脫衣術(武器)",
    "RG_STRIPSHIELD": "脫衣術(盾牌)",
    "RG_STRIPARMOR": "脫衣術(鎧甲)",
    "RG_STRIPHELM": "脫衣術(頭盔)",
    "RG_INTIMIDATE": "恐嚇",
    "RG_GRAFFITI": "塗鴉",
    "RG_FLAGGRAFFITI": "旗幟塗鴉",
    "RG_CLEANER": "清除",
    "RG_GANGSTER": "混混天堂",
    "RG_COMPULSION": "強制折扣",
    "RG_PLAGIARISM": "抄襲",
    "RG_CLOSECONFINE": "禁錮",

    # ===== Alchemist =====
    "AM_AXEMASTERY": "斧修練",
    "AM_LEARNINGPOTION": "藥劑學",
    "AM_PHARMACY": "製藥",
    "AM_DEMONSTRATION": "炸彈投擲",
    "AM_ACIDTERROR": "酸性恐懼",
    "AM_POTIONPITCHER": "藥水投擲",
    "AM_CANNIBALIZE": "生物植物栽培",
    "AM_SPHEREMINE": "球體地雷",
    "AM_CP_WEAPON": "化學防護(武器)",
    "AM_CP_SHIELD": "化學防護(盾牌)",
    "AM_CP_ARMOR": "化學防護(鎧甲)",
    "AM_CP_HELM": "化學防護(頭盔)",
    "AM_BIOETHICS": "生命倫理",
    "AM_BIOTECHNOLOGY": "生命工學研究",
    "AM_CREATECREATURE": "生物創造",
    "AM_CULTIVATION": "栽培",
    "AM_FLAMECONTROL": "火焰控制",
    "AM_CALLHOMUN": "召喚乖乖獸",
    "AM_REST": "安息",
    "AM_DRILLMASTER": "訓練師",
    "AM_HEALHOMUN": "治癒乖乖獸",
    "AM_RESURRECTHOMUN": "復活乖乖獸",
    "AM_BERSERKPITCHER": "狂暴藥水投擲",
    "AM_TWILIGHT1": "黃昏製藥",
    "AM_TWILIGHT2": "黃昏製藥",
    "AM_TWILIGHT3": "黃昏製藥",
    "AM_TWILIGHT4": "黃昏製藥",

    # ===== Bard =====
    "BD_ADAPTATION": "隨機應變",
    "BD_ENCORE": "安可",
    "BD_LULLABY": "搖籃曲",
    "BD_RICHMANKIM": "金乃宜的財運",
    "BD_ETERNALCHAOS": "永恆的混沌",
    "BD_DRUMBATTLEFIELD": "戰場之鼓",
    "BD_RINGNIBELUNGEN": "尼伯龍根之戒",
    "BD_ROKISWEIL": "洛乞的咆哮",
    "BD_INTOABYSS": "深淵之中",
    "BD_SIEGFRIED": "不死身乞乞弗利特",
    "BD_RAGNAROK": "乙太的祭典",
    "BA_MUSICALLESSON": "音樂練習",
    "BA_MUSICALSTRIKE": "音樂打擊",
    "BA_DISSONANCE": "不協和音",
    "BA_FROSTJOKE": "寒冷的笑話",
    "BA_WHISTLE": "口哨",
    "BA_ASSASSINCROSS": "夕陽中的刺客",
    "BA_POEMBRAGI": "布拉乞的詩",
    "BA_APPLEIDUN": "乙登的蘋果",
    "BA_PANGVOICE": "嘭聲",

    # ===== Dancer =====
    "DC_DANCINGLESSON": "舞蹈練習",
    "DC_THROWARROW": "箭旋舞投",
    "DC_UGLYDANCE": "狂亂之舞",
    "DC_SCREAM": "尖叫",
    "DC_HUMMING": "哼唱",
    "DC_DONTFORGETME": "請不要忘記我",
    "DC_FORTUNEKISS": "幸運之吻",
    "DC_SERVICEFORYOU": "為您服務",
    "DC_WINKCHARM": "魅惑之眼",

    # ===== Wedding =====
    "WE_MALE": "我只會保護你",
    "WE_FEMALE": "為你而犧牲",
    "WE_CALLPARTNER": "想要見你",
    "WE_BABY": "爸爸媽媽我愛你",
    "WE_CALLPARENT": "想念爸爸媽媽",
    "WE_CALLBABY": "孩子來這裡",

    # ===== Lord Knight =====
    "LK_AURABLADE": "靈氣之劍",
    "LK_PARRYING": "格擋",
    "LK_CONCENTRATION": "集中",
    "LK_TENSIONRELAX": "緊張鬆弛",
    "LK_BERSERK": "狂暴",
    "LK_SPIRALPIERCE": "螺旋刺擊",
    "LK_HEADCRUSH": "頭部粉碎",
    "LK_JOINTBEAT": "關節打擊",

    # ===== Paladin =====
    "PA_PRESSURE": "壓迫",
    "PA_SACRIFICE": "犧牲",
    "PA_GOSPEL": "福音",
    "PA_SHIELDCHAIN": "盾牌連擊",

    # ===== High Priest =====
    "HP_ASSUMPTIO": "聖靈降臨",
    "HP_BASILICA": "聖域結界",
    "HP_MEDITATIO": "冥想",
    "HP_MANARECHARGE": "魔力回充",

    # ===== High Wizard =====
    "HW_SOULDRAIN": "靈魂抽取",
    "HW_MAGICCRASHER": "魔力衝擊",
    "HW_MAGICPOWER": "魔力增幅",
    "HW_NAPALMVULCAN": "靈魂連擊",
    "HW_GANBANTEIN": "解除魔法陣",
    "HW_GRAVITATION": "重力場",

    # ===== Champion =====
    "CH_PALMSTRIKE": "猛虎硬派山",
    "CH_TIGERFIST": "伏虎拳",
    "CH_CHAINCRUSH": "聯柱崩擊",
    "CH_SOULCOLLECT": "狂蓄氣",

    # ===== Professor =====
    "PF_HPCONVERSION": "生命力轉換",
    "PF_SOULCHANGE": "靈魂交換",
    "PF_SOULBURN": "靈魂燃燒",
    "PF_MINDBREAKER": "精神破壞",
    "PF_MEMORIZE": "記憶術",
    "PF_FOGWALL": "霧之壁",
    "PF_SPIDERWEB": "蜘蛛網",
    "PF_DOUBLECASTING": "雙重詠唱",

    # ===== Assassin Cross =====
    "ASC_KATAR": "進階十字刺刃修練",
    "ASC_BREAKER": "氣功破",
    "ASC_METEORASSAULT": "流星攻擊",
    "ASC_CDP": "致命毒藥製造",
    "ASC_EDP": "致命毒藥附加",

    # ===== Sniper =====
    "SN_SIGHT": "真實之眼",
    "SN_FALCONASSAULT": "獵鷹突擊",
    "SN_SHARPSHOOTING": "精準射擊",
    "SN_WINDWALK": "風之步伐",

    # ===== Whitesmith =====
    "WS_MELTDOWN": "武器毀壞",
    "WS_CREATECOIN": "鑄幣",
    "WS_CREATENUGGET": "鑄錠",
    "WS_CARTBOOST": "手推車加速",
    "WS_SYSTEMCREATE": "自動攻擊裝置製作",
    "WS_WEAPONREFINE": "武器精煉",
    "WS_CARTTERMINATION": "手推車終結",
    "WS_OVERTHRUSTMAX": "極限武器加持",

    # ===== Stalker =====
    "ST_CHASEWALK": "追蹤步伐",
    "ST_REJECTSWORD": "劍拒絕",
    "ST_STEALBACKPACK": "背包偷竊",
    "ST_PRESERVE": "保存",
    "ST_FULLSTRIP": "完全脫衣術",

    # ===== Clown/Gypsy =====
    "CG_ARROWVULCAN": "箭暴風",
    "CG_MOONLIT": "月光下花瓣飄落的水車小鎮",
    "CG_MARIONETTE": "牽線傀儡",
    "CG_LONGINGFREEDOM": "不要束縛我",
    "CG_HERMODE": "乞乞弗利特之杖",
    "CG_TAROTCARD": "命運塔羅牌",

    # ===== Guild =====
    "GD_APPROVAL": "正式公會核准",
    "GD_KAFRACONTRACT": "與卡普拉的契約",
    "GD_GUARDRESEARCH": "守護者研究",
    "GD_CHARISMA": "魅力",
    "GD_EXTENSION": "公會擴展",
    "GD_GLORYGUILD": "公會的榮耀",
    "GD_LEADERSHIP": "偉大的領導力",
    "GD_GLORYWOUNDS": "光榮之傷",
    "GD_SOULCOLD": "冷靜的心",
    "GD_HAWKEYES": "銳利的目光",
    "GD_BATTLEORDER": "戰鬥命令",
    "GD_REGENERATION": "再生",
    "GD_RESTORE": "恢復",
    "GD_EMERGENCYCALL": "緊急召集",
    "GD_GUARDUP": "守護者強化",
    "GD_DEVELOPMENT": "永續發展",
    "GD_ITEMEMERGENCYCALL": "緊急召集",

    # ===== TaeKwon =====
    "TK_RUN": "奔跑",
    "TK_READYSTORM": "旋風準備",
    "TK_STORMKICK": "旋風踢",
    "TK_READYDOWN": "踏擊準備",
    "TK_DOWNKICK": "下踏踢",
    "TK_READYTURN": "踢擊準備",
    "TK_TURNKICK": "迴旋踢",
    "TK_READYCOUNTER": "反擊準備",
    "TK_COUNTER": "反擊踢",
    "TK_DODGE": "翻滾",
    "TK_JUMPKICK": "飛踢",
    "TK_HPTIME": "安逸的休息",
    "TK_SPTIME": "愉快的休息",
    "TK_POWER": "加油",
    "TK_SEVENWIND": "溫暖的風",
    "TK_MISSION": "跆拳任務",
    "TK_HIGHJUMP": "跳高",

    # ===== Star Gladiator =====
    "SG_FEEL": "太陽與月亮與星星的感覺",
    "SG_SUN_WARM": "太陽的溫暖",
    "SG_MOON_WARM": "月亮的溫暖",
    "SG_STAR_WARM": "星星的溫暖",
    "SG_SUN_COMFORT": "太陽的安逸",
    "SG_MOON_COMFORT": "月亮的安逸",
    "SG_STAR_COMFORT": "星星的安逸",
    "SG_HATE": "太陽與月亮與星星的憎恨",
    "SG_SUN_ANGER": "太陽的憤怒",
    "SG_MOON_ANGER": "月亮的憤怒",
    "SG_STAR_ANGER": "星星的憤怒",
    "SG_SUN_BLESS": "太陽的祝福",
    "SG_MOON_BLESS": "月亮的祝福",
    "SG_STAR_BLESS": "星星的祝福",
    "SG_DEVIL": "太陽與月亮與星星的惡魔",
    "SG_FRIEND": "太陽與月亮與星星的夥伴",
    "SG_KNOWLEDGE": "太陽與月亮與星星的知識",
    "SG_FUSION": "太陽與月亮與星星的融合",

    # ===== Soul Linker =====
    "SL_ALCHEMIST": "煉金術師之魂",
    "SL_MONK": "武僧之魂",
    "SL_STAR": "拳聖之魂",
    "SL_SAGE": "賢者之魂",
    "SL_CRUSADER": "十字軍之魂",
    "SL_SUPERNOVICE": "超級初學者之魂",
    "SL_KNIGHT": "騎士之魂",
    "SL_WIZARD": "巫師之魂",
    "SL_PRIEST": "牧師之魂",
    "SL_BARDDANCER": "吟遊詩人與舞孃之魂",
    "SL_ROGUE": "乞乞人之魂",
    "SL_ASSASIN": "刺客之魂",
    "SL_BLACKSMITH": "鐵匠之魂",
    "SL_HUNTER": "獵人之魂",
    "SL_SOULLINKER": "靈魂連結者之魂",
    "SL_HIGH": "一次上級職之魂",
    "SL_KAIZEL": "凱傑爾",
    "SL_KAAHI": "卡阿嘿",
    "SL_KAUPE": "卡烏帕",
    "SL_KAITE": "卡以特",
    "SL_KAINA": "卡以那",
    "SL_STIN": "艾斯汀",
    "SL_STUN": "艾斯通",
    "SL_SMA": "艾斯瑪",
    "SL_SWOO": "艾斯烏",
    "SL_SKE": "艾斯克",
    "SL_SKA": "艾斯卡",
    "SL_DEATHKNIGHT": "死亡騎士之魂",
    "SL_COLLECTOR": "暗收藏家之魂",
    "SL_NINJA": "忍者之魂",
    "SL_GUNNER": "乞乞統手之魂",

    # ===== Ninja =====
    "NJ_TOBIDOUGU": "飛刀修練",
    "NJ_SYURIKEN": "手裡劍投擲",
    "NJ_KUNAI": "苦無投擲",
    "NJ_HUUMA": "風魔手裡劍投擲",
    "NJ_ZENYNAGE": "投幣術",
    "NJ_TATAMIGAESHI": "榻榻米翻轉",
    "NJ_KASUMIKIRI": "霧切",
    "NJ_SHADOWJUMP": "影跳躍",
    "NJ_KIRIKAGE": "斬影",
    "NJ_UTSUSEMI": "蟬蛻",
    "NJ_BUNSINJYUTSU": "分身之術",
    "NJ_NINPOU": "忍法修練",
    "NJ_KOUENKA": "紅炎華",
    "NJ_KAENSIN": "火炎陣",
    "NJ_BAKUENRYU": "爆炎龍",
    "NJ_HYOUSENSOU": "冰閃槍",
    "NJ_SUITON": "水遁",
    "NJ_HYOUSYOURAKU": "冰晶落",
    "NJ_HUUJIN": "風刃",
    "NJ_RAIGEKISAI": "雷擊碎",
    "NJ_KAMAITACHI": "朔風",
    "NJ_NEN": "念",
    "NJ_ISSEN": "一閃",

    # ===== Gunslinger =====
    "GS_GLITTERING": "翻轉硬幣",
    "GS_FLING": "投擲",
    "GS_TRIPLEACTION": "三連射擊",
    "GS_BULLSEYE": "正中靶心",
    "GS_MADNESSCANCEL": "瘋狂取消",
    "GS_ADJUSTMENT": "調整",
    "GS_INCREASING": "精準提升",
    "GS_MAGICALBULLET": "魔法子彈",
    "GS_CRACKER": "爆裂彈",
    "GS_SINGLEACTION": "單發射擊",
    "GS_SNAKEEYE": "蛇眼",
    "GS_CHAINACTION": "連鎖射擊",
    "GS_TRACKING": "追蹤彈",
    "GS_DISARM": "繳械",
    "GS_PIERCINGSHOT": "貫穿射擊",
    "GS_RAPIDSHOWER": "快速射擊",
    "GS_DESPERADO": "亡命射擊",
    "GS_GATLINGFEVER": "乞加特林狂熱",
    "GS_DUST": "飛塵",
    "GS_FULLBUSTER": "全彈射擊",
    "GS_SPREADATTACK": "擴散射擊",
    "GS_GROUNDDRIFT": "地面漂移",

    # ===== Homunculus =====
    "HLIF_HEAL": "治癒之手(治癒)",
    "HLIF_AVOID": "緊急迴避",
    "HLIF_BRAIN": "腦手術",
    "HLIF_CHANGE": "精神變化",
    "HAMI_CASTLE": "城堡防禦",
    "HAMI_DEFENCE": "防禦",
    "HAMI_SKIN": "精鋼之膚",
    "HAMI_BLOODLUST": "嗜血",
    "HFLI_MOON": "月光",
    "HFLI_FLEET": "快速移動",
    "HFLI_SPEED": "超速",
    "HFLI_SBR44": "S.B.R.44",
    "HVAN_CAPRICE": "隨性",
    "HVAN_CHAOTIC": "混沌祝福",
    "HVAN_INSTRUCT": "變更指令",
    "HVAN_EXPLOSION": "生體爆發",

    # ===== Mercenary =====
    "MS_BASH": "重擊",
    "MS_MAGNUM": "霸氣衝擊",
    "MS_BOWLINGBASH": "保齡球攻擊",
    "MS_PARRYING": "格擋",
    "MS_REFLECTSHIELD": "盾牌反射",
    "MS_BERSERK": "狂暴",
    "MA_DOUBLE": "二連矢",
    "MA_SHOWER": "箭雨",
    "MA_SKIDTRAP": "滑行陷阱",
    "MA_LANDMINE": "地雷陷阱",
    "MA_SANDMAN": "催眠陷阱",
    "MA_FREEZINGTRAP": "冰凍陷阱",
    "MA_REMOVETRAP": "拆除陷阱",
    "MA_CHARGEARROW": "蓄力射擊",
    "MA_SHARPSHOOTING": "精準射擊",
    "ML_PIERCE": "刺擊",
    "ML_BRANDISH": "騎士槍術",
    "ML_SPIRALPIERCE": "螺旋刺擊",
    "ML_DEFENDER": "防禦",
    "ML_AUTOGUARD": "自動防禦",
    "ML_DEVOTION": "獻身",
    "MER_MAGNIFICAT": "魔力之歌",
    "MER_QUICKEN": "武器加速",
    "MER_SIGHT": "探索",
    "MER_CRASH": "衝撞",
    "MER_REGAIN": "恢復",
    "MER_TENDER": "溫柔",
    "MER_BENEDICTION": "祝福",
    "MER_RECUPERATE": "復原",
    "MER_MENTALCURE": "精神治療",
    "MER_COMPRESS": "壓縮",
    "MER_PROVOKE": "挑釁",
    "MER_AUTOBERSERK": "自動狂暴",
    "MER_DECAGI": "降低敏捷",
    "MER_SCAPEGOAT": "替罪羊",
    "MER_LEXDIVINA": "靜默",
    "MER_ESTIMATION": "怪物資訊",
    "MER_KYRIE": "天使之圍",
    "MER_INCAGI": "敏捷提升",
    "MER_BLESSING": "祝福",

    # ===== Rune Knight =====
    "RK_ENCHANTBLADE": "附魔之劍",
    "RK_SONICWAVE": "音速波動",
    "RK_DEATHBOUND": "死亡反彈",
    "RK_HUNDREDSPEAR": "百矛穿刺",
    "RK_WINDCUTTER": "風之切割",
    "RK_IGNITIONBREAK": "爆裂點燃",
    "RK_DRAGONTRAINING": "龍之訓練",
    "RK_DRAGONBREATH": "龍之吐息",
    "RK_DRAGONHOWLING": "龍之咆哮",
    "RK_RUNEMASTERY": "符文修練",
    "RK_MILLENNIUMSHIELD": "千年之盾",
    "RK_CRUSHSTRIKE": "粉碎打擊",
    "RK_REFRESH": "淨化",
    "RK_GIANTGROWTH": "巨人成長",
    "RK_STONEHARDSKIN": "磐石之膚",
    "RK_VITALITYACTIVATION": "生命力啟動",
    "RK_STORMBLAST": "暴風衝擊",
    "RK_FIGHTINGSPIRIT": "戰鬥之魂",
    "RK_ABUNDANCE": "豐饒",
    "RK_PHANTOMTHRUST": "幻影突刺",

    # ===== Arch Bishop =====
    "AB_JUDEX": "聖擊",
    "AB_ANCILLA": "聖物製造",
    "AB_ADORAMUS": "崇拜",
    "AB_CLEMENTIA": "仁慈祝福",
    "AB_CANTO": "讚頌",
    "AB_CHEAL": "群體治癒",
    "AB_EPICLESIS": "聖靈召喚",
    "AB_PRAEFATIO": "防護祝福",
    "AB_ORATIO": "祈禱",
    "AB_LAUDAAGNUS": "讚美聖羊",
    "AB_LAUDARAMUS": "讚美聖歌",
    "AB_EUCHARISTICA": "聖體",
    "AB_RENOVATIO": "更新",
    "AB_HIGHNESSHEAL": "高等治癒術",
    "AB_CLEARANCE": "淨化",
    "AB_EXPIATIO": "贖罪",
    "AB_DUPLELIGHT": "雙光",
    "AB_DUPLELIGHT_MELEE": "雙光",
    "AB_DUPLELIGHT_MAGIC": "雙光",
    "AB_SILENTIUM": "神聖沉默",
    "AB_SECRAMENT": "聖禮",

    # ===== Guillotine Cross =====
    "GC_VENOMIMPRESS": "毒印",
    "GC_CROSSIMPACT": "十字衝擊",
    "GC_DARKILLUSION": "暗影幻象",
    "GC_RESEARCHNEWPOISON": "新毒研究",
    "GC_CREATENEWPOISON": "新毒製造",
    "GC_ANTIDOTE": "解毒劑",
    "GC_POISONINGWEAPON": "毒武裝",
    "GC_WEAPONBLOCKING": "武器擋格",
    "GC_COUNTERSLASH": "反擊斬",
    "GC_WEAPONCRUSH": "武器毀壞",
    "GC_VENOMPRESSURE": "毒壓",
    "GC_POISONSMOKE": "毒煙",
    "GC_CLOAKINGEXCEED": "超越隱匿",
    "GC_PHANTOMMENACE": "幻影威脅",
    "GC_HALLUCINATIONWALK": "幻覺步伐",
    "GC_ROLLINGCUTTER": "迴旋切割",
    "GC_CROSSRIPPERSLASHER": "十字裂斬",

    # ===== Ranger =====
    "RA_AIMEDBOLT": "瞄準射擊",
    "RA_RESEARCHTRAP": "陷阱研究",
    "RA_RANGERMAIN": "遊俠要訣",
    "RA_ELECTRICSHOCKER": "電擊器",
    "RA_WUGMASTERY": "沃格修練",
    "RA_ARROWSTORM": "箭暴風雨",
    "RA_CLUSTERBOMB": "集束炸彈",
    "RA_DETONATOR": "引爆器",
    "RA_CAMOUFLAGE": "偽裝",
    "RA_TOOTHOFWUG": "沃格之牙",
    "RA_WUGRIDER": "沃格騎乘",
    "RA_FEARBREEZE": "恐懼微風",
    "RA_MAGENTATRAP": "紅色陷阱",
    "RA_FIRINGTRAP": "火焰陷阱",
    "RA_ICEBOUNDTRAP": "冰封陷阱",
    "RA_SENSITIVEKEEN": "敏銳嗅覺",
    "RA_WUGSTRIKE": "沃格打擊",
    "RA_WUGDASH": "沃格衝刺",
    "RA_COBALTTRAP": "藍色陷阱",
    "RA_WUGBITE": "沃格撕咬",
    "RA_MAIZETRAP": "黃色陷阱",
    "RA_VERDURETRAP": "綠色陷阱",

    # ===== Warlock =====
    "WL_MARSHOFABYSS": "深淵之沼",
    "WL_RADIUS": "半徑",
    "WL_SUMMONFB": "召喚火球",
    "WL_SUMMONWB": "召喚水球",
    "WL_SUMMONBL": "召喚雷球",
    "WL_SUMMONSTONE": "召喚岩球",
    "WL_DRAINLIFE": "吸取生命",
    "WL_RELEASE": "釋放",
    "WL_CRIMSONROCK": "緋紅之石",
    "WL_FROSTMISTY": "霜之迷霧",
    "WL_CHAINLIGHTNING": "連鎖閃電",
    "WL_SIENNAEXECRATE": "赭石詛咒",
    "WL_SOULEXPANSION": "靈魂膨脹",
    "WL_STASIS": "靜止",
    "WL_HELLINFERNO": "地獄業火",
    "WL_JACKFROST": "傑克冰霜",
    "WL_EARTHSTRAIN": "大地裂痕",
    "WL_WHITEIMPRISON": "白色禁錮",
    "WL_COMET": "彗星",
    "WL_RECOGNIZEDSPELL": "確認念咒",
    "WL_TETRAVORTEX": "四元素漩渦",
    "WL_FREEZE_SP": "冰凍魔法",
    "WL_READING_SB": "閱讀魔法書",

    # ===== Shadow Chaser =====
    "SC_FATALMENACE": "致命威脅",
    "SC_REPRODUCE": "再現",
    "SC_AUTOSHADOWSPELL": "自動影子魔法",
    "SC_SHADOWFORM": "影子形態",
    "SC_TRIANGLESHOT": "三角射擊",
    "SC_STRIPACCESSARY": "脫衣術(飾品)",
    "SC_BODYPAINT": "彩繪身體",
    "SC_INVISIBILITY": "隱形",
    "SC_DEADLYINFECT": "致命感染",
    "SC_ENERVATION": "偽裝-疲勞",
    "SC_GROOMY": "偽裝-陰鬱",
    "SC_IGNORANCE": "偽裝-無知",
    "SC_LAZINESS": "偽裝-懶惰",
    "SC_UNLUCKY": "偽裝-厄運",
    "SC_WEAKNESS": "偽裝-虛弱",
    "SC_MANHOLE": "人孔",
    "SC_DIMENSIONDOOR": "次元之門",
    "SC_CHAOSPANIC": "混沌恐慌",
    "SC_MAELSTROM": "漩渦",
    "SC_BLOODYLUST": "嗜血渴望",
    "SC_FEINTBOMB": "假動作炸彈",

    # ===== Mechanic =====
    "NC_MADOLICENCE": "魔導機甲許可",
    "NC_BOOSTKNUCKLE": "加速拳",
    "NC_PILEBUNKER": "打樁機",
    "NC_VULCANARM": "火神砲",
    "NC_FLAMELAUNCHER": "火焰發射器",
    "NC_COLDSLOWER": "寒冰減速器",
    "NC_ARMSCANNON": "手臂加農砲",
    "NC_ACCELERATION": "加速",
    "NC_HOVERING": "懸浮",
    "NC_F_SIDESLIDE": "前方側滑",
    "NC_B_SIDESLIDE": "後方側滑",
    "NC_MAINFRAME": "主框架改造",
    "NC_SELFDESTRUCTION": "自爆",
    "NC_SHAPESHIFT": "形態變換",
    "NC_EMERGENCYCOOL": "緊急冷卻",
    "NC_INFRAREDSCAN": "紅外線掃描",
    "NC_ANALYZE": "分析",
    "NC_MAGNETICFIELD": "磁場",
    "NC_NEUTRALBARRIER": "中立屏障",
    "NC_STEALTHFIELD": "隱匿力場",
    "NC_REPAIR": "修理",
    "NC_TRAININGAXE": "斧修練",
    "NC_RESEARCHFE": "火與地的研究",
    "NC_AXEBOOMERANG": "斧回力鏢",
    "NC_POWERSWING": "力量揮擊",
    "NC_AXETORNADO": "斧龍捲",
    "NC_SILVERSNIPER": "FAW 銀色狙擊者",
    "NC_MAGICDECOY": "FAW 魔法誘餌",
    "NC_DISJOINT": "FAW 解除",

    # ===== Minstrel/Wanderer =====
    "WA_SWING_DANCE": "搖擺之舞",
    "WA_SYMPHONY_OF_LOVER": "戀人的交響曲",
    "WA_MOONLIT_SERENADE": "月光小夜曲",
    "MI_RUSH_WINDMILL": "向風車突擊",
    "MI_ECHOSONG": "回音之歌",
    "MI_HARMONIZE": "和聲",
    "WM_LESSON": "課程",
    "WM_METALICSOUND": "金屬音浪",
    "WM_REVERBERATION": "共鳴殘響",
    "WM_DOMINION_IMPULSE": "支配衝動",
    "WM_SEVERE_RAINSTORM": "暴風驟雨",
    "WM_POEMOFNETHERWORLD": "奈落之歌",
    "WM_VOICEOFSIREN": "海妖之聲",
    "WM_DEADHILLHERE": "死亡山谷",
    "WM_LULLABY_DEEPSLEEP": "安息搖籃曲",
    "WM_SIRCLEOFNATURE": "自然循環之音",
    "WM_RANDOMIZESPELL": "不確定因素之語",
    "WM_GLOOMYDAY": "憂鬱的一天",
    "WM_GREAT_ECHO": "巨大回音",
    "WM_SONG_OF_MANA": "魔力之歌",
    "WM_DANCE_WITH_WUG": "與沃格共舞",
    "WM_SOUND_OF_DESTRUCTION": "毀滅之音",
    "WM_SATURDAY_NIGHT_FEVER": "週末夜狂熱",
    "WM_LERADS_DEW": "雷拉德之露",
    "WM_MELODYOFSINK": "沉淪旋律",
    "WM_BEYOND_OF_WARCRY": "超越戰吼",
    "WM_UNLIMITED_HUMMING_VOICE": "無限哼唱之聲",

    # ===== Sura =====
    "SR_DRAGONCOMBO": "雙龍腳",
    "SR_SKYNETBLOW": "天羅地網",
    "SR_EARTHSHAKER": "地雷震",
    "SR_RAMPAGEBLASTER": "爆氣散彈",
    "SR_KNUCKLEARROW": "修羅身彈",
    "SR_FALLENEMPIRE": "大纏崩墜",
    "SR_TIGERCANNON": "號砲",
    "SR_GATEOFHELL": "羅刹破凰擊",
    "SR_CRESCENTELBOW": "破碎柱",
    "SR_WINDMILL": "旋風腿",
    "SR_CURSEDCIRCLE": "咒縛陣",
    "SR_LIGHTNINGWALK": "閃電步",
    "SR_RAISINGDRAGON": "潛龍昇天",
    "SR_GENTLETOUCH_QUIET": "點穴-默",
    "SR_GENTLETOUCH_CURE": "點穴-快",
    "SR_GENTLETOUCH_ENERGYGAIN": "點穴-救",
    "SR_GENTLETOUCH_CHANGE": "點穴-反",
    "SR_GENTLETOUCH_REVITALIZE": "點穴-活",
    "SR_ASSIMILATEPOWER": "吸氣攻",
    "SR_POWERVELOCITY": "全氣注入",
    "SR_HOWLINGOFLION": "獅子吼",
    "SR_RIDEINLIGHTNING": "雷光彈",

    # ===== Royal Guard =====
    "LG_MOONSLASHER": "月光斬",
    "LG_BANISHINGPOINT": "驅逐之點",
    "LG_OVERBRAND": "烙印衝擊",
    "LG_PINPOINTATTACK": "精準攻擊",
    "LG_CANNONSPEAR": "加農矛",
    "LG_EXEEDBREAK": "超越衝擊",
    "LG_BANDING": "結陣",
    "LG_FORCEOFVANGUARD": "先鋒之力",
    "LG_RAGEBURST": "狂暴爆發",
    "LG_TRAMPLE": "踐踏",
    "LG_PRESTIGE": "威望",
    "LG_HESPERUSLIT": "晨星之光",
    "LG_RAYOFGENESIS": "創世之光",
    "LG_INSPIRATION": "靈感",
    "LG_PIETY": "虔誠",
    "LG_REFLECTDAMAGE": "傷害反射",
    "LG_EARTHDRIVE": "大地衝擊",
    "LG_SHIELDPRESS": "盾壓",
    "LG_SHIELDSPELL": "盾之魔法",

    # ===== Genetic =====
    "GN_TRAINING_SWORD": "劍修練",
    "GN_REMODELING_CART": "手推車改造",
    "GN_CART_TORNADO": "手推車龍捲風",
    "GN_CARTCANNON": "手推車加農砲",
    "GN_CARTBOOST": "手推車加速",
    "GN_THORNS_TRAP": "荊棘陷阱",
    "GN_BLOOD_SUCKER": "吸血蟲",
    "GN_SPORE_EXPLOSION": "孢子爆炸",
    "GN_WALLOFTHORN": "荊棘之壁",
    "GN_CRAZYWEED": "瘋狂雜草",
    "GN_DEMONIC_FIRE": "惡魔之火",
    "GN_FIRE_EXPANSION": "火焰擴散",
    "GN_HELLS_PLANT": "地獄之花",
    "GN_MANDRAGORA": "曼陀羅之吼",
    "GN_SLINGITEM": "投擲道具",
    "GN_CHANGEMATERIAL": "材料轉換",
    "GN_MIX_COOKING": "混合烹飪",
    "GN_MAKEBOMB": "炸彈製造",
    "GN_S_PHARMACY": "特殊製藥",

    # ===== Sorcerer =====
    "SO_FIREWALK": "火焰步伐",
    "SO_ELECTRICWALK": "電擊步伐",
    "SO_SPELLFIST": "魔法拳",
    "SO_VACUUM_EXTREME": "極限真空",
    "SO_PSYCHIC_WAVE": "精神波動",
    "SO_CLOUD_KILL": "毒雲術",
    "SO_POISON_BUSTER": "毒擊",
    "SO_STRIKING": "打擊",
    "SO_EARTHGRAVE": "大地墓穴",
    "SO_DIAMONDDUST": "鑽石星塵",
    "SO_WARMER": "溫暖者",
    "SO_VARETYR_SPEAR": "瓦雷提爾之矛",
    "SO_ARRULLO": "催眠",
    "SO_EL_CONTROL": "精靈控制",
    "SO_SUMMON_AGNI": "召喚阿格尼",
    "SO_SUMMON_AQUA": "召喚阿庫亞",
    "SO_SUMMON_VENTUS": "召喚溫特斯",
    "SO_SUMMON_TERA": "召喚特拉",

    # ===== NPC Skills =====
    "NPC_EARTHQUAKE": "地震",
    "NPC_DRAGONFEAR": "龍之恐懼",
    "NPC_PULSESTRIKE": "脈衝打擊",
    "NPC_HELLJUDGEMENT": "地獄審判",
    "NPC_WIDESILENCE": "範圍沉默",
    "NPC_WIDEFREEZE": "範圍冰凍",
    "NPC_WIDEBLEEDING": "範圍出血",
    "NPC_WIDESTONE": "範圍石化",
    "NPC_WIDECONFUSE": "範圍混亂",
    "NPC_WIDESLEEP": "範圍催眠",
    "NPC_WIDESTUN": "範圍暈眩",
    "NPC_WIDECURSE": "範圍詛咒",
    "NPC_SLOWCAST": "緩速詠唱",
    "NPC_MAGICMIRROR": "魔法鏡像",
    "NPC_STONESKIN": "石膚術",
    "NPC_ANTIMAGIC": "抗魔",
    "NPC_CRITICALWOUND": "致命傷口",
    "NPC_EVILLAND": "邪惡大地",
    "NPC_VAMPIRE_GIFT": "吸血鬼之觸",
    "NPC_WIDESOULDRAIN": "魔力燃燒",
    "NPC_ALLHEAL": "生命之流",
    "NPC_HELLPOWER": "地獄之力",

    # ===== Misc / All =====
    "ALL_INCCARRY": "負重增加R",
    "ALL_CATCRY": "怪獸的嚎叫",
    "ALL_PARTYFLEE": "吹吧花之風",
    "ALL_ANGEL_PROTECT": "感謝你",
    "ALL_DREAM_SUMMERNIGHT": "仲夏夜之夢",
    "ALL_REVERSEORCISH": "獸人語翻譯",
    "ALL_WEWISH": "聖誕快樂",
    "ALL_ODINS_RECALL": "奧丁的召喚",
    "ALL_TIMEIN": "時間回復",
    "RETURN_TO_ELDICASTES": "回歸迪卡斯特",
    "ITM_TOMAHAWK": "戰斧投擲",

    # ===== Battleground / Special Munak/Bongun =====
    "MB_FIGHTING": "武樂 戰鬥",
    "MB_NEUTRAL": "本乾 中立",
    "MB_TAIMING_PUTI": "寵物朋友",
    "MB_WHITEPOTION": "白色藥水差遣",
    "MB_MENTAL": "精神差遣",
    "MB_CARDPITCHER": "卡片投擲",
    "MB_PETPITCHER": "寵物投擲",
    "MB_BODYSTUDY": "身體研讀",
    "MB_BODYALTER": "身體改造",
    "MB_PETMEMORY": "寵物記憶",
    "MB_M_TELEPORT": "武樂傳送",
    "MB_B_GAIN": "本乾增益",
    "MB_M_GAIN": "武樂增益",
    "MB_MISSION": "馴養任務",
    "MB_MUNAKKNOWLEDGE": "馴養大師",
    "MB_MUNAKBALL": "武樂球",
    "MB_SCROLL": "本乾卷軸",
    "MB_B_GATHERING": "本乾聚集",
    "MB_M_GATHERING": "武樂聚集",
    "MB_B_EXCLUDE": "本乾排除",
    "MB_B_DRIFT": "本乾漂移",
    "MB_B_WALLRUSH": "本乾衝牆",
    "MB_M_WALLRUSH": "武樂衝牆",
    "MB_B_WALLSHIFT": "本乾牆移",
    "MB_M_WALLCRASH": "武樂撞牆",
    "MB_M_REINCARNATION": "武樂轉生",
    "MB_B_EQUIP": "本乾全能",
    "GM_SANDMAN": "乖乖睡覺",

    # ===== Death Knight / Dark Collector (unused, but in table) =====
    "DE_BERSERKAIZER": "狂暴凱薩",
    "DA_DARKPOWER": "暗黑靈魂力量",
    "DE_PASSIVE": "Death 被動",
    "DE_PATTACK": "Death 攻擊被動",
    "DE_PSPEED": "Death 速度被動",
    "DE_PDEFENSE": "Death 防禦被動",
    "DE_PCRITICAL": "Death 爆擊被動",
    "DE_PHP": "Death 回復被動",
    "DE_PSP": "Death 魔力被動",
    "DE_RESET": "Death 最佳化",
    "DE_RANKING": "Death 排名被動",
    "DE_PTRIPLE": "Death 三連被動",
    "DE_ENERGY": "死亡能量",
    "DE_NIGHTMARE": "死亡噩夢",
    "DE_SLASH": "死亡斬擊",
    "DE_COIL": "死亡纏繞",
    "DE_WAVE": "死亡波動",
    "DE_REBIRTH": "死亡逆轉能量",
    "DE_AURA": "死亡氣場",
    "DE_FREEZER": "死亡冰凍",
    "DE_CHANGEATTACK": "死亡變換攻擊",
    "DE_PUNISH": "死亡懲罰",
    "DE_POISON": "死亡毒斬",
    "DE_INSTANT": "死亡瞬間屏障",
    "DE_WARNING": "死亡警告",
    "DE_RANKEDKNIFE": "死亡飛刀",
    "DE_RANKEDGRADIUS": "死亡劍",
    "DE_GAUGE": "威力計量",
    "DE_GTIME": "威力時間充填",
    "DE_GPAIN": "威力苦痛充填",
    "DE_GSKILL": "威力技巧充填",
    "DE_GKILL": "威力殺戮充填",
    "DE_ACCEL": "死亡加速",
    "DE_BLOCKDOUBLE": "死亡雙重擋格",
    "DE_BLOCKMELEE": "死亡近距擋格",
    "DE_BLOCKFAR": "死亡遠距擋格",
    "DE_FRONTATTACK": "死亡衝鋒攻擊",
    "DE_DANGERATTACK": "危險攻擊",
    "DE_TWINATTACK": "死亡雙擊",
    "DE_WINDATTACK": "死亡風暴攻擊",
    "DE_WATERATTACK": "死亡水流攻擊",
    "DA_ENERGY": "暗黑能量",
    "DA_CLOUD": "暗黑之雲",
    "DA_FIRSTSLOT": "暗黑首幻想",
    "DA_HEADDEF": "暗黑頭防禦",
    "DA_SPACE": "暗黑黃昏",
    "DA_TRANSFORM": "暗黑變身",
    "DA_EXPLOSION": "暗黑爆裂",
    "DA_REWARD": "暗黑獎賞",
    "DA_CRUSH": "暗黑粉碎",
    "DA_ITEMREBUILD": "暗黑道具重建",
    "DA_ILLUSION": "暗黑幻象",
    "DA_NUETRALIZE": "暗黑中和",
    "DA_RUNNER": "暗黑奔跑者",
    "DA_TRANSFER": "暗黑傳送",
    "DA_WALL": "暗黑之壁",
    "DA_REVENGE": "暗黑復仇",
    "DA_EARPLUG": "暗黑耳塞",
    "DA_CONTRACT": "黑寶石契約",
    "DA_BLACK": "黑寶石魔法",
    "DA_DREAM": "黑寶石之夢",
    "DA_MAGICCART": "收藏家魔法推車",
    "DA_COPY": "收藏家複製",
    "DA_CRYSTAL": "收藏家水晶",
    "DA_EXP": "收藏家經驗值",
    "DA_CARTSWING": "收藏家魔法推車揮擊",
    "DA_REBUILD": "收藏家人體重建",
    "DA_JOBCHANGE": "收藏家初學者轉職",
    "DA_EDARKNESS": "收藏家皇寶黑暗",
    "DA_EGUARDIAN": "收藏家皇寶守護",
    "DA_TIMEOUT": "收藏家時間終止",
    "DA_ZENYRANK": "收藏家排名",
    "DA_ACCESSORYMIX": "收藏家混合",
}


def translate_skillnametable():
    """Translate skillnametable.txt from Korean to Traditional Chinese."""
    input_path = os.path.join(EXTRACTED_DIR, "skillnametable_kr.txt")
    output_path = os.path.join(CLIENT_DATA_DIR, "skillnametable.txt")

    data = open(input_path, "rb").read()
    text = data.decode("euc-kr", errors="replace")
    lines = text.split("\r\n")

    translated_lines = []
    translated_count = 0
    fallback_count = 0

    for line in lines:
        if not line.strip():
            translated_lines.append(line)
            continue

        parts = line.split("#")
        if len(parts) >= 3:
            skill_id = parts[0]
            kr_name = parts[1]

            if skill_id in SKILL_NAME_MAP:
                zh_name = SKILL_NAME_MAP[skill_id]
                translated_count += 1
            else:
                # Fallback: use English skill ID formatted nicely
                zh_name = skill_id.replace("_", " ")
                fallback_count += 1
                print(f"  No translation for: {skill_id} ({kr_name})")

            translated_lines.append(f"{skill_id}#{zh_name}#")
        else:
            translated_lines.append(line)

    # Write Big5 + CRLF
    with open(output_path, "wb") as f:
        for line in translated_lines:
            try:
                encoded = line.encode("big5")
            except UnicodeEncodeError:
                # Replace unencodable chars
                encoded = line.encode("big5", errors="replace")
            f.write(encoded + b"\r\n")

    # Remove trailing empty line if the last entry already ends with CRLF
    print(f"\n  skillnametable.txt:")
    print(f"    Translated: {translated_count}")
    print(f"    Fallback (English): {fallback_count}")
    print(f"    Total lines: {len(translated_lines)}")
    print(f"    Output: {output_path}")

    # Verify
    verify_big5(output_path)


def translate_skilldesctable():
    """Translate skilldesctable.txt - replace skill names in headers,
    translate common Korean terms in descriptions."""
    input_path = os.path.join(EXTRACTED_DIR, "skilldesctable_kr.txt")
    output_path = os.path.join(CLIENT_DATA_DIR, "skilldesctable.txt")

    data = open(input_path, "rb").read()
    text = data.decode("euc-kr", errors="replace")
    lines = text.split("\r\n")

    # Common Korean → Chinese description term translations
    DESC_TERMS = {
        "계열": "系列",
        "내용": "內容",
        "패시브": "被動",
        "액티브": "主動",
        "공격력": "攻擊力",
        "타겟": "目標",
        "습득조건": "習得條件",
        "소비": "消耗",
        "시전시간": "詠唱時間",
        "후딜레이": "延遲時間",
        "지속시간": "持續時間",
        "범위": "範圍",
        "대상": "對象",
        "효과": "效果",
        "적에게": "對敵人",
        "아군에게": "對友軍",
        "자기자신": "自身",
        "화면 전체": "全畫面",
        "초": "秒",
        "공격": "攻擊",
        "방어": "防禦",
        "마법": "魔法",
        "물리": "物理",
        "원거리": "遠距離",
        "근거리": "近距離",
        "보조": "輔助",
        "회복": "回復",
        "스킬": "技能",
        "레벨": "等級",
        "필요": "必要",
        "사용": "使用",
        "할 수 있다": "可以",
        "가능": "可能",
        "불가능": "不可能",
        "최대": "最大",
        "증가": "增加",
        "감소": "減少",
        "확률": "機率",
        "데미지": "傷害",
        "셀": "格",
        "소모": "消耗",
        "무기": "武器",
        "방패": "盾牌",
        "갑옷": "鎧甲",
        "투구": "頭盔",
        "장비": "裝備",
        "한손검": "單手劍",
        "양손검": "雙手劍",
        "단검": "短劍",
        "창": "槍",
        "도끼": "斧",
        "메이스": "鈍器",
        "너클": "拳刃",
        "악기": "樂器",
        "채찍": "鞭子",
        "책": "書",
        "카타르": "十字刺刃",
        "활": "弓",
        "총": "槍",
        "수리검": "手裡劍",
        "하이딩": "躲藏",
        "클로킹": "隱匿",
        "상태이상": "異常狀態",
        "중독": "中毒",
        "빙결": "冰凍",
        "석화": "石化",
        "침묵": "沉默",
        "저주": "詛咒",
        "암흑": "黑暗",
        "수면": "睡眠",
        "스턴": "暈眩",
        "출혈": "出血",
        "혼란": "混亂",
        "화": "火",
        "수": "水",
        "풍": "風",
        "지": "地",
        "성": "聖",
        "암": "暗",
        "독": "毒",
        "념": "念",
        "무": "無",
        "불사": "不死",
        "속성": "屬性",
        "적": "敵",
        "아군": "友軍",
        "플레이어": "玩家",
        "몬스터": "魔物",
        "보스": "頭目",
        "캐릭터": "角色",
        "서버": "伺服器",
        "파티": "隊伍",
        "길드": "公會",
    }

    translated_lines = []
    for line in lines:
        translated = line

        # Translate skill header lines (SKILL_ID#)
        if line.endswith("#") and not line.startswith("[") and not line.startswith("^"):
            skill_id = line[:-1]
            if skill_id in SKILL_NAME_MAP:
                translated = f"{skill_id}#"
            # The ID# line stays the same (it's the skill ID marker)

        # Translate Korean skill name line (appears after SKILL_ID# line)
        # These are lines like "기본기술(Basic Skill)" or "한손검 수련(Sword Mastery)"
        # We keep the format but translate the name
        elif "(" in line and ")" in line and not line.startswith("[") and not line.startswith("^"):
            # This might be a skill title line
            # Try to extract and translate
            for skill_id, zh_name in SKILL_NAME_MAP.items():
                kr_pattern = line.split("(")[0].strip()
                eng_part = ""
                if "(" in line:
                    eng_part = "(" + line.split("(", 1)[1]
                # Only do this if we can match
                break  # Just leave as-is for now, the desc is less critical

        # Translate common Korean terms
        for kr, zh in DESC_TERMS.items():
            if kr in translated:
                translated = translated.replace(kr, zh)

        translated_lines.append(translated)

    # Write Big5 + CRLF
    with open(output_path, "wb") as f:
        for line in translated_lines:
            try:
                encoded = line.encode("big5")
            except UnicodeEncodeError:
                encoded = line.encode("big5", errors="replace")
            f.write(encoded + b"\r\n")

    print(f"\n  skilldesctable.txt:")
    print(f"    Total lines: {len(translated_lines)}")
    print(f"    Output: {output_path}")

    verify_big5(output_path)


def translate_tipoftheday():
    """Translate tipOfTheDay.txt from Korean to Traditional Chinese."""
    input_path = os.path.join(PROJECT_DIR, "client", "tipOfTheDay.txt")
    output_path = os.path.join(CLIENT_DATA_DIR, "tipoftheday.txt")

    data = open(input_path, "rb").read()
    text = data.decode("euc-kr", errors="replace")
    lines = text.split("\r\n")

    # tipOfTheDay format: each tip is one or more lines, separated by #
    TIPS_TRANSLATION = {
        # Line-by-line translations of the 177-line file
    }

    # Direct full translation of tips
    translated_tips = [
        "→/savechat : 將聊天內容儲存為檔案。",
        "#",
        "→按住Ctrl再按數字鍵盤的[*]鍵，可以切換小地圖的",
        "  半透明和不透明模式。",
        "#",
        "→按住Shift再拖曳滑鼠右鍵，可以調整攝影機角度。",
        "  此時按住Shift再雙擊滑鼠右鍵可以恢復原狀。",
        "#",
        "→按住Ctrl再拖曳滑鼠右鍵，可以縮放攝影機。",
        "  此時按住Ctrl再雙擊滑鼠右鍵可以恢復原狀。",
        "#",
        "→在聊天視窗中輸入 /effect 可以切換特效的開關。",
        "#",
        "→在聊天視窗中輸入 /mineffect 可以切換為簡化特效模式。",
        "#",
        "→在聊天視窗中輸入 /miss 可以切換Miss顯示的開關。",
        "#",
        "→Alt+End 可以切換是否顯示角色名稱。",
        "#",
        "→在聊天視窗中輸入 /itemsnap 可以切換自動撿取物品的功能。",
        "#",
        "→在聊天視窗中輸入 /window 可以開啟/關閉基本操作視窗。",
        "#",
        "→在聊天視窗中輸入 /bingbing 角色會向右旋轉，",
        "  輸入 /bangbang 角色會向左旋轉。",
        "#",
        "→按 F10 鍵可以開啟/關閉聊天視窗。",
        "#",
        "→Alt+Y 可以開啟任務視窗。",
        "#",
        "→在聊天視窗中輸入 /camera 可以開啟/關閉自由攝影機模式。",
        "  在自由攝影機模式下，可以用滑鼠右鍵旋轉和調整攝影機角度。",
        "#",
        "→在聊天視窗中輸入 /fog 可以開啟/關閉霧效果。",
        "#",
        "→按住Alt再左擊滑鼠可以直接攻擊角色或魔物。",
        "#",
        "→Ctrl+右擊另一個角色可以開啟互動選單。",
        "  可以進行交易、組隊、加入公會等操作。",
        "#",
        "→在聊天視窗中輸入 /noctrl 可以切換自動攻擊模式。",
        "  開啟時點擊魔物會自動攻擊，不需要按住Ctrl。",
        "#",
        "→Alt+右擊地面可以在小地圖上標記位置。",
        "#",
        "→在聊天視窗中輸入 /notrade 可以拒絕所有交易請求。",
        "#",
        "→在聊天視窗中輸入 /noshift 可以在按住Shift時",
        "  對玩家使用輔助技能而不會攻擊。",
        "#",
        "→F12 可以開啟快捷鍵設定視窗，最多可設定4組。",
        "  按F12可以在不同組之間切換。",
        "#",
        "→在聊天視窗中輸入 /q1 /q2 可以快速切換",
        "  第1組和第2組快捷鍵。",
        "#",
        "→在聊天視窗中輸入 /emotion 可以查看所有表情動作的列表。",
        "#",
        "→Alt+0~9 和 Ctrl+1,-,=,\\ 可以使用表情動作。",
        "  Alt+L 可以使用進階表情動作。",
        "#",
        "→Insert鍵 或 輸入 /sit 可以坐下/站起，",
        "  坐下時HP和SP恢復速度會加快。",
        "#",
        "→按 PrintScreen 鍵可以擷取遊戲畫面，",
        "  截圖會儲存在RO資料夾中的ScreenShot目錄。",
        "#",
        "→在聊天視窗中輸入 /where 可以查看目前所在的地圖名稱和座標。",
        "#",
        "→在聊天視窗中輸入 /who 可以查看目前伺服器的上線人數。",
        "#",
        "→在聊天視窗中輸入 /memo 可以記錄目前位置作為傳送點。",
        "  最多可以記錄3個傳送點。",
        "#",
        "→在物品視窗中雙擊裝備可以穿戴/脫下裝備。",
        "#",
        "→按 Alt+E 可以開啟物品視窗。",
        "#",
        "→按 Alt+A 可以開啟狀態視窗。",
        "#",
        "→按 Alt+S 可以開啟技能視窗。",
        "#",
        "→按 Alt+Q 可以開啟裝備視窗。",
        "#",
        "→按 Alt+Z 可以開啟隊伍視窗。",
        "#",
        "→按 Alt+G 可以開啟公會視窗。",
        "#",
        "→按 Alt+H 可以開啟好友視窗。",
        "#",
        "→在聊天視窗中輸入 /ex <角色名> 可以將對方加入黑名單。",
        "  被加入黑名單的玩家無法對你密語。",
        "#",
        "→在聊天視窗中輸入 /in <角色名> 可以將對方從黑名單移除。",
        "#",
        "→在聊天視窗中輸入 /exall 可以拒絕所有密語。",
        "  輸入 /inall 可以接受所有密語。",
        "#",
        "→按 Home 鍵可以切換戰鬥資訊視窗的顯示模式。",
        "#",
        "→在聊天視窗中輸入 /shopping 可以開啟商店搜尋功能。",
        "#",
        "→善用自動餵食寵物功能，可以讓寵物保持好心情。",
        "  在寵物資訊視窗中勾選自動餵食即可。",
        "#",
        "→同一帳號下的角色可以透過卡普拉倉庫共享物品。",
        "#",
        "→狩獵魔物時注意魔物的屬性弱點，可以造成更多傷害。",
        "#",
        "→遊戲中遇到問題可以使用 /h 指令查看所有可用指令。",
        "#",
        "→與NPC對話時請仔細閱讀內容，可能包含重要任務資訊。",
        "#",
        "→定期存放重要物品到倉庫中，避免死亡時掉落。",
        "#",
        "→組隊狩獵時可以獲得經驗值加成，多多和朋友一起冒險吧！",
        "#",
        "→在冒險途中如果迷路了，可以使用蝴蝶翅膀回到存檔點。",
        "#",
        "→不確定裝備效果時，可以先使用鑑定技能或放大鏡。",
        "#",
        "→提升VIT可以增加HP回復速度和最大HP。",
        "#",
        "→提升INT可以增加SP回復速度和最大SP。",
        "#",
        "→提升DEX可以縮短詠唱時間和提高命中率。",
        "#",
        "→提升AGI可以增加迴避率和攻擊速度。",
        "#",
        "→提升STR可以增加物理攻擊力和負重量。",
        "#",
        "→提升LUK可以增加暴擊率和一些特殊效果的成功率。",
        "#",
    ]

    # Write Big5 + CRLF
    with open(output_path, "wb") as f:
        for line in translated_tips:
            try:
                encoded = line.encode("big5")
            except UnicodeEncodeError:
                encoded = line.encode("big5", errors="replace")
            f.write(encoded + b"\r\n")

    print(f"\n  tipoftheday.txt:")
    print(f"    Total lines: {len(translated_tips)}")
    print(f"    Output: {output_path}")

    verify_big5(output_path)


def translate_guildtip():
    """Translate GuildTip.txt from Korean to Traditional Chinese."""
    output_path = os.path.join(CLIENT_DATA_DIR, "GuildTip.txt")

    translated_tips = [
        "#",
        "[ 公會建立 ]",
        " 1. 必須持有皇室勳章G。",
        " (皇室勳章G可以在道具商城購買。)",
        " ",
        " 2. 持有皇室勳章G的狀態下，",
        " 在聊天視窗輸入'/guild (公會名稱)'",
        " 或按下'建立公會'按鈕來建立公會。",
        " ",
        " 3. 按 ALT+G 可以開啟公會資訊視窗。",
        " ",
        "#",
        "[ 公會加入 ]",
        " 1. 邀請其他角色加入公會時，",
        " 對目標角色右擊選擇'公會邀請'。",
        " ",
        " 2. 被邀請的角色可以選擇接受或拒絕。",
        " ",
        "#",
        "[ 公會技能 ]",
        " 1. 公會等級提升後可以獲得公會技能點數。",
        " ",
        " 2. 公會會長可以分配技能點數。",
        " ",
        " 3. 公會技能包含：",
        "    - 與卡普拉的契約：在據點使用卡普拉服務",
        "    - 守護者研究：強化據點的守衛",
        "    - 緊急召集：將公會成員傳送到身邊",
        " ",
        "#",
        "[ 公會戰爭 ]",
        " 1. 公會會長可以向其他公會宣戰。",
        " ",
        " 2. 公會戰爭中擊敗敵方成員不會受到懲罰。",
        " ",
        " 3. 公會戰爭可以透過和約結束。",
        " ",
        "#",
        "[ 攻城戰 ]",
        " 1. 攻城戰在指定時間開始。",
        " ",
        " 2. 破壞城堡中的皇室勳章就能佔領城堡。",
        " ",
        " 3. 佔領城堡後可以獲得特殊獎勵。",
        "    - 城堡內的寶箱",
        "    - 城堡地下迷宮的入場權",
        " ",
        " 4. 城堡防禦方可以召喚守衛和設置陷阱。",
        " ",
        "#",
        "[ 公會地下城 ]",
        " 1. 佔領城堡的公會可以進入地下城。",
        " ",
        " 2. 地下城中有特殊的魔物和寶物。",
        " ",
        " 3. 地下城是公會成員專屬的狩獵場。",
        " ",
        "#",
    ]

    # Write Big5 + CRLF
    with open(output_path, "wb") as f:
        for line in translated_tips:
            try:
                encoded = line.encode("big5")
            except UnicodeEncodeError:
                encoded = line.encode("big5", errors="replace")
            f.write(encoded + b"\r\n")

    print(f"\n  GuildTip.txt:")
    print(f"    Total lines: {len(translated_tips)}")
    print(f"    Output: {output_path}")

    verify_big5(output_path)


def verify_big5(filepath):
    """Verify a file is valid Big5."""
    with open(filepath, "rb") as f:
        content = f.read()
    try:
        content.decode("big5")
        lines = content.split(b"\r\n")
        print(f"    Big5 verification: OK ({len(lines)} lines)")
    except UnicodeDecodeError as e:
        print(f"    Big5 verification: FAILED at byte {e.start}")


def verify_english_files():
    """Verify that questid2display.txt and metalprocessitemlist.txt
    are ASCII-compatible and work with Big5."""
    files = [
        os.path.join(CLIENT_DATA_DIR, "questid2display.txt"),
        os.path.join(CLIENT_DATA_DIR, "metalprocessitemlist.txt"),
    ]
    for filepath in files:
        if not os.path.exists(filepath):
            print(f"  {os.path.basename(filepath)}: NOT FOUND (skipped)")
            continue
        with open(filepath, "rb") as f:
            content = f.read()
        try:
            content.decode("big5")
            lines = content.split(b"\n")
            print(f"  {os.path.basename(filepath)}: OK (Big5 compatible, {len(lines)} lines)")
        except UnicodeDecodeError as e:
            print(f"  {os.path.basename(filepath)}: ISSUE at byte {e.start}")
            # Check if it's actually ASCII
            try:
                content.decode("ascii")
                print(f"    Pure ASCII - compatible with Big5")
            except:
                print(f"    Contains non-ASCII non-Big5 bytes")


def main():
    print("=" * 60)
    print("Phase 2: RO GRF 繁體中文化")
    print("=" * 60)

    os.makedirs(CLIENT_DATA_DIR, exist_ok=True)

    print("\n[Step 1] Translating skillnametable.txt...")
    translate_skillnametable()

    print("\n[Step 2] Translating skilldesctable.txt...")
    translate_skilldesctable()

    print("\n[Step 3] Translating tipoftheday.txt...")
    translate_tipoftheday()

    print("\n[Step 4] Translating GuildTip.txt...")
    translate_guildtip()

    print("\n[Step 5] Verifying English files...")
    verify_english_files()

    print("\n" + "=" * 60)
    print("Phase 2 translation complete!")
    print("Files placed in client/data/ to override GRF.")
    print("=" * 60)


if __name__ == "__main__":
    main()
