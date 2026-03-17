#!/usr/bin/env python3
"""
scrape_divine_pride.py — Scrape monster data from divine-pride.net and generate rAthena DB entries.

Usage:
    python tools/scrape_divine_pride.py <monster_id> [--dry-run] [--force]

Options:
    --dry-run    Print output without writing files
    --force      Overwrite if monster ID already exists

Dependencies:
    pip install requests beautifulsoup4 pyyaml
"""

import sys
import os
import re
import time
import argparse
import yaml

# Fix Windows terminal encoding (cp950 can't handle Korean/other Unicode chars)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install requests beautifulsoup4 pyyaml")
    sys.exit(1)

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
MOB_DB_PATH = os.path.join(REPO_ROOT, "server", "custom-overlay", "db", "import", "mob_db.yml")
MOB_SKILL_DB_PATH = os.path.join(REPO_ROOT, "server", "custom-overlay", "db", "import", "mob_skill_db.txt")
ITEM_DB_DIR = os.path.join(REPO_ROOT, "server", "db", "re")
ITEM_DB_FILES = [
    os.path.join(REPO_ROOT, "server", "db", "re", "item_db_usable.yml"),
    os.path.join(REPO_ROOT, "server", "db", "re", "item_db_equip.yml"),
    os.path.join(REPO_ROOT, "server", "db", "re", "item_db_etc.yml"),
    os.path.join(REPO_ROOT, "server", "db", "import", "item_db.yml"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# ── Name Mappings ─────────────────────────────────────────────────────────────
# divine-pride race name → rAthena race name
RACE_MAP = {
    "Brute": "Beast",
    "Demon": "Demon",
    "DemiHuman": "DemiHuman",
    "Demi Human": "DemiHuman",
    "Angel": "Angel",
    "Dragon": "Dragon",
    "Fish": "Fish",
    "Formless": "Formless",
    "Insect": "Insect",
    "Plant": "Plant",
    "Undead": "Undead",
    "Beast": "Beast",
}

# divine-pride element name → rAthena element name
ELEMENT_MAP = {
    "Neutral": "Neutral",
    "Water": "Water",
    "Earth": "Earth",
    "Fire": "Fire",
    "Wind": "Wind",
    "Poison": "Poison",
    "Holy": "Holy",
    "Shadow": "Shadow",
    "Ghost": "Ghost",
    "Undead": "Undead",
    "Dark": "Shadow",
    "Darkness": "Shadow",
}

# divine-pride AI flag label → rAthena Modes field name
AI_FLAG_MAP = {
    "Aggressive": "Aggressive",
    "Assist": "Assist",
    "Looter": "Looter",
    "Change target": "ChangeTargetMelee",
    "Change target on attack": "ChangeTargetChase",
    "Immobile": "NoRandomWalk",
    "Cast sensor": "CastSensorIdle",
    "Detector": "Detector",
    "KnockBack immune": "KnockBackImmune",
    "Teleport block": "TeleportBlock",
}

# divine-pride skill state → rAthena mob_skill_db state
STATE_MAP = {
    "Idling": "idle",
    "Attacking": "attack",
    "Chasing": "chase",
    "Dead": "dead",
    "Following": "follow",
    "Any": "any",
}


def _parse_number(text):
    """Parse a string like '1,051,983' → 1051983."""
    try:
        return int(text.replace(",", "").strip())
    except (ValueError, TypeError):
        return 0


def _parse_float(text):
    try:
        return float(text.replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0


# ── Item DB Loader ────────────────────────────────────────────────────────────
def load_item_aegis_map():
    """Load item_id → AegisName from rAthena item_db YAML files."""
    aegis_map = {}

    def load_yaml_items(path):
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data or "Body" not in data:
                return
            for item in data["Body"]:
                item_id = item.get("Id")
                aegis = item.get("AegisName")
                if item_id and aegis:
                    aegis_map[int(item_id)] = aegis
        except Exception as e:
            print(f"  [warn] Could not load {path}: {e}")

    for path in ITEM_DB_FILES:
        load_yaml_items(path)
    return aegis_map


# ── Scraper ───────────────────────────────────────────────────────────────────
def scrape_monster(monster_id):
    url = f"https://www.divine-pride.net/database/monster/{monster_id}/"
    print(f"Fetching: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        print(f"Error: HTTP {resp.status_code} for {url}")
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "html.parser")
    data = {}

    # ── Name from page title / og:title ──────────────────────────────────────
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        # "Monster: Chaotic Side Winder" → "Chaotic Side Winder"
        raw = og["content"]
        data["name"] = raw.split(":", 1)[-1].strip() if ":" in raw else raw.strip()
    else:
        title_el = soup.find("title")
        if title_el:
            t = title_el.get_text(strip=True)
            data["name"] = t.split("-")[-1].strip() if "-" in t else t
        else:
            data["name"] = f"Monster_{monster_id}"

    # AegisName: divine-pride doesn't expose it directly.
    # We'll generate it from the name (user should verify).
    # Hint from audio file names like "anacondaq_*.wav" if present
    data["aegis_name"] = _get_aegis_name(soup, data["name"])

    # ── Parse all tables ──────────────────────────────────────────────────────
    tables = soup.find_all("table")

    # Table 0 (and 1, duplicate): Stats table
    stats = _parse_stats_table(tables[0] if tables else None)
    data.update(stats)

    # Table 2: Element resistance (we already parsed element from stats table)
    # Table 3: AI flags (modes)
    data["modes"] = _parse_ai_flags(tables[3] if len(tables) > 3 else None)

    # Tables 4 & 5: Drops (same table appears twice — take first)
    # Table 6: Map-specific drops (skip)
    data["drops"], data["mvp_drops"] = _parse_drops(soup, tables)

    # Exp table: find table with columns ['Level >=', '%', 'Exp', 'Job Exp']
    data["base_exp"], data["job_exp"] = _parse_exp(soup, tables, data.get("level", 1))

    # Skills table: columns ['Name', 'Interruptable', 'State', 'Level', 'CHANCE', ...]
    data["skills"] = _parse_skills(soup, tables)

    # Defaults for fields not found
    data.setdefault("level", 1)
    data.setdefault("hp", 1)
    data.setdefault("sp", 0)
    data.setdefault("str", 1)
    data.setdefault("agi", 1)
    data.setdefault("vit", 1)
    data.setdefault("int", 1)
    data.setdefault("dex", 1)
    data.setdefault("luk", 1)
    data.setdefault("atk_min", 0)
    data.setdefault("atk_max", 0)
    data.setdefault("def", 0)
    data.setdefault("mdef", 0)
    data.setdefault("walk_speed", 150)
    data.setdefault("atk_delay", 0)
    data.setdefault("atk_motion", 0)
    data.setdefault("dmg_motion", 0)
    data.setdefault("attack_range", 1)
    data.setdefault("skill_range", 10)
    data.setdefault("chase_range", 12)
    data.setdefault("size", "Medium")
    data.setdefault("race", "Formless")
    data.setdefault("element", "Neutral")
    data.setdefault("element_level", 1)
    data.setdefault("ai", "06")
    data.setdefault("class_", "Normal")

    return data


def _get_aegis_name(soup, name):
    """Extract AegisName from divine-pride page.

    divine-pride shows it in <legend class="entry-title">MonsterName<br/>AEGIS_NAME</legend>
    Falls back to audio file heuristic, then generated name.
    """
    # Primary: <legend class="entry-title"> contains Name<br/>AegisName
    legend = soup.find("legend", class_="entry-title")
    if legend:
        br = legend.find("br")
        if br and br.next_sibling:
            aegis = str(br.next_sibling).strip()
            if re.match(r"^[A-Z][A-Z0-9_]+$", aegis):
                return aegis

    # Fallback: audio file names like "anacondaq_attack.wav"
    audio_names = set()
    for td in soup.find_all("td"):
        text = td.get_text(strip=True)
        m = re.match(r"^([a-z0-9_]+?)_(?:attack|damage|die|move|idle)\.", text, re.I)
        if m:
            audio_names.add(m.group(1).upper())
    if audio_names:
        return sorted(audio_names, key=len)[0]

    # Last resort: generate from name
    return re.sub(r"[^A-Za-z0-9]+", "_", name).upper().strip("_")


def _parse_stats_table(table):
    """Parse the stats table (first table on divine-pride monster page)."""
    stats = {}
    if not table:
        return stats

    rows = table.find_all("tr")

    for i, row in enumerate(rows):
        cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
        if not cells:
            continue

        # Row with ID, Level: ['20526', 'Lv.176', '']
        if len(cells) >= 2 and re.match(r"^\d+$", cells[0]) and cells[1].startswith("Lv."):
            m = re.match(r"Lv\.(\d+)", cells[1])
            if m:
                stats["level"] = int(m.group(1))
            continue

        # Row with Race, Size, Element: ['Brute', 'Medium', 'Poison 1']
        if len(cells) == 3 and cells[0] in RACE_MAP and cells[1] in ("Small", "Medium", "Large"):
            stats["race"] = RACE_MAP.get(cells[0], cells[0])
            stats["size"] = cells[1]
            # Element: "Poison 1" or "Neutral 1"
            elem_m = re.match(r"(\w+)\s*(\d*)", cells[2])
            if elem_m:
                stats["element"] = ELEMENT_MAP.get(elem_m.group(1), elem_m.group(1))
                stats["element_level"] = int(elem_m.group(2)) if elem_m.group(2) else 1
            continue

        # Primary stats row: ['183STR', '94AGI', '55VIT'] or ['156INT', '177DEX', '70LUK']
        stat_pattern = re.compile(r"^(\d+)(STR|AGI|VIT|INT|DEX|LUK)$")
        for cell in cells:
            m = stat_pattern.match(cell)
            if m:
                key = m.group(2).lower()
                stats[key] = int(m.group(1))

        # Secondary stats: ['1,051,983Health', '341Def', '108MDef']
        for cell in cells:
            hm = re.match(r"^([\d,]+)Health$", cell)
            if hm:
                stats["hp"] = _parse_number(hm.group(1))
            dm = re.match(r"^([\d,]+)Def$", cell)
            if dm:
                stats["def"] = _parse_number(dm.group(1))
            mm = re.match(r"^([\d,]+)MDef$", cell)
            if mm:
                stats["mdef"] = _parse_number(mm.group(1))
            # Attack: "3,579 - 5,190Attack"
            atk_m = re.match(r"^([\d,]+)\s*-\s*([\d,]+)Attack$", cell)
            if atk_m:
                stats["atk_min"] = _parse_number(atk_m.group(1))
                stats["atk_max"] = _parse_number(atk_m.group(2))
            # Range: "1Range"
            rng_m = re.match(r"^(\d+)Range$", cell)
            if rng_m:
                stats["attack_range"] = int(rng_m.group(1))

        # Misc: speed and aspd
        for cell in cells:
            # "5.00Speed (cells/sec)"
            spd_m = re.match(r"^([\d.]+)Speed", cell)
            if spd_m:
                spd = _parse_float(spd_m.group(1))
                if spd > 0:
                    # rAthena WalkSpeed = ms per cell = round(1000 / cells_per_sec)
                    stats["walk_speed"] = max(50, round(1000.0 / spd))
            # "1.74Aspd (attacks/sec)"
            aspd_m = re.match(r"^([\d.]+)Aspd", cell)
            if aspd_m:
                aspd = _parse_float(aspd_m.group(1))
                if aspd > 0:
                    # AttackDelay = ms between attack starts ≈ round(1000 / aspd)
                    stats["atk_delay"] = max(100, round(1000.0 / aspd))

    return stats


def _parse_ai_flags(table):
    """Parse active AI flags from divine-pride AI flags table."""
    modes = {"CanMove": True, "CanAttack": True}
    if not table:
        return modes

    for row in table.find_all("tr"):
        for cell in row.find_all(["td", "th"]):
            classes = cell.get("class", [])
            text = cell.get_text(strip=True)
            if "enabled" in classes:
                rathena_flag = AI_FLAG_MAP.get(text)
                if rathena_flag:
                    modes[rathena_flag] = True

    return modes


def _parse_drops(soup, tables):
    """Parse drop tables from divine-pride page."""
    drops = []
    mvp_drops = []

    # Find all section headings to locate drop tables
    # divine-pride uses h2/h3/h4 headings before each section
    # Look for drop tables: columns ['Id', 'Name', ..., 'Drop chance']
    seen_tables = set()

    for section in soup.find_all(["h2", "h3", "h4", "h5"]):
        text = section.get_text(strip=True).lower()
        is_mvp = "mvp" in text
        is_drop = "drop" in text

        if not is_drop:
            continue

        # Find next table sibling
        sib = section.find_next_sibling()
        while sib and sib.name not in ("table",):
            sib = sib.find_next_sibling()
        if not sib or sib.name != "table" or id(sib) in seen_tables:
            continue
        seen_tables.add(id(sib))

        parsed = _parse_drop_table(sib)
        if is_mvp:
            mvp_drops.extend(parsed)
        else:
            drops.extend(parsed)

    # Fallback: find drop-like tables (have 'Drop chance' column)
    if not drops:
        for table in tables:
            if id(table) in seen_tables:
                continue
            headers = [c.get_text(strip=True).lower() for c in table.find_all("th")]
            if any("drop" in h for h in headers) and any("id" in h for h in headers):
                seen_tables.add(id(table))
                parsed = _parse_drop_table(table)
                if parsed:
                    drops.extend(parsed)
                    break

    # Remove duplicates (divine-pride shows same drop table twice)
    seen_ids = set()
    deduped_drops = []
    for drop in drops:
        k = (drop["item_id"], drop["rate"])
        if k not in seen_ids:
            seen_ids.add(k)
            deduped_drops.append(drop)

    return deduped_drops, mvp_drops


def _parse_drop_table(table):
    """Parse a single drop table. Returns list of {item_id, item_name, rate}."""
    result = []
    rows = table.find_all("tr")
    if not rows:
        return result

    headers = [c.get_text(strip=True).lower() for c in rows[0].find_all(["th", "td"])]

    # Find column indices
    id_col = next((i for i, h in enumerate(headers) if h == "id"), -1)
    name_col = next((i for i, h in enumerate(headers) if h == "name"), -1)
    rate_col = next((i for i, h in enumerate(headers) if "drop" in h or "chance" in h), -1)

    if id_col == -1:
        return result

    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue

        try:
            item_id = _parse_number(cells[id_col].get_text(strip=True))
        except IndexError:
            continue
        if item_id <= 0:
            continue

        item_name = cells[name_col].get_text(strip=True) if name_col >= 0 and name_col < len(cells) else ""
        # Strip trailing * (stolen-protected marker)
        item_name = item_name.rstrip("*").strip()

        rate_raw = cells[rate_col].get_text(strip=True) if rate_col >= 0 and rate_col < len(cells) else "0%"
        rate = _percent_to_rate(rate_raw)

        result.append({"item_id": item_id, "item_name": item_name, "rate": rate})

    return result


def _percent_to_rate(pct_str):
    """Convert '17.5%' → 1750 (rAthena 10000 = 100%)."""
    pct_str = pct_str.strip().rstrip("%").strip()
    try:
        return max(1, round(float(pct_str) * 100))
    except ValueError:
        return 1


def _parse_exp(soup, tables, monster_level):
    """Extract BaseExp/JobExp from the exp table for the monster's level."""
    for table in tables:
        headers = [c.get_text(strip=True).lower() for c in table.find_all("th")]
        # divine-pride exp table headers: ['level >=', '%', 'exp', 'job exp']
        if not (any("exp" in h for h in headers) and any("job" in h for h in headers)):
            continue

        col_level = next((i for i, h in enumerate(headers) if "level" in h), 0)
        col_exp   = next((i for i, h in enumerate(headers) if h in ("exp", "base exp") or (h == "exp")), -1)
        col_job   = next((i for i, h in enumerate(headers) if "job" in h), -1)

        if col_exp == -1 or col_job == -1:
            continue

        rows = table.find_all("tr")[1:]  # skip header

        best_level = -1
        best_base = 0
        best_job = 0

        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
            try:
                row_level = _parse_number(cells[col_level].get_text(strip=True))
                base_exp  = _parse_number(cells[col_exp].get_text(strip=True))
                job_exp   = _parse_number(cells[col_job].get_text(strip=True))
            except (ValueError, IndexError):
                continue

            if row_level == monster_level:
                return base_exp, job_exp
            if row_level <= monster_level and row_level > best_level:
                best_level = row_level
                best_base  = base_exp
                best_job   = job_exp

        if best_level >= 0:
            return best_base, best_job

    return 0, 0


def _parse_skills(soup, tables):
    """Parse skill table. Returns list of {skill_id, skill_name, skill_lv, state, rate, cancelable, cast_time, delay}."""
    skills = []
    skill_id_re = re.compile(r"/database/skill/(\d+)/")

    for table in tables:
        headers = [c.get_text(strip=True).lower() for c in table.find_all("th")]
        # Skills table: ['name', 'interruptable', 'state', 'level', 'chance', ...]
        if not (any("chance" in h for h in headers) and any("state" in h for h in headers)):
            continue

        col_name    = next((i for i, h in enumerate(headers) if h == "name"), 0)
        col_intr    = next((i for i, h in enumerate(headers) if "interrupt" in h), 1)
        col_state   = next((i for i, h in enumerate(headers) if h == "state"), 2)
        col_level   = next((i for i, h in enumerate(headers) if h == "level"), 3)
        col_chance  = next((i for i, h in enumerate(headers) if "chance" in h), 4)
        col_cast    = next((i for i, h in enumerate(headers) if "cast" in h), 5)
        col_delay   = next((i for i, h in enumerate(headers) if h == "delay"), 6)

        seen_skills = set()  # avoid duplicate rows from double-rendered table
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if not cells:
                continue

            # Skill ID from link in name cell
            skill_id = None
            skill_name = ""
            name_cell = cells[col_name] if col_name < len(cells) else None
            if name_cell:
                a = name_cell.find("a", href=True)
                if a:
                    m = skill_id_re.search(a["href"])
                    if m:
                        skill_id = int(m.group(1))
                        skill_name = a.get_text(strip=True)

            if skill_id is None:
                # Try to get skill name and use 0 as placeholder ID
                if name_cell:
                    skill_name = name_cell.get_text(strip=True)
                skill_id = 0

            skill_lv = 1
            if col_level < len(cells):
                try:
                    skill_lv = int(cells[col_level].get_text(strip=True))
                except ValueError:
                    pass

            state_raw = cells[col_state].get_text(strip=True) if col_state < len(cells) else "Attacking"
            state = STATE_MAP.get(state_raw, "attack")

            chance_raw = cells[col_chance].get_text(strip=True) if col_chance < len(cells) else "5%"
            rate = _percent_to_rate(chance_raw)

            cancelable_raw = cells[col_intr].get_text(strip=True) if col_intr < len(cells) else "yes"
            cancelable = "yes" if cancelable_raw.lower() == "yes" else "no"

            cast_raw = cells[col_cast].get_text(strip=True) if col_cast < len(cells) else "0"
            cast_time = _parse_time_ms(cast_raw)

            delay_raw = cells[col_delay].get_text(strip=True) if col_delay < len(cells) else "5 sec"
            delay_ms = _parse_time_ms(delay_raw)
            if delay_ms == 0:
                delay_ms = 5000  # default 5s delay

            key = (skill_id, skill_name, state)
            if key in seen_skills:
                continue
            seen_skills.add(key)

            skills.append({
                "skill_id": skill_id,
                "skill_name": skill_name,
                "skill_lv": skill_lv,
                "state": state,
                "rate": rate,
                "cast_time": cast_time,
                "delay": delay_ms,
                "cancelable": cancelable,
            })

        if skills:  # take from first matching table
            break

    return skills


def _parse_time_ms(text):
    """Convert '0.7 sec', '5 sec', '5 min', 'instant' → milliseconds."""
    text = text.strip().lower()
    if text in ("instant", "0", ""):
        return 0
    m = re.match(r"([\d.]+)\s*(sec|s|min|m)", text)
    if m:
        val = float(m.group(1))
        unit = m.group(2)
        if unit in ("min", "m"):
            return round(val * 60000)
        return round(val * 1000)
    return 0


# ── Output Generators ─────────────────────────────────────────────────────────
def generate_mob_db_entry(monster_id, data, item_aegis_map):
    """Build YAML string for mob_db.yml entry."""
    lines = []
    lines.append(f"  - Id: {monster_id}")
    lines.append(f"    AegisName: {data['aegis_name']}")
    lines.append(f"    Name: {data['name']}")
    lines.append(f"    Level: {data['level']}")
    lines.append(f"    Hp: {data['hp']}")
    if data["sp"]:
        lines.append(f"    Sp: {data['sp']}")
    lines.append(f"    BaseExp: {data['base_exp']}")
    lines.append(f"    JobExp: {data['job_exp']}")
    lines.append(f"    MvpExp: 0")
    lines.append(f"    Attack: {data['atk_min']}")
    lines.append(f"    Attack2: {data['atk_max']}")
    lines.append(f"    Defense: {data['def']}")
    lines.append(f"    MagicDefense: {data['mdef']}")
    lines.append(f"    Str: {data['str']}")
    lines.append(f"    Agi: {data['agi']}")
    lines.append(f"    Vit: {data['vit']}")
    lines.append(f"    Int: {data['int']}")
    lines.append(f"    Dex: {data['dex']}")
    lines.append(f"    Luk: {data['luk']}")
    lines.append(f"    AttackRange: {data['attack_range']}")
    lines.append(f"    SkillRange: 10")
    lines.append(f"    ChaseRange: 12")
    lines.append(f"    Size: {data['size']}")
    lines.append(f"    Race: {data['race']}")
    lines.append(f"    Element: {data['element']}")
    lines.append(f"    ElementLevel: {data['element_level']}")
    lines.append(f"    WalkSpeed: {data['walk_speed']}")
    lines.append(f"    AttackDelay: {data['atk_delay']}")
    lines.append(f"    AttackMotion: {data['atk_motion']}")
    lines.append(f"    DamageMotion: {data['dmg_motion']}")
    lines.append(f"    DamageTaken: 100")
    lines.append(f"    Ai: {data['ai']}")
    lines.append(f"    Class: {data['class_']}")

    # Modes
    modes = data["modes"]
    if modes:
        lines.append("    Modes:")
        for mode, val in modes.items():
            lines.append(f"      {mode}: {'true' if val else 'false'}")

    # Track unmapped items
    unmapped_items = []

    def resolve_drop(drop):
        aegis = item_aegis_map.get(drop["item_id"])
        if aegis:
            return aegis, False
        unmapped_items.append(drop["item_id"])
        return f"# ITEM_{drop['item_id']}_UNKNOWN ({drop['item_name']})", True

    # MVP Drops (max 3)
    if data["mvp_drops"]:
        lines.append("    MvpDrops:")
        for drop in data["mvp_drops"][:3]:
            aegis, unknown = resolve_drop(drop)
            lines.append(f"      - Item: {aegis}")
            lines.append(f"        Rate: {drop['rate']}")

    # Regular Drops (max 9)
    if data["drops"]:
        lines.append("    Drops:")
        for drop in data["drops"][:9]:
            aegis, unknown = resolve_drop(drop)
            lines.append(f"      - Item: {aegis}")
            lines.append(f"        Rate: {drop['rate']}")

    return "\n".join(lines) + "\n", unmapped_items


def generate_mob_skill_lines(monster_id, data):
    """Build mob_skill_db.txt lines."""
    lines = []
    mob_id = monster_id
    mob_aegis = data["aegis_name"]

    # Skill IDs that buff/heal the caster — should target self, not the player
    SELF_BUFF_IDS = {
        28,   # AL_HEAL / Heal
        60,   # KN_TWOHANDQUICKEN / Two Hand Quicken
        249,  # KN_GUARD / Guard
        361,  # PR_ASSUMPTIO / Assumptio
        687,  # Full Heal
        86,   # PR_BLESSING / Blessing
        26,   # AL_TELEPORT — keep as self (monster teleports itself)
    }

    for skill in data["skills"]:
        skill_id   = skill["skill_id"]
        skill_lv   = skill["skill_lv"]
        skill_name = skill["skill_name"]
        state      = skill["state"]
        rate       = skill["rate"]
        cast_time  = skill["cast_time"]
        delay      = skill["delay"]
        cancelable = skill["cancelable"]

        skill_target = "self" if skill_id in SELF_BUFF_IDS else "target"

        # Format: MobID,Dummy,State,SkillID,SkillLv,Rate,CastTime,Delay,Cancelable,Target,Condition,CondVal,v1,v2,v3,v4,v5,Emotion,Chat
        dummy = f"{mob_aegis}@{skill_name}"
        line = f"{mob_id},{dummy},{state},{skill_id},{skill_lv},{rate},{cast_time},{delay},{cancelable},{skill_target},always,0,,,,,,,"
        lines.append(line)

    return lines


# ── File I/O ──────────────────────────────────────────────────────────────────
def check_mob_db_duplicate(monster_id):
    if not os.path.exists(MOB_DB_PATH):
        return False
    with open(MOB_DB_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return bool(re.search(rf"^\s*-\s*Id:\s*{monster_id}\s*$", content, re.M))


def check_mob_skill_duplicate(monster_id):
    if not os.path.exists(MOB_SKILL_DB_PATH):
        return False
    with open(MOB_SKILL_DB_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return bool(re.search(rf"^{monster_id},", content, re.M))


def append_to_mob_db(entry_text):
    """Insert entry before '#Body:' comment or append at end of Body section."""
    with open(MOB_DB_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    marker = "#Body:"
    if marker in content:
        insert_pos = content.index(marker)
        prefix = content[:insert_pos]
        if not prefix.endswith("\n\n"):
            prefix = prefix.rstrip("\n") + "\n\n"
        new_content = prefix + entry_text + "\n" + content[insert_pos:]
    else:
        new_content = content.rstrip("\n") + "\n\n" + entry_text

    with open(MOB_DB_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)


MOB_SKILL_HEADER = """\
// Custom Mob Skill Database
//
// Structure of Database:
// MobID,Dummy value (info only),State,SkillID,SkillLv,Rate,CastTime,Delay,Cancelable,Target,Condition type,Condition value,val1,val2,val3,val4,val5,Emotion,Chat
//
// RATE: the chance of the skill being casted when the condition is fulfilled (10000 = 100%).
// DELAY: the time (in milliseconds) before attempting to recast the same skill.
//
"""


def append_to_mob_skill_db(skill_lines):
    if not os.path.exists(MOB_SKILL_DB_PATH):
        with open(MOB_SKILL_DB_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(MOB_SKILL_HEADER)

    with open(MOB_SKILL_DB_PATH, "a", encoding="utf-8", newline="\n") as f:
        for line in skill_lines:
            f.write(line + "\n")


# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_id_args(id_args):
    """Parse list of ID tokens: '21946' or '21946-21950' → sorted unique int list."""
    ids = []
    for token in id_args:
        m = re.match(r"^(\d+)-(\d+)$", token)
        if m:
            ids.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            ids.append(int(token))
    return sorted(set(ids))


def process_one(monster_id, item_aegis_map, dry_run, force, verbose=True):
    """Scrape and write one monster. Returns True on success."""
    try:
        data = scrape_monster(monster_id)
    except SystemExit:
        return False

    mob_entry, unmapped_items = generate_mob_db_entry(monster_id, data, item_aegis_map)
    skill_lines = generate_mob_skill_lines(monster_id, data)

    if verbose:
        print("\n" + "=" * 60)
        print(f"Monster ID   : {monster_id}")
        print(f"Name         : {data['name']}")
        print(f"AegisName    : {data['aegis_name']}")
        print(f"Level        : {data['level']}")
        print(f"HP           : {data['hp']}")
        print(f"BaseExp/Job  : {data['base_exp']} / {data['job_exp']}")
        print(f"ATK          : {data['atk_min']} ~ {data['atk_max']}")
        print(f"DEF/MDEF     : {data['def']} / {data['mdef']}")
        print(f"STR/AGI/VIT  : {data['str']} / {data['agi']} / {data['vit']}")
        print(f"INT/DEX/LUK  : {data['int']} / {data['dex']} / {data['luk']}")
        print(f"Size/Race    : {data['size']} / {data['race']}")
        print(f"Element      : {data['element']} Lv{data['element_level']}")
        print(f"Drops        : {len(data['drops'])} items  |  Skills: {len(data['skills'])}")
        print("=" * 60)

    if unmapped_items:
        print(f"  [WARN] Unmapped item IDs: {unmapped_items}")

    if dry_run:
        print("\n--- mob_db.yml entry (dry-run) ---")
        print(mob_entry)
        return True

    # mob_db.yml
    mob_dup = check_mob_db_duplicate(monster_id)
    if mob_dup and not force:
        print(f"  [SKIP] {monster_id} already in mob_db.yml (use --force to overwrite)")
    else:
        append_to_mob_db(mob_entry)
        print(f"  [OK] mob_db.yml ← {monster_id} {data['name']}")

    # mob_skill_db.txt
    skill_dup = check_mob_skill_duplicate(monster_id)
    if skill_dup and not force:
        print(f"  [SKIP] {monster_id} skills already in mob_skill_db.txt")
    elif skill_lines:
        append_to_mob_skill_db(skill_lines)
        print(f"  [OK] mob_skill_db.txt ← {len(skill_lines)} skill lines")

    return True


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Scrape monster data from divine-pride.net and generate rAthena DB entries.\n"
            "Accepts single IDs or ranges: 21946 21951-21955 22140-22155"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "monster_ids", nargs="+",
        help="One or more monster IDs or ranges (e.g. 21946 21951-21955 22140-22155)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing files")
    parser.add_argument("--force", action="store_true", help="Skip duplicate check and always append")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Seconds between requests (default: 1.5)")
    args = parser.parse_args()

    ids = parse_id_args(args.monster_ids)
    print(f"Batch: {len(ids)} monsters to scrape: {ids}")

    print("Loading item AegisName map...")
    item_aegis_map = load_item_aegis_map()
    print(f"  Loaded {len(item_aegis_map)} items.\n")

    ok, failed = 0, []
    for i, mid in enumerate(ids):
        print(f"\n[{i+1}/{len(ids)}] Monster {mid}")
        success = process_one(mid, item_aegis_map, args.dry_run, args.force)
        if success:
            ok += 1
        else:
            failed.append(mid)
        if i < len(ids) - 1:
            time.sleep(args.delay)

    print(f"\n{'='*60}")
    print(f"Done: {ok} OK, {len(failed)} failed")
    if failed:
        print(f"Failed IDs: {failed}")


if __name__ == "__main__":
    main()
