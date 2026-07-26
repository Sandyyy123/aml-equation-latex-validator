"""
Representative equations from an AML / fraud-detection codebase, written in
publication convention: single-letter symbols + subscripts, with a nomenclature
legend giving each symbol its business meaning. This is the correct way to
typeset model formulas for a methodology appendix, model card, or regulator pack
(you define symbols in a legend; you do not spell "inflow" inside a fraction -
see README "Pitfalls" for why that also breaks LaTeX parsing).

Each entry: (name, human-written algebra, {symbol: meaning}).
"""

import sympy as sp

# Symbols the parser must treat as atomic (single dict reused by the validator).
SYMBOLS = {
    n: sp.Symbol(n)
    for n in [
        "beta_0", "beta_1", "beta_2", "beta_3", "x_1", "x_2", "x_3",
        "w_1", "w_2", "w_3", "r_1", "r_2", "r_3",
        "mu", "sigma", "S_a", "S_b", "k", "t", "t_0",
        "L_0", "L_1", "pi", "v", "m", "s", "epsilon", "f_1", "f_2", "c",
    ]
}

AML_EQUATIONS = [
    (
        "Logistic fraud probability",
        "1 / (1 + exp(-(beta_0 + beta_1*x_1 + beta_2*x_2 + beta_3*x_3)))",
        {
            "beta_0": "model intercept",
            "beta_i": "coefficient on risk feature i",
            "x_i": "standardised risk feature (amount, velocity, geography)",
        },
    ),
    (
        "Weighted customer risk score",
        "(w_1*r_1 + w_2*r_2 + w_3*r_3) / (w_1 + w_2 + w_3)",
        {"w_i": "weight of risk factor i", "r_i": "risk factor i score"},
    ),
    (
        "Transaction anomaly z-score",
        "(x_1 - mu) / sigma",
        {"x_1": "transaction value", "mu": "peer mean", "sigma": "peer std. dev."},
    ),
    (
        "Structuring (smurfing) ratio",
        "S_b / (S_b + S_a)",
        {"S_b": "sum just below reporting threshold", "S_a": "sum above threshold"},
    ),
    (
        "Exponential time-decay weight",
        "exp(-k*(t - t_0))",
        {"k": "decay rate", "t": "current time", "t_0": "event time"},
    ),
    (
        "Bayesian posterior odds of laundering",
        "(pi*L_1) / ((1 - pi)*L_0)",
        {
            "pi": "prior probability of laundering",
            "L_1": "likelihood of the alert given laundering",
            "L_0": "likelihood of the alert given clean",
        },
    ),
    (
        "Peer-group deviation index",
        "(v - m) / (s + epsilon)",
        {"v": "customer value", "m": "peer-group mean", "s": "peer-group std. dev.",
         "epsilon": "small constant to avoid divide-by-zero"},
    ),
    (
        "Velocity rule (turnover over balance)",
        "(f_1 + f_2) / (2*c)",
        {"f_1": "inflow", "f_2": "outflow", "c": "average balance"},
    ),
]

# Used in main.py to show the validator catching a wrong hand-typed LaTeX:
# numerator and denominator of the z-score swapped - the classic slip.
KNOWN_BAD = {
    "source": "(x_1 - mu) / sigma",
    "bad_latex": r"\frac{\sigma}{x_1 - \mu}",
    "why": "numerator / denominator swapped",
}
