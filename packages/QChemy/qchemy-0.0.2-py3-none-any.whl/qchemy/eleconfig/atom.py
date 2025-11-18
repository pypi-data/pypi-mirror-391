"""Atomic electron configuration calculations.

This module provides functions for working with
atomic electron configurations, subshells, and related concepts.
"""

from typing import TypeAlias, Sequence, Callable
import re

import numpy as np

from qchemy import _const


# Type Definitions
# ================

AtomicSubshell: TypeAlias = tuple[int, int] | np.ndarray
"""Atomic subshell.

An atomic subshell is represented as
a 1D integer array `[n, l]` of shape `(2,)`,
containing the principal quantum number $n >= 1$
and azimuthal quantum number $0 <= l < n$
of the subshell.

Examples
--------
- The 1s subshell is represented as [1, 0].
- The 2p subshell is represented as [2, 1].
- The 3d subshell is represented as [3, 2].
"""


AtomicSubshellSequence: TypeAlias = Sequence[AtomicSubshell] | np.ndarray
"""Sequence of atomic subshells.

An atomic subshell sequence is represented as
a 2D integer array of shape `(num_subshells, 2)`,
containing atomic subshells `[n, l]`.

Examples
--------
- The sequence for the 1s, 2p, and 3d subshells is represented as:
  [[1, 0], [2, 1], [3, 2]].
"""


AtomicSubshellElectronConfig: TypeAlias = Sequence[tuple[int, int, int]] | np.ndarray
"""Atomic subshell with electron count.

An atomic subshell with electron count is represented as
a 1D integer array `[n, l, k]` of shape `(3,)`,
containing subshell quantum numbers `[n, l]` and
the number of electrons `k` in that subshell,
i.e., an `AtomicSubshell` plus its corresponding electron count.

Examples
--------
- The 1s subshell with 2 electrons is represented as [1, 0, 2].
- The 2p subshell with 6 electrons is represented as [2, 1, 6].
- The 3d subshell with 10 electrons is represented as [3, 2, 10].
"""


AtomicElectronConfig: TypeAlias = Sequence[AtomicSubshellElectronConfig] | np.ndarray
"""Atomic electron configuration.

An electron configuration is represented as
a 2D array of shape `(num_subshells, 3)`,
containing atomic subshells with electron counts `[n, l, k]`.

Examples
--------
- A configuration for carbon (1s² 2s² 2p²) is represented as:
  [(1, 0, 2), (2, 0, 2), (2, 1, 2)]
- A configuration for neon (1s² 2s² 2p⁶) is represented as:
  [(1, 0, 2), (2, 0, 2), (2, 1, 6)]
"""


# Caches
# ======

_cache_noble_gas_config: dict[int, AtomicElectronConfig] = {}
"""Cache of noble gas ground-state electron configurations.

Keys are atomic numbers (number of electrons),
values are the corresponding electron configurations.
"""


# Public Functions
# =================

def ground_state_aufbau(n_electrons: int) -> AtomicElectronConfig:
    """Get the ground state electron configuration for a given number of electrons.

    This implementation follows the aufbau (Madelung) scheme strictly;
    it does **not** encode known anomalies (e.g., Cr, Cu, Nb, Mo)
    where energetic near-degeneracies cause deviations from naive aufbau order.
    For purposes that only rely on subshell electron counts (not fine structure),
    this is typically sufficient.

    Parameters
    ----------
    n_electrons
        The total number of electrons (Z for a neutral atom).

    Returns
    -------
    Ground state electron configuration for the given number of electrons.
    The subshells are ordered according to the aufbau (Madelung) principle.
    If `n_electrons` is zero, returns an empty array with shape `(0, 3)`.

    Raises
    ------
    ValueError
        If `n_electrons` is negative.
    """
    if n_electrons < 0:
        raise ValueError("n_electrons must be non-negative.")
    if n_electrons == 0:
        return np.array([], dtype=int).reshape(0, 3)

    # Grow the sequence bound until capacity covers all electrons
    max_n_plus_l = 1
    total_capacity = 0
    while total_capacity < n_electrons:
        total_capacity = 0
        for n, l in aufbau_sequence(max_n_plus_l):
            total_capacity += subshell_capacity(l)
        max_n_plus_l += 1

    # Fill subshells
    config: list[tuple[int, int, int]] = []  # (n, l, k)
    remaining = n_electrons
    for n, l in aufbau_sequence(max_n_plus_l):
        if remaining <= 0:
            break
        cap = subshell_capacity(l)
        put = min(cap, remaining)
        if put > 0:
            config.append((n, l, put))
            remaining -= put

    return np.array(config, dtype=int)


