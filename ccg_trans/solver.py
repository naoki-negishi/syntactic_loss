# Standard Library
import sys
from typing import Any
from itertools import product

# Third Party Library
import z3
from loguru import logger

sys.path.append("..")
from utils.utils import raw_tags_to_tuple, tuple_to_raw_tags


def constraints(category_sequence: list[tuple[str]]) -> z3.z3.BoolRef:
    def ccg_to_LK(category: Any, idx: int) -> z3.BoolRef:
        if isinstance(category, str):
            if category == "np":
                return z3.Bool(f"np_{idx}")
            elif category == "s":
                return z3.Bool(f"s_{idx}")
        elif isinstance(category, tuple):
            lhs, op, rhs = category
            if op == "/":
                return z3.Implies(ccg_to_LK(rhs, idx + 1), ccg_to_LK(lhs, idx))
            elif op == "\\":
                return z3.Implies(ccg_to_LK(rhs, idx - 1), ccg_to_LK(lhs, idx))

    # category_sequence example: [('np',),  ((''s', '\np'), '/', 'np'), 'np')
    antecedent = z3.And(
        [ccg_to_LK(c, j) for j, c in enumerate(category_sequence, 1)]
    )
    consequent = z3.Or(
        [z3.Bool(f"s_{idx+1}") for idx in range(len(category_sequence))]
    )

    return antecedent, consequent


# def solve(seq, antec, conseq) -> bool:
def solve(seq) -> bool:
    antec, conseq = constraints(seq)

    simple_antec = z3.simplify(antec)
    simple_conseq = z3.simplify(conseq)

    solver = z3.Solver()
    solver.add(z3.Not(z3.Implies(simple_antec, simple_conseq)))

    if solver.check() == z3.sat:
        # logger.debug("this seq is invalid\n")
        return False
    else:
        # logger.debug(f"seq: {seq}")
        # logger.debug(f"antec: {antec}, conseq: {conseq}")
        # logger.debug(f"(simple) antec: {simple_antec}, conseq: {simple_conseq}")
        # print()
        # logger.debug("this seq is valid\n")
        return True


def solve_ccg(
    supertags: list[str],
    max_sentence_length: int,
) -> list[list[str | tuple[str]]]:
    categories = list(map(raw_tags_to_tuple, supertags))

    cat_seqs = []
    for seq_len in range(1, max_sentence_length + 1):
        for seq in product(categories, repeat=seq_len):
            if solve(seq):
                raw_seq = list(map(tuple_to_raw_tags, seq))
                cat_seqs.append(raw_seq)

    return cat_seqs
