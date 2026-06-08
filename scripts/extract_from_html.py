"""
Extract ALL course-section data from the cleaned HTML timetable and clash report.
Generates:
  - all_courses.json: every course-section with sessions
  - courses.json: user's bundle with sister sections and clash data
"""

import re
import json
from html.parser import HTMLParser
from datetime import datetime
from collections import defaultdict

TT_HTML = r"./TT_T4_Clean.html"
CR_HTML = r"./Clash_Report_Clean.html"

# Slot timing mapping (slot number -> display time)
slot_times = {
    1: '9:00 am - 10:15 am',
    2: '10:30 am - 11:45 am',
    3: '12 noon - 1:15 pm',
    4: '2:30 pm - 3:45 pm',
    5: '4:00 pm - 5:15 pm',
    6: '5:30 pm - 6:45 pm',
    7: '7:00 pm - 8:15 pm',
    8: '8:45 pm - 10:00 pm',
    9: '10:15 pm - 11:30 pm',
}

# HTML column index -> slot number for TT_T4_Clean.html
# cols 4-13 are slots, with col 7 being lunch/break
slot_cols = {
    4: 1,
    5: 2,
    6: 3,
    8: 4,
    9: 5,
    10: 6,
    11: 7,
    12: 8,
    13: 9,
}

