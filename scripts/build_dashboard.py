"""
Builds the final index.html by embedding courses.json data and adding
clash suggestions + course picker features.
"""

import json

# Load updated courses.json (with sister sections)
with open('courses.json', 'r', encoding='utf-8') as f:
    courses_data = json.load(f)

# Generate dynamic course colors for any possible course code
color_palettes = [
    ('from-pink-500 to-rose-500', 'text-pink-400', 'bg-pink-500/10', 'border-pink-500/20'),
    ('from-blue-500 to-indigo-500', 'text-blue-400', 'bg-blue-500/10', 'border-blue-500/20'),
    ('from-violet-500 to-purple-500', 'text-violet-400', 'bg-violet-500/10', 'border-violet-500/20'),
    ('from-cyan-500 to-teal-500', 'text-cyan-400', 'bg-cyan-500/10', 'border-cyan-500/20'),
    ('from-fuchsia-500 to-pink-500', 'text-fuchsia-400', 'bg-fuchsia-500/10', 'border-fuchsia-500/20'),
    ('from-amber-500 to-orange-500', 'text-amber-400', 'bg-amber-500/10', 'border-amber-500/20'),
    ('from-emerald-500 to-green-500', 'text-emerald-400', 'bg-emerald-500/10', 'border-emerald-500/20'),
    ('from-red-500 to-rose-600', 'text-red-400', 'bg-red-500/10', 'border-red-500/20'),
    ('from-slate-500 to-gray-500', 'text-slate-400', 'bg-slate-500/10', 'border-slate-500/20'),
    ('from-lime-500 to-green-500', 'text-lime-400', 'bg-lime-500/10', 'border-lime-500/20'),
    ('from-sky-500 to-blue-500', 'text-sky-400', 'bg-sky-500/10', 'border-sky-500/20'),
    ('from-yellow-500 to-amber-500', 'text-yellow-400', 'bg-yellow-500/10', 'border-yellow-500/20'),
    ('from-indigo-500 to-violet-500', 'text-indigo-400', 'bg-indigo-500/10', 'border-indigo-500/20'),
    ('from-orange-500 to-red-500', 'text-orange-400', 'bg-orange-500/10', 'border-orange-500/20'),
    ('from-teal-500 to-cyan-500', 'text-teal-400', 'bg-teal-500/10', 'border-teal-500/20'),
]

courses_json_str = json.dumps(courses_data, ensure_ascii=False)
color_palettes_json = json.dumps(color_palettes)

