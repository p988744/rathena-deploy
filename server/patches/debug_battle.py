#!/usr/bin/env python3
"""Find where NC_AXETORNADO and similar weapon skills are handled in skill.cpp"""
import sys, re

path = sys.argv[1]
content = open(path, encoding="utf-8", errors="replace").read()

# Find NC_AXETORNADO - definitely a weapon damage skill
for skill in ["NC_AXETORNADO", "NC_ARMSCANNON", "MT_RUSH_STRIKE", "MT_RUSH_QUAKE"]:
    for m in re.finditer(f"case {skill}:", content):
        idx = m.start()
        ctx = content[max(0, idx-50): idx+300]
        print(f"\n{skill} at pos {idx}:")
        print(repr(ctx))

print("\n\n--- All function-like definitions containing skill_castend ---")
for m in re.finditer(r'\n((?:static\s+)?(?:int|bool|void|auto|t_tick|int32_t?)\s+)(skill_castend\w+)\s*\(', content):
    print(f"  {m.group(2)} at pos {m.start()}: {repr(content[m.start():m.start()+120])}")
