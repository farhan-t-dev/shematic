# Workflows — Pipeline Workspace

## What This Workspace Is
The step-by-step pipeline from Excel upload to PPTX download.
Four stages. Each stage must complete before the next begins.
Upstream: user uploads an Excel file.
Downstream: user downloads a PPTX and the session ends.

---

## What to Load Per Stage

| Stage | Load These | Skip These |
|-------|-----------|------------|
| 01 — Ingest | `01-ingest.md`, `docs/excel-format-spec.md` | `docs/output-spec.md`, `docs/deployment-options.md` |
| 02 — Validate | `02-validate.md`, `docs/validation-rules.md` | `docs/output-spec.md`, `docs/deployment-options.md` |
| 03 — Render | `03-render.md`, `docs/output-spec.md` | `docs/excel-format-spec.md`, `docs/validation-rules.md` |
| 04 — Deliver | `04-deliver.md` | everything else |

---

## Folder Structure

```
workflows/
├── CONTEXT.md       ← This file
├── 01-ingest.md     ← Parse Excel, extract layers + carriers
├── 02-validate.md   ← Run checks, surface flags, gate the pipeline
├── 03-render.md     ← Generate PPTX
└── 04-deliver.md    ← Return file, end session
```

---

## The Pipeline

```
01 INGEST
   Read Excel → detect column layout → extract account name, policy period,
   layers, carriers, pct, auth, status
   Output: structured data object passed to validator
   Fail condition: file unreadable, no layers found → STOP, tell user

        ↓

02 VALIDATE
   Run all checks in docs/validation-rules.md
   Blocking flags → STOP, surface to user, require confirmation or fix
   Warning flags  → surface to user, ask "continue anyway?"
   Output: clean data object + flag report
   Nothing proceeds until user responds to every blocking flag

        ↓

03 RENDER
   Only runs on confirmed data
   Build PPTX: title, y-axis, carrier blocks, layer labels, legend
   No AI calls — pure python-pptx
   Output: .pptx file in memory

        ↓

04 DELIVER
   Return file to user for download
   Clear all session data
   Log nothing
```

---

## Skills & Tools

| Skill / Tool | When | Purpose |
|-------------|------|---------|
| `openpyxl` | Stage 01 | Read Excel, extract values |
| `validate.py` | Stage 02 | Run all validation checks |
| `generate_schematic.py` | Stage 03 | Build the PPTX |
| `/xlsx` skill | Stage 01 changes | When adding new Excel format support |
| `/pptx` skill | Stage 03 changes | When changing visual layout |

---

## What NOT to Do

- Do not skip Stage 02. Ever.
- Do not pass raw Excel data directly to Stage 03.
- Do not store the uploaded file after the session ends.
- Do not add AI to the render stage — it belongs only in validation narrative.
- Do not combine Stage 01 and Stage 02 into one script — they are separate concerns.