# Template parts
head = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Term-IV Dashboard | PGP 2025-27</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: { sans: ['Inter', 'sans-serif'] },
          colors: { slate: { 850: '#1e293b', 900: '#0f172a', 950: '#020617' } }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Inter', sans-serif; }
    .glass { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.06); }
    .card-hover { transition: all 0.2s ease; cursor: pointer; }
    .card-hover:hover { transform: translateY(-3px); box-shadow: 0 12px 48px -12px rgba(0,0,0,0.6); }
    .tab-btn { transition: all 0.2s ease; position: relative; }
    .tab-btn.active { color: #fff; }
    .tab-btn.active::after { content: ''; position: absolute; bottom: -1px; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 2px; }
    .tab-btn:not(.active):hover { color: #cbd5e1; }
    .session-row { transition: background 0.15s ease; }
    .session-row:hover { background: rgba(255,255,255,0.03); }
    .animate-fade { animation: fadeIn 0.3s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    .back-to-back { border-left: 2px solid rgba(99, 102, 241, 0.4); }
    .scrollbar-hide::-webkit-scrollbar { display: none; }
    .picker-course { transition: all 0.15s ease; }
    .picker-course:hover { background: rgba(99,102,241,0.1); }
    .clash-suggestion { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.25); }
    .clash-rigid { background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.25); }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">
'''

navbar = '''
  <!-- Navbar -->
  <nav class="glass sticky top-0 z-40 border-b border-slate-800">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between py-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">IV</div>
          <div>
            <h1 class="text-base font-bold text-white leading-tight">Term-IV Dashboard</h1>
            <p class="text-[10px] text-slate-400">PGP 2025-27</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="openBundlePicker()" class="text-[11px] px-2.5 py-1.5 rounded-md bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 transition-colors hidden sm:block">⚙️ Bundle</button>
          <button onclick="exportAttendance()" class="text-[11px] px-2.5 py-1.5 rounded-md bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors hidden sm:block">Export</button>
          <button onclick="resetAttendance()" class="text-[11px] px-2.5 py-1.5 rounded-md bg-slate-800 text-slate-300 hover:bg-rose-500/20 hover:text-rose-400 transition-colors hidden sm:block">Reset</button>
          <div class="text-right ml-2">
            <p id="current-date" class="text-xs font-medium text-slate-300"></p>
            <p id="current-time" class="text-[10px] text-slate-500"></p>
          </div>
        </div>
      </div>
      <div class="flex gap-6 text-sm border-b border-slate-800/50 -mb-px">
        <button class="tab-btn active pb-3 text-slate-300 font-medium" onclick="switchTab('home')" data-tab="home">Home</button>
        <button class="tab-btn pb-3 text-slate-500 font-medium" onclick="switchTab('courses')" data-tab="courses">My Courses</button>
        <button class="tab-btn pb-3 text-slate-500 font-medium" onclick="switchTab('calendar')" data-tab="calendar">Session Calendar</button>
      </div>
    </div>
  </nav>
'''

main = '''
  <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

    <!-- HOME TAB -->
    <div id="tab-home" class="tab-content animate-fade">
      <!-- Stats Row -->
      <section class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="glass rounded-2xl p-5 flex flex-col items-center text-center">
          <div class="relative w-20 h-20 mb-3">
            <div class="absolute inset-0 rounded-full" id="term-ring" style="background: conic-gradient(from 0deg, #6366f1 var(--progress), rgba(255,255,255,0.05) var(--progress))"></div>
            <div class="absolute inset-1.5 rounded-full bg-slate-900 flex items-center justify-center"><span id="term-pct" class="text-lg font-bold text-white">0%</span></div>
          </div>
          <p class="text-xs text-slate-400 font-medium">Term Done</p>
          <p id="term-dates" class="text-[10px] text-slate-600 mt-0.5">Jun 15 &ndash; Aug 8</p>
        </div>
        <div class="glass rounded-2xl p-5 flex flex-col items-center text-center">
          <div class="relative w-20 h-20 mb-3">
            <div class="absolute inset-0 rounded-full" id="cfa-ring" style="background: conic-gradient(from 0deg, #10b981 var(--progress), rgba(255,255,255,0.05) var(--progress))"></div>
            <div class="absolute inset-1.5 rounded-full bg-slate-900 flex items-center justify-center"><span id="cfa-days" class="text-xl font-bold text-emerald-400">0</span></div>
          </div>
          <p class="text-xs text-slate-400 font-medium">Days to CFA</p>
          <p class="text-[10px] text-slate-600 mt-0.5">Aug 19, 2026</p>
        </div>
        <div class="glass rounded-2xl p-5 flex flex-col items-center text-center">
          <div class="relative w-20 h-20 mb-3">
            <div class="absolute inset-0 rounded-full bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30 flex items-center justify-center">
              <span id="free-days" class="text-2xl font-bold text-amber-400">--</span>
            </div>
          </div>
          <p class="text-xs text-slate-400 font-medium">Next Free Day</p>
          <p id="free-date" class="text-[10px] text-slate-600 mt-0.5">--</p>
        </div>
        <div class="glass rounded-2xl p-5 flex flex-col items-center text-center">
          <div class="relative w-20 h-20 mb-3">
            <div class="absolute inset-0 rounded-full" id="att-ring" style="background: conic-gradient(from 0deg, #8b5cf6 var(--progress), rgba(255,255,255,0.05) var(--progress))"></div>
            <div class="absolute inset-1.5 rounded-full bg-slate-900 flex items-center justify-center"><span id="att-pct" class="text-lg font-bold text-white">--</span></div>
          </div>
          <p class="text-xs text-slate-400 font-medium">Attendance</p>
          <p id="att-detail" class="text-[10px] text-slate-600 mt-0.5">--/--</p>
        </div>
      </section>

      <!-- Today & Tomorrow -->
      <section class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div class="glass rounded-2xl p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-bold text-white flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>Today</h2>
            <span id="home-today-date" class="text-[11px] text-slate-500"></span>
          </div>
          <div id="home-today-list" class="space-y-2"></div>
        </div>
        <div class="glass rounded-2xl p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-bold text-white flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>Tomorrow</h2>
            <span id="home-tmrw-date" class="text-[11px] text-slate-500"></span>
          </div>
          <div id="home-tmrw-list" class="space-y-2"></div>
        </div>
      </section>

      <!-- Course Progress -->
      <section class="glass rounded-2xl p-5">
        <h2 class="text-sm font-bold text-white mb-4">Course Progress</h2>
        <div id="home-progress-list" class="space-y-3"></div>
      </section>
    </div>

    <!-- COURSES TAB -->
    <div id="tab-courses" class="tab-content hidden animate-fade">
      <div id="courses-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"></div>
    </div>

    <!-- CALENDAR TAB -->
    <div id="tab-calendar" class="tab-content hidden animate-fade">
      <div class="glass rounded-2xl p-5 overflow-x-auto">
        <div id="cal-container" class="min-w-[700px]"></div>
      </div>
    </div>

    <footer class="text-center text-[11px] text-slate-700 py-10 mt-4">Term-IV PGP 2025-27 &bull; Attendance saved locally</footer>
  </main>
'''

modals = '''
  <!-- Course Detail Modal -->
  <div id="course-modal" class="fixed inset-0 z-50 hidden">
    <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" onclick="closeModal()"></div>
    <div class="absolute inset-0 flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl" style="animation: fadeIn 0.2s ease-out">
        <div id="modal-header" class="p-6 border-b border-slate-800 relative shrink-0"></div>
        <div class="overflow-y-auto p-6 scrollbar-hide" id="modal-body"></div>
      </div>
    </div>
  </div>

  <!-- Bundle Picker Modal -->
  <div id="bundle-modal" class="fixed inset-0 z-50 hidden">
    <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" onclick="closeBundlePicker()"></div>
    <div class="absolute inset-0 flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl" style="animation: fadeIn 0.2s ease-out">
        <div class="p-6 border-b border-slate-800 relative shrink-0 flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-white">Configure Your Bundle</h2>
            <p class="text-sm text-slate-400 mt-0.5">Select your courses and sections</p>
          </div>
          <button onclick="closeBundlePicker()" class="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 flex items-center justify-center text-lg">&times;</button>
        </div>
        <div class="overflow-y-auto p-6 scrollbar-hide flex-1" id="bundle-body">
          <div id="bundle-picker-loading" class="text-center py-10 text-slate-500">Loading all courses...</div>
        </div>
        <div class="p-4 border-t border-slate-800 flex items-center justify-between shrink-0">
          <div class="text-sm">
            <span class="text-slate-400">Credits:</span>
            <span id="bundle-credits" class="font-bold text-white ml-1">0</span>
            <span class="text-slate-500">/ 24 max</span>
          </div>
          <div class="flex gap-2">
            <button onclick="resetBundle()" class="px-3 py-2 rounded-lg bg-slate-800 text-slate-300 text-sm hover:bg-slate-700">Reset to Default</button>
            <button onclick="saveBundle()" class="px-3 py-2 rounded-lg bg-indigo-500 text-white text-sm font-medium hover:bg-indigo-600">Save Bundle</button>
          </div>
        </div>
      </div>
    </div>
  </div>
'''

script_start = '''
  <script>
    const DEFAULT_DATA = ''' + courses_json_str + ''';
    let data = DEFAULT_DATA;
    let allCoursesData = null;
    let selectedBundle = [];

    // Try to load user's saved bundle
    const BUNDLE_KEY = 'term4_bundle';
    const savedBundle = localStorage.getItem(BUNDLE_KEY);
    if (savedBundle) {
      try {
        const parsed = JSON.parse(savedBundle);
        if (parsed && parsed.courses && parsed.courses.length > 0) {
          data = parsed;
        }
      } catch(e) { console.log('Invalid saved bundle'); }
    }

    // Storage key includes bundle hash to prevent cross-bundle pollution
    function getStorageKey() {
      const codes = data.courses.map(c => c.code).sort().join(',');
      let hash = 0;
      for (let i = 0; i < codes.length; i++) {
        hash = ((hash << 5) - hash) + codes.charCodeAt(i);
        hash |= 0;
      }
      return 'term4_attendance_' + Math.abs(hash);
    }
    const STORAGE_KEY = getStorageKey();

    // Dynamic color assignment
    function getCourseColor(code) {
      const idx = data.courses.findIndex(c => c.code === code);
      const palettes = ''' + color_palettes_json + ''';
      const p = palettes[idx % palettes.length];
      return { gradient: p[0], text: p[1], light: p[2], border: p[3] };
    }

    // ─── Load all courses for picker ───
    async function loadAllCourses() {
      if (allCoursesData) return allCoursesData;
      try {
        const res = await fetch('all_courses.json');
        if (!res.ok) throw new Error('Failed to fetch');
        allCoursesData = await res.json();
        return allCoursesData;
      } catch (e) {
        console.log('Could not load all_courses.json:', e);
        return null;
      }
    }

    // ─── Tabs ───
    function switchTab(tabName) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.getElementById('tab-' + tabName).classList.remove('hidden');
      document.querySelector('[data-tab="' + tabName + '"]').classList.add('active');
      if (tabName === 'courses') renderCoursesTab();
      if (tabName === 'calendar') renderCalendarTab();
    }

    // ─── Attendance ───
    function getAttendance() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch { return {}; } }
    function setAttendance(date, code, slot, status) {
      const att = getAttendance();
      const key = date + '_' + code + '_' + slot;
      if (status == null) delete att[key]; else att[key] = status;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(att));
      renderHomeTab();
      if (!document.getElementById('tab-courses').classList.contains('hidden')) renderCoursesTab();
      if (!document.getElementById('tab-calendar').classList.contains('hidden')) renderCalendarTab();
      if (!document.getElementById('course-modal').classList.contains('hidden')) openCourseModal(code);
    }
    function getStatus(date, code, slot) { return getAttendance()[date + '_' + code + '_' + slot] || null; }
    function getCourseStats(code) {
      const c = data.courses.find(x => x.code === code);
      const today = new Date().toISOString().split('T')[0];
      let present = 0, absent = 0, done = 0;
      c.sessions.forEach(s => {
        if (s.date <= today) {
          done++;
          const st = getStatus(s.date, code, s.slot);
          if (st === 'present') present++;
          else if (st === 'absent') absent++;
        }
      });
      return { present, absent, done, total: c.sessions.length, rate: done ? Math.round((present / done) * 100) : 0 };
    }
    function getOverallAttendance() {
      const today = new Date().toISOString().split('T')[0];
      let present = 0, absent = 0, marked = 0;
      data.courses.forEach(c => c.sessions.forEach(s => {
        if (s.date <= today) {
          const st = getStatus(s.date, c.code, s.slot);
          if (st === 'present') { present++; marked++; }
          else if (st === 'absent') { absent++; marked++; }
        }
      }));
      return { present, absent, marked, rate: marked ? Math.round((present / marked) * 100) : 0 };
    }
    function exportAttendance() {
      const payload = { bundle: data.courses.map(c => c.code), attendance: getAttendance() };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = 'attendance_' + new Date().toISOString().split('T')[0] + '.json'; a.click(); URL.revokeObjectURL(url);
    }
    function resetAttendance() { if (confirm('Reset all attendance data?')) { localStorage.removeItem(STORAGE_KEY); renderHomeTab(); renderCoursesTab(); renderCalendarTab(); } }

    function attBtn(date, code, slot, compact) {
      const st = getStatus(date, code, slot);
      const pc = st === 'present' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700';
      const ac = st === 'absent' ? 'bg-rose-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700';
      const size = compact ? 'px-2 py-1 text-[10px]' : 'px-3 py-1.5 text-xs';
      return '<div class="flex items-center gap-1">' +
        `<button class="${size} rounded-md font-semibold ${pc}" onclick="event.stopPropagation();setAttendance('${date}','${code}',${slot},'present')">&#10003;</button>` +
        `<button class="${size} rounded-md font-semibold ${ac}" onclick="event.stopPropagation();setAttendance('${date}','${code}',${slot},'absent')">&#10007;</button>` +
        (st ? `<button class="${size} rounded-md font-semibold bg-slate-800 text-slate-500 hover:text-slate-300" onclick="event.stopPropagation();setAttendance('${date}','${code}',${slot},null)">&#9003;</button>` : '') +
        '</div>';
    }
