#!/usr/bin/env python3
"""
Final clash report for locked-in courses.
User cannot change courses anymore.
"""

import json

with open('all_courses.json', 'r') as f:
    data = json.load(f)

courses = {c['code']: c for c in data['courses']}

# User's FIXED courses
FIXED_ELECTIVES = ['CCR A', 'ACEL A', 'GAIB', 'TSB A', 'MSN', 'CEDA A', 'M&A', 'SITS A']

# Merged courses from user's data
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

def sister_available(code):
    if code in MERGED: return False
    s = get_sister(code)
    if not s or s not in courses: return False
    return courses[s].get('sisterAllowed', False)

def sister_clashes_too(code, date, slot):
    s = get_sister(code)
    if not s or s not in courses: return True
    for sess in courses[s]['sessions']:
        if sess['date'] == date and sess['slot'] == slot:
            return True
    return False

# PART 1: Clashes AMONG electives (no SS needed)
print("="*80)
print("PART 1: CLASHES AMONG YOUR 8 ELECTIVES (Independent of SS)")
print("="*80)

elective_clashes = []
for i, c1 in enumerate(FIXED_ELECTIVES):
    for c2 in FIXED_ELECTIVES[i+1:]:
        for clash in find_clashes(c1, c2):
            elective_clashes.append({'c1': c1, 'c2': c2, **clash})

if not elective_clashes:
    print("None found.")
else:
    for c in elective_clashes:
        s1_ok = sister_available(c['c1']) and not sister_clashes_too(c['c1'], c['date'], c['slot'])
        s2_ok = sister_available(c['c2']) and not sister_clashes_too(c['c2'], c['date'], c['slot'])
        status = "RESOLVABLE" if (s1_ok or s2_ok) else "RIGID"
        fix = ""
        if s1_ok: fix = f"Attend {get_sister(c['c1'])} instead of {c['c1']}"
        elif s2_ok: fix = f"Attend {get_sister(c['c2'])} instead of {c['c2']}"
        else: fix = "No sister fallback available"
        print(f"\n[{status}] {c['c1']} <-> {c['c2']}")
        print(f"  When: {c['day']}, {c['date']} at {c['time']} (Slot {c['slot']})")
        print(f"  Fix: {fix}")

# PART 2: SS-dependent clash matrix
print("\n" + "="*80)
print("PART 2: SS-SECTION DEPENDENT CLASHES")
print("="*80)
print("""
Since your SS section is fixed but wasn't specified, here is the complete
breakdown by section. FIND YOUR SS SECTION and read the row.
""")

print(f"{'SS':<5} {'Total':>6} {'Rigid':>6} {'Resolvable':>12} {'How to Resolve':<40}")
print("-"*80)

for sec in ['A','B','C','D','E','F','G','H','I','J']:
    ss = f"SS {sec}"
    all_clashes = []
    for c in FIXED_ELECTIVES:
        for clash in find_clashes(ss, c):
            all_clashes.append({'c1': ss, 'c2': c, **clash})
    
    rigid = 0
    resolvable = 0
    fixes = []
    
    for c in all_clashes:
        s2_ok = sister_available(c['c2']) and not sister_clashes_too(c['c2'], c['date'], c['slot'])
        if s2_ok:
            resolvable += 1
            fixes.append(f"{c['c2']}->{get_sister(c['c2'])}")
        else:
            rigid += 1
            fixes.append(f"RIGID:{c['c2']}")
    
    fix_str = "; ".join(fixes) if fixes else "None"
    print(f"SS-{sec:<3} {len(all_clashes):>6} {rigid:>6} {resolvable:>12} {fix_str:<40}")

# PART 3: Detailed for common sections
print("\n" + "="*80)
print("PART 3: DETAILED BY SS SECTION (Most Common)")
print("="*80)

for sec in ['E', 'G', 'J']:
    ss = f"SS {sec}"
    print(f"\n--- SS-{sec} ---")
    clashes = []
    for c in FIXED_ELECTIVES:
        for clash in find_clashes(ss, c):
            clashes.append({'c1': ss, 'c2': c, **clash})
    
    if not clashes:
        print("  No clashes with electives.")
        continue
    
    for c in clashes:
        s2_ok = sister_available(c['c2']) and not sister_clashes_too(c['c2'], c['date'], c['slot'])
        status = "RESOLVABLE" if s2_ok else "RIGID"
        if s2_ok:
            fix = f"Attend {get_sister(c['c2'])} for this session"
        else:
            reasons = []
            if c['c2'] in MERGED: reasons.append(f"{c['c2']} is merged")
            if not get_sister(c['c2']): reasons.append("no sister section")
            elif not courses.get(get_sister(c['c2']), {}).get('sisterAllowed'): reasons.append("sister not allowed")
            elif sister_clashes_too(c['c2'], c['date'], c['slot']): reasons.append("sister also clashes")
            fix = "RIGID: " + ", ".join(reasons)
        
        print(f"  [{status}] {c['c2']} on {c['day']} {c['date']} Slot {c['slot']} ({c['time']})")
        print(f"         Fix: {fix}")

# PART 4: Action plan
print("\n" + "="*80)
print("PART 4: WHAT TO DO NOW (Courses Are Locked)")
print("="*80)

print("""
For RESOLVABLE clashes:
1. Email the professor of the course whose sister section you will attend.
2. Submit the PGP Office Google Form for sister section attendance.
3. Attend the sister section for that specific session only.

For RIGID clashes:
1. Email BOTH professors explaining the clash.
2. Ask if you can miss one session or get the material asynchronously.
3. Some professors record sessions or provide slides — ask about this.
4. If attendance is mandatory, you may need to physically attend one and 
   catch up on the other via classmates/notes.

Sister section rules reminder:
- Allowed ONLY for genuine clashes (not convenience)
- Requires instructor approval + PGP Office form
- Do it BEFORE the session, not after
""")
