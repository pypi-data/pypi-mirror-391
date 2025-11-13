from typing import Literal, final


AccessModeLiteral = Literal["r", "r+", "a", "w", "w-"]
"""
mode : {'r', 'r+', 'a', 'w', 'w-'}, optional
    Persistence mode: 'r' means read only (must exist); 'r+' means
    read/write (must exist); 'a' means read/write (create if doesn't
    exist); 'w' means create (overwrite if exists); 'w-' means create
    (fail if exists).
"""


@final
class Attribute:
    EZType = "__ez_type__"
    EZClass = "__ez_class__"


@final
class EZType:
    Object = "object"
    List = "list"


UNKNOWN = "<UNKNWON>"