'''

clash_js = '''
    // ─── Clash Detection ───
    function findClashes(dateStr) {
      const sessions = [];
      data.courses.forEach(c => c.sessions.forEach(s => {
        if (s.date === dateStr) sessions.push({ ...s, course: c });
      }));
      sessions.sort((a, b) => a.slot - b.slot);
      const clashes = [];
      for (let i = 0; i < sessions.length; i++) {
        for (let j = i + 1; j < sessions.length; j++) {
          if (sessions[i].slot === sessions[j].slot) {
            const a = sessions[i].course;
            const b = sessions[j].course;
            const known = data.clashes && data.clashes.find(c =>
              (c.courseA === a.code && c.courseB === b.code) ||
              (c.courseA === b.code && c.courseB === a.code)
            );
            const hasSisterA = a.sisterAllowed && a.sisterSection;
            const hasSisterB = b.sisterAllowed && b.sisterSection;
            clashes.push({
              sessionA: sessions[i],
              sessionB: sessions[j],
              known: known,
              hasSisterA,
              hasSisterB,
              rigid: known ? known.rigid : !(hasSisterA || hasSisterB)
            });
          }
        }
      }
      return clashes;
    }

    function getClashSuggestionHTML(clash) {
      const { sessionA, sessionB, hasSisterA, hasSisterB, rigid } = clash;
      if (rigid) {
        return '<div class="clash-rigid rounded-lg px-3 py-2 mt-2 text-xs">' +
          '<span class="font-semibold text-rose-400">&#9888; Rigid Clash:</span>' +
          '<span class="text-rose-300"> No sister section available. You must miss one class.</span>' +
          '</div>';
      }
      let suggestions = [];
      if (hasSisterA) {
        const sister = sessionA.course.sisterSection;
        const sisterSess = sister.sessions.find(s => s.sessionNum === sessionA.sessionNum);
        if (sisterSess) {
          suggestions.push('Attend <strong>' + sister.code + '</strong> instead of ' + sessionA.course.code + ' (' + sisterSess.time + ', ' + sisterSess.classroom + ')');
        }
      }
      if (hasSisterB) {
        const sister = sessionB.course.sisterSection;
        const sisterSess = sister.sessions.find(s => s.sessionNum === sessionB.sessionNum);
        if (sisterSess) {
          suggestions.push('Attend <strong>' + sister.code + '</strong> instead of ' + sessionB.course.code + ' (' + sisterSess.time + ', ' + sisterSess.classroom + ')');
        }
      }
      if (suggestions.length === 0) {
        return '<div class="clash-suggestion rounded-lg px-3 py-2 mt-2 text-xs">' +
          '<span class="font-semibold text-amber-400">&#9888; Clash:</span>' +
          '<span class="text-amber-300"> Sister section allowed but schedule data unavailable.</span>' +
          '</div>';
      }
      return '<div class="clash-suggestion rounded-lg px-3 py-2 mt-2 text-xs">' +
        '<span class="font-semibold text-amber-400">&#128161; Suggestion:</span>' +
        '<span class="text-amber-200"> ' + suggestions.join(' OR ') + '</span>' +
        '</div>';
    }
'''

clock_js = '''
    // ─── Clock ───
    function updateClock() {
      const n = new Date();
      document.getElementById('current-date').textContent = n.toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' });
      document.getElementById('current-time').textContent = n.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    }
'''

home_tab_js = '''
    // HOME TAB
    function renderHomeTab() {
      const now = new Date();
      const todayStr = now.toISOString().split('T')[0];
      const termStart = new Date(data.termStart);
      const termEnd = new Date(data.termEnd);
      const cfaDate = new Date(data.cfaDate);

      const totalDays = Math.ceil((termEnd - termStart) / (1000*60*60*24));
      const elapsed = Math.ceil((now - termStart) / (1000*60*60*24));
      const termPct = Math.max(0, Math.min(100, Math.round((elapsed / totalDays) * 100)));
      document.getElementById('term-pct').textContent = termPct + '%';
      document.getElementById('term-ring').style.setProperty('--progress', termPct + '%');
      document.getElementById('term-dates').textContent = new Date(data.termStart).toLocaleDateString('en-IN', {month:'short', day:'numeric'}) + ' \u2013 ' + new Date(data.termEnd).toLocaleDateString('en-IN', {month:'short', day:'numeric'});

      const cfaTotal = Math.ceil((cfaDate - termStart) / (1000*60*60*24));
      const cfaLeft = Math.max(0, Math.ceil((cfaDate - now) / (1000*60*60*24)));
      const cfaPct = Math.max(0, Math.min(100, Math.round(((cfaTotal - cfaLeft) / cfaTotal) * 100)));
      document.getElementById('cfa-days').textContent = cfaLeft;
      document.getElementById('cfa-ring').style.setProperty('--progress', cfaPct + '%');

      const sessionDates = new Set();
      data.courses.forEach(c => c.sessions.forEach(s => sessionDates.add(s.date)));
      let nextFree = null, freeDaysCount = 0;
      const checkDate = new Date(now);
      for (let i = 0; i < 60; i++) {
        checkDate.setDate(checkDate.getDate() + 1);
        const dStr = checkDate.toISOString().split('T')[0];
        if (!sessionDates.has(dStr)) { nextFree = dStr; freeDaysCount = i + 1; break; }
      }
      document.getElementById('free-days').textContent = nextFree ? freeDaysCount : '--';
      document.getElementById('free-date').textContent = nextFree ? new Date(nextFree).toLocaleDateString('en-IN', {weekday:'short', month:'short', day:'numeric'}) : 'No free day found';

      const overall = getOverallAttendance();
      document.getElementById('att-pct').textContent = overall.rate + '%';
      document.getElementById('att-ring').style.setProperty('--progress', overall.rate + '%');
      document.getElementById('att-detail').textContent = overall.present + '/' + overall.marked;

      renderDayList('home-today-list', 'home-today-date', todayStr, 'No classes today &#127881;');
      const tmrw = new Date(now); tmrw.setDate(tmrw.getDate() + 1);
      renderDayList('home-tmrw-list', 'home-tmrw-date', tmrw.toISOString().split('T')[0], 'No classes tomorrow');

      const progressEl = document.getElementById('home-progress-list');
      progressEl.innerHTML = data.courses.map(c => {
        const stats = getCourseStats(c.code);
        const col = getCourseColor(c.code);
        const donePct = Math.round((stats.done / stats.total) * 100);
        return '<div class="flex items-center gap-3">' +
          '<div class="w-20 shrink-0">' +
            '<div class="text-xs font-bold ' + col.text + '">' + c.code + '</div>' +
            '<div class="text-[10px] text-slate-500">' + stats.done + '/' + stats.total + ' done</div>' +
          '</div>' +
          '<div class="flex-1 h-2.5 bg-slate-800 rounded-full overflow-hidden">' +
            '<div class="h-full bg-gradient-to-r ' + col.gradient + ' rounded-full transition-all duration-500" style="width:' + donePct + '%"></div>' +
          '</div>' +
          '<div class="w-12 text-right shrink-0"><div class="text-xs font-bold text-white">' + donePct + '%</div></div>' +
          `<button onclick="switchTab('courses'); setTimeout(()=>openCourseModal('${c.code}'), 350)" class="shrink-0 text-[10px] px-2 py-1 rounded bg-slate-800 text-slate-400 hover:text-white transition-colors">View</button>` +
        '</div>';
      }).join('');
    }

    function renderDayList(listId, dateId, dateStr, emptyMsg) {
      const list = [];
      data.courses.forEach(c => c.sessions.forEach(s => { if (s.date === dateStr) list.push({ ...s, course: c }); }));
      list.sort((a, b) => a.slot - b.slot);
      document.getElementById(dateId).textContent = new Date(dateStr).toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' });
      const el = document.getElementById(listId);
      if (!list.length) { el.innerHTML = '<div class="text-sm text-slate-500 text-center py-6">' + emptyMsg + '</div>'; return; }

      const clashes = findClashes(dateStr);
      const clashSessionKeys = new Set();
      clashes.forEach(c => {
        clashSessionKeys.add(c.sessionA.date + '_' + c.sessionA.course.code + '_' + c.sessionA.slot);
        clashSessionKeys.add(c.sessionB.date + '_' + c.sessionB.course.code + '_' + c.sessionB.slot);
      });

      el.innerHTML = list.map(s => {
        const col = getCourseColor(s.course.code);
        const st = getStatus(s.date, s.course.code, s.slot);
        const stBadge = st === 'present' ? '<span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-medium">Present</span>' :
                        st === 'absent' ? '<span class="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 font-medium">Absent</span>' :
                        '<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-700 text-slate-400">Not marked</span>';
        const isClash = clashSessionKeys.has(s.date + '_' + s.course.code + '_' + s.slot);
        const clashHTML = isClash ? getClashSuggestionHTML(clashes.find(c =>
          (c.sessionA.course.code === s.course.code && c.sessionA.slot === s.slot) ||
          (c.sessionB.course.code === s.course.code && c.sessionB.slot === s.slot)
        )) : '';
        return '<div class="flex items-center gap-3 p-3 rounded-xl bg-slate-900/50 border border-slate-800/60 ' + (isClash ? 'border-amber-500/30' : '') + '">' +
          '<div class="w-11 h-11 rounded-lg bg-gradient-to-br ' + col.gradient + ' flex flex-col items-center justify-center text-white shrink-0">' +
            '<span class="text-[9px] font-bold leading-none">' + s.time.split(' ')[0] + '</span>' +
            '<span class="text-[9px] opacity-80 leading-none">' + s.time.split(' ')[1] + '</span>' +
          '</div>' +
          '<div class="flex-1 min-w-0">' +
            '<div class="flex items-center gap-2">' +
              '<span class="font-semibold text-sm text-white truncate">' + s.course.name + '</span>' +
              stBadge +
              (isClash ? '<span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-medium">CLASH</span>' : '') +
            '</div>' +
            '<div class="text-xs text-slate-500 mt-0.5">' + s.course.faculty + ' &bull; ' + s.classroom + '</div>' +
            clashHTML +
          '</div>' +
          '<div class="shrink-0">' + attBtn(s.date, s.course.code, s.slot, true) + '</div>' +
        '</div>';
      }).join('');
    }
