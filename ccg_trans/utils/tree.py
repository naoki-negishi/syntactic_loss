from __future__ import annotations

# Standard Library
from itertools import chain
from typing import Literal

# Third Party Library
from pydantic import BaseModel


class Tree(BaseModel):
    data: str
    node_idx: int
    lleaf: Tree | None = None
    rleaf: Tree | None = None

    def __setitem__(self, key: Literal["lleaf", "rleaf"], value: str) -> None:
        if key == "lleaf":
            assert self.lleaf is None, "left leaf already exists"
            self.lleaf = Tree(data=value, node_idx=2 * self.node_idx + 1)
        elif key == "rleaf":
            assert self.rleaf is None, "right leaf already exists"
            self.rleaf = Tree(data=value, node_idx=2 * self.node_idx + 2)
        else:
            raise KeyError(f"Invalid key: {key}")

    def __getitem__(self, key: str | int):
        if key == "data":
            return self.data
        elif key == "lleaf":
            return self.lleaf
        elif key == "rleaf":
            return self.rleaf
        elif key == "node_idx":
            return self.node_idx
        elif isinstance(key, int):
            for subnode in self.__iter_all():
                if subnode.node_idx == key:
                    return subnode

    def __iter__(self):
        # depth-first search
        if self.lleaf is None and self.rleaf is None:
            yield self
        elif self.rleaf is None:
            yield self.lleaf
        elif self.lleaf is None:
            yield self.rleaf
        else:
            yield from chain(self.lleaf, self.rleaf)

    def __iter_all(self):
        yield self
        if self.lleaf is not None:
            yield from self.lleaf.__iter_all()
        if self.rleaf is not None:
            yield from self.rleaf.__iter_all()

    def __len__(self):
        if self.lleaf is None and self.rleaf is None:
            return 1
        else:
            return len(self.lleaf) + (
                len(self.rleaf) if self.rleaf != None else 0
            )

    def __str__(self):
        return " ".join(node.data for node in self)

    def __eq__(self, other: Tree):
        return repr(self) == repr(other)

    def get_tuple(self):
        data_of_leaves = tuple(node.data for node in self)
        return data_of_leaves
