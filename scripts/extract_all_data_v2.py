"""
Extract ALL course-section data from the NEW Post-bid Excel timetable.
Generates:
  - all_courses.json: every course-section with sessions
  - courses.json: user's bundle
"""

import pandas as pd
import re
import json
from datetime import datetime
from collections import defaultdict

excel_file = r"./docs/Term-IV Time Table (PGP 2025-27 batch) AY 2026-27.xlsx"

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

def parse_cell(val):
    """Parse a cell value like 'TSB 1', 'M&A 5', 'SS A 1', 'GAFW A 1', 'SM A&B 3'."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    # Merged/single section: 'ACEL 1', 'M&A 5', 'GAIB 1'
    m = re.match(r'^([A-Z][a-zA-Z&]*)\s+(\d+)$', s)
    if m:
        return (m.group(1), None, int(m.group(2)))
    # SM A&B
    m = re.match(r'^SM\s+(A&B)\s+(\d+)$', s)
    if m:
        return ('SM', m.group(1), int(m.group(2)))
    # SS section
    m = re.match(r'^SS\s+([A-J])\s+(\d+)$', s)
    if m:
        return ('SS', m.group(1), int(m.group(2)))
    # Regular sectioned: 'GAFW A 1', 'BF A 1'
    m = re.match(r'^([A-Z][a-zA-Z&]*)\s+([A-Z])\s+(\d+)$', s)
    if m:
        return (m.group(1), m.group(2), int(m.group(3)))
    return None

# Read NEW post-bid timetable
tt = pd.read_excel(excel_file, sheet_name='Post bid TT T-4', header=None)
slot_cols = [c for c in tt.columns if c in slot_times]

sessions = defaultdict(list)
classrooms = defaultdict(dict)
date_seen = set()

for _, row in tt.iterrows():
    date_val = row.iloc[0]
    if not (isinstance(date_val, pd.Timestamp) or isinstance(date_val, datetime)):
        continue
    d = date_val.date().isoformat()
    date_seen.add(d)
    classroom = row.iloc[1] if not pd.isna(row.iloc[1]) else ''
    
    for col_idx in slot_cols:
        val = row.iloc[col_idx]
        parsed = parse_cell(val)
        if parsed:
            code, section, num = parsed
            key = f"{code} {section}" if section else code
            sessions[key].append({'date': d, 'slot': col_idx, 'num': num})
            classrooms[key][(d, col_idx)] = classroom

print(f"Found {len(sessions)} course-sections")
print(f"Date range: {min(date_seen)} to {max(date_seen)}")

course_metadata = {
    'ACEL': {'name': 'Advanced Corporate and Economic Laws', 'faculty': 'Prof. I. Sridhar', 'credits': 2, 'sister': False},
    'ADMA': {'name': 'Advanced Decision Modeling & Analytics in Excel with VBA', 'faculty': 'Prof. Madhukar Dayal', 'credits': 3, 'sister': False},
    'AIHRM': {'name': 'AI and Generative AI Applications in HRM', 'faculty': 'Prof. Antarpreet Singh (VF)', 'credits': 2, 'sister': True},
    'AIMLB': {'name': 'Artificial Intelligence and Machine Learning For Business', 'faculty': 'Prof. Mukul Gupta', 'credits': 3, 'sister': False},
    'B2B': {'name': 'Business To Business Marketing', 'faculty': 'Prof. Bipul Kumar', 'credits': 4, 'sister': False},
    'BF': {'name': 'Behavioural Finance', 'faculty': 'Prof. Kirti Saxena', 'credits': 2, 'sister': True},
    'BM': {'name': 'Brand Management', 'faculty': 'Prof. Ashish Sadh', 'credits': 4, 'sister': True},
    'Bmod': {'name': 'Business Models', 'faculty': 'Prof. Prashant Salwan', 'credits': 4, 'sister': True},
    'CABV': {'name': 'Critical Aspects of Business Valuation', 'faculty': 'Prof. Pradip Banerjee', 'credits': 2, 'sister': False},
    'CB': {'name': 'Consumer Behaviour', 'faculty': 'Prof. Sabita Mahapatra', 'credits': 4, 'sister': False},
    'CCIT': {'name': 'Cryptos, Central Bank and Inflation Targeting', 'faculty': 'Prof. Indrajit Thakurata', 'credits': 3, 'sister': True},
    'CCR': {'name': 'Communicating Corporate Reputation', 'faculty': 'Prof. Shivani Sharma', 'credits': 2, 'sister': False},
    'CEAM': {'name': 'Communicating with/about AI: Ethics, Accountability', 'faculty': 'Prof. Dibyadyuti Roy (VF)', 'credits': 2, 'sister': False},
    'CEDA': {'name': 'Corporate Entrepreneurship In The Disruptive Age', 'faculty': 'Prof. Sumit Chakraborty', 'credits': 3, 'sister': False},
    'CHW': {'name': 'Consciousness and Holistic Wellbeing', 'faculty': 'Prof. Akhaya Kumar Nayak', 'credits': 3, 'sister': False},
    'CNN': {'name': 'Consumer Neuroscience and Neuromarketing', 'faculty': 'Prof. Sudipta Mandal', 'credits': 4, 'sister': True},
    'DIW': {'name': 'Diversity and Inclusion in The Workplace', 'faculty': 'Prof. Shweta Kushal + Kshitija Bhandari (VF)', 'credits': 2, 'sister': False},
    'DM': {'name': 'Digital Marketing', 'faculty': 'Prof. Subin Sudhir', 'credits': 3, 'sister': True},
    'DV': {'name': 'Data Visualization', 'faculty': 'Prof. Sanjog Ray', 'credits': 3, 'sister': True},
    'EECPP': {'name': 'Environmental Economics: Corporate and Policy Perspectives', 'faculty': 'Prof. Mohammad Azeem Khan', 'credits': 2, 'sister': True},
    'ExO': {'name': 'Extreme Outdoors', 'faculty': 'Prof. Kamal Sharma', 'credits': 4, 'sister': False},
    'FAMA': {'name': 'Financial Aspects of Mergers and Acquisitions', 'faculty': 'Prof. Radha M. Ladkani', 'credits': 4, 'sister': True},
    'FAuR': {'name': 'Financial Analytics Using R', 'faculty': 'Prof. K Kiran Kumar', 'credits': 4, 'sister': True},
    'FBETDM': {'name': 'Financial Behaviour, Emerging Technologies and Decision-Making', 'faculty': 'Prof. L V Ramana + T C Ramesh (VF)', 'credits': 2, 'sister': False},
    'Fmac': {'name': 'Financial Macroeconomics', 'faculty': 'Prof. Subhasankar Chattopadhyay', 'credits': 4, 'sister': False},
    'GAFW': {'name': 'Gen AI and Future of Work', 'faculty': 'Prof. Kajari Mukherjee', 'credits': 1, 'sister': True},
    'GAIB': {'name': 'Generative Artificial Intelligence in Business', 'faculty': 'Prof. Prabin K Panigrahi', 'credits': 2, 'sister': False},
    'GBM': {'name': 'Gamification and Behavioural Design for Business', 'faculty': 'Prof. Sudipta Mandal', 'credits': 2, 'sister': True},
    'HRAI': {'name': 'Human Resource Analytics', 'faculty': 'Prof. Srinath Jagannathan', 'credits': 4, 'sister': True},
    'IAPM': {'name': 'Investment Analysis and Portfolio Management', 'faculty': 'Prof. Gaurav Singh Chauhan', 'credits': 4, 'sister': True},
    'IB': {'name': 'Investment Banking', 'faculty': 'Prof. Udayan Sharma', 'credits': 4, 'sister': True},
    'IBSCG': {'name': 'International Business Strategies for The Complex Global World', 'faculty': 'Prof. Ankit Surana', 'credits': 3, 'sister': False},
    'IF': {'name': 'International Finance', 'faculty': 'Prof. Ganesh Kumar Nidugala', 'credits': 4, 'sister': False},
    'ITA': {'name': 'Introduction to Technical Analysis', 'faculty': 'Prof. Vaibhav Jain (VF)', 'credits': 3, 'sister': False},
    'ITWTO': {'name': 'International Trade and WTO', 'faculty': 'Prof. Siddhartha K. Rastogi', 'credits': 3, 'sister': False},
    'LMPO': {'name': 'Logistics Management and Platform Operations', 'faculty': 'Prof. Tanmoy Kundu', 'credits': 3, 'sister': False},
    'LMW': {'name': 'Leading in a Multipolar World', 'faculty': 'Prof. G Venkat Raman + Vivek Kelkar (VF)', 'credits': 4, 'sister': True},
    'LSS': {'name': 'Lean Six Sigma', 'faculty': 'Prof. Sanjay Choudhari', 'credits': 4, 'sister': False},
    'M&A': {'name': 'Mergers and Acquisitions', 'faculty': 'Prof. Manish Popli', 'credits': 3, 'sister': False},
    'MACR': {'name': 'Mergers, Acquisitions and Corporate Restructuring', 'faculty': 'Prof. D.L. Sunder', 'credits': 2, 'sister': False},
    'MSN': {'name': 'Managing Social Networks', 'faculty': 'Prof. Nobin Thomas', 'credits': 2, 'sister': False},
    'NCIS': {'name': 'Nonverbal Communication in Interpersonal Success', 'faculty': 'Prof. Swatantra', 'credits': 2, 'sister': False},
    'OCMC': {'name': 'Organizational Change Management and Consulting', 'faculty': 'Prof. Ranjeet Nambudiri', 'credits': 4, 'sister': False},
    'OFD': {'name': 'Options, Futures and Other Derivatives', 'faculty': 'Prof. Gaurav Singh Chauhan', 'credits': 3, 'sister': True},
    'People': {'name': 'People Resources: Questions That Business Managers Need to Ask', 'faculty': 'Prof. Kajari Mukherjee', 'credits': 2, 'sister': False},
    'PM': {'name': 'Project Management', 'faculty': 'Prof. Hasmukh Gajjar', 'credits': 4, 'sister': False},
    'PPA': {'name': 'Public Policy Analysis: Theory and Practice', 'faculty': 'Prof. Ajit Phadnis + Sridhar Pabbisetty (VF)', 'credits': 4, 'sister': False},
    'Pricing': {'name': 'Pricing', 'faculty': 'Prof. Sanjeev Tripathi', 'credits': 4, 'sister': True},
    'Python': {'name': 'Python Hands-on', 'faculty': 'Prof. Rajhans Mishra', 'credits': 2, 'sister': False},
    'RegA': {'name': 'Regression Analysis', 'faculty': 'Prof. Pritam Ranjan', 'credits': 2, 'sister': False},
    'Retail': {'name': 'Retail Management', 'faculty': 'Prof. Subin Sudhir', 'credits': 4, 'sister': False},
    'SA': {'name': 'Strategic Alliances', 'faculty': 'Prof. Swapnil Garg + Sumit Chakraborty', 'credits': 4, 'sister': True},
    'SABE': {'name': 'Strategic Analysis of Business Events', 'faculty': 'Prof. Sasanka Sekhar Chanda', 'credits': 3, 'sister': False},
    'SITS': {'name': 'Sustainable Innovation & Technology Strategy', 'faculty': 'Prof. Punyashlok Dwibedy', 'credits': 1, 'sister': True},
    'SM': {'name': 'Strategic Marketing', 'faculty': 'Prof. Sanjeev Tripathi', 'credits': 4, 'sister': False},
    'SS': {'name': 'Strategy Simulation', 'faculty': 'Prof. Rotation (Surana/Dwibedy/Basu/Gunta/Sunder)', 'credits': 3, 'sister': False},
    'TOC': {'name': 'Theory of Constraints', 'faculty': 'Prof. R. Raghavendra Ravi (VF) + Harshal Lowalekar', 'credits': 4, 'sister': True},
    'TSB': {'name': 'Technology Strategy for Business', 'faculty': 'Prof. Rajhans Mishra', 'credits': 2, 'sister': False},
}

# Build all_courses.json
all_courses = []
for key in sorted(sessions.keys()):
    parts = key.rsplit(' ', 1)
    if len(parts) == 2 and parts[1] in 'ABCDEFGHIJ&A&B':
        base_code = parts[0]
        section = parts[1]
    else:
        base_code = key
        section = None
    
    meta = course_metadata.get(base_code, {'name': base_code, 'faculty': 'TBA', 'credits': 0, 'sister': False})
    
    course_sessions = sorted(sessions[key], key=lambda x: (x['date'], x['slot']))
    course_sessions_out = []
    for i, s in enumerate(course_sessions, start=1):
        day_name = datetime.fromisoformat(s['date']).strftime('%A')
        time_range = slot_times.get(s['slot'], f"Slot {s['slot']}")
        room = classrooms[key].get((s['date'], s['slot']), '')
        course_sessions_out.append({
            'date': s['date'],
            'day': day_name,
            'slot': s['slot'],
            'time': time_range,
            'classroom': str(room) if room else 'TBA',
            'sessionNum': i
        })
    
    dates = [s['date'] for s in course_sessions]
    all_courses.append({
        'code': key,
        'name': meta['name'],
        'faculty': meta['faculty'],
        'credits': meta['credits'],
        'sisterAllowed': meta['sister'],
        'startDate': min(dates),
        'endDate': max(dates),
        'totalSessions': len(course_sessions_out),
        'sessions': course_sessions_out
    })

# Compute term boundaries from actual session data
all_dates = [s['date'] for c in all_courses for s in c['sessions']]
term_start = min(all_dates) if all_dates else '2026-06-15'
term_end = max(all_dates) if all_dates else '2026-08-08'

all_output = {
    'termStart': term_start,
    'termEnd': term_end,
    'cfaDate': '2026-08-19',
    'courses': all_courses
}

with open('all_courses.json', 'w', encoding='utf-8') as f:
    json.dump(all_output, f, indent=2, ensure_ascii=False)

print(f"\nSaved all_courses.json with {len(all_courses)} course-sections")

# User's courses after merging (no section letters for merged courses)
user_courses = ['CCR', 'ACEL', 'GAIB', 'TSB', 'GAFW A', 'MSN', 'CEDA', 'M&A', 'SS G']

user_output_courses = []
for uc in user_courses:
    course = next((c for c in all_courses if c['code'] == uc), None)
    if not course:
        print(f"WARNING: {uc} not found")
        continue
    
    # Find sister section if applicable
    base = uc.rsplit(' ', 1)[0] if ' ' in uc else uc
    section = uc.rsplit(' ', 1)[1] if ' ' in uc else None
    
    if section and section in 'AB' and course['sisterAllowed']:
        sister_section = 'B' if section == 'A' else 'A'
        sister_code = f"{base} {sister_section}"
        sister_course = next((c for c in all_courses if c['code'] == sister_code), None)
        if sister_course:
            course = dict(course)
            course['sisterSection'] = {
                'code': sister_course['code'],
                'name': sister_course['name'],
                'faculty': sister_course['faculty'],
                'sessions': sister_course['sessions']
            }
    
    user_output_courses.append(course)

def normalize_clash_label(label):
    """Clash Report uses hyphens (e.g. 'GAFW-A') while course codes use spaces ('GAFW A')."""
    if pd.isna(label):
        return ''
    return str(label).strip().replace(' ', '-')

# Build clash data from Clash Report
cr = pd.read_excel(excel_file, sheet_name='Clash Report', header=None)
labels = [normalize_clash_label(l) for l in cr.iloc[1, 1:].tolist()]
clash_matrix = {}
for i, lab_i in enumerate(labels):
    for j, lab_j in enumerate(labels):
        v = cr.iloc[i+2, j+1]
        if not pd.isna(v):
            clash_matrix[(lab_i, lab_j)] = int(v)

clashes = []
for i, a in enumerate(user_courses):
    for j, b in enumerate(user_courses):
        if i >= j:
            continue
        a_norm = normalize_clash_label(a)
        b_norm = normalize_clash_label(b)
        c = clash_matrix.get((a_norm, b_norm), 0)
        if not c:
            # Try reverse key
            c = clash_matrix.get((b_norm, a_norm), 0)
        if c:
            meta_a = next((x for x in all_courses if x['code'] == a), None)
            meta_b = next((x for x in all_courses if x['code'] == b), None)
            # After merging, no sister fallback for merged courses
            sister_a = meta_a['sisterAllowed'] if meta_a else False
            sister_b = meta_b['sisterAllowed'] if meta_b else False
            rigid = not (sister_a or sister_b)
            clashes.append({
                'courseA': a,
                'courseB': b,
                'count': c,
                'rigid': rigid,
                'manageable': not rigid
            })

user_output = {
    'termStart': term_start,
    'termEnd': term_end,
    'cfaDate': '2026-08-19',
    'courses': user_output_courses,
    'clashes': clashes
}

with open('courses.json', 'w', encoding='utf-8') as f:
    json.dump(user_output, f, indent=2, ensure_ascii=False)

print(f"Saved courses.json with {len(user_output_courses)} courses")
print(f"Clashes: {len(clashes)}")
for cl in clashes:
    print(f"  {cl['courseA']} <-> {cl['courseB']}: {cl['count']} sessions, rigid={cl['rigid']}")
