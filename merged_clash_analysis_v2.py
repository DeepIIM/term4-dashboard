#!/usr/bin/env python3
"""
Comprehensive analysis of merged course impact on clashes.
"""

import json

with open('all_courses.json', 'r') as f:
    data = json.load(f)

courses = {c['code']: c for c in data['courses']}

USER_ADDED = {
    'CCR A', 'ACEL A', 'GAIB', 'TSB A', 'MSN', 'CEDA A', 'M&A'
}

# All courses marked as merged in user's data
MERGED_COURSES = {
    'CCR A', 'CCR B', 'DIW A', 'DIW B', 'IF A', 'IF B',
    'ITWTO A', 'ITWTO B', 'ITA A', 'ITA B', 'ACEL A', 'ACEL B',
    'PPA A', 'PPA B', 'ADMA A', 'ADMA B', 'AIMLB A', 'AIMLB B',
    'Python A', 'Python B', 'TSB A', 'TSB B', 'B2B A', 'B2B B',
    'CB A', 'CB B', 'Retail A', 'Retail B', 'LSS A', 'LSS B',
    'PM A', 'PM B', 'CEDA A', 'CEDA B',
}

def find_clashes(c1_code, c2_code):
    c1 = courses.get(c1_code)
    c2 = courses.get(c2_code)
    if not c1 or not c2:
        return []
    clashes = []
    for s1 in c1['sessions']:
        for s2 in c2['sessions']:
            if s1['date'] == s2['date'] and s1['slot'] == s2['slot']:
                clashes.append({
                    'date': s1['date'], 'day': s1['day'], 'slot': s1['slot'],
                    'time': s1['time'], 'c1_s': s1['sessionNum'], 'c2_s': s2['sessionNum']
                })
    return clashes

def get_sister(code):
    if ' A' in code:
        return code.replace(' A', ' B')
    elif ' B' in code:
        return code.replace(' B', ' A')
    return None

def can_resolve(course_code, clash_date, clash_slot):
    if course_code in MERGED_COURSES:
        return False, "MERGED - no sister section"
    sister = get_sister(course_code)
    if not sister or sister not in courses:
        return False, "No sister section exists"
    if not courses[sister].get('sisterAllowed', False):
        return False, "Sister attendance not allowed"
    for s in courses[sister]['sessions']:
        if s['date'] == clash_date and s['slot'] == clash_slot:
            return False, f"Sister {sister} also clashes"
    return True, f"Attend {sister}"

def analyze_with_ss(ss_code):
    bundle = USER_ADDED | {ss_code, 'SITS A'}
    bundle_list = sorted(bundle)
    clashes = []
    for i, c1 in enumerate(bundle_list):
        for c2 in bundle_list[i+1:]:
            for clash in find_clashes(c1, c2):
                clashes.append({'c1': c1, 'c2': c2, **clash})
    
    resolvable = 0
    rigid = 0
    details = []
    
    for c in clashes:
        r1, m1 = can_resolve(c['c1'], c['date'], c['slot'])
        r2, m2 = can_resolve(c['c2'], c['date'], c['slot'])
        if r1 or r2:
            resolvable += 1
            fix = m1 if r1 else m2
        else:
            rigid += 1
            fix = f"{m1} | {m2}"
        details.append({**c, 'resolvable': r1 or r2, 'fix': fix})
    
    return resolvable, rigid, details

# Check ALL SS sections A-J
print("="*90)
print("SS SECTION COMPARISON (With Merged Course Constraints)")
print("="*90)
print(f"{'SS Section':<12} {'Resolvable':>12} {'Rigid':>8} {'Total':>8}")
print("-"*90)

best_sections = []
for sec in ['A','B','C','D','E','F','G','H','I','J']:
    ss_code = f"SS {sec}"
    res, rig, det = analyze_with_ss(ss_code)
    total = res + rig
    marker = ""
    if rig == 0:
        marker = " <-- ZERO RIGID!"
        best_sections.append((sec, res, rig, total))
    elif rig <= 1:
        marker = " <-- GOOD"
        best_sections.append((sec, res, rig, total))
    print(f"SS-{sec:<9} {res:>12} {rig:>8} {total:>8}{marker}")

