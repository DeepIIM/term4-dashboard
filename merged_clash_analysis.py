#!/usr/bin/env python3
"""
Analyze how merged courses affect clash resolution for the user's final bundle.
"""

import json
from collections import defaultdict

# Load course data
with open('all_courses.json', 'r') as f:
    data = json.load(f)

courses = {c['code']: c for c in data['courses']}

# User's added courses from their pasted data
USER_ADDED = {
    'CCR A',   # Communicating Corporate Reputation - added, merged
    'ACEL A',  # Advanced Corporate and Economic Laws - added, merged
    'GAIB',    # Generative AI in Business - added
    'TSB A',   # Technology Strategy for Business - added, merged
    'MSN',     # Managing Social Networks - added
    'CEDA A',  # Corporate Entrepreneurship - added, merged
    'M&A',     # Mergers and Acquisitions - added
}

# Courses that are "merged" according to user's data
MERGED_COURSES = {
    'CCR A', 'CCR B',
    'DIW A', 'DIW B',
    'IF A', 'IF B',
    'ITWTO A', 'ITWTO B',
    'ITA A', 'ITA B',
    'ACEL A', 'ACEL B',
    'PPA A', 'PPA B',
    'ADMA A', 'ADMA B',
    'AIMLB A', 'AIMLB B',
    'Python A', 'Python B',
    'TSB A', 'TSB B',
    'B2B A', 'B2B B',
    'CB A', 'CB B',
    'Retail A', 'Retail B',
    'LSS A', 'LSS B',
    'PM A', 'PM B',
    'CEDA A', 'CEDA B',
}

def find_clashes(course1_code, course2_code):
    """Find all session clashes between two courses."""
    c1 = courses.get(course1_code)
    c2 = courses.get(course2_code)
    
    if not c1 or not c2:
        return []
    
    clashes = []
    for s1 in c1['sessions']:
        for s2 in c2['sessions']:
            if s1['date'] == s2['date'] and s1['slot'] == s2['slot']:
                clashes.append({
                    'date': s1['date'],
                    'day': s1['day'],
                    'slot': s1['slot'],
                    'time': s1['time'],
                    'c1_session': s1['sessionNum'],
                    'c2_session': s2['sessionNum'],
                    'c1_classroom': s1['classroom'],
                    'c2_classroom': s2['classroom'],
                })
    return clashes

def get_sister_code(code):
    """Get sister section code if it exists."""
    if ' A' in code:
        return code.replace(' A', ' B')
    elif ' B' in code:
        return code.replace(' B', ' A')
    return None

def can_resolve_via_sister(course_code, clash_date, clash_slot):
    """Check if a clash can be resolved by attending sister section."""
    if course_code in MERGED_COURSES:
        return False, "Course is merged - no sister section available"
    
    sister = get_sister_code(course_code)
    if not sister or sister not in courses:
        return False, "No sister section exists"
    
    sister_course = courses[sister]
    if not sister_course.get('sisterAllowed', False):
        return False, "Sister section attendance not allowed"
    
    for s in sister_course['sessions']:
        if s['date'] == clash_date and s['slot'] == clash_slot:
            return False, f"Sister section {sister} also clashes on this slot"
    
    return True, f"Can attend {sister} instead"

