"""Constants used in Qchemy."""


L_TO_LABEL: dict[int, str] = {
    0: "s",
    1: "p",
    2: "d",
    3: "f",
    4: "g",
    5: "h",
    6: "i",
    7: "k",
    8: "l",
    9: "m",
    10: "n",
    11: "o",
    12: "q",
    13: "r",
    14: "t",
    15: "u",
    16: "v",
    17: "w",
    18: "x",
    19: "y",
    20: "z",
}
"""Mapping from azimuthal quantum number `l` to subshell label."""


LABEL_TO_L: dict[str, int] = {v: k for k, v in L_TO_LABEL.items()}
"""Mapping from subshell label to azimuthal quantum number `l`."""


NOBLE_GAS_Z_TO_SYMBOL: dict[int, str] = {
    2: "He",
    10: "Ne",
    18: "Ar",
    36: "Kr",
    54: "Xe",
    86: "Rn",
    118: "Og",
}
"""Mapping from noble gas atomic number (also number of electrons) to symbol."""


NOBLE_GAS_SYMBOL_TO_Z: dict[str, int] = {sym: Z for Z, sym in NOBLE_GAS_Z_TO_SYMBOL.items()}
"""Mapping from noble gas symbol to atomic number (also number of electrons)."""