def from_string(
    config: str,
    aufbau_order: bool = True,
    *,
    regex_ng: str = r"^\s*\[\s*([A-Za-z]{1,2})\s*\]",
    regex_config: str = r"""
        (?P<n>\d+)
        (?P<l>[spdfghiklmnopqrstuvwxyzSPDFGHIKLMNOPQRSTUVWXYZ])
        (?:
            \^\{\s*(?P<k_braced>\d+)\s*\}   # ^{k}
        | \^(?P<k_hat>\d+)                  # ^k
        | (?P<k_plain>\d+)                  # k
        )
    """
) -> AtomicElectronConfig:
    """Parse an electron configuration string.

    Parameters
    ----------
    config
        Electron configuration string.
        Handles:
        - Plain tokens: ``1s2 2s2 2p6``
        - Superscripts: ``2p^6``, ``2p^{6}``
        - Noble-gas abbreviations: ``[He] 2s2 2p5``, ``[Ne]3s^{2}3p^{5}``
        - Light LaTeX wrappers: ``$\\mathrm{[Ne] 3s^{2} 3p^{5}}$``
    aufbau_order
        Whether to return the resulting configuration in aufbau order.
        If False, the order of subshells follows their appearance
        in the input string.
    regex_ng
        Regular expression pattern to identify a leading noble-gas core.
        The pattern must contain one capturing group for the noble gas symbol.
    regex_config
        Regular expression pattern to parse each subshell token.
        The pattern must contain three named capturing groups that start with:
        - `n`: Principal quantum number (integer).
        - `l`: Subshell letter (string).
        - `k`: Number of electrons (integer).
        You can use multiple named groups for each component
        (e.g., `k_braced`, `k_hat`, `k_plain`);
        the first non-empty group found will be used.

    Returns
    -------
    Electron configuration as an `AtomicElectronConfig` array.

    Raises
    ------
    ValueError
        If a token is malformed, references an unknown subshell letter,
        or the resulting configuration violates capacity/quantum rules.

    Notes
    -----
    - If a leading noble-gas core is present, it is expanded using
      `ground_state_aufbau` and then the remainder tokens are added on top.
    - If a token repeats a subshell, electron counts are **added**.
    - Final validation ensures ``0 ≤ k ≤ 2(2l+1)``.
    """
    def _get_first_group(prefix: str):
        for group_label, group_value in token.items():
            if group_label.startswith(prefix) and group_value:
                return group_value
        raise ValueError(f"No group starting with prefix '{prefix}' found in token: {token}")

    s = _normalize_config_string(config)
    if not s:
        return np.array([], dtype=int).reshape(0, 3)

    # Seed with noble-gas core if present
    base: dict[tuple[int, int], int] = {}
    m = re.match(regex_ng, s)
    if m:
        ng_symbol = m.group(1)
        if ng_symbol not in _const.NOBLE_GAS_SYMBOL_TO_Z:
            raise ValueError(f"Unknown noble gas symbol: [{ng_symbol}]")
        ng_z = _const.NOBLE_GAS_SYMBOL_TO_Z[ng_symbol]
        ng_econfig = _cache_noble_gas_config.get(ng_z)
        if ng_econfig is None:
            ng_econfig = ground_state_aufbau(ng_z)
            _cache_noble_gas_config[ng_z] = ng_econfig
        for n, l, k in ng_econfig:
            base[(int(n), int(l))] = base.get((int(n), int(l)), 0) + int(k)
        s = s[m.end():].lstrip()  # strip the prefix and any following spaces

    # Parse the rest of the orbital tokens
    regex_config = re.compile(regex_config, re.VERBOSE if '\n' in regex_config else 0)
    pos = 0
    while pos < len(s):
        # skip whitespace
        while pos < len(s) and s[pos].isspace():
            pos += 1
        if pos >= len(s):
            break
        m = regex_config.match(s, pos)
        if not m:
            raise ValueError(f"Invalid token near: '{s[pos:pos+16]}'")
        token = m.groupdict()
        n = int(_get_first_group("n"))
        letter = _get_first_group("l").lower()
        if letter not in _const.LABEL_TO_L:
            raise ValueError(f"Unsupported subshell letter in token: {s[pos:m.end()]}")
        l = _const.LABEL_TO_L[letter]
        k = int(_get_first_group("k"))
        base[(n, l)] = base.get((n, l), 0) + k
        pos = m.end()

    # Build array and validate
    if not base:
        return np.array([], dtype=int).reshape(0, 3)

    arr = np.array([[n, l, k] for (n, l), k in base.items()], dtype=int)
    # Validate quantum numbers and capacities
    invalid = is_invalid(arr)
    if np.any(invalid):
        raise ValueError(
            f"Parsed configuration is invalid: violates n/l/k constraints "
            f"at indices {np.where(invalid)[0]}: {arr}"
        )

    return aufbau_sort(arr) if aufbau_order else arr


