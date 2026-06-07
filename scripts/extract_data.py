import pandas as pd
import re
import json
from datetime import datetime
from collections import defaultdict

# File paths
excel_file = r"C:/Users/dknun/Downloads/Course selection/docs/Term-IV Time Table (PGP 2025-27 batch) AY 2026-27.xlsx"
output_file = r"C:/Users/dknun/Downloads/Course selection/dashboard/courses.json"

# User's final courses with metadata
user_courses = {
    'CCR A': {'name': 'Communicating Corporate Reputation', 'faculty': 'Prof. Shivani Sharma', 'credits': 2, 'sister': True},
    'ACEL A': {'name': 'Advanced Corporate and Economic Laws', 'faculty': 'Prof. I. Sridhar', 'credits': 2, 'sister': True},
    'GAIB': {'name': 'Generative Artificial Intelligence in Business', 'faculty': 'Prof. Prabin K Panigrahi', 'credits': 2, 'sister': False},
    'TSB A': {'name': 'Technology Strategy for Business', 'faculty': 'Prof. Rajhans Mishra', 'credits': 2, 'sister': True},
    'GAFW A': {'name': 'Gen AI and Future of Work', 'faculty': 'Prof. Kajari Mukherjee', 'credits': 1, 'sister': True},
    'MSN': {'name': 'Managing Social Networks', 'faculty': 'Prof. Nobin Thomas', 'credits': 2, 'sister': False},
    'CEDA A': {'name': 'Corporate Entrepreneurship In The Disruptive Age', 'faculty': 'Prof. Sumit Chakraborty', 'credits': 3, 'sister': True},
    'M&A': {'name': 'Mergers and Acquisitions', 'faculty': 'Prof. Manish Popli', 'credits': 3, 'sister': False},
    'SS G': {'name': 'Strategy Simulation', 'faculty': 'Prof. Rotation (Surana/Dwibedy/Basu/Gunta/Sunder)', 'credits': 3, 'sister': False},
}

# Slot timing mapping
slot_times = {
    2: '9:00 am - 10:15 am',
    3: '10:30 am - 11:45 am',
    4: '12 noon - 1:15 pm',
    6: '2:30 pm - 3:45 pm',
    7: '4:00 pm - 5:15 pm',
    8: '5:30 pm - 6:45 pm',
    9: '7:00 pm - 8:15 pm',
    10: '8:45 pm - 10:00 pm',
    11: '10:15 pm - 11:30 pm',
}

# Read timetable
tt = pd.read_excel(excel_file, sheet_name='TT T-4', header=None)
slot_cols = list(tt.columns[2:])

# Patterns that capture session numbers
patterns = {
    'ACEL': re.compile(r'^ACEL\s+([A-B])\s*(\d*)$'),
    'CCR': re.compile(r'^CCR\s+([A-B])\s*(\d*)$'),
    'CEDA': re.compile(r'^CEDA\s+([A-B])\s*(\d*)$'),
    'TSB': re.compile(r'^TSB\s+([A-B])\s*(\d*)$'),
    'SITS': re.compile(r'^SITS\s+([A-B])\s*(\d*)$'),
    'SS': re.compile(r'^SS\s+([A-J])\s*(\d*)$'),
    'GAFW': re.compile(r'^GAFW\s+([A-B])\s*(\d*)$'),
    'GAIB': re.compile(r'^GAIB\s+(\d+)$'),
    'MSN': re.compile(r'^MSN\s+(\d+)$'),
    'M&A': re.compile(r'^M&A\s+(\d+)$'),
}

sessions = defaultdict(list)
classrooms = defaultdict(dict)

