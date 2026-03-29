"""
run_pipeline.py — Insurance Schematic Pipeline Entry Point

Usage (CLI):
    python run_pipeline.py input.xlsx output.pptx

Usage (programmatic / web wrapper):
    from run_pipeline import run_pipeline
    result = run_pipeline(excel_bytes, filename)
    if result["status"] == "needs_confirmation":
        # show result["report"] to user, collect answers
    elif result["status"] == "blocked":
        # show result["report"] to user, ask them to fix file
    elif result["status"] == "ok":
        # result["pptx_bytes"] is the file to return to user

This module is the ONLY entry point. Never call generate_schematic.py directly
without going through validation first.
"""

import sys
import io
from validate import validate, ValidationResult
from generate_schematic import parse_excel, parse_layer_bounds, build_schematic


def _serialize_flags(flags):
    return [
        {
            "key": f"{flag.id}:{index}",
            "id": flag.id,
            "level": flag.level,
            "message": flag.message,
            "question": flag.question,
            "metadata": flag.metadata,
        }
        for index, flag in enumerate(flags)
    ]


def run_pipeline(
    excel_path: str,
    output_path: str = None,
    confirmed_warnings: bool = False,
    account_name_override: str = None,
    carrier_merges: dict = None,      # {"Llyods": "Lloyds"} — from W04 user answers
    render: bool = True               # New flag to skip Stage 03
) -> dict:
    """
    Full pipeline: ingest → validate → (gate) → render.

    Parameters
    ----------
    excel_path            : str  — path to input .xlsx file
    output_path           : str  — path for output .pptx (None = return bytes)
    confirmed_warnings    : bool — True if user has already confirmed all warnings
    account_name_override : str  — user-supplied account name (W03 answer)
    carrier_merges        : dict — carrier name remappings (W04 answers)

    Returns
    -------
    dict with keys:
        status : "ok" | "blocked" | "needs_confirmation"
        report : str (validation report, always present)
        pptx_bytes : bytes (only when status == "ok" and output_path is None)
    """

    # ── Stage 01: Ingest ──────────────────────────────────────────────────────
    try:
        account_name, policy_period, layers = parse_excel(excel_path)
    except Exception as e:
        return {
            "status": "blocked",
            "report": (
                "─" * 53 + "\n"
                "🚫 BLOCKING\n\n"
                f"  [B01] Could not read the file: {e}\n\n"
                "Please check it's a valid .xlsx and try again.\n"
                + "─" * 53
            )
        }

    # Apply account name override from W03 response
    if account_name_override:
        account_name = account_name_override

    # Apply carrier name merges from W04 responses
    if carrier_merges:
        for layer in layers:
            for c in layer["carriers"]:
                if c["name"] in carrier_merges:
                    c["name"] = carrier_merges[c["name"]]

    bounds_raw = [parse_layer_bounds(l["label"]) for l in layers]
    valid_pairs = [(l, b) for l, b in zip(layers, bounds_raw) if b is not None]
    for layer, _ in valid_pairs:
        real = [c for c in layer["carriers"] if c["pct"] > 0 and c["auth"] > 0]
        if not real:
            real = [c for c in layer["carriers"] if c["pct"] > 0]
        layer["carriers"] = real
    valid_pairs = [(l, b) for l, b in valid_pairs if l["carriers"]]
    clean_layers = [l for l, b in valid_pairs]
    clean_bounds = [b for l, b in valid_pairs]

    # ── Stage 02: Validate ────────────────────────────────────────────────────
    result: ValidationResult = validate(
        account_name, policy_period, clean_layers, clean_bounds
    )

    if result.is_blocked:
        return {
            "status": "blocked",
            "report": result.report(),
            "flags": _serialize_flags(result.blocking_flags),
        }

    if result.warning_flags and not confirmed_warnings:
        return {
            "status": "needs_confirmation",
            "report": result.report(),
            "flags": _serialize_flags(result.warning_flags),
        }

    # ── Stage 03: Render ──────────────────────────────────────────────────────
    if not render:
        return {
            "status": "ok",
            "report": result.report(),
            "flags": _serialize_flags(result.warning_flags),
        }

    # Apply W03 override once more in case it came through confirmed_warnings path
    if account_name_override:
        account_name = account_name_override

    if output_path:
        build_schematic(excel_path, output_path,
                        account_name_override=account_name_override,
                        carrier_merges=carrier_merges)
        return {
            "status": "ok",
            "report": result.report(),
            "output_path": output_path,
        }
    else:
        # In-memory mode for web wrapper (no file written to disk)
        buf = io.BytesIO()
        build_schematic(excel_path, buf,
                        account_name_override=account_name_override,
                        carrier_merges=carrier_merges)
        buf.seek(0)
        return {
            "status": "ok",
            "report": result.report(),
            "pptx_bytes": buf.getvalue(),
        }


# ── CLI entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_pipeline.py input.xlsx output.pptx")
        sys.exit(1)

    excel_path  = sys.argv[1]
    output_path = sys.argv[2]

    # First pass — check for issues
    result = run_pipeline(excel_path, output_path=None)

    if result["status"] == "blocked":
        print(result["report"])
        sys.exit(1)

    if result["status"] == "needs_confirmation":
        print(result["report"])
        answer = input("\nYour reply: ").strip().lower()
        if answer != "continue":
            print("Cancelled. Fix the file and try again.")
            sys.exit(0)
        # Re-run with confirmed warnings
        result = run_pipeline(excel_path, output_path=output_path, confirmed_warnings=True)

    if result["status"] == "ok":
        print(f"\n✅ Schematic saved to: {output_path}")
