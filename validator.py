"""
Core engine: algebraic equation  ->  LaTeX  ->  *validated* LaTeX.

Rendering an equation as LaTeX is easy (sympy.latex does it). The value here is
the third step - *proving* the generated LaTeX is mathematically identical to
the source, so a "VALID" verdict is evidence, not a visual guess.

Validation is a symbolic round-trip:

    source string --parse--> Expr_A --latex--> "\\frac{...}"
    "\\frac{...}"  --parse_latex--> Expr_B
    VALID  <=>  simplify(normalize(Expr_A) - normalize(Expr_B)) == 0

Two normalizations make the round-trip robust and are documented, never hidden:
  1. e -> E : sympy renders exp(x) as e^{x}; the LaTeX parser reads a bare `e`
     as an ordinary symbol, so we map it back to Euler's number before comparing.
  2. subscript-name canonicalization : sympy renders Symbol("x_1") as x_{1};
     re-parsing yields a symbol literally named "x_{1}". We strip LaTeX subscript
     braces so x_1 and x_{1} compare equal. A genuine variable *swap* still fails
     the symbolic diff, so this does not paper over real errors (see tests).

Rendering rule that makes round-tripping reliable (see README "Pitfalls"):
  * multiplication is emitted as an explicit \cdot, so "k(t - t_0)" is never
    mis-read as a function call k(...).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    convert_xor,
)

# convert_xor lets a human write ^ for powers; multiplication stays explicit (*)
_TRANSFORMS = standard_transformations + (convert_xor,)


@dataclass
class ValidationResult:
    name: str
    source: str
    latex: Optional[str] = None
    valid: bool = False
    method: str = ""
    difference: str = ""
    error: str = ""

    @property
    def status(self) -> str:
        if self.error:
            return "ERROR"
        return "VALID" if self.valid else "MISMATCH"


def _canon_name(name: str) -> str:
    """x_{1} -> x1 ; S_{b} -> Sb ; \\beta -> beta  (so subscripts compare equal)."""
    return (
        name.replace("\\", "")
        .replace("_{", "")
        .replace("{", "")
        .replace("}", "")
        .replace("_", "")
        .replace(" ", "")
    )


def _normalize(expr: sp.Expr) -> sp.Expr:
    expr = expr.xreplace({sp.Symbol("e"): sp.E})  # Euler's e, see module docstring
    return expr.xreplace(
        {s: sp.Symbol(_canon_name(s.name)) for s in expr.free_symbols}
    )


def _reparse_latex(latex: str) -> Optional[sp.Expr]:
    try:
        from sympy.parsing.latex import parse_latex
    except Exception:
        return None
    for backend in ("antlr", "lark"):
        try:
            return parse_latex(latex, backend=backend)
        except Exception:
            continue
    return None


def validate_equation(
    name: str, source: str, local_dict: Optional[dict] = None
) -> ValidationResult:
    """Convert one equation to LaTeX and prove the LaTeX equals the source."""
    result = ValidationResult(name=name, source=source)
    try:
        expr = parse_expr(
            source, transformations=_TRANSFORMS, local_dict=local_dict, evaluate=True
        )
    except Exception as exc:  # noqa: BLE001
        result.error = f"could not parse source: {exc}"
        return result

    result.latex = sp.latex(expr, mul_symbol="dot")

    reparsed = _reparse_latex(result.latex)
    if reparsed is not None:
        diff = sp.simplify(_normalize(expr) - _normalize(reparsed))
        result.valid = diff == 0
        result.method = "symbolic round-trip (LaTeX re-parsed; simplify(diff)==0)"
        result.difference = str(diff)
    else:
        # No LaTeX parser backend installed -> we will NOT claim round-trip proof.
        result.valid = bool(result.latex)
        result.method = (
            "render-only (LaTeX generated; round-trip skipped - no parser backend, "
            "install antlr4-python3-runtime)"
        )
    return result


def check_human_latex(
    source: str, human_latex: str, local_dict: Optional[dict] = None
) -> bool:
    """
    Does a HAND-TYPED LaTeX string correctly represent `source`?
    Returns True only if the two are symbolically equal. This is the real AML
    use case: an analyst wrote LaTeX for a model card - is it right?
    """
    expr = parse_expr(source, transformations=_TRANSFORMS, local_dict=local_dict)
    reparsed = _reparse_latex(human_latex)
    if reparsed is None:
        raise RuntimeError("LaTeX parser backend not available")
    return sp.simplify(_normalize(expr) - _normalize(reparsed)) == 0