'''

courses_tab_js = '''
    // COURSES TAB
    function renderCoursesTab() {
      const el = document.getElementById('courses-grid');
      el.innerHTML = data.courses.map(c => {
        const col = getCourseColor(c.code);
        const stats = getCourseStats(c.code);
        const donePct = Math.round((stats.done / stats.total) * 100);
        return `<div class="glass rounded-2xl p-5 card-hover relative overflow-hidden" onclick="openCourseModal('${c.code}')">` +
          '<div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r ' + col.gradient + '"></div>' +
          '<div class="flex justify-between items-start mb-3">' +
            '<span class="text-[10px] font-bold px-2 py-1 rounded bg-slate-800 text-slate-300 tracking-wide">' + c.code + '</span>' +
            '<span class="text-lg font-bold ' + col.text + '">' + c.credits + 'cr</span>' +
          '</div>' +
          '<h3 class="font-bold text-white text-base leading-snug mb-1">' + c.name + '</h3>' +
          '<p class="text-xs text-slate-400 mb-4">' + c.faculty + '</p>' +
          '<div class="flex items-center justify-between text-xs mb-1.5">' +
            '<span class="text-slate-500">Classes Done</span>' +
            '<span class="font-semibold text-white">' + stats.done + '/' + stats.total + '</span>' +
          '</div>' +
          '<div class="h-2 bg-slate-800 rounded-full overflow-hidden mb-4">' +
            '<div class="h-full bg-gradient-to-r ' + col.gradient + ' rounded-full transition-all duration-500" style="width:' + donePct + '%"></div>' +
          '</div>' +
          '<div class="flex items-center justify-between">' +
            '<div class="flex items-center gap-2">' +
              '<span class="text-xs text-slate-500">Attendance</span>' +
              '<span class="text-xs font-bold ' + (stats.rate >= 75 ? 'text-emerald-400' : stats.rate >= 50 ? 'text-amber-400' : 'text-rose-400') + '">' + stats.rate + '%</span>' +
            '</div>' +
            '<span class="text-[10px] px-2 py-0.5 rounded-full ' + (stats.present > 0 ? col.light + ' ' + col.text + ' ' + col.border : 'bg-slate-800 text-slate-500') + ' border">' + stats.present + ' Present</span>' +
          '</div>' +
        '</div>';
      }).join('');
    }
