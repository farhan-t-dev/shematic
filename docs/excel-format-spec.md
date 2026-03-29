# Excel Input Format Specification

The parser auto-detects column layout. This doc defines what it looks for
and what it handles gracefully vs. what will cause a failure.

---

## What the Parser Expects

### Layer Headers
Any cell in any column that matches:
- Starts with `$`
- Contains `Primary` OR `xs`

Examples that work:
```
$10,000,000 Primary
$5,000,000 xs $10,000,000
$15,000,000 xs $10,000,000 Including Flood and Quake
$150,000,000 xs $100,000,000 Excluding Flood and Quake
```

Examples that will be skipped (non-standard):
```
DBB - $500k xs $500k - 2x
Layer 1 - Primary $10M       ← doesn't start with $
```

### Carrier Rows
A row is treated as a carrier if:
- The carrier name column is non-empty
- The name is not in the skip list: `Totals`, `Percent Complete`, `Carrier`, `""`
- The name doesn't start with `$`
- Either `auth` or `pct` is non-zero

### Column Auto-Detection
The parser scans for a header row containing both `Carrier` and `Authorization`
(case-insensitive). From that row it infers:
- `name_col` = column containing "carrier"
- `status_col` = column containing "status"
- `auth_col` = column containing "auth"
- `pct_col` = column containing "%" or "particip"
- `prem_col` = column containing "share" + "prem" (or fallback: pct_col + 1)

If no header row is found, fallback defaults are: name=0, status=1, auth=2, pct=3, prem=4.

### Account Name Detection
Scans columns 0 and 1 of rows 0–3.
Skips cells matching: `Named Insured`, `Share`, `Layer`, `Carrier`, `Status`,
`Authorization`, `Total`, `Totals`, `Premium`, `Participation`, `As of`,
`Rate`, `Fees`, `Comm`, `Comm %`, `Comm $`
First non-skipped string that isn't a date → account name.
First cell matching `MM/DD/YYYY` pattern → policy period.

---

## Supported Variations

| Variation | Handled? | Notes |
|-----------|----------|-------|
| Carrier name in col 0 | ✅ | Original template format |
| Carrier name in col 1 | ✅ | Midwest-style format |
| Layer label in col 0 | ✅ | |
| Layer label in col 1 | ✅ | |
| "Included" instead of a number | ✅ | Treated as 0 |
| Blank participation % | ✅ | Carrier skipped |
| Parallel layers (same attachment) | ✅ | Rendered side by side |
| Long layer labels with qualifiers | ✅ | Shown truncated on right side |
| TBD carrier | ✅ | Shown as placeholder, triggers W08 |
| Non-standard layers (DBB etc.) | ✅ | Silently skipped |
| Zero-auth carriers | ✅ | Filtered out if real carriers exist in layer |
| Multiple sheets | ⚠️ | Only first sheet is read |
| .xls (old format) | ❌ | Must be .xlsx |
| Password-protected files | ❌ | Cannot read |

---

## To Add Support for a New Format

1. Open `scripts/generate_schematic.py`
2. Find the `detect_columns()` function
3. Add detection logic for the new header pattern
4. Test against the new file
5. Update this doc with the new variation

---

## Known Edge Cases

- If a carrier appears in multiple layers under slightly different spellings,
  the validator (W04) will flag it. They get different colors if not merged.
- If the total program limit jumps by a very large amount between layers
  (e.g. $20M to $250M with nothing in between), validator B06 will flag a gap.
