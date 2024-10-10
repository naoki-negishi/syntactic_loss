# Standard Library
from typing import TypeAlias, TypeVar
import dataclasses


class PrimitiveCategory:
    _categ: str
    _restriction: set


class FunctionalCategory:
    _categ: str
    _restriction: set
    _feature: dict


Category: TypeAlias = PrimitiveCategory | FunctionalCategory

class CCGLexicon:
    lexicon: dict[str, tuple[Term, Category]] = {
        "John": ("j", "NP"),
        "Mary": ("m", "NP"),
        "runs": (lambda x: f"run({x})", r"S\NP"),
        "walks": (lambda x: f"walk({x})", r"S\NP"),
        "loves": (lambda x: lambda y: f"love({x}, {y})", r"(S\NP)/NP"),
        "finds": (lambda x: lambda y: f"find({x}, {y})", r"(S\NP)/NP"),
        "and": (lambda x: lambda y: f"{x}and{y}", r"(T\T)/T"),
        "or": (lambda x: lambda y: f"{x}or{y}", r"(T\T)/T"),
    }


class CCGrules:
    def __init__(self):
        pass

    def forward_app(self, xy: Callable, y: str) -> Union[Callable]:
        return

    def backward_app(self, x: str, yx: Callable) -> Union[Callable]:
        return

    def conjunction(self, x: str, y: str) -> Union[str]:
        return

    def forward_composition(self, x: str, y: str) -> Union[str]:
        return

    def backward_composition(self, x: str, y: str) -> Union[str]:
        return

    def subject_type_raising(self, x: str) -> Union[str]:
