from typing import Iterable

from tdm import TalismanDocument

from tp_interfaces.abstract.dataset import AbstractSplitData


class SplitTdmData(AbstractSplitData[TalismanDocument]):
    def __init__(self, data: dict[str | None, Iterable[TalismanDocument]]):
        self._role2docs = data

    @property
    def roles(self) -> set[str]:
        return set(self._role2docs)

    def get_data(self, role: str | None = None) -> Iterable[TalismanDocument]:
        return self._role2docs[role]
