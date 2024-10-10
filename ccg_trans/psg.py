# Standard Library
import random
from abc import ABC
from collections import deque
from collections.abc import Generator, Iterator
from copy import deepcopy

# Third Party Library
from loguru import logger
from pydantic import BaseModel, model_validator
from typing_extensions import Self

# First Party Library
# from ccg_trans.utils.tree import Tree
from utils.tree import Tree

type NonTerminal = str
type Alphabet = str


# input must be Chomsky Normal Form
class PhraseStructureGrammar(ABC):
    non_term: frozenset[NonTerminal]
    term: frozenset[Alphabet]
    prod_rule: dict[
        NonTerminal,
        list[tuple[NonTerminal, NonTerminal] | NonTerminal] | list[Alphabet],
    ]
    start: NonTerminal

    @model_validator(mode="after")
    def check(self) -> Self:
        assert (
            self.start in self.non_term
        ), "The start symbol must be in non-terminal symbols"
        assert self.non_term.isdisjoint(
            self.term
        ), "Non-terminal and terminal symbols must be disjoint"

        return self

    def auto_infer_non_term(self):
        self.non_term = frozenset(self.prod_rule.keys())

    def print_grammar(self):
        print(f"NonTerminal Symbols: {", ".join(self.non_term)}")
        print(f"Terminal Symbols   : {", ".join(f"'{t}'" for t in self.term)}")
        print(f"Production Rules   : {self.prod_rule}")
        print(f"Start Symbol       : {self.start}")


class RegularGrammar(PhraseStructureGrammar, BaseModel, frozen=True):
    non_term: frozenset[NonTerminal]
    term: frozenset[Alphabet]
    prod_rule: dict[NonTerminal, list[tuple[str, str]] | list[Alphabet]]
    start: NonTerminal

    @model_validator(mode="after")
    def check_linearity(self) -> Self:
        # for convinience, we allow re-reading non-terminal symbols \
        # only for terminal symbols
        valid_rereading_nt = set()
        for key, list_value in self.prod_rule.items():
            if all(isinstance(v, str) for v in list_value):
                valid_rereading_nt.add(key)

        for key, list_value in self.prod_rule.items():
            assert isinstance(list_value, list)
            if isinstance(list_value[0], str):  # only produces terminals
                for value in self.prod_rule[key]:
                    assert value in self.term
            elif isinstance(list_value[0], tuple):
                for value in self.prod_rule[key]:
                    assert len(value) == 2
                    assert (
                        value[0] in self.non_term
                        and value[1] in self.term | valid_rereading_nt
                    ) or (
                        value[0] in self.term | valid_rereading_nt
                        and value[1] in self.non_term
                    ), (
                        "In RG, the production rule must be in the form of "
                        f"A -> aB or A -> Ba, not {key} -> {value}"
                    )
            else:
                raise ValueError("The production rule is invalid")
        logger.debug("The grammar is linear grammar (regular grammar)")
        return self


class ContextFreeGrammar(PhraseStructureGrammar):
    _non_term: frozenset[NonTerminal]
    _term: frozenset[Alphabet]
    prod_rule: dict[
        NonTerminal, list[tuple[NonTerminal, NonTerminal]] | list[Alphabet]
    ]
    _start: NonTerminal

    @model_validator(mode="after")
    def check_cnf(self):
        for key, list_value in self.prod_rule.items():
            assert isinstance(list_value, list)
            # TODO: A -> BC | a
            if isinstance(list_value[0], str):  # only produces terminals
                for value in self.prod_rule[key]:
                    assert len(value) == 1
                    assert value in self.term
            elif isinstance(list_value[0], tuple):
                for value in self.prod_rule[key]:
                    assert len(value) == 2
                    assert {value[0], value[1]} <= self.non_term, (
                        "In RG, the production rule must be in the form of "
                        f"A -> aB or A -> Ba, not {key} -> {value}"
                    )
            else:
                raise ValueError("The production rule is invalid")
        logger.debug("The grammar is the form of CNF")
        return self


class ContextSensitiveGrammar(PhraseStructureGrammar):
    _non_term: frozenset[NonTerminal]
    _term: frozenset[Alphabet]
    _prod_rule: dict[NonTerminal, tuple[NonTerminal] | Alphabet]
    _start: NonTerminal

    def __post_init__(self):
        self.check_csg()

    # @validator("p")
    def check_csg(self):  # TODO
        for key, value in self._prod.items():
            if len(value) == 1:
                assert value[0] in self._term
            elif len(value) == 2:
                assert value[0] in self._non_term
                assert value[1] in self._non_term
            else:
                raise ValueError("The production rule is not in CNF")
        print("The grammar is in CSG")


class LanguageGenerator:
    def __init__(self, grammar: PhraseStructureGrammar):
        self.grammar: PhraseStructureGrammar = grammar
        self.syntax_trees: deque[Tree]
        self.sentences: set[str] = set()

        self._s = self.grammar.start
        self._n = self.grammar.non_term
        self._t = self.grammar.term
        self._pr = self.grammar.prod_rule

        # TODO
        self.rereading_nt = set()
        for key, list_value in self._pr.items():
            if all(isinstance(v, str) for v in list_value):
                self.rereading_nt.add(key)

    def generate_all(self, max_length: int) -> Generator[Tree, None, None]:
        self.max_length = max_length

        root: Tree = Tree(data=self._s, node_idx=0)
        yield from self._recursive_production(root_node=root)

    def random_generate(self, max_length: int, num: int) -> list[str]:
        random.seed(42)
        _ = [_ for _ in self.generate_all(max_length)]
        sentences = random.sample(list(self.sentences), num)
        return sentences

    def _recursive_production(
        self, root_node: Tree
    ) -> Generator[Tree, None, None]:
        self.syntax_trees = deque(root_node)

        while len(self.syntax_trees) != 0:
            # logger.debug(f"syntactic trees: {[t.get_tuple() for t in self.syntax_trees]}")
            tree = self.syntax_trees.popleft()
            # print(f"Current tree: {tree.get_tuple()}")

            # if the length of the tree is greater than the max_length
            if len(tree) > self.max_length:
                continue
            # if all leaves are terminal
            if all(symbol.data in self._t for symbol in tree):
                self.sentences.add(tree.get_tuple())
                yield tree

            for leaf in tree:
                if leaf.data not in self._n:
                    continue

                idx = leaf.node_idx
                for product in self._production(tree, idx):
                    # print(f"Product: {leaf.data} -> {product}")
                    new_tree = deepcopy(tree)
                    if isinstance(product, str):
                        new_tree[idx]["lleaf"] = product
                    elif isinstance(product, tuple):
                        new_tree[idx]["lleaf"] = product[0]
                        if len(product) == 2:
                            new_tree[idx]["rleaf"] = product[1]
                    if new_tree not in self.syntax_trees:
                        self.syntax_trees.append(new_tree)

    def _production(self, tree: Tree, idx: int) -> Iterator[list[str]]:
        leaf = tree[idx]
        left_hand = leaf["data"]
        assert left_hand in self._pr.keys(), f"Unkown production: {left_hand}"
        yield from self._pr[left_hand]
