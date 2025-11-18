"""Atomic term symbols and LS terms."""

from typing import TypeAlias, Sequence
from itertools import combinations

import numpy as np

from qchemy import _const
from qchemy.eleconfig.atom import AtomicElectronConfig, is_partially_filled, hoao, subshell_capacity


# Type Definitions
# ================

Term: TypeAlias = tuple[int, float] | np.ndarray
"""LS term.

An LS term is represented as
a 1D float array `[L, S]` of shape (2,),
containing the total orbital angular momentum quantum number $L >= 0$
(where 0→S, 1→P, 2→D, 3→F, 4→G, 5→H, 6→I, 7→K, ...)
and total spin quantum number $S >= 0$ (e.g., 0, 0.5, 1, 1.5, ...).
The spectroscopic label is ``^{2S+1}L``; fine-structure levels are given by
$J = L+S, L+S-1, ..., |L-S|$.

Examples
--------
- The term ^3P (L=1, S=1) is represented as `[1.0, 1.0]`.
- The term ^2D (L=2, S=0.5) is represented as `[2.0, 0.5]`.
"""

Terms: TypeAlias = Sequence[Term] | np.ndarray
"""Collection of LS terms.

An LS term collection is represented as
a 2D float array of shape `(num_terms, 2)`,
where each row is an LS term as defined in :class:`Term`.
"""


Level: TypeAlias = tuple[int, float, float] | np.ndarray
"""LSJ level.

An LSJ level is represented as
a 1D float array `[L, S, J]` of shape (3,),
containing the $L$, $S$, and total angular momentum quantum number
$J >= 0$ (e.g., 0, 0.5, 1, 1.5, ...).

Examples
--------
- The level ^3P_2 (L=1, S=1, J=2) is represented as `[1.0, 1.0, 2.0]`.
- The level ^2D_3/2 (L=2, S=0.5, J=1.5) is represented as `[2.0, 0.5, 1.5]`.
"""

Levels: TypeAlias = Sequence[Level] | np.ndarray
"""Collection of LSJ levels.

An LSJ level collection is represented as
a 2D float array of shape `(num_levels, 3)`,
where each row is an LSJ level as defined in :class:`Level`.
"""


def from_electron_config(config: AtomicElectronConfig) -> tuple[Terms, np.ndarray]:
    """Enumerate all LS terms for an electron configuration.

    Parameters
    ----------
    config
        Electron configuration.

    Returns
    -------
    terms
        Array of LS terms for the configuration.
        Terms are sorted according to Hund's rules (lowest to highest energy).
    multiplicities
        Array of occurrence multiplicities corresponding to each term.

    Notes
    -----
    Algorithmic outline (no empirical ordering):
    1) For each open subshell ``(n,l)^occ``, enumerate all Pauli-allowed
       microstates and tabulate counts over ``(M_L, M_S)``.
    2) Convolve these distributions across subshells to get the total
       ``(M_L, M_S)`` multiplicity table for the configuration.
    3) Apply the highest-weight **reduction** algorithm to decompose the table
       exactly into LS terms and their multiplicities.

    This yields the mathematically exact set of LS terms under pure LS coupling.
    """
    config = np.asarray(config)

    # Build ML,MS distribution for each open subshell and convolve them
    total = {(0, 0.0): 1}

    # Filter out closed/empty subshells (they contribute identity to convolution)
    is_partial = is_partially_filled(config)
    config_partial = config[is_partial]

    for _, l, k in config_partial:
        dist = _ml_ms_distribution_for_subshell(l, k)
        total = _convolve_ml_ms(total, dist)
    # Reduce the total (ML,MS) multiplicity table into LS terms
    term_map = _reduce_distribution_to_terms(total)
    return hund_sort(np.array(list(term_map.keys())), config=config), np.array(list(term_map.values()))