def aufbau_sequence(max_nl: int) -> AtomicSubshellSequence:
    """Generate subshells ordered by the aufbau (Madelung) rule.

    Parameters
    ----------
    max_nl
        Upper bound for $(n + l)$.

    Returns
    -------
    Subshell quantum numbers `[n, l]` in aufbau order,
    for all subshells with
    $n >= 1$, $0 <= l < n$, and $(n + l) <= max_{nl}$.

    Notes
    ------
    According to the [aufbau principle](https://en.wikipedia.org/wiki/Aufbau_principle):
    1. Subshells are filled in the order of increasing $n + l$.
    2. Where two subshells have the same value of $n + l$,
       they are filled in order of increasing $n$.

    Example
    -------
    >>> aufbau_sequence(5)
    array([[1, 0],   # 1s
           [2, 0],   # 2s
           [2, 1],   # 2p
           [3, 0],   # 3s
           [3, 1],   # 3p
           [4, 0],   # 4s
           [3, 2],   # 3d
           [4, 1],   # 4p
           [5, 0]])  # 5s
    >>> aufbau_sequence(9)
    array([[1, 0],   # 1s
           [2, 0],   # 2s
           [2, 1],   # 2p
           [3, 0],   # 3s
           [3, 1],   # 3p
           [4, 0],   # 4s
           [3, 2],   # 3d
           [4, 1],   # 4p
           [5, 0],   # 5s
           [4, 2],   # 4d
           [5, 1],   # 5p
           [6, 0],   # 6s
           [4, 3],   # 4f
           [5, 2],   # 5d
           [6, 1],   # 6p
           [7, 0],   # 7s
           [5, 3],   # 5f
           [6, 2],   # 6d
           [7, 1],   # 7p
           [8, 0],   # 8s
           [5, 4],   # 5g
           [6, 3],   # 6f
           [7, 2],   # 7d
           [8, 1],   # 8p
           [9, 0]])  # 9s
    """
    out = []
    for n_plus_l in range(1, max_nl + 1):
        for n in range(1, n_plus_l + 1):
            l = n_plus_l - n
            if 0 <= l < n:
                out.append([n, l])
    return np.array(out, dtype=int)


