#!/usr/bin/env python3
"""
Enchant Probability Calculator
===============================
Input format (comma-separated):
  ID 名稱Lv.N, ID 名稱Lv.N, ...

Rules:
  - Same level → same probability
  - Higher level → lower probability
  - Total = 100%

Usage:
  python tools/enchant_prob.py
  python tools/enchant_prob.py --ratio 2.5
  python tools/enchant_prob.py --ratio 2 --rathena
"""

import re
import sys
import argparse
from collections import defaultdict
from math import gcd
from functools import reduce


def parse_items(text: str) -> list[dict]:
    items = []
    for entry in (e.strip() for e in text.split(",") if e.strip()):
        entry = entry.strip()

        # Pattern 1: explicit Lv.N  e.g. "310692 霸氣星光Lv.1"
        m = re.match(r"^(\d+)\s+(.+?)Lv[.．]?(\d+)\s*$", entry, re.UNICODE)
        if m:
            items.append({
                "id":    int(m.group(1)),
                "name":  m.group(2).strip() + "Lv." + m.group(3),
                "level": int(m.group(3)),
            })
            continue

        # Pattern 2: trailing number as level  e.g. "4714 INT+5"  "4808 鬥志Lv.4" already caught above
        # Matches anything ending with a digit (after optional non-digit separator like +, ., space)
        m = re.match(r"^(\d+)\s+(.+?)[\+＋]?(\d+)\s*$", entry, re.UNICODE)
        if m:
            items.append({
                "id":    int(m.group(1)),
                "name":  m.group(2).strip() + "+" + m.group(3),
                "level": int(m.group(3)),
            })
            continue

        print(f"  [skip] cannot parse: '{entry}'", file=sys.stderr)
    return items


def assign_weights(items: list[dict], ratio: float) -> list[dict]:
    """
    weight per item = ratio ^ (max_level - item_level)
    → Lv.max gets weight 1, each step down multiplies by ratio.
    """
    max_lv = max(i["level"] for i in items)
    for item in items:
        item["raw_weight"] = ratio ** (max_lv - item["level"])
    total = sum(i["raw_weight"] for i in items)
    for item in items:
        item["prob_pct"] = item["raw_weight"] / total * 100
    return items


def int_weights(items: list[dict]) -> tuple[list[int], int]:
    """
    Scale raw_weight to integers.
    Multiply so minimum weight is exactly 1 (or close to it for non-integer ratios).
    For integer ratios this is exact; for others we scale by 10^6.
    """
    min_w = min(i["raw_weight"] for i in items)
    # check if scaling by min gives integers
    scaled = [round(i["raw_weight"] / min_w) for i in items]
    # verify probabilities are preserved reasonably
    return scaled, sum(scaled)


def print_table(items: list[dict]):
    by_level: dict[int, list] = defaultdict(list)
    for item in items:
        by_level[item["level"]].append(item)

    col_id   = max(len(str(i["id"])) for i in items)
    col_name = max(len(i["name"]) for i in items)
    col_id   = max(col_id, 2)
    col_name = max(col_name, 4)

    header = f"  {'ID':<{col_id}}  {'Name':<{col_name}}  {'Lv':>2}  {'Probability':>12}"
    print("\n" + header)
    print("  " + "-" * (len(header) - 2))

    grand_total = 0.0
    for lv in sorted(by_level):
        lv_items = by_level[lv]
        lv_total = sum(i["prob_pct"] for i in lv_items)
        for item in lv_items:
            print(f"  {item['id']:<{col_id}}  {item['name']:<{col_name}}  {item['level']:>2}  {item['prob_pct']:>11.4f}%")
        print(f"  {'':>{col_id}}  {'  └ Lv.' + str(lv) + ' subtotal':<{col_name}}  {'':>2}  {lv_total:>11.4f}%")
        grand_total += lv_total
        print()

    print(f"  {'TOTAL':>{col_id + col_name + 6}}  {grand_total:>11.4f}%")


def print_rathena(items: list[dict]):
    wts, total = int_weights(items)

    def chunked(lst, n=6):
        return [lst[i:i+n] for i in range(0, len(lst), n)]

    ids_str = [str(i["id"]) for i in items]
    wts_str = [str(w) for w in wts]

    def fmt_array(name, values):
        chunks = chunked(values)
        lines = [f"\tsetarray {name}[0],"]
        for k, chunk in enumerate(chunks):
            sep = ";" if k == len(chunks) - 1 else ","
            lines.append(f"\t\t{', '.join(chunk)}{sep}")
        return "\n".join(lines)

    print("\n// ── rAthena arrays ────────────────────────────────────────")
    print(fmt_array(".@ids", ids_str))
    print()
    print(fmt_array(".@wts", wts_str))
    print(f"\n\t// Total weight: {total}")
    print(f"\t.@r = rand({total}); .@cum = 0;")
    print("""\t for (.@i = 0; .@i < getarraysize(.@ids); .@i++) {
\t     .@cum += .@wts[.@i];
\t     if (.@r < .@cum) { .@result = .@ids[.@i]; break; }
\t }""")


def read_multiline_input(prompt: str) -> str:
    print(prompt)
    print("  (press Enter twice to finish)")
    lines = []
    while True:
        line = input()
        if line == "" and lines:
            break
        if line:
            lines.append(line)
    return " ".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Enchant Probability Calculator")
    parser.add_argument("--ratio",   type=float, default=None,
                        help="Weight ratio between consecutive levels (default: interactive)")
    parser.add_argument("--rathena", action="store_true",
                        help="Also output rAthena setarray code")
    args = parser.parse_args()

    print("=" * 60)
    print("  Enchant Probability Calculator")
    print("  Format:  ID 名稱Lv.N, ID 名稱Lv.N, ...")
    print("=" * 60)

    text = read_multiline_input("\nPaste item list:")
    items = parse_items(text)
    if not items:
        sys.exit("No items parsed.")

    levels = sorted(set(i["level"] for i in items))
    counts = defaultdict(int)
    for item in items:
        counts[item["level"]] += 1

    print(f"\nParsed {len(items)} items  |  Levels found: {levels}")
    for lv in levels:
        print(f"  Lv.{lv}: {counts[lv]} item(s)")

    if args.ratio is not None:
        ratio = args.ratio
    else:
        print(f"\nWeight ratio between consecutive levels")
        print(f"  ratio=2 → Lv.(n+1) gets 1/2 the chance of Lv.n")
        print(f"  ratio=3 → Lv.(n+1) gets 1/3 the chance of Lv.n")
        raw = input("Ratio [2]: ").strip()
        try:
            ratio = float(raw) if raw else 2.0
        except ValueError:
            ratio = 2.0

    print(f"\nUsing ratio = {ratio}")
    max_lv = max(levels)
    for lv in levels:
        w = ratio ** (max_lv - lv)
        print(f"  Lv.{lv} weight per item = {ratio}^({max_lv}-{lv}) = {w:g}")

    items = assign_weights(items, ratio)
    print_table(items)

    do_rathena = args.rathena
    if not do_rathena:
        try:
            ans = input("\nOutput rAthena arrays? [y/N]: ").strip().lower()
            do_rathena = ans == "y"
        except EOFError:
            pass

    if do_rathena:
        print_rathena(items)


if __name__ == "__main__":
    main()
