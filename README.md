# AML Equation → LaTeX → Validation

A small, runnable demo for the task: **translate algebraic equations from an
AML / fraud codebase into LaTeX, and *validate* that the LaTeX is correct.**

The point is the third step. Rendering an equation as LaTeX is a one-liner
(`sympy.latex`). Proving the LaTeX means the same thing as the source equation
is where errors hide, and where this tool earns its place.

```
python3 main.py                     # validate the built-in AML equation set
python3 main.py "(x_1 - mu)/sigma"  # validate one ad-hoc equation
```

## How validation works

A symbolic **round-trip**, not a visual proofread:

```
source string ──parse──▶ Expr_A ──latex──▶ "\frac{...}"
"\frac{...}"  ──parse_latex──▶ Expr_B
VALID  ⇔  simplify( normalize(Expr_A) − normalize(Expr_B) ) == 0
```

If the generated LaTeX is re-parsed to a different expression, the symbolic
difference is non-zero and the equation is flagged. `main.py` ends by feeding in
a **wrong** hand-typed z-score LaTeX (numerator/denominator swapped) and shows it
being caught — that is the real use case: an analyst wrote LaTeX for a model
card, is it right?

Two normalizations are applied and **documented, never hidden**:

1. `e → E` — sympy renders `exp(x)` as `e^{x}`; a LaTeX parser reads a bare `e`
   as an ordinary symbol, so we map it back to Euler's number before comparing.
2. subscript canonicalization — `Symbol("x_1")` renders as `x_{1}` and re-parses
   as a symbol literally named `x_{1}`; we strip the LaTeX braces so they compare
   equal. A genuine **variable swap still fails** the check, so this does not mask
   real errors.

## Pitfalls this surfaces (the advisory layer)

Naive "just re-parse the LaTeX" validation has real, enumerable failure modes.
This demo renders around them, and they are worth knowing before wiring this into
a codebase:

| Pitfall | What breaks | Fix used here |
|---|---|---|
| Multi-letter names in math mode | `inflow` → `i·n·f·l·o·w` (six-way product) | single-letter symbols + subscripts, with a nomenclature legend; wrap true words in `\mathrm{}` |
| Multi-letter **subscripts** | `f_{in}` → `f_{i·n}` | single-token subscripts (`f_1`, `f_2`) |
| `X\left(...\right)` adjacency | `k(t−t₀)` read as *function call* `k(...)`, `k` vanishes | render multiplication as explicit `\cdot` |
| `exp` vs `e^{}` | bare `e` parsed as a symbol, not Euler's number | `e → E` normalization |

The takeaway for the codebase: equations should be authored with a **controlled
symbol vocabulary + a legend**, which is both the correct publication convention
and what makes automated validation reliable.

## Files

- `validator.py` — parse → LaTeX → round-trip validation + `check_human_latex()`
- `equations.py` — the AML equation set with per-symbol nomenclature legends
- `main.py` — CLI report + the catch-a-wrong-LaTeX demo

## Install

```
pip install -r requirements.txt
```

`sympy` alone runs the tool (render-only mode). `antlr4-python3-runtime` enables
the full symbolic round-trip; the tool degrades gracefully and states which mode
it ran in rather than claiming a proof it did not perform.

---
Demo built for an Upwork AML equation-to-LaTeX engagement · Dr. Sandeep Grover
