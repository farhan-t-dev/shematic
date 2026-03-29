# Output Specification — PPTX Schematic

This document defines what the generated schematic must look like.
Any change to the visual output should be validated against this spec.

---

## Slide Setup

- Layout: WIDE (13.3" × 7.5")
- Background: #F4F6F9 (light blue-gray)
- Font: Calibri throughout
- One slide per program (one Excel = one slide)

---

## Title Area

| Element | Position | Style |
|---------|----------|-------|
| Account name | Top center, y=0.08" | 24pt, bold, #1B3A6B |
| Policy period | Below account name, y=0.68" | 11pt, regular, #666666 |

If account name = "Insurance Program Schematic", this is a placeholder —
the validator (W03) should have prompted the user for the real name.

---

## Chart Area

| Property | Value |
|----------|-------|
| Left edge | 1.62" |
| Top edge | 1.02" |
| Width | 10.50" |
| Height | 5.72" |
| Background | White (#FFFFFF) |
| Border | #BBBBBB, 0.5pt |

---

## Y-Axis

- Labels sit LEFT of chart, right-aligned, in column x=0.0" w=1.55"
- Only show labels at true layer boundaries (bottom and top of each layer)
- Dominant boundaries (tallest layer at each attachment): 9pt, #222222
- Sub-boundaries from parallel/interceding layers: 8pt, #999999, lighter rule
- Program $0 and total limit: 10pt bold
- Horizontal rules: 0.008" height, #999999 fill, no line stroke

---

## Carrier Blocks

### Width
Proportional to carrier's participation % within that layer.
Percentages normalized to sum to 100% within the layer for rendering.

### Height
Layer height = proportional to dollar size, minimum floor of 10% of chart height.
Parallel layers (same attachment point) share the same vertical band — split horizontally.

### Gap between blocks
0.016" gap between adjacent carrier blocks within a layer.
Background color shows through the gap.

### Label Rules (inside each block)

| Condition | Label Style |
|-----------|-------------|
| Block width < 0.22" OR height < 0.22" | No label |
| Block width < 0.50" | Carrier name only, rotated 270°, 7pt |
| Block width < 0.85" OR height < 0.50" | "Name  pct%" single line, 8pt bold |
| Otherwise | 3-line: Name (9pt bold) / pct% (8pt #E0E0E0) / $XM (8pt #E0E0E0) |

All label text: white (#FFFFFF), centered, vertically centered.

### Color Assignment
Colors assigned in order of first appearance across layers (top to bottom, left to right).
Same carrier name always gets the same color across all layers.
Palette (16 colors, cycles if more carriers):
```
1B3A6B  B03A2E  2E86C1  1E8449  884EA0  E67E22  117A65  7B241C
1A5276  6C3483  1D6A39  626567  943126  2E4057  0E6655  A04000
```

---

## Layer Labels (Right Side)

- Position: CHART_L + CHART_W + 0.14" from left, vertically centered in layer band
- Width: 1.05", Height: 0.64"
- Format: abbreviate `$10,000,000` → `$10M` etc.
- Only show for the rightmost parallel layer in each band
- Style: 8pt, regular, #444444, left-aligned

---

## Legend

- Position: below chart, CHART_T + CHART_H + 0.16"
- Color swatch: 0.13" × 0.13"
- Item width: 1.28" per carrier
- Max per row: floor(CHART_W / 1.28)
- Font: 7.5pt, #333333, left-aligned

---

## Quality Bar

Before declaring a render complete, verify:
- [ ] All layers from the Excel are represented
- [ ] Carrier block widths visually match their participation %
- [ ] No carrier label overflows its block
- [ ] Y-axis labels appear only at true layer boundaries
- [ ] Legend includes every carrier that appears in the chart
- [ ] Title shows the real account name (not "Insurance Program Schematic")
- [ ] Policy period shown if present in source data
- [ ] Parallel layers (same attachment) render side by side, not overlapping
