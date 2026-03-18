#!/usr/bin/env python3
"""
Scrape monster skill data from shining-moon.com and output mob_skill_db.txt entries.

Usage:
    python3 tools/scrape_mob_skills.py

Output:
    tools/output/scraped_mob_skills.txt   - mob_skill_db.txt formatted entries
    tools/output/scrape_log.txt           - per-monster log (success/fail/unknown skills)
"""

import re
import time
import random
import yaml
import requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://web.shining-moon.com/?module=monster&action=view&id={}"
DELAY_MIN = 1.5   # seconds between requests (be polite)
DELAY_MAX = 3.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://web.shining-moon.com/",
}

# ── monsters to scrape ──────────────────────────────────────────────────────
MONSTERS = {
    # bl_depth1
    22143: "BIO_LAVA_TOAD",
    22146: "BIO_EMPATHIZER",
    22140: "BIO_ANOLIAN",
    22144: "BIO_LITTLE_FATUM",
    22148: "BIO_HOLY_FRUS",
    22150: "BIO_KAPHA",
    22154: "BIO_PRAY_GIVER",
    22141: "BIO_SKELETON_ARCHER",
    22142: "BIO_DRAGON_TAIL",
    22151: "BIO_SKELETON_SOLDIER",
    22152: "BIO_DARK_PINGUICULA",
    22155: "BIO_WOOD_GOBLIN",
    22145: "BIO_STING",
    22147: "BIO_FIRE_FRILLDORA",
    22149: "BIO_HOLY_SKOGUL",
    22153: "BIO_POM_SPIDER",
    # mjo_wst01
    21951: "MJO_PUNCH_BUG",
    21952: "MJO_AFERDE",
    21953: "MJO_DISPOL",
    21954: "MJO_TIMBERS",
    21955: "MJO_RENIRE",
    # ra_pol01
    21946: "RA_BURNING_NIGHT",
    21947: "RA_DEADSERA",
    21948: "RA_HARDROCK_TITAN",
    21949: "RA_DEADWEEN",
    21950: "RA_GAIA_POL",
}

# ── load skill name → ID map from skill_db.yml ──────────────────────────────
def load_skill_name_map() -> dict[str, int]:
    skill_db_path = Path(__file__).parent.parent / "server" / "db" / "re" / "skill_db.yml"
    with open(skill_db_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    name_to_id = {}
    for entry in data.get("Body", []):
        sid = entry.get("Id")
        name = entry.get("Name")
        if sid and name:
            name_to_id[name.upper()] = sid
    print(f"[skill_db] Loaded {len(name_to_id)} skill name→ID mappings")
    return name_to_id


# ── value converters ─────────────────────────────────────────────────────────
def parse_rate(s: str) -> int:
    """'30%' → 3000,  '5%' → 500,  '100%' → 10000"""
    s = s.strip().rstrip("%")
    return round(float(s) * 100)


def parse_time_ms(s: str) -> int:
    """'0.3s' → 300,  '1s' → 1000,  '0s' → 0"""
    s = s.strip().rstrip("s")
    return round(float(s) * 1000)


def parse_cancelable(s: str) -> str:
    return "yes" if s.strip().lower() == "yes" else "no"


def parse_state(s: str) -> str:
    return s.strip().lower()


def parse_target(s: str) -> str:
    return s.strip().lower().replace(" ", "")


def parse_condition(s: str) -> str:
    # site sometimes wraps in underscores: _always_ → always
    return s.strip().strip("_").lower()


# ── fetch & parse one monster page ───────────────────────────────────────────
def fetch_skills(mob_id: int, session: requests.Session) -> list[dict] | None:
    """
    Returns list of skill row dicts, or None on HTTP error.
    Each dict: name, level, state, rate, cast_time, delay, cancelable, target, condition, cond_value
    """
    url = BASE_URL.format(mob_id)
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERROR] {mob_id}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # find the skills table — look for a table that has a header with "Name" and "Level"
    skills_table = None
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if "name" in headers and "level" in headers and "state" in headers:
            skills_table = table
            break

    if not skills_table:
        print(f"  [WARN] {mob_id}: skills table not found in HTML")
        return []

    # parse header order
    headers = [th.get_text(strip=True).lower() for th in skills_table.find_all("th")]
    col = {h: i for i, h in enumerate(headers)}

    rows = []
    for tr in skills_table.find("tbody").find_all("tr") if skills_table.find("tbody") else skills_table.find_all("tr")[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) < 8:
            continue
        rows.append({
            "name":       cells[col.get("name", 0)],
            "level":      cells[col.get("level", 1)],
            "state":      cells[col.get("state", 2)],
            "rate":       cells[col.get("rate", 3)],
            "cast_time":  cells[col.get("cast time", 4)],
            "delay":      cells[col.get("delay", 5)],
            "cancelable": cells[col.get("cancelable", 6)],
            "target":     cells[col.get("target", 7)],
            "condition":  cells[col.get("condition", 8)] if len(cells) > 8 else "always",
            "cond_value": cells[col.get("value", 9)]     if len(cells) > 9 else "0",
        })
    return rows


