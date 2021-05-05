from abc import ABC, abstractmethod
from time import time, sleep
from typing import List, Final
from utils import int_32, Const, GET_CLASS_CONSTANTS, COLLECT_CLASS_CONSTANTS


class RandomMethods(ABC):
    def __init__(self):
        self._seed: float = 0

    def seed(self, a: float = 0):
        self._seed = a

    @abstractmethod
    def random(self) -> float:  ...

    @abstractmethod
    def randrange(self, a, b) -> int:   ...

    @abstractmethod
    def randint(self, a, b) -> int: ...

    @abstractmethod
    def randoms(self, count: int) -> List[int]:  ...


@COLLECT_CLASS_CONSTANTS
class LinearCongruentialMethod(RandomMethods):
    """선형합동법 (Linear Congruential Method) - ANSI의 C 표준을 참고해 구현함."""
    # values used in ANSI C Standards
    M: Final[int] = 2 ** 31
    A: Final[int] = 1103515245
    C: Final[int] = 12345

    def __init__(self):
        super(LinearCongruentialMethod, self).__init__()
        self.seed(time())
        self.__last: float = self._seed
        self.__index: int = 0

    @GET_CLASS_CONSTANTS
    def generate_next_number(self, x, *, A: Const, C: Const, M: Const) -> float:
        self.__index += 1
        return (A * x + C) % M

    def generate_next_int(self, x) -> int:
        return int(self.generate_next_number(x))

    @GET_CLASS_CONSTANTS
    def randoms(self, count: int, *, M: Const) -> List[float]:
        if self.__index >= M:
            self.seed(time())
        results: List[float] = [self.__last]
        for i in range(count):
            results.append(self.generate_next_number(results[i]))
        self.__last = results[-1]
        return results[1:]

    def random(self) -> float:
        return self.randoms(1)[0]

    def randrange(self, a, b) -> int:
        """ return random int in [a,b) """
        n = self.random()
        return int(n / (1 / (b - a)) + a)

    def randint(self, a, b) -> int:
        """ return random int in [a,b] """
        return self.randrange(a, b+1)

    def test(self):
        print(f'| 현재 시드 : {self._seed}')
        print('1개 랜덤값 :')
        print(self.random())
        print('5개 랜덤값 :')
        for i, value in enumerate(self.randoms(5)):
            print(f'| {i + 1} 번째 랜덤 값 : {value}')


@COLLECT_CLASS_CONSTANTS
class MersenneTwister(RandomMethods):
    """메르센 트위스터 알고리즘을 구현함. 2002년도 개선 버전"""
    # Coefficients
    A: Final[int] = 0x9908B0DF  # 2567483615
    B: Final[int] = 0x9D2C5680  # 2636928640
    C: Final[int] = 0xEFC60000  # 4022730752
    F: Final[int] = 1812433253
    L: Final[int] = 18
    M: Final[int] = 397
    N: Final[int] = 624
    S: Final[int] = 7
    T: Final[int] = 15
    U: Final[int] = 11
    W: Final[int] = 32

    UPPER_MASK: Final[int] = (2 ** 32) / 2  # 0x80000000 = 2147483648
    LOWER_MASK: Final[int] = UPPER_MASK - 1  # 0x7fffffff = 2147483647
    MATRIX_A: Final[int] = 0x9908b0df

    def __init__(self):
        super(MersenneTwister, self).__init__()
        self.state = [0] * 624
        self.index = 625

    @GET_CLASS_CONSTANTS
    def seed(self, a=0, *, F: Const, N: Const, W: Const):
        # Official Python implementation at
        # https://github.com/python/cpython/blob/6989af0bc7ea1e9a1acea16794e6f723d7b44110/Modules/_randommodule.c#L265
        self.state[0] = self._seed = a
        for i in range(1, N):
            temp = (
                    F * (self.state[i - 1] ^ (self.state[i - 1] >> (W - 2))) + i
            )
            self.state[i] = int_32(temp)

    @GET_CLASS_CONSTANTS
    def twist(self, *, N: Const):
        # 32비트 int를 사용하므로 0xFFFFFFFF 마스킹 스킵
        for i in range(1, N):
            # Can skip in 32-bit
            """temp = (self.state[i] & self.upper_mask) + (
                self.state[(i + 1) % self.n] & self.lower_mask
            )

            temp_shift = temp >> 1
            if temp % 2 != 0:
                temp_shift ^= self.a
            self.state[i] = self.state[(i + self.m) % self.n] ^ temp_shift
            """
            self.state[i] = (
                    0x6C078965 * (self.state[i - 1] ^ self.state[i - 1] >> 30) + i
            )
        self.index = 0

    @GET_CLASS_CONSTANTS
    def generate_random_int(self, *, N: Const, U: Const, S: Const, B: Const, T: Const, C: Const, L: Const):
        if self.index >= N:
            self.twist()

        y = self.state[self.index]
        y = y ^ (y >> U)
        y = y ^ ((y << S) & B)
        y = y ^ ((y << T) & C)
        y = y ^ (y >> L)

        self.index += 1

        return int_32(y)

    def random(self) -> float:
        """ return uniform distribution in [0,1) """
        return self.generate_random_int() / 4294967296  # = 0xFFFFFFFF + 1

    def randrange(self, a, b):
        # Official Python implementation at
        # https://github.com/python/cpython/blob/master/Lib/random.py
        """ return random int in [a,b) """
        n = self.random()
        return int(n / (1 / (b - a)) + a)

    def randint(self, a, b):
        """return random int in [a, b]"""
        return self.randrange(a, b + 1)

    def randoms(self, count: int) -> List[float]:
        return [self.random() for _ in range(count)]

    def test(self):
        print(f'| 현재 시드 : {self._seed}')
        for i in range(3):
            print(f'| {i + 1} 번째 랜덤 숫자 : {self.generate_random_int()}')

        print(f'| 0, 1 사이의 임의의 실수 : {self.random()}')

        print(f'| [1, 10) 범위의 임의의 정수 :')
        for _ in range(10):
            print(self.randrange(1, 10), end=" ")
        print()

        print(f'| [1, 10] 범위의 임의의 정수 :')
        for _ in range(10):
            print(self.randint(1, 10), end=" ")
        print()


def main():
    print('선형 합동법 :')
    randLinear = LinearCongruentialMethod()
    randLinear.test()
    randLinear.seed(2021)
    randLinear.test()

    print('메르센 트위스터 :')
    randMT = MersenneTwister()
    randMT.test()
    randMT.seed(2021)
    randMT.test()


main()
