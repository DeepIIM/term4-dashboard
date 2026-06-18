#!/usr/bin/env python3
"""
Analyze user's ACTUAL locked-in bundle.
Courses: CCR A, ACEL A, GAIB, TSB A, GAFW A, MSN, CEDA A, M&A, SS G
"""

import json

with open('all_courses.json', 'r') as f:
    data = json.load(f)

courses = {c['code']: c for c in data['courses']}

ACTUAL_BUNDLE = ['CCR A', 'ACEL A', 'GAIB', 'TSB A', 'GAFW A', 'MSN', 'CEDA A', 'M&A', 'SS G']

# Merged courses from user's first message
MERGED = {
    'CCR A', 'CCR B', 'ACEL A', 'ACEL B', 'TSB A', 'TSB B', 'CEDA A', 'CEDA B',
    'DIW A', 'DIW B', 'IF A', 'IF B', 'ITWTO A', 'ITWTO B', 'ITA A', 'ITA B',
    'PPA A', 'PPA B', 'ADMA A', 'ADMA B', 'AIMLB A', 'AIMLB B',
    'Python A', 'Python B', 'B2B A', 'B2B B', 'CB A', 'CB B',
    'Retail A', 'Retail B', 'LSS A', 'LSS B', 'PM A', 'PM B',
}

def find_clashes(c1, c2):
    a, b = courses.get(c1), courses.get(c2)
    if not a or not b: return []
    out = []
    for s1 in a['sessions']:
        for s2 in b['sessions']:
            if s1['date'] == s2['date'] and s1['slot'] == s2['slot']:
                out.append({
                    'date': s1['date'], 'day': s1['day'], 'slot': s1['slot'],
                    'time': s1['time'], 'c1_s': s1['sessionNum'], 'c2_s': s2['sessionNum']
                })
    return out

def get_sister(code):
    if ' A' in code: return code.replace(' A', ' B')
    if ' B' in code: return code.replace(' B', ' A')
    return None

def can_use_sister(code, date, slot):
    if code in MERGED:
        return False, "Course is merged - no sister section"
    s = get_sister(code)
    if not s or s not in courses:
        return False, "No sister section exists"
    if not courses[s].get('sisterAllowed', False):
        return False, "Sister attendance not allowed"
    for sess in courses[s]['sessions']:
        if sess['date'] == date and sess['slot'] == slot:
            return False, f"Sister section {s} also clashes on this slot"
    return True, f"Attend {s} instead"

print("="*80)
print("YOUR ACTUAL BUNDLE ANALYSIS")
print("="*80)
print("Courses:", ", ".join(ACTUAL_BUNDLE))
print("Total Credits:", sum(courses.get(c, {}).get('credits', 0) for c in ACTUAL_BUNDLE))

print("\n" + "="*80)
print("ALL CLASHES IN YOUR BUNDLE")
print("="*80)

all_clashes = []
for i, c1 in enumerate(ACTUAL_BUNDLE):
    for c2 in ACTUAL_BUNDLE[i+1:]:
        for clash in find_clashes(c1, c2):
            all_clashes.append({'c1': c1, 'c2': c2, **clash})

resolvable = 0
rigid = 0

for c in all_clashes:
    r1, m1 = can_use_sister(c['c1'], c['date'], c['slot'])
    r2, m2 = can_use_sister(c['c2'], c['date'], c['slot'])
    
    if r1 or r2:
        status = "RESOLVABLE"
        fix = m1 if r1 else m2
        resolvable += 1
    else:
        status = "RIGID"
        fix = f"{m1} | {m2}"
        rigid += 1
    
    print(f"\n[{status}] {c['c1']} <-> {c['c2']}")
    print(f"  When: {c['day']}, {c['date']} at {c['time']} (Slot {c['slot']})")
    print(f"  Sessions: {c['c1']}#{c['c1_s']} <-> {c['c2']}#{c['c2_s']}")
    print(f"  Fix: {fix}")

print("\n" + "="*80)
print(f"SUMMARY: {len(all_clashes)} total clashes | {resolvable} resolvable | {rigid} rigid")
print("="*80)

# Group by how to handle
print("\n" + "="*80)
print("ACTIONABLE BREAKDOWN")
print("="*80)

print("\n1. RIGID CLASHES (You must email professors):")
rigid_list = [c for c in all_clashes if not (can_use_sister(c['c1'], c['date'], c['slot'])[0] or can_use_sister(c['c2'], c['date'], c['slot'])[0])]
for c in rigid_list:
    r1, m1 = can_use_sister(c['c1'], c['date'], c['slot'])
    r2, m2 = can_use_sister(c['c2'], c['date'], c['slot'])
    print(f"\n  • {c['c1']} <-> {c['c2']}")
    print(f"    {c['day']}, {c['date']} | {c['time']} | Slot {c['slot']}")
    print(f"    Why rigid: {m1} AND {m2}")

print("\n2. RESOLVABLE CLASHES (Use sister section + PGP form):")
res_list = [c for c in all_clashes if (can_use_sister(c['c1'], c['date'], c['slot'])[0] or can_use_sister(c['c2'], c['date'], c['slot'])[0])]
for c in res_list:
    r1, m1 = can_use_sister(c['c1'], c['date'], c['slot'])
    r2, m2 = can_use_sister(c['c2'], c['date'], c['slot'])
    fix = m1 if r1 else m2
    sister_course = c['c1'] if r1 else c['c2']
    print(f"\n  • {c['c1']} <-> {c['c2']}")
    print(f"    {c['day']}, {c['date']} | {c['time']} | Slot {c['slot']}")
    print(f"    Fix: {fix}")
    print(f"    Action: Email professor of {sister_course} + submit PGP Office form")