# ── convert one skill row to mob_skill_db line ───────────────────────────────
def to_db_line(
    mob_id: int,
    mob_aegis: str,
    row: dict,
    skill_name_map: dict[str, int],
    unknown_skills: set[str],
) -> str | None:
    """
    Returns a formatted mob_skill_db line, or None if skill ID can't be resolved.
    Format:
    MobID,MobAegis@SkillAegis,state,SkillID,Level,Rate,CastTime,Delay,Cancelable,Target,Condition,CondValue,,,,,,,
    """
    # skill aegis name is after '@' in the Name column
    raw_name = row["name"]
    skill_aegis = raw_name.split("@")[-1].strip() if "@" in raw_name else raw_name.strip()

    skill_id = skill_name_map.get(skill_aegis.upper())
    if skill_id is None:
        unknown_skills.add(skill_aegis)
        return None

    try:
        level      = int(row["level"])
        rate       = parse_rate(row["rate"])
        cast_time  = parse_time_ms(row["cast_time"])
        delay      = parse_time_ms(row["delay"])
        cancelable = parse_cancelable(row["cancelable"])
        state      = parse_state(row["state"])
        target     = parse_target(row["target"])
        condition  = parse_condition(row["condition"])
        cond_value = row["cond_value"].strip() or "0"
        # normalise "none" condition value
        if cond_value.lower() in ("none", ""):
            cond_value = "0"
    except (ValueError, KeyError) as e:
        print(f"  [WARN] parse error for {mob_id}@{skill_aegis}: {e} — row={row}")
        return None

    dummy = f"{mob_aegis}@{skill_aegis}"
    return (
        f"{mob_id},{dummy},{state},{skill_id},{level},"
        f"{rate},{cast_time},{delay},{cancelable},{target},"
        f"{condition},{cond_value},,,,,,,,"
    )


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_skills = out_dir / "scraped_mob_skills.txt"
    out_log    = out_dir / "scrape_log.txt"

    skill_name_map = load_skill_name_map()

    session = requests.Session()
    all_lines = []
    log_lines = []
    unknown_skills: set[str] = set()

    total = len(MONSTERS)
    for i, (mob_id, mob_aegis) in enumerate(MONSTERS.items(), 1):
        print(f"[{i:2d}/{total}] Fetching mob {mob_id} ({mob_aegis})...")
        rows = fetch_skills(mob_id, session)

        if rows is None:
            log_lines.append(f"FAIL  {mob_id} {mob_aegis}")
            time.sleep(DELAY_MAX)
            continue

        if not rows:
            log_lines.append(f"EMPTY {mob_id} {mob_aegis} (no skills table found)")
            time.sleep(DELAY_MIN)
            continue

        mob_lines = []
        unknown_for_mob = []
        for row in rows:
            raw_name = row["name"]
            skill_aegis = raw_name.split("@")[-1].strip() if "@" in raw_name else raw_name.strip()
            line = to_db_line(mob_id, mob_aegis, row, skill_name_map, unknown_skills)
            if line:
                mob_lines.append(line)
            else:
                unknown_for_mob.append(skill_aegis)

        all_lines.extend(mob_lines)
        status = f"OK    {mob_id} {mob_aegis}: {len(mob_lines)} entries"
        if unknown_for_mob:
            status += f"  (unknown skills: {', '.join(set(unknown_for_mob))})"
        log_lines.append(status)
        print(f"       → {len(mob_lines)} skill entries")

        # polite delay (skip after last request)
        if i < total:
            sleep_t = random.uniform(DELAY_MIN, DELAY_MAX)
            time.sleep(sleep_t)

    # ── write output ──────────────────────────────────────────────────────────
    header = (
        "// Scraped mob skills — shining-moon.com\n"
        "// Generated by tools/scrape_mob_skills.py\n"
        "// Format: MobID,Dummy,State,SkillID,SkillLv,Rate,CastTime,Delay,Cancelable,Target,Condition,CondValue,...\n\n"
    )
    out_skills.write_text(header + "\n".join(all_lines) + "\n", encoding="utf-8")
    print(f"\n[output] {len(all_lines)} total entries → {out_skills}")

    log_header = "Scrape log\n==========\n"
    if unknown_skills:
        log_header += f"\nUnresolved skill names (not in skill_db.yml):\n"
        for s in sorted(unknown_skills):
            log_header += f"  {s}\n"
        log_header += "\n"
    out_log.write_text(log_header + "\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"[output] Log → {out_log}")

    if unknown_skills:
        print(f"\n[WARN] {len(unknown_skills)} skill name(s) could not be resolved to IDs:")
        for s in sorted(unknown_skills):
            print(f"  {s}")


if __name__ == "__main__":
    main()
