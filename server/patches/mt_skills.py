#!/usr/bin/env python3
"""
Patches rAthena battle.cpp to add per-hit damage ratios for:
  MT_SPARK_BLASTER (6002) - Ranged AoE, 2 hits (via HitCount), ignores DEF
  MT_TRIPLE_LASER  (6003) - Ranged single target, 3 hits (via HitCount), can crit
  MT_MIGHTY_SMASH  (6004) - Melee AoE, 5/7 hits (wd.div_ already handled in battle.cpp)

Damage formulas from divine-pride.net:
  MT_SPARK_BLASTER per hit: (600+1400*lv)%, Lv1=2000% to Lv10=14600%
  MT_TRIPLE_LASER  per hit: (550+900*lv)%
  MT_MIGHTY_SMASH  per hit normal:    {205,345,485,745,925,1095,1280,1465,1645,1825}%
                   per hit AXE_STOMP: {230,370,510,770,950,1120,1305,1490,1670,1850}%

Architecture notes (rAthena commit f464a8b81):
  - Weapon-type skills are handled generically — no castend case needed in skill.cpp
  - NC_AXETORNADO, NC_ARMSCANNON etc. also have no explicit castend case
  - Damage ratio lives in battle_calc_weapon_skill_dmg() in battle.cpp
  - The switch there ends with: case SKE_ALL_IN_THE_SKY (insert before it)
  - wd.div_ for MT_MIGHTY_SMASH (5 normal / 7 w/ SC_AXE_STOMP) already implemented
  - status_change public API: sc->hasSCE(SC_X) returns bool
"""

import sys, os, re

def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def find_first_anchor(content, anchors):
    for a in anchors:
        if a in content:
            return a
    return None

def print_cases(content, label):
    found = sorted(set(re.findall(r'case\s+((?:MT_|NC_)\w+)\s*:', content)))
    print(f"  [{label}] MT_/NC_ cases: {', '.join(found[:30]) if found else 'none'}")


# ── battle.cpp damage ratios ───────────────────────────────────────────────
# Insert into the skillratio switch in battle_calc_weapon_skill_dmg().
# The switch ends just before "return skillratio;" with case SKE_ALL_IN_THE_SKY.

MARKER  = "case MT_SPARK_BLASTER:"

ANCHORS = [
    "\t\tcase SKE_ALL_IN_THE_SKY:\n",
    "\t\t\tcase SKE_ALL_IN_THE_SKY:\n",
    "\t\tcase ABR_INFINITY_BUSTER:\n",
    "\t\t\tcase ABR_INFINITY_BUSTER:\n",
    "\t\tcase ABR_BATTLE_BUSTER:\n",
    "\t\t\tcase ABR_BATTLE_BUSTER:\n",
]

CODE = """\
\t\tcase MT_SPARK_BLASTER:
\t\t\t// Per hit: (600+1400*lv)%, Lv1=2000% to Lv10=14600%
\t\t\tskillratio += -100 + 600 + 1400 * skill_lv;
\t\t\tbreak;
\t\tcase MT_TRIPLE_LASER:
\t\t\t// Per hit: (550+900*lv)%
\t\t\tskillratio += -100 + 550 + 900 * skill_lv;
\t\t\tbreak;
\t\tcase MT_MIGHTY_SMASH:
\t\t{
\t\t\t// Per hit normal:    {205,345,485,745,925,1095,1280,1465,1645,1825}%
\t\t\t// Per hit AXE_STOMP: {230,370,510,770,950,1120,1305,1490,1670,1850}%
\t\t\tconst int32_t ratio_normal[10] = {205, 345, 485, 745, 925, 1095, 1280, 1465, 1645, 1825};
\t\t\tconst int32_t ratio_stomp[10]  = {230, 370, 510, 770, 950, 1120, 1305, 1490, 1670, 1850};
\t\t\tint32_t lv = cap_value(skill_lv, 1, 10) - 1;
\t\t\tif (sc != nullptr && sc->hasSCE(SC_AXE_STOMP))
\t\t\t\tskillratio += -100 + ratio_stomp[lv];
\t\t\telse
\t\t\t\tskillratio += -100 + ratio_normal[lv];
\t\t\tbreak;
\t\t}
"""


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <battle.cpp>")
        sys.exit(1)

    battle_cpp = sys.argv[1]
    if not os.path.isfile(battle_cpp):
        print(f"ERROR: file not found: {battle_cpp}")
        sys.exit(1)

    print(f"Patching {battle_cpp} (damage formulas)...")
    content = read(battle_cpp)

    if MARKER in content:
        print("  Already patched, skipping.")
        return

    anchor = find_first_anchor(content, ANCHORS)
    if anchor is None:
        print("  ERROR: no anchor found.")
        print_cases(content, "battle.cpp")
        sys.exit(1)

    write(battle_cpp, content.replace(anchor, CODE + anchor, 1))
    print(f"  Patched (anchor: {repr(anchor.strip())}).")
    print("Done.")


if __name__ == "__main__":
    main()
