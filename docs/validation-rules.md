# Validation Rules

All checks run in `scripts/validate.py` during Stage 02.
Checks are classified as BLOCKING or WARNING.

**BLOCKING** = pipeline stops. User must confirm or fix before render.
**WARNING**  = pipeline surfaces the issue, asks for confirmation or extra input, then proceeds if the user confirms.

---

## BLOCKING Checks

| ID | Check | Condition | Message to User |
|----|-------|-----------|-----------------|
| B01 | File unreadable | Excel cannot be opened or has no sheets | "We couldn't read your file. Please check it's a valid .xlsx and try again." |
| B02 | No layers found | Zero layer headers parsed from the file | "No insurance layers were found in this file. Check that layers are labeled like '$10,000,000 Primary' or '$5,000,000 xs $10,000,000'." |
| B03 | No carriers in any layer | All layers parsed but all are empty | "Layers were found but no carrier data could be read. Check that carrier rows have authorization amounts and participation %." |
| B04 | Layer bounds invalid | A layer's top ≤ bottom (e.g. xs amount is 0) | "Layer '[label]' has invalid bounds — the limit or attachment point looks wrong. Please review." |
| B05 | Duplicate layer labels | Two layers have identical labels | "Layer '[label]' appears twice. Please remove the duplicate or rename one." |
| B06 | Program has gaps | Layers don't form a continuous tower (e.g. $10M primary + $25M xs $25M with nothing in between) | "There's a gap in the program between $[X] and $[Y]. Either a layer is missing or the attachment points are wrong." |

---

## WARNING Checks

| ID | Check | Condition | Message to User |
|----|-------|-----------|-----------------|
| W01 | Incomplete layer | Layer participation sums to < 95% | "The '[label]' layer is only [X]% complete. The schematic will show what's confirmed. Continue?" |
| W02 | Layer over-subscribed | Layer participation sums to > 105% | "The '[label]' layer adds up to [X]% — slightly over 100%. This may be a rounding issue. Continue?" |
| W03 | No account name | Account name is blank or still reads 'Named Insured' | "We couldn't find an account name in your file. What should the title of the schematic be?" → prompt user to type it |
| W04 | Possible carrier name mismatch | Same carrier appears with slightly different spelling across layers | "We found what might be the same carrier spelled two ways: '[name A]' and '[name B]'. Are these the same carrier?" → Yes/No → merge if Yes |
| W05 | Carrier with no participation % | A carrier row has an auth amount but pct = 0 | "Carrier '[name]' in layer '[label]' has an authorization amount but no participation %. It will be skipped. Continue?" |
| W06 | Very large program | Total program limit > $1 billion | "This program has a total limit of $[X]. Just confirming this is correct before we render." |
| W08 | TBD carrier present | A carrier is named 'TBD' | "Layer '[label]' contains a TBD carrier at [X]%. The schematic will show TBD as a placeholder. Continue?" |

---

## Flag Report Format

When any flags are triggered in the web app, show them in the validation screen before allowing generation:

```
─────────────────────────────────────────
SCHEMATIC VALIDATION REPORT
File: [filename]
─────────────────────────────────────────
BLOCKING (must resolve before continuing)
  [B01] ...

WARNINGS (review and confirm)
  [W01] The '$5M xs $10M' layer is 80% complete...
  [W03] No account name found — what should the title be?

─────────────────────────────────────────
User actions:
  - Fix the spreadsheet and upload again if blocked
  - Enter any requested values such as the schematic title
  - Answer any carrier merge confirmations
  - Click Generate when ready
─────────────────────────────────────────
```

---

## Checks to Add Later

- Carrier auth amount doesn't match pct × layer size (math check)
- Policy period date is in the past by more than 2 years (stale data warning)
- Same carrier takes >60% of any single layer (concentration flag)
- Layer label format non-standard (can't parse but data is present)
