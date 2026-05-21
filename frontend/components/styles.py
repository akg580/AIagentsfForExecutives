"""
frontend/components/styles.py
──────────────────────────────
Enterprise design system for RAG Executive Analyst.
Import get_css() in every page to apply the full design system.

Aesthetic: Premium obsidian dark — Bloomberg × Linear × Notion
Fonts: DM Sans (body) + Space Grotesk (headings/mono)
"""

MASTER_CSS = """
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ═══════════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
═══════════════════════════════════════════════════════════════════════════ */
:root {
  /* Background layers */
  --bg-base:        #080C14;
  --bg-surface:     #0D1321;
  --bg-elevated:    #111827;
  --bg-overlay:     #161E2E;
  --bg-hover:       #1A2332;

  /* Border */
  --border-subtle:  rgba(255,255,255,0.06);
  --border-default: rgba(255,255,255,0.10);
  --border-strong:  rgba(255,255,255,0.18);

  /* Brand — Indigo */
  --indigo-400: #818CF8;
  --indigo-500: #6366F1;
  --indigo-600: #4F46E5;
  --indigo-700: #4338CA;
  --indigo-900: #1E1B4B;
  --indigo-glow: rgba(99,102,241,0.20);

  /* Accent — Amber */
  --amber-400:  #FBD34D;
  --amber-500:  #F59E0B;
  --amber-600:  #D97706;
  --amber-glow: rgba(245,158,11,0.15);

  /* Semantic */
  --emerald:     #10B981;
  --emerald-dim: rgba(16,185,129,0.12);
  --red:         #F87171;
  --red-dim:     rgba(248,113,113,0.12);
  --sky:         #38BDF8;
  --sky-dim:     rgba(56,189,248,0.12);
  --violet:      #A78BFA;
  --violet-dim:  rgba(167,139,250,0.12);

  /* Text */
  --text-primary:   #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted:     #64748B;
  --text-accent:    #818CF8;

  /* Spacing */
  --radius-sm:  6px;
  --radius-md:  10px;
  --radius-lg:  14px;
  --radius-xl:  20px;

  /* Shadows */
  --shadow-card:   0 4px 24px rgba(0,0,0,0.4), 0 1px 4px rgba(0,0,0,0.3);
  --shadow-glow:   0 0 40px rgba(99,102,241,0.12);
  --shadow-amber:  0 0 30px rgba(245,158,11,0.10);
}

/* ═══════════════════════════════════════════════════════════════════════════
   GLOBAL RESET + BODY
═══════════════════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body,
.main, .block-container,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background-color: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.block-container {
  padding: 2rem 2.5rem 4rem !important;
  max-width: 1280px !important;
}

/* Remove Streamlit top padding */
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, header { visibility: hidden !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0A0F1E 0%, #080C14 100%) !important;
  border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] > div:first-child {
  padding: 1.5rem 1rem !important;
}

[data-testid="stSidebar"] * {
  color: var(--text-secondary) !important;
  font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebar"] a:hover {
  color: var(--indigo-400) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TYPOGRAPHY OVERRIDES
═══════════════════════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
  font-family: 'Space Grotesk', sans-serif !important;
  color: var(--text-primary) !important;
  letter-spacing: -0.02em !important;
}

p, li, span, label, div {
  font-family: 'DM Sans', sans-serif !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stButton"] > button {
  background: linear-gradient(135deg, var(--indigo-600), var(--indigo-500)) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  letter-spacing: 0.01em !important;
  padding: 0.6rem 1.4rem !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 2px 12px rgba(99,102,241,0.3) !important;
}

[data-testid="stButton"] > button:hover {
  background: linear-gradient(135deg, var(--indigo-500), var(--indigo-400)) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 20px rgba(99,102,241,0.45) !important;
}

[data-testid="stButton"] > button[kind="secondary"] {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-default) !important;
  color: var(--text-secondary) !important;
  box-shadow: none !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   DOWNLOAD BUTTON
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stDownloadButton"] > button {
  background: linear-gradient(135deg, #065F46, #10B981) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 12px rgba(16,185,129,0.25) !important;
  transition: all 0.2s ease !important;
}

[data-testid="stDownloadButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 20px rgba(16,185,129,0.40) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   INPUTS + SELECTS + TEXTAREAS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb],
[data-testid="stMultiSelect"] div[data-baseweb],
[data-baseweb="select"] {
  background-color: var(--bg-elevated) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-primary) !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: border-color 0.2s ease !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--indigo-500) !important;
  box-shadow: 0 0 0 3px var(--indigo-glow) !important;
  outline: none !important;
}

/* Labels */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stCheckbox"] label,
[data-testid="stSlider"] label {
  color: var(--text-secondary) !important;
  font-size: 0.8125rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  font-family: 'Space Grotesk', sans-serif !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FILE UPLOADER
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
  border: 2px dashed var(--border-default) !important;
  border-radius: var(--radius-lg) !important;
  background: var(--bg-elevated) !important;
  transition: border-color 0.2s ease !important;
}

[data-testid="stFileUploader"]:hover {
  border-color: var(--indigo-500) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   METRICS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-lg) !important;
  padding: 1rem 1.25rem !important;
}

[data-testid="stMetricValue"] {
  color: var(--text-primary) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 1.75rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em !important;
}

[data-testid="stMetricLabel"] {
  color: var(--text-muted) !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
}

[data-testid="stMetricDelta"] {
  font-size: 0.75rem !important;
  font-weight: 600 !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   ALERTS / CALLOUTS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
  border-radius: var(--radius-lg) !important;
  border: none !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
}

.stSuccess  { background: var(--emerald-dim) !important; color: var(--emerald) !important; }
.stWarning  { background: var(--amber-glow) !important; color: var(--amber-500) !important; }
.stError    { background: var(--red-dim) !important; color: var(--red) !important; }
.stInfo     { background: var(--indigo-glow) !important; color: var(--indigo-400) !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   EXPANDERS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-lg) !important;
  margin-bottom: 0.5rem !important;
}

[data-testid="stExpander"] summary {
  color: var(--text-secondary) !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  padding: 0.75rem 1rem !important;
}

[data-testid="stExpander"] summary:hover {
  color: var(--text-primary) !important;
  background: var(--bg-hover) !important;
  border-radius: var(--radius-lg) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, var(--indigo-600), var(--indigo-400)) !important;
  border-radius: 9999px !important;
}

[data-testid="stProgress"] > div {
  background: var(--bg-elevated) !important;
  border-radius: 9999px !important;
  height: 6px !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stSpinner"] {
  color: var(--indigo-400) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   DIVIDER
═══════════════════════════════════════════════════════════════════════════ */
hr {
  border: none !important;
  border-top: 1px solid var(--border-subtle) !important;
  margin: 1.5rem 0 !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 9999px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }

/* ═══════════════════════════════════════════════════════════════════════════
   CHECKBOX + SLIDER
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stCheckbox"] {
  color: var(--text-secondary) !important;
}

[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: var(--indigo-500) !important;
  border: 2px solid var(--indigo-400) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   COLUMNS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="column"] {
  gap: 0.75rem !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS (injected via st.markdown)
═══════════════════════════════════════════════════════════════════════════ */

/* Page header banner */
.rea-page-header {
  background: linear-gradient(135deg, #0D1321 0%, #111827 50%, #0D1321 100%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 2rem 2.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.rea-page-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 70% 50%, rgba(99,102,241,0.10) 0%, transparent 60%);
  pointer-events: none;
}

.rea-page-header::after {
  content: '';
  position: absolute;
  top: 0; left: 0;
  right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--indigo-500), transparent);
}

.rea-page-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.03em;
  margin: 0 0 0.375rem;
  line-height: 1.2;
}

.rea-page-subtitle {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9375rem;
  color: var(--text-muted);
  margin: 0;
  font-weight: 400;
}

.rea-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: 9999px;
  margin-bottom: 0.75rem;
}

.rea-badge-indigo { background: var(--indigo-glow); color: var(--indigo-400); border: 1px solid rgba(99,102,241,0.3); }
.rea-badge-amber  { background: var(--amber-glow);  color: var(--amber-500);  border: 1px solid rgba(245,158,11,0.3);  }
.rea-badge-emerald{ background: var(--emerald-dim); color: var(--emerald);    border: 1px solid rgba(16,185,129,0.3);  }
.rea-badge-sky    { background: var(--sky-dim);     color: var(--sky);        border: 1px solid rgba(56,189,248,0.3);   }

/* KPI cards */
.rea-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.rea-kpi-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.rea-kpi-card:hover {
  border-color: var(--border-strong);
  transform: translateY(-2px);
}

.rea-kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
}

.rea-kpi-card.indigo::before { background: linear-gradient(90deg, var(--indigo-600), var(--indigo-400)); }
.rea-kpi-card.amber::before  { background: linear-gradient(90deg, var(--amber-600),  var(--amber-400));  }
.rea-kpi-card.emerald::before{ background: linear-gradient(90deg, #065F46,            var(--emerald));    }
.rea-kpi-card.sky::before    { background: linear-gradient(90deg, #0369A1,            var(--sky));        }

.rea-kpi-label {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.rea-kpi-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.875rem;
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.rea-kpi-value.indigo  { color: var(--indigo-400); }
.rea-kpi-value.amber   { color: var(--amber-400);  }
.rea-kpi-value.emerald { color: var(--emerald);    }
.rea-kpi-value.sky     { color: var(--sky);        }

.rea-kpi-sub {
  font-size: 0.8125rem;
  color: var(--text-muted);
  font-weight: 400;
}

/* Section divider with label */
.rea-section-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1.75rem 0 1rem;
}

.rea-section-label span {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  white-space: nowrap;
}

.rea-section-label::before,
.rea-section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-subtle);
}

/* Source card */
.rea-source-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  margin-bottom: 0.625rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  transition: border-color 0.15s ease;
}

.rea-source-card:hover { border-color: var(--border-default); }

.rea-source-num {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--indigo-400);
  background: var(--indigo-glow);
  border: 1px solid rgba(99,102,241,0.25);
  border-radius: 6px;
  padding: 2px 8px;
  white-space: nowrap;
  flex-shrink: 0;
  margin-top: 1px;
}

.rea-source-body { flex: 1; min-width: 0; }
.rea-source-title {
  font-family: 'DM Sans', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-primary);
  margin-bottom: 0.2rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rea-source-meta {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.rea-score-pill {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
  background: var(--emerald-dim);
  color: var(--emerald);
  border: 1px solid rgba(16,185,129,0.2);
  flex-shrink: 0;
  margin-top: 2px;
}

/* Doc row */
.rea-doc-row {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 0.875rem 1.25rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: border-color 0.15s ease;
}

.rea-doc-row:hover { border-color: var(--border-default); }

.rea-doc-icon {
  width: 36px; height: 36px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.rea-doc-icon.pdf     { background: rgba(248,113,113,0.12); }
.rea-doc-icon.docx    { background: rgba(56,189,248,0.12);  }
.rea-doc-icon.xlsx    { background: rgba(16,185,129,0.12);  }
.rea-doc-icon.default { background: var(--indigo-glow);     }

.rea-doc-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-primary);
  margin-bottom: 0.125rem;
}

.rea-doc-meta { font-size: 0.8125rem; color: var(--text-muted); }
.rea-doc-info { flex: 1; min-width: 0; }
.rea-doc-chips { display: flex; gap: 0.5rem; align-items: center; flex-shrink: 0; }

/* Report section card */
.rea-report-section {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.rea-report-section-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  margin-bottom: 0.875rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rea-report-content {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  line-height: 1.75;
  white-space: pre-wrap;
}

/* Trace step */
.rea-trace-step {
  display: flex;
  gap: 0.75rem;
  padding: 0.625rem 0;
  border-bottom: 1px solid var(--border-subtle);
  align-items: flex-start;
}

.rea-trace-step:last-child { border-bottom: none; }

.rea-trace-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.rea-trace-icon.THINK   { background: var(--indigo-glow); }
.rea-trace-icon.ACT     { background: var(--amber-glow);  }
.rea-trace-icon.OBSERVE { background: var(--sky-dim);     }
.rea-trace-icon.ANSWER  { background: var(--emerald-dim); }

.rea-trace-label {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.2rem;
}

.rea-trace-content {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Answer block */
.rea-answer-block {
  background: linear-gradient(135deg, #0D1321, #111827);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: 1.75rem 2rem;
  position: relative;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.rea-answer-block::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--indigo-500), transparent);
}

.rea-answer-text {
  font-size: 1rem;
  color: var(--text-primary);
  line-height: 1.8;
  white-space: pre-wrap;
}

/* Step card for how-it-works */
.rea-step-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  text-align: center;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.rea-step-card:hover {
  border-color: var(--indigo-500);
  transform: translateY(-3px);
}

.rea-step-num {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--indigo-400);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.rea-step-emoji { font-size: 2rem; margin-bottom: 0.75rem; display: block; }

.rea-step-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.rea-step-desc {
  font-size: 0.875rem;
  color: var(--text-muted);
  line-height: 1.6;
}

/* Status dot */
.rea-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}
.rea-dot.green { background: var(--emerald); box-shadow: 0 0 6px var(--emerald); }
.rea-dot.amber { background: var(--amber-500); }
.rea-dot.red   { background: var(--red); }

/* Sidebar nav item */
.rea-nav-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background 0.15s ease;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-muted);
  text-decoration: none;
  margin-bottom: 2px;
}

.rea-nav-item:hover {
  background: rgba(255,255,255,0.05);
  color: var(--text-primary);
}

.rea-nav-item.active {
  background: var(--indigo-glow);
  color: var(--indigo-400);
  border: 1px solid rgba(99,102,241,0.2);
}

/* Sidebar logo */
.rea-sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.25rem 0;
  margin-bottom: 1.5rem;
}

.rea-sidebar-logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--indigo-600), var(--indigo-400));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  flex-shrink: 0;
  box-shadow: 0 2px 10px var(--indigo-glow);
}

.rea-sidebar-logo-text {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 0.9375rem;
  color: var(--text-primary) !important;
  line-height: 1.3;
}

.rea-sidebar-logo-sub {
  font-size: 0.6875rem;
  color: var(--text-muted) !important;
  font-weight: 400;
  font-family: 'DM Sans', sans-serif;
}

.rea-sidebar-section {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted) !important;
  padding: 0.25rem 0.75rem;
  margin: 1rem 0 0.375rem;
}

/* Stat row in sidebar */
.rea-sidebar-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  color: var(--text-muted) !important;
  border-radius: var(--radius-sm);
}

.rea-sidebar-stat-val {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  color: var(--text-primary) !important;
  font-size: 0.875rem;
}

/* Animations */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0);    }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0.15); }
  50%       { box-shadow: 0 0 0 8px rgba(99,102,241,0);   }
}

.rea-page-header   { animation: fadeInUp 0.4s ease both; }
.rea-kpi-grid      { animation: fadeInUp 0.4s 0.1s ease both; }
.rea-answer-block  { animation: fadeInUp 0.35s ease both; }
</style>
"""