# Course metadata reused from previous extraction
# Keys use timetable casing; clash-report labels are normalized case-insensitively.
course_metadata = {
    'ACEL': {'name': 'Advanced Corporate and Economic Laws', 'faculty': 'Prof. I. Sridhar', 'credits': 2, 'sister': True},
    'ADMA': {'name': 'Advanced Decision Modeling & Analytics in Excel with VBA', 'faculty': 'Prof. Madhukar Dayal', 'credits': 3, 'sister': True},
    'AIHRM': {'name': 'AI and Generative AI Applications in HRM', 'faculty': 'Prof. Antarpreet Singh (VF)', 'credits': 2, 'sister': True},
    'AIMLB': {'name': 'Artificial Intelligence and Machine Learning For Business', 'faculty': 'Prof. Mukul Gupta', 'credits': 3, 'sister': True},
    'B2B': {'name': 'Business To Business Marketing', 'faculty': 'Prof. Bipul Kumar', 'credits': 4, 'sister': True},
    'BF': {'name': 'Behavioural Finance', 'faculty': 'Prof. Kirti Saxena', 'credits': 2, 'sister': True},
    'BM': {'name': 'Brand Management', 'faculty': 'Prof. Ashish Sadh', 'credits': 4, 'sister': False},
    'Bmod': {'name': 'Business Models', 'faculty': 'Prof. Prashant Salwan', 'credits': 4, 'sister': True},
    'CABV': {'name': 'Critical Aspects of Business Valuation', 'faculty': 'Prof. Pradip Banerjee', 'credits': 2, 'sister': False},
    'CB': {'name': 'Consumer Behaviour', 'faculty': 'Prof. Sabita Mahapatra', 'credits': 4, 'sister': True},
    'CCIT': {'name': 'Cryptos, Central Bank and Inflation Targeting', 'faculty': 'Prof. Indrajit Thakurata', 'credits': 3, 'sister': True},
    'CCR': {'name': 'Communicating Corporate Reputation', 'faculty': 'Prof. Shivani Sharma', 'credits': 2, 'sister': True},
    'CEAM': {'name': 'Communicating with/about AI: Ethics, Accountability', 'faculty': 'Prof. Dibyadyuti Roy (VF)', 'credits': 2, 'sister': False},
    'CEDA': {'name': 'Corporate Entrepreneurship In The Disruptive Age', 'faculty': 'Prof. Sumit Chakraborty', 'credits': 3, 'sister': True},
    'CHW': {'name': 'Consciousness and Holistic Wellbeing', 'faculty': 'Prof. Akhaya Kumar Nayak', 'credits': 3, 'sister': False},
    'CNN': {'name': 'Consumer Neuroscience and Neuromarketing', 'faculty': 'Prof. Sudipta Mandal', 'credits': 4, 'sister': True},
    'DIW': {'name': 'Diversity and Inclusion in The Workplace', 'faculty': 'Prof. Shweta Kushal + Kshitija Bhandari (VF)', 'credits': 2, 'sister': True},
    'DM': {'name': 'Digital Marketing', 'faculty': 'Prof. Subin Sudhir', 'credits': 3, 'sister': True},
    'DV': {'name': 'Data Visualization', 'faculty': 'Prof. Sanjog Ray', 'credits': 3, 'sister': True},
    'EECPP': {'name': 'Environmental Economics: Corporate and Policy Perspectives', 'faculty': 'Prof. Mohammad Azeem Khan', 'credits': 2, 'sister': True},
    'ExO': {'name': 'Extreme Outdoors', 'faculty': 'Prof. Kamal Sharma', 'credits': 4, 'sister': False},
    'FAMA': {'name': 'Financial Aspects of Mergers and Acquisitions', 'faculty': 'Prof. Radha M. Ladkani', 'credits': 4, 'sister': True},
    'FAuR': {'name': 'Financial Analytics Using R', 'faculty': 'Prof. K Kiran Kumar', 'credits': 4, 'sister': True},
    'FBETDM': {'name': 'Financial Behaviour, Emerging Technologies and Decision-Making', 'faculty': 'Prof. L V Ramana + T C Ramesh (VF)', 'credits': 2, 'sister': False},
    'FMac': {'name': 'Financial Macroeconomics', 'faculty': 'Prof. Subhasankar Chattopadhyay', 'credits': 4, 'sister': False},
    'GAFW': {'name': 'Gen AI and Future of Work', 'faculty': 'Prof. Kajari Mukherjee', 'credits': 1, 'sister': True},
    'GAIB': {'name': 'Generative Artificial Intelligence in Business', 'faculty': 'Prof. Prabin K Panigrahi', 'credits': 2, 'sister': False},
    'GBM': {'name': 'Gamification and Behavioural Design for Business', 'faculty': 'Prof. Sudipta Mandal', 'credits': 2, 'sister': True},
    'HRAI': {'name': 'Human Resource Analytics', 'faculty': 'Prof. Srinath Jagannathan', 'credits': 4, 'sister': True},
    'IAPM': {'name': 'Investment Analysis and Portfolio Management', 'faculty': 'Prof. Gaurav Singh Chauhan', 'credits': 4, 'sister': True},
    'IB': {'name': 'Investment Banking', 'faculty': 'Prof. Udayan Sharma', 'credits': 4, 'sister': True},
    'IBSCG': {'name': 'International Business Strategies for The Complex Global World', 'faculty': 'Prof. Ankit Surana', 'credits': 3, 'sister': False},
    'IF': {'name': 'International Finance', 'faculty': 'Prof. Ganesh Kumar Nidugala', 'credits': 4, 'sister': True},
    'ITA': {'name': 'Introduction to Technical Analysis', 'faculty': 'Prof. Vaibhav Jain (VF)', 'credits': 3, 'sister': True},
    'ITWTO': {'name': 'International Trade and WTO', 'faculty': 'Prof. Siddhartha K. Rastogi', 'credits': 3, 'sister': True},
    'LMPO': {'name': 'Logistics Management and Platform Operations', 'faculty': 'Prof. Tanmoy Kundu', 'credits': 3, 'sister': False},
    'LMW': {'name': 'Leading in a Multipolar World', 'faculty': 'Prof. G Venkat Raman + Vivek Kelkar (VF)', 'credits': 4, 'sister': True},
    'LSS': {'name': 'Lean Six Sigma', 'faculty': 'Prof. Sanjay Choudhari', 'credits': 4, 'sister': True},
    'M&A': {'name': 'Mergers and Acquisitions', 'faculty': 'Prof. Manish Popli', 'credits': 3, 'sister': False},
    'MACR': {'name': 'Mergers, Acquisitions and Corporate Restructuring', 'faculty': 'Prof. D.L. Sunder', 'credits': 2, 'sister': False},
    'MSN': {'name': 'Managing Social Networks', 'faculty': 'Prof. Nobin Thomas', 'credits': 2, 'sister': False},
    'NCIS': {'name': 'Nonverbal Communication in Interpersonal Success', 'faculty': 'Prof. Swatantra', 'credits': 2, 'sister': False},
    'OCMC': {'name': 'Organizational Change Management and Consulting', 'faculty': 'Prof. Ranjeet Nambudiri', 'credits': 4, 'sister': False},
    'OFD': {'name': 'Options, Futures and Other Derivatives', 'faculty': 'Prof. Gaurav Singh Chauhan', 'credits': 3, 'sister': True},
    'People': {'name': 'People Resources: Questions That Business Managers Need to Ask', 'faculty': 'Prof. Kajari Mukherjee', 'credits': 2, 'sister': False},
    'PM': {'name': 'Project Management', 'faculty': 'Prof. Hasmukh Gajjar', 'credits': 4, 'sister': False},
    'PPA': {'name': 'Public Policy Analysis: Theory and Practice', 'faculty': 'Prof. Ajit Phadnis + Sridhar Pabbisetty (VF)', 'credits': 4, 'sister': True},
    'Pricing': {'name': 'Pricing', 'faculty': 'Prof. Sanjeev Tripathi', 'credits': 4, 'sister': True},
    'Python': {'name': 'Python Hands-on', 'faculty': 'Prof. Rajhans Mishra', 'credits': 2, 'sister': True},
    'RegA': {'name': 'Regression Analysis', 'faculty': 'Prof. Pritam Ranjan', 'credits': 2, 'sister': False},
    'Retail': {'name': 'Retail Management', 'faculty': 'Prof. Subin Sudhir', 'credits': 4, 'sister': True},
    'SA': {'name': 'Strategic Alliances', 'faculty': 'Prof. Swapnil Garg + Sumit Chakraborty', 'credits': 4, 'sister': True},
    'SABE': {'name': 'Strategic Analysis of Business Events', 'faculty': 'Prof. Sasanka Sekhar Chanda', 'credits': 3, 'sister': False},
    'SITS': {'name': 'Sustainable Innovation & Technology Strategy', 'faculty': 'Prof. Punyashlok Dwibedy', 'credits': 1, 'sister': True},
    'SM': {'name': 'Strategic Marketing', 'faculty': 'Prof. Sanjeev Tripathi', 'credits': 4, 'sister': False},
    'SS': {'name': 'Strategy Simulation', 'faculty': 'Prof. Rotation (Surana/Dwibedy/Basu/Gunta/Sunder)', 'credits': 3, 'sister': False},
    'TOC': {'name': 'Theory of Constraints', 'faculty': 'Prof. R. Raghavendra Ravi (VF) + Harshal Lowalekar', 'credits': 4, 'sister': True},
    'TSB': {'name': 'Technology Strategy for Business', 'faculty': 'Prof. Rajhans Mishra', 'credits': 2, 'sister': True},
}


