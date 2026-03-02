#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a clean Traditional Chinese skilldesctable.txt for RO client.

Instead of partially translating Korean (which creates garbled Big5),
we generate complete Chinese entries based on the original structure.
"""

import os
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(TOOLS_DIR)
CLIENT_DATA_DIR = os.path.join(PROJECT_DIR, "client", "data")
EXTRACTED_DIR = os.path.join(TOOLS_DIR, "extracted")

# Import skill name mapping from translate_skills
sys.path.insert(0, TOOLS_DIR)
from translate_skills import SKILL_NAME_MAP

# =============================================================================
# Full Chinese skill descriptions
# Format: "SKILL_ID": [list of description lines]
# Each entry starts with SKILL_ID# and ends with #
# =============================================================================
SKILL_DESC_MAP = {
    # ===== Novice =====
    "NV_BASIC": [
        "基本技能(Basic Skill)",
        "^777777使基本介面相關技能可以使用。^000000",
        "[Level 1] : 交換視窗",
        "^777777可以與其他角色進行道具交換。^000000",
        "[Level 2] : 表情動作",
        "^777777使用Alt+0~9, Ctrl+1,-,=,\\鍵表達情緒。Alt+L可使用進階表情。^000000",
        "[Level 3] : 坐下",
        "^777777坐下後加快體力恢復速度。^000000",
        "^990000按Insert鍵或輸入/sit使用。^000000",
        "[Level 4] : 聊天室",
        "^777777可以開設聊天室。按Alt+C使用。^000000",
        "[Level 5] : 加入隊伍",
        "^777777可以加入其他人組成的隊伍。^000000",
        "[Level 6] : 使用倉庫",
        "^777777可以使用卡普拉倉庫。^000000",
        "[Level 7] : 組建隊伍",
        "^777777可以組建隊伍。^000000",
        "^990000輸入/organize [隊伍名] 使用。Alt+Z調整隊伍設定。^000000",
        "[Level 9] : 可轉職",
        "^777777可以轉職為一次職業。^000000",
    ],
    "NV_FIRSTAID": [
        "急救(First Aid)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使用繃帶恢復少量HP。^000000",
        "[Level 1] : ^777777恢復HP 5^000000",
    ],
    "NV_TRICKDEAD": [
        "裝死(Play Dead)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777裝死躺在地上，魔物將不再攻擊你。移動或使用技能時解除。^000000",
    ],

    # ===== Swordman =====
    "SM_SWORD": [
        "劍術修練(Sword Mastery)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加使用單手劍時的攻擊力。^000000",
        "[Level 1] : ^777777攻擊力 +4^000000",
        "[Level 2] : ^777777攻擊力 +8^000000",
        "[Level 3] : ^777777攻擊力 +12^000000",
        "[Level 4] : ^777777攻擊力 +16^000000",
        "[Level 5] : ^777777攻擊力 +20^000000",
        "[Level 6] : ^777777攻擊力 +24^000000",
        "[Level 7] : ^777777攻擊力 +28^000000",
        "[Level 8] : ^777777攻擊力 +32^000000",
        "[Level 9] : ^777777攻擊力 +36^000000",
        "[Level 10] : ^777777攻擊力 +40^000000",
    ],
    "SM_TWOHAND": [
        "雙手劍修練(Two-Handed Sword Mastery)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加使用雙手劍時的攻擊力。^000000",
        "[Level 1] : ^777777攻擊力 +4^000000",
        "[Level 2] : ^777777攻擊力 +8^000000",
        "[Level 3] : ^777777攻擊力 +12^000000",
        "[Level 4] : ^777777攻擊力 +16^000000",
        "[Level 5] : ^777777攻擊力 +20^000000",
        "[Level 6] : ^777777攻擊力 +24^000000",
        "[Level 7] : ^777777攻擊力 +28^000000",
        "[Level 8] : ^777777攻擊力 +32^000000",
        "[Level 9] : ^777777攻擊力 +36^000000",
        "[Level 10] : ^777777攻擊力 +40^000000",
    ],
    "SM_RECOVERY": [
        "HP回復力向上(Increase HP Recovery)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777提升HP自然回復速度。^000000",
        "[Level 1] : ^777777每10秒回復量+5^000000",
        "[Level 2] : ^777777每10秒回復量+10^000000",
        "[Level 3] : ^777777每10秒回復量+15^000000",
        "[Level 4] : ^777777每10秒回復量+20^000000",
        "[Level 5] : ^777777每10秒回復量+25^000000",
        "[Level 6] : ^777777每10秒回復量+30^000000",
        "[Level 7] : ^777777每10秒回復量+35^000000",
        "[Level 8] : ^777777每10秒回復量+40^000000",
        "[Level 9] : ^777777每10秒回復量+45^000000",
        "[Level 10] : ^777777每10秒回復量+50^000000",
    ],
    "SM_BASH": [
        "重擊(Bash)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標造成強力物理攻擊。^000000",
        "[Level 1] : ^777777攻擊力 130%, SP消耗 8^000000",
        "[Level 2] : ^777777攻擊力 160%, SP消耗 8^000000",
        "[Level 3] : ^777777攻擊力 190%, SP消耗 8^000000",
        "[Level 4] : ^777777攻擊力 220%, SP消耗 8^000000",
        "[Level 5] : ^777777攻擊力 250%, SP消耗 8^000000",
        "[Level 6] : ^777777攻擊力 280%, SP消耗 15^000000",
        "[Level 7] : ^777777攻擊力 310%, SP消耗 15^000000",
        "[Level 8] : ^777777攻擊力 340%, SP消耗 15^000000",
        "[Level 9] : ^777777攻擊力 370%, SP消耗 15^000000",
        "[Level 10] : ^777777攻擊力 400%, SP消耗 15^000000",
    ],
    "SM_PROVOKE": [
        "挑釁(Provoke)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777挑釁目標，降低其防禦但增加其攻擊力。^000000",
        "^777777對Boss級魔物、不死屬性魔物無效。^000000",
        "[Level 1] : ^777777ATK+5%, DEF-10%^000000",
        "[Level 2] : ^777777ATK+8%, DEF-15%^000000",
        "[Level 3] : ^777777ATK+11%, DEF-20%^000000",
        "[Level 4] : ^777777ATK+14%, DEF-25%^000000",
        "[Level 5] : ^777777ATK+17%, DEF-30%^000000",
        "[Level 6] : ^777777ATK+20%, DEF-35%^000000",
        "[Level 7] : ^777777ATK+23%, DEF-40%^000000",
        "[Level 8] : ^777777ATK+26%, DEF-45%^000000",
        "[Level 9] : ^777777ATK+29%, DEF-50%^000000",
        "[Level 10] : ^777777ATK+32%, DEF-55%^000000",
    ],
    "SM_MAGNUM": [
        "霸氣衝擊(Magnum Break)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對周圍5x5範圍的敵人造成火屬性物理攻擊，並將敵人擊退。^000000",
        "^777777使用後附加20%火屬性攻擊10秒。^000000",
        "[Level 1] : ^777777攻擊力 120%, SP消耗 30^000000",
        "[Level 2] : ^777777攻擊力 140%, SP消耗 30^000000",
        "[Level 3] : ^777777攻擊力 160%, SP消耗 30^000000",
        "[Level 4] : ^777777攻擊力 180%, SP消耗 30^000000",
        "[Level 5] : ^777777攻擊力 200%, SP消耗 30^000000",
        "[Level 6] : ^777777攻擊力 220%, SP消耗 30^000000",
        "[Level 7] : ^777777攻擊力 240%, SP消耗 30^000000",
        "[Level 8] : ^777777攻擊力 260%, SP消耗 30^000000",
        "[Level 9] : ^777777攻擊力 280%, SP消耗 30^000000",
        "[Level 10] : ^777777攻擊力 300%, SP消耗 30^000000",
    ],
    "SM_ENDURE": [
        "耐久(Endure)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777一定時間內受到攻擊不會被中斷行動。^000000",
        "[Level 1] : ^777777持續10秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 2] : ^777777持續13秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 3] : ^777777持續16秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 4] : ^777777持續19秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 5] : ^777777持續22秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 6] : ^777777持續25秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 7] : ^777777持續28秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 8] : ^777777持續31秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 9] : ^777777持續34秒, 可承受7次攻擊, SP消耗 10^000000",
        "[Level 10] : ^777777持續37秒, 可承受7次攻擊, SP消耗 10^000000",
        "^777777MDEF+1 (永久效果)^000000",
    ],

    # ===== Mage =====
    "MG_SRECOVERY": [
        "SP回復力向上(Increase SP Recovery)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777提升SP自然回復速度。^000000",
    ],
    "MG_SIGHT": [
        "探索(Sight)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777探測周圍隱藏的敵人。^000000",
        "^990000SP消耗 10^000000",
    ],
    "MG_NAPALMBEAT": [
        "靈魂攻擊(Napalm Beat)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標及周圍敵人造成念屬性魔法攻擊。^000000",
    ],
    "MG_SAFETYWALL": [
        "安全防護罩(Safety Wall)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定位置設置防護罩，可阻擋一定次數的近距離物理攻擊。^000000",
    ],
    "MG_SOULSTRIKE": [
        "靈魂打擊(Soul Strike)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標造成念屬性魔法傷害。對不死屬性魔物傷害增加。^000000",
    ],
    "MG_COLDBOLT": [
        "冰箭術(Cold Bolt)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777召喚冰箭攻擊目標，造成水屬性魔法傷害。^000000",
    ],
    "MG_FROSTDIVER": [
        "冰凍術(Frost Diver)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777向目標發射冰柱，有機率冰凍目標。^000000",
    ],
    "MG_STONECURSE": [
        "石化術(Stone Curse)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777有機率使目標石化。消耗1個紅色寶石。^000000",
    ],
    "MG_FIREBOLT": [
        "火箭術(Fire Bolt)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777召喚火箭攻擊目標，造成火屬性魔法傷害。^000000",
    ],
    "MG_FIREBALL": [
        "火球術(Fire Ball)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777向目標發射火球，對目標及周圍造成火屬性魔法範圍傷害。^000000",
    ],
    "MG_FIREWALL": [
        "火牆(Fire Wall)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定位置設置火牆，碰觸的敵人受到火屬性傷害並被擊退。^000000",
    ],
    "MG_LIGHTNINGBOLT": [
        "雷擊術(Lightning Bolt)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777召喚雷電攻擊目標，造成風屬性魔法傷害。^000000",
    ],
    "MG_THUNDERSTORM": [
        "雷暴(Thunderstorm)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域降下雷暴，造成風屬性範圍魔法傷害。^000000",
    ],
    "MG_ENERGYCOAT": [
        "魔力外衣(Energy Coat)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777消耗SP來減少受到的物理傷害。SP越多減傷越高。^000000",
    ],

    # ===== Acolyte =====
    "AL_DP": [
        "天使之護(Divine Protection)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777降低受到不死屬性和暗屬性魔物的傷害。^000000",
    ],
    "AL_DEMONBANE": [
        "惡魔剋星(Demon Bane)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加對不死屬性和暗屬性魔物的攻擊力。^000000",
    ],
    "AL_HEAL": [
        "治癒術(Heal)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777恢復目標的HP。對不死屬性魔物造成聖屬性傷害。^000000",
    ],
    "AL_INCAGI": [
        "敏捷提升(Increase Agility)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777提升目標的AGI和移動速度。^000000",
    ],
    "AL_BLESSING": [
        "祝福(Blessing)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777提升目標的STR、DEX、INT。對不死和暗屬性目標造成詛咒效果。^000000",
    ],
    "AL_CURE": [
        "治療術(Cure)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777治癒目標的沉默、混亂和黑暗狀態。^000000",
    ],
    "AL_TELEPORT": [
        "瞬間移動(Teleport)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777瞬間移動到同一地圖的隨機位置，或回到存檔點。^000000",
        "[Level 1] : ^777777隨機傳送^000000",
        "[Level 2] : ^777777可選擇隨機傳送或回到存檔點^000000",
    ],
    "AL_WARP": [
        "傳送之陣(Warp Portal)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777開啟傳送陣，可傳送到記憶的地點。消耗1個藍色寶石。^000000",
    ],
    "AL_RUWACH": [
        "霸邪陣(Ruwach)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777探測並攻擊周圍隱藏的敵人，造成聖屬性傷害。^000000",
    ],
    "AL_PNEUMA": [
        "氣功彈防護(Pneuma)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定位置設置防護，可完全阻擋遠距離物理攻擊。^000000",
    ],
    "AL_HOLYWATER": [
        "聖水創造(Aqua Benedicta)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777站在水上時，可將空瓶轉化為聖水。^000000",
    ],
    "AL_CRUCIS": [
        "十字驅魔(Signum Crucis)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777降低畫面內不死屬性和暗屬性魔物的防禦力。^000000",
    ],
    "AL_ANGELUS": [
        "天使之障壁(Angelus)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777提升自身和隊伍成員的VIT防禦力。^000000",
    ],
    "AL_HOLYLIGHT": [
        "聖光術(Holy Light)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標造成聖屬性魔法傷害。^000000",
    ],

    # ===== Archer =====
    "AC_OWL": [
        "貓頭鷹之眼(Owl's Eye)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777提升DEX。^000000",
    ],
    "AC_VULTURE": [
        "鷹之眼(Vulture's Eye)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加弓箭的攻擊距離。^000000",
    ],
    "AC_CONCENTRATION": [
        "集中力提升(Improve Concentration)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777提升AGI和DEX，並偵測周圍隱藏的敵人。^000000",
    ],
    "AC_DOUBLE": [
        "二連矢(Double Strafe)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777快速射出兩支箭矢攻擊目標。^000000",
    ],
    "AC_SHOWER": [
        "箭雨(Arrow Shower)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777向指定區域射出箭雨，造成範圍傷害。^000000",
    ],

    # ===== Thief =====
    "TF_DOUBLE": [
        "連續攻擊(Double Attack)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777裝備短劍時有機率進行二次攻擊。^000000",
    ],
    "TF_MISS": [
        "迴避率增加(Improve Dodge)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777提升FLEE。^000000",
    ],
    "TF_STEAL": [
        "偷竊(Steal)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777嘗試從魔物身上偷取道具。^000000",
    ],
    "TF_HIDING": [
        "躲藏(Hiding)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777躲藏起來，使敵人無法鎖定你。持續消耗SP。^000000",
    ],
    "TF_POISON": [
        "塗毒(Envenom)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標造成毒屬性傷害，有機率使目標中毒。^000000",
    ],

    # ===== Merchant =====
    "MC_INCCARRY": [
        "負重增加(Increase Weight Limit)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加負重上限。^000000",
    ],
    "MC_DISCOUNT": [
        "折扣(Discount)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777向NPC購買道具時獲得折扣。^000000",
    ],
    "MC_OVERCHARGE": [
        "漫天喊價(Overcharge)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777向NPC販賣道具時獲得更高價格。^000000",
    ],
    "MC_MAMMONITE": [
        "金幣投擲(Mammonite)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777投擲Zeny攻擊目標，造成強力物理傷害。^000000",
    ],
    "MC_VENDING": [
        "露天商店(Vending)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777開設露天商店販賣物品。需要手推車。^000000",
    ],

    # ===== Knight =====
    "KN_SPEARMASTERY": [
        "槍術修練(Spear Mastery)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加使用槍時的攻擊力。^000000",
    ],
    "KN_PIERCE": [
        "刺擊(Pierce)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777以長槍刺擊敵人，攻擊次數取決於敵人體型。^000000",
    ],
    "KN_BRANDISHSPEAR": [
        "騎士槍術(Brandish Spear)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777騎乘狀態下使用長槍進行範圍攻擊。^000000",
    ],
    "KN_TWOHANDQUICKEN": [
        "雙手劍加速(Two-Hand Quicken)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777裝備雙手劍時，大幅提升攻擊速度。^000000",
    ],
    "KN_AUTOCOUNTER": [
        "自動反擊(Auto Counter)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使用後短時間內，受到近距離攻擊時自動進行反擊。^000000",
    ],
    "KN_BOWLINGBASH": [
        "保齡球攻擊(Bowling Bash)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777將敵人擊飛碰撞周圍的敵人，造成範圍傷害。^000000",
    ],
    "KN_RIDING": [
        "騎乘(Riding)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777使角色可以騎乘座騎。^000000",
    ],

    # ===== Priest =====
    "PR_MACEMASTERY": [
        "鈍器修練(Mace Mastery)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加使用鈍器時的攻擊力。^000000",
    ],
    "PR_IMPOSITIO": [
        "神聖之光(Impositio Manus)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777提升目標的攻擊力。^000000",
    ],
    "PR_ASPERSIO": [
        "聖水噴灑(Aspersio)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使目標的武器附加聖屬性。消耗1個聖水。^000000",
    ],
    "PR_SANCTUARY": [
        "聖域(Sanctuary)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定位置設置聖域，範圍內的玩家會持續恢復HP。^000000",
        "^777777不死屬性魔物進入會受到傷害。消耗1個藍色寶石。^000000",
    ],
    "ALL_RESURRECTION": [
        "復活術(Resurrection)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777復活已死亡的玩家。消耗1個藍色寶石。^000000",
        "[Level 1] : ^777777復活時HP恢復10%^000000",
        "[Level 2] : ^777777復活時HP恢復30%^000000",
        "[Level 3] : ^777777復活時HP恢復50%^000000",
        "[Level 4] : ^777777復活時HP恢復80%^000000",
    ],
    "PR_KYRIE": [
        "天使之圍(Kyrie Eleison)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777以防護壁保護目標，可擋住一定次數或一定量的物理傷害。^000000",
    ],
    "PR_MAGNIFICAT": [
        "天恩頌歌(Magnificat)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使隊伍全體成員的SP回復速度倍增。^000000",
    ],
    "PR_GLORIA": [
        "榮耀聖歌(Gloria)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777暫時大幅提升隊伍全體成員的LUK。^000000",
    ],
    "PR_LEXDIVINA": [
        "靜默(Lex Divina)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使目標陷入沉默狀態，無法使用技能。^000000",
    ],
    "PR_TURNUNDEAD": [
        "驅魔(Turn Undead)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777有機率一擊消滅不死屬性魔物，否則造成聖屬性傷害。^000000",
    ],
    "PR_LEXAETERNA": [
        "紊亂(Lex Aeterna)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使目標下次受到的傷害倍增。^000000",
    ],
    "PR_MAGNUS": [
        "聖十字攻擊(Magnus Exorcismus)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域降下聖十字，持續造成聖屬性範圍傷害。^000000",
        "^777777消耗1個藍色寶石。^000000",
    ],

    # ===== Wizard =====
    "WZ_METEOR": [
        "隕石術(Meteor Storm)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域降下隕石群，造成火屬性範圍傷害，有機率使敵人暈眩。^000000",
    ],
    "WZ_JUPITEL": [
        "雷擊之盾(Jupitel Thunder)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標發射連續雷球，造成風屬性傷害並擊退目標。^000000",
    ],
    "WZ_VERMILION": [
        "暴風術(Lord of Vermilion)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域引發雷暴，造成風屬性範圍傷害。^000000",
    ],
    "WZ_STORMGUST": [
        "暴風雪(Storm Gust)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域引發暴風雪，造成水屬性範圍傷害，有機率冰凍敵人。^000000",
    ],
    "WZ_WATERBALL": [
        "水球術(Water Ball)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在水上使用時，向目標發射多個水球造成水屬性傷害。^000000",
    ],
    "WZ_ICEWALL": [
        "冰牆(Ice Wall)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定位置設置冰牆，阻擋移動。^000000",
    ],

    # ===== Assassin =====
    "AS_SONICBLOW": [
        "音速擊(Sonic Blow)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標進行8次快速連續攻擊，有機率使目標暈眩。^000000",
    ],
    "AS_CLOAKING": [
        "隱匿(Cloaking)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777隱匿身形，靠近牆壁時可移動。持續消耗SP。^000000",
    ],
    "AS_GRIMTOOTH": [
        "鬼牙擊(Grimtooth)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777隱藏狀態下對遠處目標進行範圍攻擊。^000000",
    ],
    "AS_ENCHANTPOISON": [
        "附魔毒(Enchant Poison)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使武器附加毒屬性。^000000",
    ],

    # ===== Hunter =====
    "HT_BLITZBEAT": [
        "猛鷹襲擊(Blitz Beat)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777命令獵鷹攻擊目標。不受普通攻擊影響。^000000",
    ],
    "HT_ANKLESNARE": [
        "定位陷阱(Ankle Snare)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777設置可捕捉目標的陷阱。被捕捉的目標無法移動。^000000",
    ],

    # ===== Blacksmith =====
    "BS_HAMMERFALL": [
        "猛力鐵鎚(Hammer Fall)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777以鐵鎚猛擊地面，有機率使周圍敵人暈眩。^000000",
    ],
    "BS_ADRENALINE": [
        "腎上腺素飆升(Adrenaline Rush)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777提升隊伍中使用斧和鈍器角色的攻擊速度。^000000",
    ],
    "BS_WEAPONPERFECT": [
        "完美武器(Weapon Perfection)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使隊伍成員的攻擊不受目標體型影響。^000000",
    ],
    "BS_OVERTHRUST": [
        "武器加持(Over Thrust)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777提升隊伍成員的攻擊力，但武器有機率損壞。^000000",
    ],
    "BS_MAXIMIZE": [
        "武器力量最大化(Maximize Power)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使攻擊傷害固定為最大值。持續消耗SP。^000000",
    ],

    # ===== Crusader =====
    "CR_AUTOGUARD": [
        "自動防禦(Auto Guard)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777裝備盾牌時，有機率自動擋住攻擊。^000000",
    ],
    "CR_SHIELDBOOMERANG": [
        "盾牌回力標(Shield Boomerang)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777投擲盾牌攻擊遠距離的目標。傷害受盾牌重量影響。^000000",
    ],
    "CR_REFLECTSHIELD": [
        "盾牌反射(Shield Reflect)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777將受到的部分物理傷害反彈給攻擊者。^000000",
    ],
    "CR_HOLYCROSS": [
        "神聖十字攻擊(Holy Cross)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777以十字攻擊造成聖屬性傷害，有機率使目標黑暗。^000000",
    ],
    "CR_GRANDCROSS": [
        "大十字攻擊(Grand Cross)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在自身周圍造成聖屬性範圍傷害，同時自身也會受到傷害。^000000",
    ],
    "CR_DEVOTION": [
        "獻身(Devotion)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777代替目標承受傷害。^000000",
    ],

    # ===== Monk =====
    "MO_IRONHAND": [
        "鐵砂掌(Iron Fists)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加空手和拳刃的攻擊力。^000000",
    ],
    "MO_CALLSPIRITS": [
        "蓄氣(Summon Spirit Sphere)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777召喚氣彈。最多同時擁有5個氣彈。^000000",
    ],
    "MO_TRIPLEATTACK": [
        "六合拳(Triple Attack)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777普通攻擊時有機率自動進行三次連續攻擊。^000000",
    ],
    "MO_FINGEROFFENSIVE": [
        "彈指神通(Finger Offensive)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777將氣彈射向目標造成傷害。^000000",
    ],
    "MO_STEELBODY": [
        "金剛不壞(Mental Strength)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777極大幅提升DEF和MDEF，但移動速度和攻擊速度大幅下降。^000000",
    ],
    "MO_EXTREMITYFIST": [
        "阿修羅霸凰拳(Asura Strike)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777消耗所有SP和氣彈，對目標造成超高傷害。使用後SP歸零。^000000",
    ],
    "MO_CHAINCOMBO": [
        "連環全身掌(Chain Combo)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777六合拳發動後可接續使用的連擊技能。^000000",
    ],
    "MO_COMBOFINISH": [
        "猛龍誇強(Combo Finish)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777連環全身掌後可接續使用的終結技。^000000",
    ],

    # ===== Sage =====
    "SA_AUTOSPELL": [
        "自動念咒(Auto Spell)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777設定一個魔法，普通攻擊時有機率自動施放該魔法。^000000",
    ],
    "SA_FREECAST": [
        "自由詠唱(Free Cast)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777詠唱魔法時可以移動。^000000",
    ],
    "SA_DISPELL": [
        "消除魔法(Dispell)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777消除目標身上的增益效果。^000000",
    ],
    "SA_VOLCANO": [
        "火山(Volcano)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域設置火山地帶，提升區域內火屬性攻擊力。^000000",
    ],
    "SA_DELUGE": [
        "洪水(Deluge)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域設置洪水地帶，提升區域內水屬性攻擊力。^000000",
    ],
    "SA_VIOLENTGALE": [
        "暴風(Violent Gale)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域設置暴風地帶，提升區域內風屬性攻擊力。^000000",
    ],
    "SA_LANDPROTECTOR": [
        "大地保護(Land Protector)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在指定區域設置保護，消除和阻擋該區域的地面魔法。^000000",
    ],

    # ===== Rogue =====
    "RG_SNATCHER": [
        "掠奪者(Snatcher)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777普通攻擊時有機率自動偷取道具。^000000",
    ],
    "RG_BACKSTAP": [
        "背刺(Back Stab)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777從背後攻擊目標造成高傷害。^000000",
    ],
    "RG_RAID": [
        "襲擊(Raid)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777隱藏狀態下現身並攻擊周圍敵人。^000000",
    ],
    "RG_PLAGIARISM": [
        "抄襲(Plagiarism)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777記憶最後一個受到的技能，可以使用該技能。^000000",
    ],

    # ===== Lord Knight =====
    "LK_AURABLADE": [
        "靈氣之劍(Aura Blade)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777在武器上附加靈氣之力，增加攻擊力，且不受目標DEF影響。^000000",
    ],
    "LK_PARRYING": [
        "格擋(Parrying)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777裝備雙手劍時，有機率完全擋住攻擊。^000000",
    ],
    "LK_BERSERK": [
        "狂暴(Berserk)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777進入狂暴狀態，ATK倍增但無法使用技能和道具。^000000",
        "^777777HP持續減少，結束後HP為1。^000000",
    ],
    "LK_SPIRALPIERCE": [
        "螺旋刺擊(Spiral Pierce)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使用長槍旋轉貫穿目標，傷害受武器重量影響。^000000",
    ],

    # ===== High Priest =====
    "HP_ASSUMPTIO": [
        "聖靈降臨(Assumptio)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777大幅降低目標受到的傷害。與天使之圍不可並存。^000000",
    ],
    "HP_BASILICA": [
        "聖域結界(Basilica)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777設置聖域結界，範圍內的角色不受任何攻擊。^000000",
        "^777777但範圍內的角色也無法攻擊。消耗1個藍色寶石和1個聖水。^000000",
    ],
    "HP_MEDITATIO": [
        "冥想(Meditatio)",
        "系列 : ^000099被動^000000",
        "內容 : ^777777增加SP回復力，提升治癒系技能的回復量。^000000",
    ],

    # ===== High Wizard =====
    "HW_MAGICPOWER": [
        "魔力增幅(Magic Power)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777下一次魔法攻擊的MATK大幅增加。^000000",
    ],
    "HW_NAPALMVULCAN": [
        "靈魂連擊(Napalm Vulcan)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標及周圍造成念屬性多段魔法傷害。^000000",
    ],

    # ===== Assassin Cross =====
    "ASC_EDP": [
        "致命毒藥附加(Enchant Deadly Poison)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777使用致命毒藥塗抹武器，大幅提升攻擊力。消耗1個致命毒藥。^000000",
    ],
    "ASC_METEORASSAULT": [
        "流星攻擊(Meteor Assault)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對周圍敵人造成範圍傷害，有機率造成暈眩、出血、黑暗。^000000",
    ],
    "ASC_BREAKER": [
        "氣功破(Soul Breaker)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777對目標造成物理和魔法的混合傷害。^000000",
    ],

    # ===== Sniper =====
    "SN_FALCONASSAULT": [
        "獵鷹突擊(Falcon Assault)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777命令獵鷹對目標進行強力攻擊。^000000",
    ],
    "SN_SHARPSHOOTING": [
        "精準射擊(Sharp Shooting)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777以精準射擊攻擊直線上的所有目標，高爆擊率。^000000",
    ],
    "SN_WINDWALK": [
        "風之步伐(Wind Walk)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777提升隊伍成員的移動速度和FLEE。^000000",
    ],

    # ===== Champion =====
    "CH_PALMSTRIKE": [
        "猛虎硬派山(Tiger Knuckle Fist)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777猛龍誇強後可接續使用的強力拳擊。^000000",
    ],
    "CH_CHAINCRUSH": [
        "聯柱崩擊(Chain Crush Combo)",
        "系列 : ^000099主動^000000",
        "內容 : ^777777猛虎硬派山後可接續使用的連擊技。消耗氣彈。^000000",
    ],
}


def parse_original_entries(filepath):
    """Parse the original Korean skill description file into entries."""
    data = open(filepath, "rb").read()
    text = data.decode("euc-kr", errors="replace")
    lines = text.split("\r\n")

    entries = {}
    current_id = None
    current_lines = []

    for line in lines:
        if line.endswith("#") and not line.startswith("[") and not line.startswith("^") and not line.startswith(" "):
            skill_id = line[:-1]
            # Check if this looks like a skill ID (contains _ or is all uppercase)
            if "_" in skill_id or skill_id.isupper():
                if current_id is not None:
                    entries[current_id] = current_lines
                current_id = skill_id
                current_lines = []
                continue

        if line == "#":
            if current_id is not None:
                entries[current_id] = current_lines
                current_id = None
                current_lines = []
            continue

        if current_id is not None:
            current_lines.append(line)

    if current_id is not None:
        entries[current_id] = current_lines

    return entries


def generate_simple_desc(skill_id):
    """Generate a simple Chinese description for skills without full translations."""
    zh_name = SKILL_NAME_MAP.get(skill_id, skill_id.replace("_", " "))

    # Determine category
    category = "主動"
    if any(skill_id.startswith(p) for p in ["NPC_", "ALL_"]):
        category = "特殊"

    return [
        f"{zh_name}",
        f"系列 : ^000099{category}^000000",
    ]


def main():
    input_path = os.path.join(EXTRACTED_DIR, "skilldesctable_kr.txt")
    output_path = os.path.join(CLIENT_DATA_DIR, "skilldesctable.txt")

    # Parse original entries to get the skill ID ordering
    original_entries = parse_original_entries(input_path)
    print(f"Original entries: {len(original_entries)}")

    # Read original file to preserve exact structure
    data = open(input_path, "rb").read()
    text = data.decode("euc-kr", errors="replace")
    orig_lines = text.split("\r\n")

    # Rebuild the file: for each entry, use Chinese translation if available,
    # otherwise generate a simple entry
    output_lines = []
    current_id = None
    skip_until_hash = False
    translated = 0
    simple = 0

    for line in orig_lines:
        # Detect skill ID header
        if line.endswith("#") and not line.startswith("[") and not line.startswith("^") and not line.startswith(" "):
            skill_id = line[:-1]
            if "_" in skill_id or (skill_id.isupper() and len(skill_id) > 2):
                current_id = skill_id
                output_lines.append(f"{skill_id}#")

                if skill_id in SKILL_DESC_MAP:
                    # Use full Chinese translation
                    for desc_line in SKILL_DESC_MAP[skill_id]:
                        output_lines.append(desc_line)
                    skip_until_hash = True
                    translated += 1
                elif skill_id in SKILL_NAME_MAP:
                    # Generate simple description
                    for desc_line in generate_simple_desc(skill_id):
                        output_lines.append(desc_line)
                    skip_until_hash = True
                    simple += 1
                else:
                    # Unknown skill - generate minimal entry
                    output_lines.append(skill_id.replace("_", " "))
                    skip_until_hash = True
                    simple += 1
                continue

        if line == "#":
            skip_until_hash = False
            current_id = None
            output_lines.append("#")
            continue

        if skip_until_hash:
            # Skip original Korean lines for entries we've already written
            continue

        # Pass through other lines
        output_lines.append(line)

    # Write Big5 + CRLF
    with open(output_path, "wb") as f:
        for line in output_lines:
            try:
                encoded = line.encode("big5")
            except UnicodeEncodeError:
                encoded = line.encode("big5", errors="replace")
            f.write(encoded + b"\r\n")

    print(f"\n  skilldesctable.txt:")
    print(f"    Full translations: {translated}")
    print(f"    Simple entries: {simple}")
    print(f"    Total output lines: {len(output_lines)}")
    print(f"    Output: {output_path}")

    # Verify
    with open(output_path, "rb") as f:
        content = f.read()
    try:
        content.decode("big5")
        print(f"    Big5 verification: OK")
    except UnicodeDecodeError as e:
        print(f"    Big5 verification: FAILED at byte {e.start}")

    # Sample output
    decoded = content.decode("big5", errors="replace")
    sample_lines = decoded.split("\r\n")
    print(f"\n  Sample output:")
    for i, line in enumerate(sample_lines[:25], 1):
        print(f"    L{i}: {line}")


if __name__ == "__main__":
    main()