'''

calendar_tab_js = '''
    // CALENDAR TAB
    function renderCalendarTab() {
      const container = document.getElementById('cal-container');
      const sessionMap = {};
      data.courses.forEach(c => c.sessions.forEach(s => {
        if (!sessionMap[s.date]) sessionMap[s.date] = [];
        sessionMap[s.date].push({ ...s, course: c });
      }));

      const months = [
        { year: 2026, month: 5, label: 'June 2026' },
        { year: 2026, month: 6, label: 'July 2026' },
        { year: 2026, month: 7, label: 'August 2026' },
      ];

      let html = '<div class="space-y-8">';
      const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      const todayStr = new Date().toISOString().split('T')[0];

      months.forEach(({ year, month, label }) => {
        const firstDay = new Date(year, month, 1);
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const startOffset = firstDay.getDay();

        html += '<div><h3 class="text-sm font-bold text-slate-300 mb-3">' + label + '</h3><div class="grid grid-cols-7 gap-1">';
        dayNames.forEach(d => html += '<div class="text-[10px] font-semibold text-slate-500 text-center py-1">' + d + '</div>');
        for (let i = 0; i < startOffset; i++) html += '<div></div>';
        for (let d = 1; d <= daysInMonth; d++) {
          const dateStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');
          const sessions = sessionMap[dateStr] || [];
          const isToday = dateStr === todayStr;
          const isPast = dateStr < todayStr;
          let cellClass = 'min-h-[72px] rounded-lg p-1.5 border ';
          if (isToday) cellClass += 'bg-indigo-500/10 border-indigo-500/30';
          else if (isPast) cellClass += 'bg-slate-900/40 border-slate-800/40 opacity-60';
          else cellClass += 'bg-slate-900/20 border-slate-800/30';

          const daySlots = {};
          sessions.forEach(s => {
            if (!daySlots[s.slot]) daySlots[s.slot] = [];
            daySlots[s.slot].push(s);
          });
          const clashSlots = Object.keys(daySlots).filter(slot => daySlots[slot].length > 1);

          html += '<div class="' + cellClass + '"><div class="text-[10px] font-bold ' + (isToday ? 'text-indigo-400' : 'text-slate-500') + ' mb-1">' + d + '</div>';
          if (clashSlots.length > 0) {
            html += '<div class="text-[8px] font-bold text-amber-400 mb-0.5">&#9888; CLASH</div>';
          }
          sessions.forEach(s => {
            const col = getCourseColor(s.course.code);
            const st = getStatus(s.date, s.course.code, s.slot);
            const dot = st === 'present' ? '&#128994;' : st === 'absent' ? '&#128308;' : '&#9898;';
            html += `<div class="text-[9px] truncate rounded px-1 py-0.5 mb-0.5 bg-gradient-to-r ${col.gradient} text-white font-medium cursor-pointer hover:opacity-90" onclick="event.stopPropagation();openCourseModal('${s.course.code}')" title="${s.course.name} | ${s.time}">${dot} ${s.course.code}</div>`;
          });
          html += '</div>';
        }
        html += '</div></div>';
      });
      html += '</div>';
      container.innerHTML = html;
    }