def aufbau_sort(subshells: AtomicSubshellSequence | AtomicElectronConfig) -> AtomicSubshellSequence | AtomicElectronConfig:
    """Sort subshells according to the aufbau (Madelung) rule.

    Parameters
    ----------
    subshells
        2D integer array of shape `(num_subshells, num_values >= 2)`,
        containing the `(n, l)` value pairs of subshells to sort.
        The first two columns are used for sorting; any additional columns
        (e.g., electron counts when the input is electron configuration)
        are ignored.

    Returns
    -------
        2D integer array of shape `(num_subshells, num_values)`,
        containing the input subshells sorted in aufbau order.

    Notes
    ------
    - Ordering follows the Madelung rule: subshells are ranked by increasing
      (n + l); ties are broken by increasing n.
    - This function preserves the input subshells but returns them in
      aufbau order.

    Examples
    --------
    >>> subshells = np.array([[3, 2],   # 3d
    ...                       [2, 1],   # 2p
    ...                       [4, 0],   # 4s
    ...                       [3, 1],   # 3p
    ...                       [2, 0]])  # 2s
    >>> aufbau_sort(subshells)
    array([[2, 0],   # 2s
           [2, 1],   # 2p
           [3, 1],   # 3p
           [4, 0],   # 4s
           [3, 2]])  # 3d
    >>> electron_config = np.array([[3, 2, 5],   # 3d5
    ...                             [2, 1, 6],   # 2p6
    ...                             [4, 0, 2],   # 4s2
    ...                             [3, 1, 0],   # 3p0
    ...                             [2, 0, 2]])  # 2s2
    >>> aufbau_sort(electron_config)
    array([[2, 0, 2],   # 2s2
           [2, 1, 6],   # 2p6
           [3, 1, 0],   # 3p0
           [4, 0, 2],   # 4s2
           [3, 2, 5]])  # 3d5
    """
    subshells = np.asarray(subshells)
    if subshells.ndim != 2 or subshells.shape[1] < 2:
        raise ValueError("subshells must be a 2D array with at least two columns (n, l).")
    n = subshells[:, 0]
    l = subshells[:, 1]
    order = np.lexsort((n, n + l))  # last key is primary
    return subshells[order]


def hoao(
    config: AtomicElectronConfig,
    prefer_partial: bool = True
) -> AtomicSubshellElectronConfig | None:
    """Get the highest occupied atomic orbital (HOAO) of an electron configuration.

    This function selects the occupied subshell with the highest order
    according to the aufbau (Madelung) principle,
    i.e., the subshell of interest for Hund's rules.

    Parameters
    ----------
    config
        Atomic electron configuration.
    prefer_partial
        Prefer a partially filled subshell over a fully
        occupied one with the same or higher order, if available.
        If False, ignore partiality and just return the
        highest-energy occupied subshell by Madelung order.

    Returns
    -------
    Atomic subshell `(n, l, k)` representing the HOAO,
    or ``None`` if no electrons are present.

    Notes
    -----
    - In standard aufbau ground states, there is at most one partially filled
    subshell; this method also behaves sensibly for arbitrary user-provided
    configurations with multiple open subshells.
    """
    config = np.asarray(config)
    l = config[:, 1]
    k = config[:, 2]
    is_occupied = k > 0
    if prefer_partial:
        is_partially_filled = np.logical_and(is_occupied, k < subshell_capacity(l))
        partial_subshells = config[is_partially_filled]
        if partial_subshells.size > 0:
            return aufbau_sort(partial_subshells)[-1]

    # Any occupied subshell (including closed)
    occupied_subshells = config[is_occupied]
    return None if occupied_subshells.size == 0 else aufbau_sort(occupied_subshells)[-1]


def is_invalid(config: AtomicSubshell | AtomicSubshellSequence | AtomicElectronConfig) -> bool | np.ndarray:
    r"""Check if the given subshell(s) or electron configuration is invalid.

    This function checks:
    - $n \geq 1$
    - $0 \leq l < n$
    - $0 \leq k \leq 2(2l + 1)$
    A subshell or configuration is considered invalid
    if any of the above conditions are violated.

    Parameters
    ----------
    config
        An atomic subshell `(n, l)`,
        a sequence of atomic subshells `[(n1, l1), (n2, l2), ...]`,
        or an electron configuration `[(n1, l1, k1), (n2, l2, k2), ...]`.

    Returns
    -------
    True if the configuration is invalid, False otherwise.
    If the input is a sequence of subshells or an electron configuration,
    an array of booleans is returned, indicating the invalidity of each
    subshell or configuration.
    """
    config = np.asarray(config)
    single_input = False
    if config.ndim == 1:
        config = config[np.newaxis, :]  # Make it 2D for uniform processing
        single_input = True

    n = config[:, 0]
    l = config[:, 1]

    invalid_n = n < 1
    invalid_l = (l < 0) | (l >= n)
    invalid = invalid_n | invalid_l
    if config.shape[1] > 2:
        # Electron configuration: (n, l, k)
        k = config[:, 2]
        capacity = subshell_capacity(l)
        invalid_k = (k < 0) | (k > capacity)
        invalid = invalid | invalid_k

    return invalid[0] if single_input else invalid


def is_partially_filled(config: AtomicElectronConfig) -> np.ndarray:
    """Check which subshells are partially filled.

    Parameters
    ----------
    config
        Atomic electron configuration.

    Returns
    -------
    A boolean array indicating which subshells are partially filled,
    i.e., those with 0 < k < 2(2l+1).
    """
    config = np.asarray(config)
    l = config[:, 1]
    k = config[:, 2]
    return np.logical_and(k > 0, k < subshell_capacity(l))


def is_subset(
    sub_config: AtomicElectronConfig,
    super_config: AtomicElectronConfig
) -> tuple[bool, AtomicElectronConfig]:
    """Check if one electron configuration is a subset of another.

    Parameters
    ----------
    sub_config
        Potential subset electron configuration.
    super_config
        Potential superset electron configuration.

    Returns
    -------
    is_subset
        True if `sub_config` is a subset of `super_config`, False otherwise.
    super_extras
        Remaining electron configuration,
        i.e., the subshells and electron counts
        that are in `super_config` but not in `sub_config`.
        If `sub_config` is not a subset of `super_config`,
        this will contain all subshells from `super_config`.

    Notes
    -----
    A configuration A is a subset of configuration B if,
    for every subshell in A, the number of electrons in that subshell
    is equal to the number of electrons in the same subshell in B.
    """
    sub_config = np.asarray(sub_config)
    super_config = np.asarray(super_config)
    # Convert rows (i.e. subshells) to structured arrays
    # so that each row can be compared as a single element
    sub_view = sub_config.view([('', sub_config.dtype)] * sub_config.shape[1])
    super_view = super_config.view([('', super_config.dtype)] * super_config.shape[1])

    # Use NumPy's set operations on rows
    is_subset = np.isin(sub_view, super_view).all()
    super_extras = np.setdiff1d(super_view, sub_view)

    # Convert structured array back to plain ndarray (handle empty result cleanly)
    super_extras = super_extras.view(sub_config.dtype).reshape(-1, sub_config.shape[1])
    return is_subset, super_extras


def subshell_capacity(l: int | np.ndarray) -> int | np.ndarray:
    """Get the maximum number of electrons allowed in a subshell.

    Parameters
    ----------
    l
        Azimuthal quantum number(s) of the subshell(s).

    Returns
    -------
        Electron capacity 2(2l + 1) for the given l value(s).

    Notes
    -----
    - This function can accept both scalar and array-like inputs for `l`.
    - The output will match the input shape, with the capacity calculated for each subshell.

    Examples
    --------
    >>> subshell_capacity(0)
    2
    >>> subshell_capacity(1)
    6
    >>> subshell_capacity(np.array([0, 1, 2]))
    array([ 2,  6, 10])
    >>> subshell_capacity(np.array([[0, 1], [2, 3]]))
    array([[ 2,  6],
           [10, 14]])
    """
    return 2 * (2 * l + 1)