def get_css() -> str:
    """Return the full enterprise CSS + font injection."""
    return MASTER_CSS


def sidebar_html() -> str:
    """Return the custom sidebar logo HTML block."""
    return """
<div class="rea-sidebar-logo">
  <div class="rea-sidebar-logo-icon">📊</div>
  <div>
    <div class="rea-sidebar-logo-text">RAG Analyst</div>
    <div class="rea-sidebar-logo-sub">Executive Intelligence</div>
  </div>
</div>
"""


def page_header(title: str, subtitle: str, badge: str = "", badge_type: str = "indigo") -> str:
    badge_html = f'<div class="rea-badge rea-badge-{badge_type}">{badge}</div>' if badge else ""
    return f"""
<div class="rea-page-header">
  {badge_html}
  <div class="rea-page-title">{title}</div>
  <div class="rea-page-subtitle">{subtitle}</div>
</div>
"""


def kpi_grid(cards: list[dict]) -> str:
    """cards = list of dict(label, value, sub, color)"""
    items = ""
    for c in cards:
        color = c.get("color", "indigo")
        items += f"""
<div class="rea-kpi-card {color}">
  <div class="rea-kpi-label">{c['label']}</div>
  <div class="rea-kpi-value {color}">{c['value']}</div>
  <div class="rea-kpi-sub">{c.get('sub','')}</div>
</div>"""
    return f'<div class="rea-kpi-grid">{items}</div>'


