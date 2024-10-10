# Standard Library
import re

# Third Party Library
import nltk
from loguru import logger


def raw_tags_to_tuple(c: str) -> tuple[str]:
    CCG_grammar = nltk.CFG.fromstring(
        R"""
        S -> A '/' A | A '\' A | A
        A -> 'np' | 's' | '(' S ')'
        """
    )
    parser = nltk.ChartParser(CCG_grammar)

    def to_touple(tokens: tuple):
        if tokens[0] == "(" and tokens[-1] == ")":
            tokens = tokens[1:-1]

        trees = list(parser.parse(tokens))
        if len(trees) > 1:
            logger.warning("Multiple trees")
        tokens = trees[0]

        if len(tokens) == 1:
            # logger.debug(f"return: {tokens.leaves()[0]}")
            return tokens.leaves()[0]
        elif len(tokens) == 3:
            lhs, op, rhs = tokens
            # print(f"lhs: {lhs}, op: {op}, rhs: {rhs}")
            # print(f"lhs.leaves: {lhs.leaves()}, rhs.leaves: {rhs.leaves()}")
            # logger.debug(
            #     f"return: {to_touple(lhs.leaves())}, {op}, {to_touple(rhs.leaves())}"
            # )
            return (to_touple(lhs.leaves()), op, to_touple(rhs.leaves()))
        else:
            raise ValueError(f"Invalid tokens: {tokens}")

    pattern = r"([/()\\])"
    tokens = re.split(pattern, c)
    tokens = [x for x in tokens if x]
    # logger.debug(f"input: {c}, tokens: {tokens}")

    return to_touple(tokens)


def tuple_to_raw_tags(t: str | tuple[str], is_first: bool = True) -> str:
    if isinstance(t, str):
        return t
    elif isinstance(t, tuple):
        if is_first:
            return (f"{tuple_to_raw_tags(t[0], False)}{t[1]}"
                    f"{tuple_to_raw_tags(t[2], False)}")
        else:
            return (f"({tuple_to_raw_tags(t[0], False)}{t[1]}"
                    f"{tuple_to_raw_tags(t[2], False)})")