def to_latex(
    config: AtomicElectronConfig,
    abbreviate: bool = True,
    *,
    template: str = "{n}{l}^{k}",
    template_high_l: str = "{n}({l})^{k}",
    assembler: Callable[[str | None, list[str]], str] | None = None,
    empty: str = "",
) -> str:
    """Get the atomic electron configuration in LaTeX format.

    Parameters
    ----------
    config
        Atomic electron configuration.
    abbreviate
        Whether to abbreviate the configuration using noble gas notation
        when possible (e.g., ``[Ne]3s^2 3p^5``).
    template
        Template string for formatting each subshell.
        The string should contain placeholders `{n}`, `{l}`, and `{k}`.
    assembler
        Function to assemble the final LaTeX string.
        It takes two arguments:
        1. The noble gas symbol (or `None` if not abbreviated).
        2. A list of formatted subshell strings.
        If `None`, a default assembler is used.
    empty
        String to return for an empty configuration (zero electrons).

    Returns
    -------
    LaTeX representation of the electronic configuration.

    Notes
    -----
    - Output uses conventional aufbau ordering.
    - Abbreviation attempts to remove a noble-gas core only when the noble
      gas ground-state configuration is a subshell-wise subset of this
      configuration.
    """
    def _default_assembler(ng: str | None, parts: list[str]) -> str:
        tail = r"\,".join(parts)
        if ng is None:
            return rf"$\mathrm{{{tail}}}$"
        return rf"$\mathrm{{[{ng}] {tail}}}$"

    # Build full (non-abbreviated) string in aufbau order
    def _fmt(ng: str | None, cfg: np.ndarray) -> str:
        parts: list[str] = []
        occupied = cfg[cfg[:, 2] > 0]
        for n, l, k in aufbau_sort(occupied):
            l_label = _const.L_TO_LABEL.get(l)
            templ = template_high_l if l_label else template
            part = templ.format(n=n, l=l_label or l, k=k)
            parts.append(part)
        assembler_fn = assembler or _default_assembler
        return assembler_fn(ng, parts)

    config = np.asarray(config)
    n_electrons = np.sum(config[:, 2]) if config.size > 0 else 0
    if n_electrons == 0:
        return empty
    if not abbreviate:
        return _fmt(None, config)

    # Try noble-gas abbreviation
    eligible = {z: ng for z, ng in _const.NOBLE_GAS_Z_TO_SYMBOL.items() if z < n_electrons}
    if not eligible:
        return _fmt(None, config)

    # Precompute noble-gas core configurations via ground_state
    for ng_z, ng_symbol in reversed(eligible.items()):
        ng_config = _cache_noble_gas_config.get(ng_z)
        if ng_config is None:
            ng_config = ground_state_aufbau(ng_z)
            _cache_noble_gas_config[ng_z] = ng_config
        # Check subset: every subshell count in core <= this config
        is_sub, extras = is_subset(ng_config, config)
        if is_sub:
            return _fmt(ng_symbol, extras)
    # If no suitable noble gas core found, return full
    return _fmt(None, config)


# Private Functions
# =================


def _normalize_config_string(s: str) -> str:
    """Normalize a configuration string by stripping light LaTeX and spacing.

    Removes surrounding `$...$`, unwraps a single outer `\\mathrm{...}`,
    replaces thin spaces (`\\,`, `\\;`, `\\:`) with a normal space, and
    collapses multiple spaces. Does not attempt to fully parse LaTeX.
    """
    s = s.strip()
    if s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    # unwrap a single outer \mathrm{...}
    if s.startswith(r"\mathrm{") and s.endswith("}"):
        s = s[len(r"\mathrm{"):-1].strip()
    # normalize thin spaces and commas-as-separators
    s = (s
         .replace(r"\,", " ")
         .replace(r"\;", " ")
         .replace(r"\:", " ")
         .replace(",", " "))
    # collapse whitespace
    s = " ".join(s.split())
    return s