def get_metadata(code):
    """Look up course metadata case-insensitively (e.g., Fmac -> FMac)."""
    if code in course_metadata:
        return course_metadata[code]
    low = code.lower()
    for k, v in course_metadata.items():
        if k.lower() == low:
            return v
    return {'name': code, 'faculty': 'TBA', 'credits': 0, 'sister': False}


class TableParser(HTMLParser):
    """Extracts all table cells (both td and th) row by row."""
    def __init__(self):
        super().__init__()
        self.in_cell = False
        self.rows = []
        self.current_row = []
        self.current_cell = ''

    def handle_starttag(self, tag, attrs):
        if tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = ''

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.rows.append(self.current_row)
            self.current_row = []
        elif tag in ('td', 'th'):
            self.current_row.append(self.current_cell.strip())
            self.in_cell = False

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data


def parse_tt_html(path):
    """Parse timetable HTML and return sessions dict and classrooms dict."""
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    parser = TableParser()
    parser.feed(html)

    sessions = defaultdict(list)
    classrooms = defaultdict(dict)
    date_seen = set()

    date_re = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})$')

    def parse_cell(val):
        """Parse a cell value like 'TSB A 1' or 'M&A 5' or 'SM A&B 3' or 'GAIB 1'."""
        if not val:
            return None
        s = str(val).strip()
        # Skip non-course text
        if s in ('Registration', 'Independence Day'):
            return None
        patterns = [
            (r'^SM\s+(A&B)\s+(\d+)$', 'SM'),
            (r'^SS\s+([A-J])\s+(\d+)$', 'SS'),
            (r'^M&A\s+(\d+)$', 'M&A'),
            (r'^([A-Za-z0-9&]+)\s+([A-B])\s+(\d+)$', None),  # TSB A 1, B2B B 3, ACEL A 1
            (r'^([A-Za-z0-9&]+)\s+(\d+)$', None),            # GAIB 1, MSN 5, Python 3
        ]
        for pat, forced_code in patterns:
            m = re.match(pat, s)
            if m:
                if forced_code == 'M&A':
                    return ('M&A', None, int(m.group(1)))
                elif forced_code == 'SM':
                    return ('SM', m.group(1), int(m.group(2)))
                elif forced_code == 'SS':
                    return ('SS', m.group(1), int(m.group(2)))
                else:
                    if len(m.groups()) == 3:
                        return (m.group(1), m.group(2), int(m.group(3)))
                    else:
                        return (m.group(1), None, int(m.group(2)))
        return None

    for row in parser.rows:
        if len(row) < 14:
            continue
        date_cell = row[1].strip()
        m = date_re.match(date_cell)
        if not m:
            continue
        # Parse date
        try:
            dt = datetime.strptime(date_cell, '%A, %B %d, %Y')
        except ValueError:
            continue
        d = dt.date().isoformat()
        date_seen.add(d)
        classroom = row[2].strip() if row[2] else ''

        for col_idx, slot_num in slot_cols.items():
            if col_idx >= len(row):
                continue
            val = row[col_idx]
            parsed = parse_cell(val)
            if parsed:
                code, section, num = parsed
                key = f"{code} {section}" if section else code
                sessions[key].append({'date': d, 'slot': slot_num, 'num': num})
                classrooms[key][(d, slot_num)] = classroom

    return sessions, classrooms, date_seen


