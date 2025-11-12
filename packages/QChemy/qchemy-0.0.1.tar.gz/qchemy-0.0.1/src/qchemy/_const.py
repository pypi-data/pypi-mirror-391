"""Constants used in Qchemy."""


L_TO_LABEL: dict[int, str] = {
    0: "s", 1: "p", 2: "d", 3: "f", 4: "g", 5: "h", 6: "i"
} | dict(
    zip(range(7, 7 + (ord('z') - ord('k') + 1)), map(chr, range(ord('k'), ord('z') + 1)))
)
"""Mapping from azimuthal quantum number `l` to subshell label."""


LABEL_TO_L: dict[str, int] = {v: k for k, v in L_TO_LABEL.items()}
"""Mapping from subshell label to azimuthal quantum number `l`."""


NOBLE_GASES: list[tuple[int, str]] = [
    (2, "He"),
    (10, "Ne"),
    (18, "Ar"),
    (36, "Kr"),
    (54, "Xe"),
    (86, "Rn"),
    (118, "Og"),
]
"""List of noble gases as (number of electrons, symbol) pairs."""
