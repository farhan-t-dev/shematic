"""
validate.py — Insurance Schematic Validator
Runs all checks defined in docs/validation-rules.md before any render.
Returns a ValidationResult with blocking flags and warnings.
The render stage must not run if result.is_blocked is True.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Flag:
    id: str           # e.g. "B01", "W03"
    level: str        # "BLOCKING" or "WARNING"
    message: str      # Plain-English message shown to user
    question: Optional[str] = None   # If user must answer, the question text
    answer: Optional[str] = None     # Filled in after user responds
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    flags: List[Flag] = field(default_factory=list)
    account_name_override: Optional[str] = None   # Set if user provides name via W03

    @property
    def blocking_flags(self):
        return [f for f in self.flags if f.level == "BLOCKING"]

    @property
    def warning_flags(self):
        return [f for f in self.flags if f.level == "WARNING"]

    @property
    def is_blocked(self):
        return len(self.blocking_flags) > 0

    def report(self) -> str:
        lines = [
            "─" * 53,
            "SCHEMATIC VALIDATION REPORT",
            "─" * 53,
        ]
        if self.blocking_flags:
            lines.append("\n🚫 BLOCKING — must resolve before continuing:\n")
            for f in self.blocking_flags:
                lines.append(f"  [{f.id}] {f.message}")
                if f.question:
                    lines.append(f"         → {f.question}")
        if self.warning_flags:
            lines.append("\n⚠️  WARNINGS — review and confirm:\n")
            for f in self.warning_flags:
                lines.append(f"  [{f.id}] {f.message}")
                if f.question:
                    lines.append(f"         → {f.question}")
        if not self.flags:
            lines.append("\n✅  All checks passed. Ready to render.\n")
        else:
            lines.append("\n" + "─" * 53)
            if self.blocking_flags:
                lines.append("Please fix the blocking issues and re-upload.")
            else:
                lines.append('Reply "continue" to render with warnings, or "stop" to fix first.')
        lines.append("─" * 53)
        return "\n".join(lines)


def validate(account_name: str, policy_period: str, layers: list, bounds: list) -> ValidationResult:
    """
    Run all validation checks.

    Parameters
    ----------
    account_name  : str   — detected account name (may be placeholder)
    policy_period : str   — detected policy period string
    layers        : list  — list of layer dicts with 'label' and 'carriers'
    bounds        : list  — list of (bottom, top) tuples matching layers

    Returns
    -------
    ValidationResult
    """
    result = ValidationResult()

    # ── B02: No layers found ──────────────────────────────────────────────────
    if not layers:
        result.flags.append(Flag(
            id="B02", level="BLOCKING",
            message="No insurance layers were found in this file.",
            question="Check that layers are labeled like '$10,000,000 Primary' or "
                     "'$5,000,000 xs $10,000,000' and re-upload."
        ))
        return result  # No point running further checks

    # ── B03: No carriers in any layer ────────────────────────────────────────
    total_carriers = sum(len(l["carriers"]) for l in layers)
    if total_carriers == 0:
        result.flags.append(Flag(
            id="B03", level="BLOCKING",
            message="Layers were found but no carrier data could be read.",
            question="Check that carrier rows have authorization amounts and participation % filled in."
        ))
        return result

    # ── B04: Layer bounds invalid ─────────────────────────────────────────────
    for layer, (bot, top) in zip(layers, bounds):
        if top <= bot:
            result.flags.append(Flag(
                id="B04", level="BLOCKING",
                message=f"Layer '{layer['label']}' has invalid bounds "
                        f"(bottom=${bot:,}, top=${top:,}).",
                question="Check the limit and attachment point for this layer."
            ))

    # ── B05: Duplicate layer labels ───────────────────────────────────────────
    seen_labels = {}
    for layer in layers:
        lbl = layer["label"].strip()
        if lbl in seen_labels:
            result.flags.append(Flag(
                id="B05", level="BLOCKING",
                message=f"Layer '{lbl}' appears more than once in the file.",
                question="Remove the duplicate or rename one layer."
            ))
        seen_labels[lbl] = True

    # ── B06: Gap in program tower ─────────────────────────────────────────────
    # Build unique sorted levels; check for gaps > $0 between top of one and bottom of next
    all_tops    = set(b[1] for b in bounds)
    all_bottoms = set(b[0] for b in bounds)
    sorted_bottoms = sorted(all_bottoms)
    for bot in sorted_bottoms:
        if bot == 0:
            continue
        if bot not in all_tops:
            # Find the nearest top below this bottom
            tops_below = [t for t in all_tops if t < bot]
            nearest_top = max(tops_below) if tops_below else 0
            result.flags.append(Flag(
                id="B06", level="BLOCKING",
                message=f"There is a gap in the program between "
                        f"${nearest_top/1_000_000:,.0f}M and ${bot/1_000_000:,.0f}M.",
                question="Either a layer is missing or the attachment points are wrong."
            ))

    # ── W01 / W02: Layer participation completeness ───────────────────────────
    for layer in layers:
        carriers = layer["carriers"]
        if not carriers:
            continue
        total_pct = sum(c["pct"] for c in carriers)
        pct_display = round(total_pct * 100, 1)

        if total_pct < 0.95:
            result.flags.append(Flag(
                id="W01", level="WARNING",
                message=f"Layer '{layer['label']}' is only {pct_display}% subscribed.",
                question="The schematic will show what's confirmed so far. Continue?"
            ))
        elif total_pct > 1.05:
            result.flags.append(Flag(
                id="W02", level="WARNING",
                message=f"Layer '{layer['label']}' adds up to {pct_display}% — over 100%.",
                question="This may be a rounding issue. Continue?"
            ))

    # ── W03: No account name ──────────────────────────────────────────────────
    placeholder_names = {"insurance program schematic", "named insured", "", "none"}
    if account_name.lower().strip() in placeholder_names:
        result.flags.append(Flag(
            id="W03", level="WARNING",
            message="No account name was found in the file.",
            question="What should the title of the schematic be?",
            metadata={"input_type": "account_name"}
        ))

    # ── W04: Possible carrier name mismatch (fuzzy) ───────────────────────────
    all_carrier_names = list({c["name"] for layer in layers for c in layer["carriers"]})
    mismatch_pairs = _find_fuzzy_matches(all_carrier_names)
    for name_a, name_b in mismatch_pairs:
        result.flags.append(Flag(
            id="W04", level="WARNING",
            message=f"'{name_a}' and '{name_b}' might be the same carrier spelled differently.",
            question=f"Are '{name_a}' and '{name_b}' the same carrier? (yes/no)",
            metadata={
                "input_type": "boolean",
                "merge_candidates": [name_a, name_b],
            }
        ))

    # ── W05: Carrier with auth but no pct ─────────────────────────────────────
    for layer in layers:
        for c in layer["carriers"]:
            if c.get("auth", 0) > 0 and c.get("pct", 0) == 0:
                result.flags.append(Flag(
                    id="W05", level="WARNING",
                    message=f"Carrier '{c['name']}' in layer '{layer['label']}' "
                            f"has an auth amount but no participation %. It will be skipped.",
                    question="Continue?"
                ))

    # ── W06: Very large program ───────────────────────────────────────────────
    if bounds:
        program_max = max(b[1] for b in bounds)
        if program_max > 1_000_000_000:
            result.flags.append(Flag(
                id="W06", level="WARNING",
                message=f"Total program limit is ${program_max/1_000_000_000:.2f}B. "
                        f"Just confirming this is correct.",
                question="Continue?"
            ))

    # ── W08: TBD carrier ─────────────────────────────────────────────────────
    for layer in layers:
        for c in layer["carriers"]:
            if c["name"].strip().upper() == "TBD":
                result.flags.append(Flag(
                    id="W08", level="WARNING",
                    message=f"Layer '{layer['label']}' contains a TBD carrier "
                            f"at {c['pct']*100:.0f}%. It will render as a placeholder.",
                    question="Continue?"
                ))

    return result


# ── Fuzzy match helper ────────────────────────────────────────────────────────

def _find_fuzzy_matches(names: list, threshold: float = 0.82) -> list:
    """
    Find pairs of carrier names that are likely the same but spelled differently.
    Uses a simple character-overlap ratio (no external deps required).
    """
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = names[i].lower().strip()
            b = names[j].lower().strip()
            if a == b:
                continue
            score = _similarity(a, b)
            if score >= threshold:
                pairs.append((names[i], names[j]))
    return pairs

def _similarity(a: str, b: str) -> float:
    """Simple Dice coefficient on bigrams."""
    def bigrams(s):
        return set(s[i:i+2] for i in range(len(s) - 1))
    ba, bb = bigrams(a), bigrams(b)
    if not ba or not bb:
        return 0.0
    return 2 * len(ba & bb) / (len(ba) + len(bb))


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Minimal smoke test
    test_layers = [
        {"label": "$10,000,000 Primary", "carriers": [
            {"name": "Carrier A", "auth": 5000000, "pct": 0.5, "premium": 0, "status": ""},
            {"name": "Carrier B", "auth": 5000000, "pct": 0.5, "premium": 0, "status": ""},
        ]},
        {"label": "$5,000,000 xs $10,000,000", "carriers": [
            {"name": "Kinsale",   "auth": 2500000, "pct": 0.5, "premium": 0, "status": "Quoted"},
        ]},  # W01: only 50% complete
    ]
    test_bounds = [(0, 10_000_000), (10_000_000, 15_000_000)]

    result = validate("Named Insured", "11/1/2023-11/1/2024", test_layers, test_bounds)
    print(result.report())
    print(f"\nis_blocked: {result.is_blocked}")
    print(f"warnings:   {len(result.warning_flags)}")