for _, row in tt.iterrows():
    date = row.iloc[0]
    if not (isinstance(date, pd.Timestamp) or isinstance(date, datetime)):
        continue
    d = date.date().isoformat()
    classroom = row.iloc[1] if not pd.isna(row.iloc[1]) else ''
    
    for col_idx in slot_cols:
        val = row[col_idx]
        if pd.isna(val): 
            continue
        s = str(val).strip()
        
        # Skip SM entirely
        if s.startswith('SM'):
            continue
            
        for code, pat in patterns.items():
            m = pat.match(s)
            if m:
                if code in ['GAIB', 'MSN', 'M&A']:
                    key = code
                    num = int(m.group(1)) if m.group(1) else None
                else:
                    sec = m.group(1)
                    num = int(m.group(2)) if m.group(2) else None
                    key = f'{code} {sec}'
                sessions[key].append({'date': d, 'slot': col_idx, 'num': num})
                classrooms[key][(d, col_idx)] = classroom
                break

# Build output data
courses_output = []
for course_code, meta in user_courses.items():
    if course_code not in sessions:
        print(f"WARNING: {course_code} not found in timetable")
        continue
    
    # Sort by official session number (if available), otherwise by date+slot
    course_sessions = sorted(sessions[course_code], key=lambda x: (x['num'] if x['num'] else 999, x['date'], x['slot']))
    
    course_sessions_out = []
    for s in course_sessions:
        day_name = datetime.fromisoformat(s['date']).strftime('%A')
        time_range = slot_times.get(s['slot'], f"Slot {s['slot']}")
        room = classrooms[course_code].get((s['date'], s['slot']), '')
        course_sessions_out.append({
            'date': s['date'],
            'day': day_name,
            'slot': s['slot'],
            'time': time_range,
            'classroom': str(room) if room else 'TBA',
            'sessionNum': s['num']
        })
    
    dates = [s['date'] for s in course_sessions]
    courses_output.append({
        'code': course_code,
        'name': meta['name'],
        'faculty': meta['faculty'],
        'credits': meta['credits'],
        'sisterAllowed': meta['sister'],
        'startDate': min(dates),
        'endDate': max(dates),
        'totalSessions': len(course_sessions_out),
        'sessions': course_sessions_out
    })

# Add clash data from Clash Report
cr = pd.read_excel(excel_file, sheet_name='Clash Report', header=None)
labels = cr.iloc[0, 1:].tolist()
clash_matrix = {}
for i, lab_i in enumerate(labels):
    for j, lab_j in enumerate(labels):
        v = cr.iloc[i+1, j+1]
        if not pd.isna(v):
            clash_matrix[(lab_i, lab_j)] = int(v)

clashes = []
for i, a in enumerate(user_courses.keys()):
    for j, b in enumerate(user_courses.keys()):
        if i >= j:
            continue
        c = clash_matrix.get((a, b), 0)
        if c:
            sister_a = user_courses[a]['sister']
            sister_b = user_courses[b]['sister']
            # MSN has Sister Yes per guide but only 1 section - effectively rigid
            if a == 'MSN' or b == 'MSN':
                sister_a = sister_b = False
            rigid = not (sister_a or sister_b)
            clashes.append({
                'courseA': a,
                'courseB': b,
                'count': c,
                'rigid': rigid,
                'manageable': not rigid
            })

output = {
    'termStart': '2026-06-15',
    'termEnd': '2026-08-08',
    'cfaDate': '2026-08-19',
    'courses': courses_output,
    'clashes': clashes
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(courses_output)} courses with {sum(len(c['sessions']) for c in courses_output)} total sessions.")
print(f"Found {len(clashes)} clash pairs.")
print(f"Saved to: {output_file}")

# Verify session numbers
print("\n=== Session Number Verification ===")
for c in courses_output:
    nums = [s['sessionNum'] for s in c['sessions'] if s['sessionNum']]
    if nums:
        expected = list(range(1, len(nums) + 1))
        ok = nums == expected
        print(f"{c['code']:15s} | {len(c['sessions'])} sessions | Official nums OK: {ok}")
        if not ok:
            print(f"  Expected: {expected}")
            print(f"  Got:      {nums}")
