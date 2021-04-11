from abc import ABC, abstractmethod
from time import time
from typing import List, Final


class RandomMethods(ABC):
    def __init__(self, seed: int):
        self.seed: int = seed

    @abstractmethod
    def random(self, count: int) -> List[int]:


class MidSquareMethod(RandomMethods):
    """중앙제곱법 (Mid Square Method) - 폰 노이만 (1949)"""
    def random(self, count: int) -> List[int]:
        prev: int = self.seed
        for count in range(1, count+1):
            value: int = prev**2
            print(f'Phase {count} : {value}')
            length = len(str(value))


class LinearCongruentialMethod(RandomMethods):
    """선형합동법 (Linear Congruential Method) - ANSI의 C 표준을 참고해 구현함."""
    # values used in ANSI C Standards
    m: int = 2 ** 31
    a: Final[int] = 1103515245
    c: Final[int] = 12345

    def _genNextNumber(self, x: int) -> int:
        return (self.a * x + self.c) % self.m

    def random(self, count: int) -> List[int]:
        results: List[int] = [time()]
        for i in range(count):
            results.append(self._genNextNumber(results[i]))
        return results

class MersenneTwister(RandomMethods):




