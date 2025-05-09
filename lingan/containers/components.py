import pickle
from typing import Optional, List, Sequence, overload, Tuple, Union, Iterable

from lingan.containers.definitions import Container
from lingan.models.definitions import Data, VData


class Corpus[T: Data](Container, Data):

    def __init__(self, name: Optional[str] = None, lang: Optional[str] = None,
                 beginning: Optional[int] = None, end: Optional[int] = None,
                 data: Union[Data, Iterable[Data], None] = None):
        self.name = name

        self.lang = lang
        self._beginning = beginning
        self._end = end
        self.data: T = data

    def __eq__(self, other: "Corpus"):
        if not isinstance(other, Corpus):
            return False

        return other.beginning == self.beginning and other.end == self.end

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

    def __repr__(self):
        return f'Corpus:{self.name} <{self.beginning}, {self.end}>'

    @classmethod
    def load(cls, path: str) -> "Corpus":
        with open(path, "rb") as f:
            corpus = pickle.load(f)
        return corpus

    def perform(self, operation: 'Operation'):
        return operation.on_synchronic(self)


class DiachronicCorpus[T: Data](Container[T]):

    def __init__(self, name: Optional[str] = None, lang: Optional[str] = None,
                 beginning: Optional[str] = None, end: Optional[str] = None,
                 corpora: Optional[List[Container[T]]] = None):

        self.name = name
        self.lang = lang
        self._beginning = beginning
        self._end = end
        self._occupied: List[Tuple[int, int]] = list()

        if not corpora:
            corpora: List[Container[T]] = list()

        self.corpora = list()
        for c in corpora:
            self.add(c)

    def periods(self) -> List[Tuple[int, int]]:
        return self._occupied

    def add(self, c: Container) -> None:
        if not Container.is_diachronic(c):
            raise Exception(f"Cannot add {c.name}; timestamps cannot be None")

        time_range = c.period()
        for _c in self._occupied:
            if _c[0] >= time_range[0] <= _c[1] or _c[0] >= time_range[1] <= _c[1]:
                raise ValueError(f"Cannot add {c.name};occupied time range")

        self._occupied.append(time_range)
        self.corpora.append(c)
        self.corpora = sorted(self.corpora, key=lambda x: x.beginning)
        self._beginning = self._occupied[0][0]
        self._end = self._occupied[-1][1]

    def remove(self, c: Container) -> None:
        if c in self.corpora:
            pass

    @overload
    def __getitem__(self, index: Tuple[int, int]) -> Corpus[T]:
        ...

    @overload
    def __getitem__(self, index: slice) -> Union[Corpus[T], List[Container[T]], None]:
        ...

    def __getitem__(self, index) -> Union[Corpus[T], List[Container[T]], None]:
        if isinstance(index, slice):
            beginning = index.start
            end = index.stop
            if index.start is None:
                beginning = self.beginning
            if index.stop is None:
                end = self.end

            return list(filter(lambda c: c.beginning >= beginning and c.end <= end, self.corpora))

        elif isinstance(index, tuple):
            if len(index) != 2:
                raise ValueError("Invalid time range")

            beginning = index[0]
            end = index[1]

            c = None
            queue: list = self.corpora
            for cont in iter(queue):
                if isinstance(cont, Corpus):
                    if beginning == cont.beginning and end == cont.end:
                        return cont
            if not c:
                raise ValueError("Corpus cannot be found")

            return c

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, path: str) -> "Corpus":
        with open(path, "rb") as f:
            corpus = pickle.load(f)
        return corpus

    def perform(self, operation: 'Operation'):
        return operation.on_diachronic(self)

    def corpus_iterator(self, time_range: slice) -> Iterable[Corpus[T]]:
        if not time_range:
            time_range = slice(None, None, None)
        beginning = time_range.start
        end = time_range.stop
        if time_range.start is None:
            beginning = self.beginning
        if time_range.stop is None:
            end = self.end

        queue: list = self.corpora
        for cont in iter(queue):
            if isinstance(cont, Corpus):
                if beginning <= cont.beginning and end >= cont.end:
                    yield cont
            if isinstance(cont, DiachronicCorpus):
                queue.extend(cont.corpora)

    def get_corpus(self, name):
        corpora = self[:]
        for c in corpora:
            if c.name == name:
                return c

        return None

    def __repr__(self):
        return f'DiachronicCorpus <{self.name},{self.beginning}, {self.end}>'
