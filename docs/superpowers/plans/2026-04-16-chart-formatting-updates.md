# Chart Formatting and Layout Updates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the insurance schematic generator to match specific sample styles: larger chart area, no legend/right-axis, regular-weight left axis labels, and fully written out dollar/percentage formats.

**Architecture:** Modify constants and rendering logic in `scripts/generate_schematic.py`. No architectural changes required.

**Tech Stack:** Python, `python-pptx`, `openpyxl`.

---

### Task 1: Update Layout Constants and Remove Legend Space

**Files:**
- Modify: `scripts/generate_schematic.py`

- [ ] **Step 1: Update layout constants for a larger chart**

Modify `CHART_L`, `CHART_W`, `CHART_H`, and `CHART_T` in `build_schematic` function.

```python
    # Layout constants
    CHART_L = 1.40
    CHART_T = 1.00
    CHART_W = 11.50
    CHART_H = 6.20
```

- [ ] **Step 2: Remove any code related to legend (if found) or right-side labels**

Ensure no calls to `add_textbox` exist for coordinates on the right side. (Already verified in research).

- [ ] **Step 3: Commit layout changes**

```bash
git add scripts/generate_schematic.py
git commit -m "style: increase chart dimensions and adjust layout"
```

---

### Task 2: Revise Axis and Label Formatting

**Files:**
- Modify: `scripts/generate_schematic.py`

- [ ] **Step 1: Update Left Axis label formatting**

Ensure labels are regular weight (not bold) and have full dollar signs/commas.

```python
        lbl = f"${level:,.0f}"
        is_bold = False # Changed from True
        add_textbox(0.0, y - 0.20, CHART_L - 0.05, 0.40,
                    [(lbl, is_bold, "222222", 10)],
                    align=PP_ALIGN.RIGHT, valign="ctr", wrap=False)
```

- [ ] **Step 2: Update sub-level axis labels formatting**

```python
            lbl = f"${level:,.0f}"
            add_textbox(0.0, y - 0.18, CHART_L - 0.05, 0.36,
                        [(lbl, False, "222222", 9)], # Changed from True
                        align=PP_ALIGN.RIGHT, valign="ctr", wrap=False)
```

- [ ] **Step 3: Update Carrier Participation labels**

Update the labels inside carrier blocks to show full dollar value and hundredth percentage.

```python
            # Label
            name       = carrier["name"]
            pct_val    = carrier["pct"] * 100
            pct_str    = f"{pct_val:.2f}%"
            dol_str    = f"${carrier['auth']:,.0f}"
            
            # ... in the label rendering logic ...
            elif dw < 0.85 or blk_h < 0.50:
                add_textbox(dx, y_top, dw, blk_h,
                            [(f"{name}\n{pct_str} ({dol_str})", True, "FFFFFF", 8)],
                            align=PP_ALIGN.CENTER, valign="ctr")

            else:
                add_textbox(dx, y_top, dw, blk_h, [
                    (name,    True,  "FFFFFF",  9),
                    (f"{pct_str} ({dol_str})", False, "E0E0E0",  8),
                ], align=PP_ALIGN.CENTER, valign="ctr")
```

- [ ] **Step 4: Commit formatting changes**

```bash
git add scripts/generate_schematic.py
git commit -m "style: update axis and carrier label formatting to match samples"
```

---

### Task 3: Verification

**Files:**
- Create: `tests/repro_formatting.py`

- [ ] **Step 1: Create a reproduction script that generates a sample PPTX**

Use a mock Excel file or existing test data to run `build_schematic`.

- [ ] **Step 2: Run the script**

```bash
python scripts/generate_schematic.py tests/data/sample_input.xlsx test_output.pptx
```

- [ ] **Step 3: Verify the output (Manual/Code check)**

Check the console output and file existence. (In a real scenario, I would open the file).
