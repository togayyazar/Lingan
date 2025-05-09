from abc import abstractmethod
from typing import Protocol, Optional, List, Dict

from lingan.models import Data


class Container[T:Data](Protocol):
    name: Optional[str]
    _beginning: Optional[int]
    _end: Optional[int]
    lang: Optional[str]

    def period(self) -> tuple[int, int]:
        return self.beginning, self.end

    @classmethod
    def is_diachronic(cls, c: "Container") -> bool:
        return c.beginning is not None and c.end is not None

    @property
    def beginning(self):
        return self._beginning

    @beginning.setter
    def beginning(self, value: int):
        if self.end:
            if value > self._end:
                raise ValueError("beginning cannot be greater than end")
        self._beginning = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value: int):
        if self._beginning:
            if value < self._beginning:
                raise ValueError("end cannot be less than beginning")

        self._end = value

    @classmethod
    def is_valid_range(cls, beginning: int, end: int) -> bool:
        return beginning <= end

    @abstractmethod
    def perform(self, operation: 'Operation'):
        ...