'''

modal_js = '''
    // COURSE MODAL
    function openCourseModal(code) {
      const c = data.courses.find(x => x.code === code);
      const col = getCourseColor(code);
      const stats = getCourseStats(code);
      const todayStr = new Date().toISOString().split('T')[0];

      let sisterHtml = '';
      if (c.sisterSection) {
        sisterHtml = '<div class="mt-3 p-3 rounded-lg bg-indigo-500/5 border border-indigo-500/20">' +
          '<div class="text-xs font-semibold text-indigo-400 mb-1">Sister Section: ' + c.sisterSection.code + '</div>' +
          '<div class="text-xs text-slate-400">Same faculty, same content. Use when clashing.</div>' +
        '</div>';
      }

      document.getElementById('modal-header').innerHTML =
        '<button onclick="closeModal()" class="absolute top-4 right-4 w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 flex items-center justify-center text-lg">&times;</button>' +
        '<div class="flex items-start gap-4">' +
          '<div class="w-14 h-14 rounded-xl bg-gradient-to-br ' + col.gradient + ' flex items-center justify-center text-white font-bold text-xl shrink-0">' + code.split(' ')[0] + '</div>' +
          '<div>' +
            '<h2 class="text-xl font-bold text-white">' + c.name + '</h2>' +
            '<p class="text-sm text-slate-400 mt-0.5">' + c.faculty + '</p>' +
            '<div class="flex items-center gap-3 mt-2 flex-wrap">' +
              '<span class="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">' + c.credits + ' Credits</span>' +
              '<span class="text-xs px-2 py-0.5 rounded ' + (c.sisterAllowed ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400') + '">' + (c.sisterAllowed ? 'Sister Allowed' : 'No Sister') + '</span>' +
              '<span class="text-xs text-slate-500">' + new Date(c.startDate).toLocaleDateString('en-IN', {month:'short', day:'numeric'}) + ' \u2013 ' + new Date(c.endDate).toLocaleDateString('en-IN', {month:'short', day:'numeric'}) + '</span>' +
            '</div>' +
            sisterHtml +
          '</div>' +
        '</div>' +
        '<div class="mt-5 grid grid-cols-4 gap-3">' +
          '<div class="bg-slate-800/50 rounded-lg p-3 text-center"><div class="text-lg font-bold text-white">' + stats.total + '</div><div class="text-[10px] text-slate-500">Total</div></div>' +
          '<div class="bg-slate-800/50 rounded-lg p-3 text-center"><div class="text-lg font-bold text-white">' + stats.done + '</div><div class="text-[10px] text-slate-500">Done</div></div>' +
          '<div class="bg-slate-800/50 rounded-lg p-3 text-center"><div class="text-lg font-bold text-emerald-400">' + stats.present + '</div><div class="text-[10px] text-slate-500">Present</div></div>' +
          '<div class="bg-slate-800/50 rounded-lg p-3 text-center"><div class="text-lg font-bold text-rose-400">' + stats.absent + '</div><div class="text-[10px] text-slate-500">Absent</div></div>' +
        '</div>';

      let rowsHtml = '';
      for (let i = 0; i < c.sessions.length; i++) {
        const s = c.sessions[i];
        const prev = i > 0 ? c.sessions[i - 1] : null;
        const isBackToBack = prev && prev.date === s.date && Math.abs(prev.slot - s.slot) <= 1;
        const st = getStatus(s.date, code, s.slot);
        const isPast = s.date < todayStr;
        const isToday = s.date === todayStr;
        const statusHtml = st === 'present'
          ? '<div class="flex items-center gap-1.5 text-emerald-400 font-semibold text-sm"><span class="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center text-xs">&#10003;</span> Present</div>'
          : st === 'absent'
          ? '<div class="flex items-center gap-1.5 text-rose-400 font-semibold text-sm"><span class="w-5 h-5 rounded-full bg-rose-500/20 flex items-center justify-center text-xs">&#10007;</span> Absent</div>'
          : '<div class="flex items-center gap-1.5 text-slate-500 text-sm"><span class="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-xs">\u2014</span> Not marked</div>';

        const btbClass = isBackToBack ? 'back-to-back' : '';
        const btbBadge = isBackToBack ? '<span class="text-[9px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 ml-2">Back-to-back</span>' : '';

        let clashHtml = '';
        const dayClashes = findClashes(s.date);
        const myClash = dayClashes.find(cl =>
          (cl.sessionA.course.code === code && cl.sessionA.slot === s.slot) ||
          (cl.sessionB.course.code === code && cl.sessionB.slot === s.slot)
        );
        if (myClash) {
          clashHtml = getClashSuggestionHTML(myClash);
        }

        rowsHtml += '<div class="session-row flex flex-col gap-1 p-3 rounded-xl ' + (isToday ? 'bg-indigo-500/5 border border-indigo-500/20' : 'border-b border-slate-800/50') + ' ' + (isPast && !st ? 'opacity-60' : '') + ' ' + btbClass + '">' +
          '<div class="flex items-center gap-4">' +
            '<div class="w-14 text-center shrink-0">' +
              '<div class="text-xs font-bold text-white">Session ' + s.sessionNum + '</div>' +
              '<div class="text-[10px] text-slate-500">' + s.day.slice(0,3) + '</div>' +
            '</div>' +
            '<div class="w-20 shrink-0">' +
              '<div class="text-sm font-semibold text-white">' + new Date(s.date).toLocaleDateString('en-IN', {month:'short', day:'numeric'}) + '</div>' +
              '<div class="text-xs text-slate-500">' + s.time + '</div>' +
            '</div>' +
            '<div class="flex-1 min-w-0">' +
              '<div class="text-xs text-slate-500">' + s.classroom + ' ' + btbBadge + '</div>' +
            '</div>' +
            '<div class="shrink-0 w-28 flex justify-end">' + statusHtml + '</div>' +
            '<div class="shrink-0">' + attBtn(s.date, code, s.slot, true) + '</div>' +
          '</div>' +
          clashHtml +
        '</div>';
      }

      document.getElementById('modal-body').innerHTML = '<div class="space-y-1">' + rowsHtml + '</div>';
      document.getElementById('course-modal').classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      document.getElementById('course-modal').classList.add('hidden');
      document.body.style.overflow = '';
    }
'''

bundle_picker_js = '''
    // ─── Bundle Picker ───
    async function openBundlePicker() {
      document.getElementById('bundle-modal').classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      const allData = await loadAllCourses();
      const container = document.getElementById('bundle-body');
      if (!allData) {
        container.innerHTML = '<div class="text-center py-10 text-amber-400">' +
          '<p>Could not load all_courses.json</p>' +
          '<p class="text-sm text-slate-500 mt-2">Course picker requires the dashboard to be hosted (not opened via file://).</p>' +
          '<p class="text-sm text-slate-500">Run <code class="bg-slate-800 px-1 rounded">python -m http.server</code> and open localhost:8000</p>' +
        '</div>';
        return;
      }

      const groups = {};
      allData.courses.forEach(c => {
        const base = c.code.includes(' ') ? c.code.split(' ')[0] : c.code;
        if (!groups[base]) groups[base] = [];
        groups[base].push(c);
      });

      selectedBundle = data.courses.map(c => c.code);
      updateBundleCredits();

      let html = '<div class="space-y-4">';
      Object.keys(groups).sort().forEach(base => {
        const courses = groups[base];
        const meta = courses[0];
        html += '<div class="picker-course rounded-xl border border-slate-700 p-4">' +
          '<div class="flex items-center justify-between mb-2">' +
            '<div>' +
              '<div class="font-semibold text-white text-sm">' + meta.name + '</div>' +
              '<div class="text-xs text-slate-500">' + meta.faculty + ' &bull; ' + meta.credits + ' cr &bull; Sister: ' + (meta.sisterAllowed ? 'Yes' : 'No') + '</div>' +
            '</div>' +
          '</div>' +
          '<div class="flex gap-2 flex-wrap">' +
            courses.map(c =>
              `<button onclick="toggleCourse('${c.code}')" id="picker-${c.code}" class="px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ` +
              (selectedBundle.includes(c.code) ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700') + '">' +
              c.code +
              '</button>'
            ).join('') +
          '</div>' +
        '</div>';
      });
      html += '</div>';
      container.innerHTML = html;
    }

    function closeBundlePicker() {
      document.getElementById('bundle-modal').classList.add('hidden');
      document.body.style.overflow = '';
    }

    function toggleCourse(code) {
      if (selectedBundle.includes(code)) {
        selectedBundle = selectedBundle.filter(c => c !== code);
      } else {
        selectedBundle.push(code);
      }
      const btn = document.getElementById('picker-' + code);
      if (btn) {
        if (selectedBundle.includes(code)) {
          btn.className = 'px-3 py-1.5 rounded-lg text-xs font-medium border transition-all bg-indigo-500/20 border-indigo-500 text-indigo-300';
        } else {
          btn.className = 'px-3 py-1.5 rounded-lg text-xs font-medium border transition-all bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700';
        }
      }
      updateBundleCredits();
    }

    function updateBundleCredits() {
      if (!allCoursesData) return;
      const credits = selectedBundle.reduce((sum, code) => {
        const c = allCoursesData.courses.find(x => x.code === code);
        return sum + (c ? c.credits : 0);
      }, 0);
      const el = document.getElementById('bundle-credits');
      el.textContent = credits;
      el.className = credits > 24 ? 'font-bold text-rose-400 ml-1' : 'font-bold text-white ml-1';
    }

    async function saveBundle() {
      if (!allCoursesData) return;
      const newCourses = [];
      for (const code of selectedBundle) {
        const c = allCoursesData.courses.find(x => x.code === code);
        if (c) newCourses.push(c);
      }
      if (newCourses.length === 0) {
        alert('Please select at least one course');
        return;
      }
      const newData = {
        termStart: allCoursesData.termStart,
        termEnd: allCoursesData.termEnd,
        cfaDate: allCoursesData.cfaDate,
        courses: newCourses,
        clashes: []
      };
      data = newData;
      localStorage.setItem(BUNDLE_KEY, JSON.stringify(newData));
      closeBundlePicker();
      renderHomeTab();
      renderCoursesTab();
      renderCalendarTab();
      alert('Bundle saved! ' + newCourses.length + ' courses selected.');
    }

    function resetBundle() {
      if (!confirm('Reset to default bundle?')) return;
      localStorage.removeItem(BUNDLE_KEY);
      data = DEFAULT_DATA;
      location.reload();
    }

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') { closeModal(); closeBundlePicker(); }
    });

    // Init
    setInterval(updateClock, 30000);
    updateClock();
    renderHomeTab();
  </script>
</body>
</html>
'''

# Combine all parts
full_html = head + navbar + main + modals + script_start + clash_js + clock_js + home_tab_js + courses_tab_js + calendar_tab_js + modal_js + bundle_picker_js

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Built index.html successfully")
print(f"File size: {len(full_html):,} bytes")
