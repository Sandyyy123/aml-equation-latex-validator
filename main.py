#!/usr/bin/env python3
"""
AML equation -> LaTeX -> validation demo.

    python3 main.py                     # validate the built-in AML equation set
    python3 main.py "(x_1 - mu)/sigma"  # validate one ad-hoc equation

Every equation is parsed from human algebra, rendered to LaTeX, and validated by
symbolic round-trip, so "VALID" is a proof rather than a visual guess. The run
ends by catching a deliberately wrong hand-typed LaTeX - the real selling point.
"""

from __future__ import annotations

import sys

from equations import AML_EQUATIONS, KNOWN_BAD, SYMBOLS
from validator import check_human_latex, validate_equation

GREEN, RED, YEL, DIM, BOLD, RST = (
    "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[1m", "\033[0m",
)


def _mark(status: str) -> str:
    return {"VALID": f"{GREEN}VALID{RST}", "MISMATCH": f"{RED}MISMATCH{RST}"}.get(
        status, f"{YEL}ERROR{RST}"
    )


def main() -> int:
    if len(sys.argv) > 1:
        r = validate_equation("ad-hoc equation", " ".join(sys.argv[1:]), SYMBOLS)
        print(f"\n[{_mark(r.status)}] {r.source}")
        print(f"  latex : {r.latex}")
        print(f"  check : {r.method}")
        if r.error:
            print(f"  {RED}error : {r.error}{RST}")
        return 0 if r.status == "VALID" else 1

    print(f"\n{BOLD}AML equation -> LaTeX -> validation{RST}")
    print("=" * 74)
    n_ok = 0
    for name, src, legend in AML_EQUATIONS:
        r = validate_equation(name, src, SYMBOLS)
        n_ok += r.status == "VALID"
        print(f"\n[{_mark(r.status)}] {BOLD}{name}{RST}")
        print(f"  {DIM}source :{RST} {src}")
        print(f"  {DIM}latex  :{RST} {r.latex}")
        legend_txt = ", ".join(f"{k}={val}" for k, val in legend.items())
        print(f"  {DIM}legend :{RST} {legend_txt}")
        if r.error:
            print(f"  {RED}error  : {r.error}{RST}")
    print("\n" + "=" * 74)
    print(f"{BOLD}{n_ok}/{len(AML_EQUATIONS)} equations validated "
          f"(symbolic round-trip){RST}")

    # The selling point: catch a wrong hand-typed LaTeX.
    print(f"\n{BOLD}Catching a hand-typed error{RST}")
    print("-" * 74)
    print(f"  source           : {KNOWN_BAD['source']}")
    print(f"  hand-typed LaTeX : {KNOWN_BAD['bad_latex']}   {DIM}({KNOWN_BAD['why']}){RST}")
    try:
        ok = check_human_latex(KNOWN_BAD["source"], KNOWN_BAD["bad_latex"], SYMBOLS)
        verdict = (f"{GREEN}passes{RST}" if ok
                   else f"{RED}CAUGHT - flagged as not equivalent{RST}")
    except RuntimeError as exc:
        verdict = f"{YEL}{exc}{RST}"
    print(f"  symbolic verdict : {verdict}")
    print("-" * 74 + "\n")
    return 0 if n_ok == len(AML_EQUATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
