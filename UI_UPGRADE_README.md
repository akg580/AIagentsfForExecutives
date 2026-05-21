# UI Upgrade — RAG Executive Analyst
## Enterprise Dark Theme · Space Grotesk · Obsidian × Indigo

---

## What's in this package

```
ui-upgrade/
├── frontend/
│   ├── app.py                   ← Home dashboard (REPLACE existing)
│   ├── components/
│   │   └── styles.py            ← NEW — full design system
│   └── pages/
│       ├── 1_upload.py          ← Upload page (REPLACE existing)
│       ├── 2_query.py           ← Q&A page    (REPLACE existing)
│       └── 3_reports.py         ← Reports page (REPLACE existing)
└── .streamlit/
    └── config.toml              ← NEW — dark theme config
```

---

## How to apply

### Option A — Replace files directly (recommended)

```bash
# From your project root (rag-executive-analyst/)
cp ui-upgrade/frontend/app.py              frontend/app.py
cp ui-upgrade/frontend/components/styles.py frontend/components/styles.py
cp ui-upgrade/frontend/pages/1_upload.py   frontend/pages/1_upload.py
cp ui-upgrade/frontend/pages/2_query.py    frontend/pages/2_query.py
cp ui-upgrade/frontend/pages/3_reports.py  frontend/pages/3_reports.py
cp ui-upgrade/.streamlit/config.toml       .streamlit/config.toml

# Create components dir if not exists
mkdir -p frontend/components
touch frontend/components/__init__.py
```

### Option B — Manual paste in VS Code

1. Open each file from `ui-upgrade/frontend/` in VS Code
2. Select All (`Ctrl+A`) → Copy
3. Open the matching file in your project
4. Select All → Paste → Save

---

## Design System

### Palette
| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-base` | `#080C14` | Page background |
| `--bg-surface` | `#0D1321` | Card backgrounds |
| `--bg-elevated` | `#111827` | Input/hover states |
| `--indigo-500` | `#6366F1` | Primary brand, buttons |
| `--indigo-400` | `#818CF8` | Accents, links, badges |
| `--amber-500` | `#F59E0B` | Warnings, highlights |
| `--emerald` | `#10B981` | Success, indexing, scores |
| `--sky` | `#38BDF8` | Web sources, info |
| `--text-primary` | `#F1F5F9` | Headlines, key values |
| `--text-secondary`| `#94A3B8` | Body copy |
| `--text-muted` | `#64748B` | Labels, metadata |

### Typography
- **Headlines / labels**: Space Grotesk (700 weight, -0.02em tracking)
- **Body / UI text**: DM Sans (400–600 weight)
- Both loaded from Google Fonts CDN (zero install)

### Component library (`styles.py`)
| Function | Output |
|----------|--------|
| `get_css()` | Full CSS design system injection |
| `sidebar_html()` | Logo + branding block |
| `page_header(title, subtitle, badge)` | Hero banner with gradient top-line |
| `kpi_grid(cards)` | 4-column KPI metric strip |
| `section_label(text)` | Divider with centered uppercase label |
| `source_card(num, filename, meta, score, content, url)` | Evidence source row |
| `doc_row(filename, type, chunks, pages)` | Document library row |
| `answer_block(text)` | Highlighted answer container |
| `trace_step(type, content)` | Agent reasoning step |
| `report_section_card(title, icon, content)` | Report section container |

---

## Visual highlights per page

### 🏠 Home (`app.py`)
- Full-bleed obsidian hero with animated gradient top-line
- 4-column KPI strip (indigo / amber / emerald / sky)
- Architecture flow diagram in HTML
- 3-column "How it works" step cards with hover lift
- 8-cell free-tier stack grid
- Live API health check in sidebar with status dot

### 📁 Upload (`1_upload.py`)
- Drag-and-drop zone with dashed indigo border on hover
- File preview card with format badge before upload
- Animated progress bar (Upload → Chunk → Embed → Store)
- Success card with chunk count, file name, doc ID
- Document library with type-specific icons (📄 PDF, 📝 DOCX, 📊 XLSX)
- Stats bar showing total documents + total chunks

### 🔍 Q&A (`2_query.py`)
- Example query shortcuts in sidebar (click to prefill)
- Answer block with gradient top-line border
- 5-cell metrics strip (latency / internal / web / mode)
- Two-column source layout (internal left, web right)
- Expandable source cards with content preview
- Collapsible agent reasoning trace

### 📄 Reports (`3_reports.py`)
- Report config form: title + query + section chips preview
- 7-stage animated progress bar during generation
- Report hero card with gradient rainbow top-line
- Per-section cards with icon + formatted content
- Numbered reference list (internal = indigo, web = sky)
- DOCX + Markdown download buttons (emerald gradient)