def hund_sort(
    levels: Terms | Levels,
    config: AtomicElectronConfig,
) -> Levels:
    """Sort terms/levels according to Hund's rules.

    The function assumes pure LS coupling and does not consider inter-subshell coupling.

    Parameters
    ----------
    levels
        Terms/levels to sort.
    config
        Electron configuration corresponding to the terms/levels.

    Returns
    -------
    Terms/levels sorted from *lowest* to *highest* energy according to Hund's rules.

    Notes
    -----
    Hund's rules for a single open subshell state that for a given electron configuration:
    1. Terms with **larger total spin $S$** (or larger multiplicity 2S+1) lie lower.
    2. For terms of equal $S$, terms with larger $L$ lie lower.
    3. Within a given term,
       - If the atom's outermost subshell is **half-filled or less**, then levels with smaller $J$ lie lower.
       - If the atom's outermost subshell is **more than half-filled**, then levels with larger $J$ lie lower.
    """
    levels = np.asarray(levels)
    L = levels[:, 0]
    S = levels[:, 1]
    if levels.shape[1] == 2:
        sort_keys = (
            # Rule 2: descending L
            -L,
            # Rule 1: descending S
            -S,
        )
    else:
        outermost_shell = hoao(config)
        if outermost_shell is None:
            half_filled_or_less = True
        else:
            _, l, k = outermost_shell
            hoao_half_capacity = subshell_capacity(l) / 2
            half_filled_or_less = k <= hoao_half_capacity

        J = levels[:, 2]
        sort_keys = (
            # Rule 3: J ordering flips depending on filling
            J if half_filled_or_less else -J,
            # Rule 2: descending L
            -L,
            # Rule 1: descending S
            -S,
        )
    order = np.lexsort(sort_keys)
    return levels[order]


def term_to_levels(term: Term | Terms) -> Levels:
    """Generate all possible LSJ levels for given LS term(s).

    Parameters
    ----------
    terms
        LS term(s).

    Returns
    -------
    Levels
        All possible LSJ levels for the input term(s).
    """
    term = np.asarray(term).reshape(-1, 2)
    level_list: list[np.ndarray] = []
    for L, S in term:
        jmax = L + S
        jmin = abs(L - S)
        n = int(round((jmax - jmin) / 1.0)) + 1
        levels = np.empty((n, 3), dtype=float)
        levels[:, 0] = L
        levels[:, 1] = S
        levels[:, 2] = np.array([jmax - i for i in range(n)], dtype=float)
        level_list.append(levels)
    return np.vstack(level_list)


def to_latex(
    term: Term | Terms | Level | Levels,
    *,
    term_template: str = r"$\textsuperscript{{{M}}}{L}$",
    term_template_high_l: str = r"$\textsuperscript{{{M}}}({L})$",
    level_template: str = r"$\textsuperscript{{{M}}}{L}_{{{J}}}$",
    level_template_high_l: str = r"$\textsuperscript{{{M}}}({L})_{{{J}}}$",
) -> str | list[str]:
    """Convert term(s) or level(s) to LaTeX string(s).

    Parameters
    ----------
    term
        LS term(s) or LSJ level(s).
    term_template
        Template string for formatting terms with standard L labels (L ≤ 22).
        The string should contain placeholders `{M}` for multiplicity and `{L}` for the L label.
    term_template_high_l
        Template string for formatting terms with high L labels (L > 22).
        The string should contain placeholders `{M}` for multiplicity and `{L}` for the L label.
    level_template
        Template string for formatting levels with standard L labels (L ≤ 22).
        The string should contain placeholders `{M}`, `{L}`, and `{J}`.

    Returns
    -------
    LaTeX representation of the spectroscopic term label, e.g. ``'^3P_2'``.
    For multiple terms/levels, a list of strings is returned.
    """
    terms = np.asarray(term)
    single_input = False
    if terms.ndim == 1:
        terms = terms.reshape(1, -1)
        single_input = True
    out: list[str] = []
    for entry in terms:
        L = int(entry[0])
        S = entry[1]
        M = int(2 * S + 1)
        L_label = _const.L_TO_LABEL.get(L)
        if L_label is None:
            L_label = L
            templ_term = term_template_high_l
            templ_level = level_template_high_l
        else:
            L_label = L_label.upper()
            templ_term = term_template
            templ_level = level_template
        if entry.shape[0] == 2:
            # Term
            entry_str = templ_term.format(M=M, L=L_label)
        elif entry.shape[0] == 3:
            # Level
            J = entry[2]
            J_as_int_or_frac = (
                f"{int(J)}" if J.is_integer() else f"{int(2 * J)}/2"
            )
            entry_str = templ_level.format(M=M, L=L_label, J=J_as_int_or_frac)
        else:
            raise ValueError("Each term/level must have shape (2,) or (3,).")
        out.append(entry_str)
    if single_input:
        return out[0]
    return out


# Private Functions
# =================
# Parsing, microstate enumeration, convolution, and reduction.