print("-"*90)

# Detailed analysis for best sections
if best_sections:
    print("\n" + "="*90)
    print("DETAILED ANALYSIS FOR BEST SS SECTIONS")
    print("="*90)
    for sec, res, rig, total in sorted(best_sections, key=lambda x: (x[2], -x[3])):
        print(f"\n--- SS-{sec} ({res} resolvable, {rig} rigid) ---")
        ss_code = f"SS {sec}"
        _, _, details = analyze_with_ss(ss_code)
        for d in details:
            status = "[OK]" if d['resolvable'] else "[RIGID]"
            print(f"  {status} {d['c1']} <-> {d['c2']} on {d['day']} {d['date']} Slot {d['slot']}")
            print(f"       Fix: {d['fix']}")

# Detailed analysis for user's preferred section G
print("\n" + "="*90)
print("YOUR PREFERRED SECTION: SS-G (DETAILED)")
print("="*90)
res, rig, details = analyze_with_ss("SS G")
print(f"Total clashes: {res + rig} ({res} resolvable, {rig} rigid)")
for d in details:
    status = "[RESOLVABLE]" if d['resolvable'] else "[RIGID]"
    print(f"\n{status}: {d['c1']} <-> {d['c2']}")
    print(f"  When: {d['day']}, {d['date']} at {d['time']} (Slot {d['slot']})")
    print(f"  Sessions: {d['c1']}#{d['c1_s']} and {d['c2']}#{d['c2_s']}")
    print(f"  Fix option: {d['fix']}")

# Identify which merged courses are causing the most damage
print("\n" + "="*90)
print("IMPACT BREAKDOWN: WHICH MERGED COURSES ARE CAUSING PROBLEMS")
print("="*90)

# For SS-G, count how many rigid clashes each merged course causes
res, rig, details = analyze_with_ss("SS G")
merged_impact = {}
for d in details:
    if not d['resolvable']:
        for c in [d['c1'], d['c2']]:
            if c in MERGED_COURSES:
                merged_impact[c] = merged_impact.get(c, 0) + 1

print("\nRigid clashes caused by YOUR merged courses (with SS-G):")
for course, count in sorted(merged_impact.items(), key=lambda x: -x[1]):
    name = courses.get(course, {}).get('name', 'Unknown')
    print(f"  {course}: {count} rigid clash(es) - {name}")

# Recommendations
print("\n" + "="*90)
print("RECOMMENDATIONS")
print("="*90)

print("""
1. ACEL A <-> CCR A clash (July 23, Slot 1):
   - BOTH courses are merged -> NO sister fallback possible
   - This clash is UNAVOIDABLE if you keep both
   - Options: Drop ACEL A OR Drop CCR A
   - Alternative if dropping ACEL: ACEL is merged anyway, no B section available
   - Alternative if dropping CCR: CCR is merged anyway, no B section available
   - Neither has a direct replacement with sister flexibility since both are merged

2. SS-G <-> TSB A clash (June 19, Slot 4):
   - TSB A is merged -> NO TSB-B fallback
   - SS has no sister sections
   - This clash is UNAVOIDABLE with SS-G
   - FIX: Switch to a different SS section!

3. SS-G <-> MSN clash (July 8, Slot 4):
   - MSN has NO sister section (never did)
   - SS has no sister sections
   - This clash was ALWAYS rigid, not caused by merging
   - FIX: Switch to a different SS section!

4. SS-G <-> SITS A clash (June 22, Slot 6):
   - SITS A is NOT merged -> SITS B fallback still works!
   - This is your ONLY resolvable clash
""")

# If they switch SS sections, what happens?
print("\n" + "="*90)
print("WHAT IF YOU SWITCH SS SECTIONS?")
print("="*90)

# Check sections with 0 or 1 rigid clashes
for sec in ['E', 'J', 'A', 'B', 'H']:
    res, rig, det = analyze_with_ss(f"SS {sec}")
    if rig <= 2:
        print(f"\nSS-{sec}: {res} resolvable, {rig} rigid")
        for d in det:
            if not d['resolvable']:
                print(f"  RIGID: {d['c1']} <-> {d['c2']} on {d['date']} Slot {d['slot']}")