def parse_cr_html(path):
    """Parse clash report HTML and return labels list and clash counts dict."""
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    parser = TableParser()
    parser.feed(html)

    rows = parser.rows
    if len(rows) < 4:
        raise ValueError('Clash report has too few rows')

    # Labels are in row 1 starting at col 3
    labels_row = rows[1]
    labels = []
    for cell in labels_row[3:]:
        if cell:
            labels.append(cell)
        else:
            break

    # Data starts at row 3, each row's data is cols 3+
    clash_counts = {}
    for i in range(3, 3 + len(labels)):
        if i >= len(rows):
            break
        row = rows[i]
        row_label = row[1].strip() if len(row) > 1 else ''
        for j, col_label in enumerate(labels):
            col_idx = 3 + j
            if col_idx >= len(row):
                continue
            val = row[col_idx].strip()
            if val == '':
                continue
            try:
                count = int(val)
            except ValueError:
                continue
            # Store with case-insensitive keys
            k = (row_label.lower(), col_label.lower())
            clash_counts[k] = count

    return labels, clash_counts


def get_clash_count(clash_counts, a, b):
    """Look up clash count between two course labels case-insensitively."""
    return clash_counts.get((a.lower(), b.lower()), 0) or clash_counts.get((b.lower(), a.lower()), 0)


def build_all_courses(sessions, classrooms):
    all_courses = []
    for key in sorted(sessions.keys()):
        parts = key.rsplit(' ', 1)
        if len(parts) == 2 and parts[1] in 'ABCDEFGHIJ&A&B':
            base_code = parts[0]
            section = parts[1]
        else:
            base_code = key
            section = None

        meta = get_metadata(base_code)

        # Sort chronologically by date then slot
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

    return all_courses


def build_user_courses(all_courses, user_courses, clash_counts):
    user_output_courses = []
    for uc in user_courses:
        course = next((c for c in all_courses if c['code'] == uc), None)
        if not course:
            print(f"WARNING: {uc} not found")
            continue

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

    clashes = []
    for i, a in enumerate(user_courses):
        for j, b in enumerate(user_courses):
            if i >= j:
                continue
            c = get_clash_count(clash_counts, a, b)
            if c:
                meta_a = next((x for x in all_courses if x['code'] == a), None)
                meta_b = next((x for x in all_courses if x['code'] == b), None)
                sister_a = meta_a['sisterAllowed'] if meta_a else False
                sister_b = meta_b['sisterAllowed'] if meta_b else False
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

    return user_output_courses, clashes


def main():
    print('Parsing timetable HTML...')
    sessions, classrooms, date_seen = parse_tt_html(TT_HTML)
    print(f"Found {len(sessions)} course-sections")
    print(f"Date range: {min(date_seen)} to {max(date_seen)}")

    print('Parsing clash report HTML...')
    cr_labels, clash_counts = parse_cr_html(CR_HTML)
    print(f"Clash report courses: {len(cr_labels)}")

    print('Building all_courses.json...')
    all_courses = build_all_courses(sessions, classrooms)
    all_output = {
        'termStart': '2026-06-15',
        'termEnd': '2026-08-08',
        'cfaDate': '2026-08-19',
        'courses': all_courses
    }
    with open('all_courses.json', 'w', encoding='utf-8') as f:
        json.dump(all_output, f, indent=2, ensure_ascii=False)
    print(f"Saved all_courses.json with {len(all_courses)} course-sections, "
          f"{sum(len(c['sessions']) for c in all_courses)} total sessions")

    print('Building courses.json...')
    user_courses = ['CCR A', 'ACEL A', 'GAIB', 'TSB A', 'GAFW A', 'MSN', 'CEDA A', 'M&A', 'SS G']
    user_output_courses, clashes = build_user_courses(all_courses, user_courses, clash_counts)
    user_output = {
        'termStart': '2026-06-15',
        'termEnd': '2026-08-08',
        'cfaDate': '2026-08-19',
        'courses': user_output_courses,
        'clashes': clashes
    }
    with open('courses.json', 'w', encoding='utf-8') as f:
        json.dump(user_output, f, indent=2, ensure_ascii=False)
    print(f"Saved courses.json with {len(user_output_courses)} courses")
    print(f"Clashes: {len(clashes)}")

    print('\n=== Sister Sections ===')
    for c in user_output_courses:
        if 'sisterSection' in c:
            print(f"{c['code']} -> {c['sisterSection']['code']} ({len(c['sisterSection']['sessions'])} sessions)")


if __name__ == '__main__':
    main()