def analyze_bundle(ss_section):
    """Analyze the full bundle with a given SS section."""
    bundle = USER_ADDED | {f'SS {ss_section}', 'SITS A'}
    bundle_list = sorted(bundle)
    
    print(f"\n{'='*80}")
    print(f"ANALYZING BUNDLE WITH SS-{ss_section}")
    print(f"{'='*80}")
    print(f"Courses: {', '.join(bundle_list)}")
    print(f"Total Credits: {sum(courses.get(c, {}).get('credits', 0) for c in bundle)}")
    
    all_clashes = []
    
    for i, c1 in enumerate(bundle_list):
        for c2 in bundle_list[i+1:]:
            clashes = find_clashes(c1, c2)
            for clash in clashes:
                all_clashes.append({
                    'course1': c1,
                    'course2': c2,
                    **clash
                })
    
    if not all_clashes:
        print("\n[OK] NO CLASHES FOUND!")
        return []
    
    print(f"\n{'-'*80}")
    print(f"TOTAL CLASHES FOUND: {len(all_clashes)}")
    print(f"{'-'*80}")
    
    resolvable = 0
    unresolvable = 0
    
    for clash in all_clashes:
        c1, c2 = clash['course1'], clash['course2']
        
        r1, msg1 = can_resolve_via_sister(c1, clash['date'], clash['slot'])
        r2, msg2 = can_resolve_via_sister(c2, clash['date'], clash['slot'])
        
        status = "[RIGID]"
        fix = "No fix available"
        
        if r1 or r2:
            status = "[RESOLVABLE]"
            fix = msg1 if r1 else msg2
            resolvable += 1
        else:
            unresolvable += 1
            if "merged" in msg1.lower() or "merged" in msg2.lower():
                fix = f"BOTH COURSES MERGED or NO SISTER: {msg1}; {msg2}"
            else:
                fix = f"{msg1}; {msg2}"
        
        print(f"\n{status} | {c1} <-> {c2}")
        print(f"   Date: {clash['day']}, {clash['date']} | Slot {clash['slot']} ({clash['time']})")
        print(f"   Sessions: {c1}#{clash['c1_session']} <-> {c2}#{clash['c2_session']}")
        print(f"   Fix: {fix}")
    
    print(f"\n{'-'*80}")
    print(f"SUMMARY FOR SS-{ss_section}:")
    print(f"  Total Clashes: {len(all_clashes)}")
    print(f"  [RESOLVABLE]: {resolvable}")
    print(f"  [RIGID]: {unresolvable}")
    print(f"{'-'*80}")
    
    return all_clashes

print("="*80)
print("MERGED COURSE IMPACT ANALYSIS")
print("="*80)
print("\nYour ADDED courses that are MERGED:")
print("  * CCR A  (Communicating Corporate Reputation)")
print("  * ACEL A (Advanced Corporate and Economic Laws)")
print("  * TSB A  (Technology Strategy for Business)")
print("  * CEDA A (Corporate Entrepreneurship)")
print("\nYour ADDED courses NOT merged:")
print("  * GAIB   (Generative AI in Business) - single section")
print("  * MSN    (Managing Social Networks) - single section")
print("  * M&A    (Mergers and Acquisitions) - single section")

print("\n" + "="*80)
print("SISTER SECTION AVAILABILITY CHECK")
print("="*80)

for code in ['CCR A', 'ACEL A', 'TSB A', 'CEDA A']:
    sister = get_sister_code(code)
    has_sister = sister in courses
    is_merged = code in MERGED_COURSES
    
    status = "LOST" if is_merged else ("Available" if has_sister else "Never existed")
    print(f"\n{code}:")
    print(f"  Sister section: {sister if has_sister else 'None'}")
    print(f"  Merged: {'YES' if is_merged else 'No'}")
    print(f"  Fallback status: {status}")

print("\n" + "="*80)
print("FULL BUNDLE CLASH ANALYSIS")
print("="*80)
print("\nNote: You didn't specify which SS section you got.")
print("Testing sections G (your preference) and J (only one with seats in mock):\n")

for ss in ['G', 'J']:
    analyze_bundle(ss)

print("\n" + "="*80)
print("BONUS: ANALYSIS OF JUST YOUR 7 ELECTIVES (no SS, no SITS)")
print("="*80)

electives_only = list(USER_ADDED)
all_clashes_electives = []

for i, c1 in enumerate(electives_only):
    for c2 in electives_only[i+1:]:
        clashes = find_clashes(c1, c2)
        for clash in clashes:
            all_clashes_electives.append({
                'course1': c1,
                'course2': c2,
                **clash
            })

print(f"\nClashes among just your 7 added electives: {len(all_clashes_electives)}")

resolvable_e = 0
unresolvable_e = 0

for clash in all_clashes_electives:
    c1, c2 = clash['course1'], clash['course2']
    r1, msg1 = can_resolve_via_sister(c1, clash['date'], clash['slot'])
    r2, msg2 = can_resolve_via_sister(c2, clash['date'], clash['slot'])
    
    if r1 or r2:
        status = "[RESOLVABLE]"
        resolvable_e += 1
    else:
        status = "[RIGID]"
        unresolvable_e += 1
    
    print(f"\n{status} | {c1} <-> {c2}")
    print(f"   {clash['day']}, {clash['date']} | Slot {clash['slot']} ({clash['time']})")
    if r1 or r2:
        print(f"   Fix: {msg1 if r1 else msg2}")
    else:
        print(f"   Fix: NONE - {msg1}; {msg2}")

print(f"\nSummary (Electives only): {resolvable_e} resolvable, {unresolvable_e} rigid")