def section_label(text: str) -> str:
    return f'<div class="rea-section-label"><span>{text}</span></div>'


def source_card(num: int, filename: str, meta: str, score: float, content: str, url: str = "") -> str:
    score_pct = f"{score * 100:.0f}%"
    link = f' · <a href="{url}" target="_blank" style="color:var(--sky);font-size:0.8rem;">↗ source</a>' if url else ""
    return f"""
<div class="rea-source-card">
  <div class="rea-source-num">SRC {num}</div>
  <div class="rea-source-body">
    <div class="rea-source-title">{filename}</div>
    <div class="rea-source-meta">{meta}{link}</div>
    <div style="margin-top:0.5rem;font-size:0.85rem;color:var(--text-muted);line-height:1.6">{content[:280]}{"…" if len(content)>280 else ""}</div>
  </div>
  <div class="rea-score-pill">{score_pct}</div>
</div>"""


def doc_row(filename: str, file_type: str, chunks: int, pages: int) -> str:
    icons = {"pdf": "📄", "docx": "📝", "doc": "📝", "xlsx": "📊", "xls": "📊", "txt": "📋", "md": "📋"}
    icon = icons.get(file_type.lower(), "📁")
    css_class = "pdf" if "pdf" in file_type else "docx" if "doc" in file_type else "xlsx" if "xls" in file_type else "default"
    return f"""
<div class="rea-doc-row">
  <div class="rea-doc-icon {css_class}">{icon}</div>
  <div class="rea-doc-info">
    <div class="rea-doc-name">{filename}</div>
    <div class="rea-doc-meta">{file_type.upper()} · {pages} pages · {chunks} chunks indexed</div>
  </div>
  <div class="rea-doc-chips">
    <span class="rea-badge rea-badge-emerald">✓ Indexed</span>
  </div>
</div>"""


def answer_block(text: str) -> str:
    return f'<div class="rea-answer-block"><div class="rea-answer-text">{text}</div></div>'


def trace_step(step_type: str, content: str) -> str:
    icons = {"THINK": "🤔", "ACT": "⚡", "OBSERVE": "👁", "ANSWER": "✅"}
    icon = icons.get(step_type, "•")
    return f"""
<div class="rea-trace-step">
  <div class="rea-trace-icon {step_type}">{icon}</div>
  <div>
    <div class="rea-trace-label">{step_type}</div>
    <div class="rea-trace-content">{content}</div>
  </div>
</div>"""


def report_section_card(title: str, icon: str, content: str) -> str:
    safe = content.replace("<", "&lt;").replace(">", "&gt;")
    return f"""
<div class="rea-report-section">
  <div class="rea-report-section-title">{icon} {title}</div>
  <div class="rea-report-content">{safe}</div>
</div>"""