def _ml_ms_distribution_for_subshell(l: int, n: int) -> dict[tuple[int, float], int]:
    """Enumerate ML,MS multiplicities for a single subshell ``l^n``.

    Parameters
    ----------
    l
        Subshell orbital quantum number (0→s, 1→p, 2→d, 3→f, ...).
    n
        Number of electrons in the subshell (0..``2(2l+1)``).

    Returns
    -------
    dict
        Multiplicity table mapping ``(M_L, M_S) -> count`` produced by all
        Pauli-allowed microstates of the subshell.

    Notes
    -----
    - Enumerates all distinct sets of ``n`` spin-orbitals from the available
      ``(2l+1)×2`` orbitals ``(m_l, m_s)`` with ``m_l∈{-l,...,+l}`` and
      ``m_s∈{-1/2,+1/2}``.
    - This is exact and enforces Pauli automatically via combinations.
    - Complexity grows like ``C(2(2l+1), n)``; manageable for typical atomic
      cases (e.g., ``f^7`` → ``C(14,7)=3432`` microstates before aggregation).
    """
    assert 0 <= n <= 2 * (2 * l + 1)
    orbitals: list[tuple[int, float]] = []
    for ml in range(-l, l + 1):
        orbitals.append((ml, -0.5))
        orbitals.append((ml, +0.5))

    counts: dict[tuple[int, float], int] = {}
    for combo in combinations(orbitals, n):
        ML = sum(o[0] for o in combo)
        MS = float(sum(o[1] for o in combo))
        key = (ML, MS)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _convolve_ml_ms(
    a: dict[tuple[int, float], int],
    b: dict[tuple[int, float], int],
) -> dict[tuple[int, float], int]:
    """Convolve two (M_L, M_S) multiplicity tables.

    Parameters
    ----------
    a, b
        Dictionaries mapping ``(M_L, M_S)`` to counts. The result corresponds to
        adding angular momentum projections from independent subshells.

    Returns
    -------
    dict
        Convolved multiplicity table.
    """
    out: dict[tuple[int, float], int] = {}
    for (ML1, MS1), c1 in a.items():
        for (ML2, MS2), c2 in b.items():
            key = (ML1 + ML2, float(MS1 + MS2))
            out[key] = out.get(key, 0) + c1 * c2
    return out


def _reduce_distribution_to_terms(counts: dict[tuple[int, float], int]) -> dict[tuple[int, float], int]:
    """Decompose a (M_L, M_S) table exactly into LS terms via highest-weights.

    Parameters
    ----------
    counts
        Multiplicity table mapping ``(M_L, M_S)`` to nonnegative integers.

    Returns
    -------
    Mapping from `(L, S)` to its occurrence multiplicity in the LS
    decomposition for the configuration.

    Notes
    -----
    This performs the standard highest-weight subtraction algorithm:
    1. repeatedly pick the largest existing ``M_L``; within it the largest existing ``M_S``.
    2. Assign the LS irrep with ``L=M_L_max`` and ``S=M_S_max``, then
       subtract one copy of its rectangle pattern over all ``M_L∈[-L..L]`` and ``M_S∈[-S..S]``.
    3. When the table is zero everywhere, the reduction is done.
    """
    # Make a mutable copy
    table: dict[tuple[int, float], int] = {k: int(v) for k, v in counts.items() if v}
    terms: dict[tuple[int, float], int] = {}

    def has_entries() -> bool:
        return any(v > 0 for v in table.values())

    while has_entries():
        # Find maximum ML, then maximum MS at that ML with positive count
        ML_candidates = [ML for (ML, _), c in table.items() if c > 0]
        ML_max = max(ML_candidates)
        MS_candidates = [MS for (ML, MS), c in table.items() if c > 0 and ML == ML_max]
        MS_max = max(MS_candidates)

        L = int(ML_max)
        S = float(MS_max)
        # Subtract the rectangle pattern once
        for ML in range(-L, L + 1):
            for k in range(int(2 * S) + 1):
                MS = -S + k
                key = (ML, float(MS))
                if table.get(key, 0) <= 0:
                    raise RuntimeError(
                        "Inconsistent (M_L,M_S) table during reduction; cannot subtract term pattern."
                    )
                table[key] = table.get(key, 0) - 1
                if table[key] == 0:
                    del table[key]
        terms[(L, S)] = terms.get((L, S), 0) + 1

    return terms
