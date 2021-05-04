"""
컴퓨터에서 난수를 구하는 방식인, 의사 난수 (pseudo-random) 방식을 Python 코드로 작성해 보았습니다.
@author 영훈고등학교 30604 김민준
@copyright 2021
"""

from random import Random, SystemRandom

# 의사 랜덤 방식 (pseudorandom)
# 일반적으로, 컴퓨터에서 의사 난수를 만들 때에는 컴퓨터의 현재 시간, 프로세스 정보 등을 seed 로 사용합니다.
random = Random()
print(f'Regular random (using current time as seed) : {random.random()}')

# seed 값이 다르면 다른 결과를 얻을 수 있습니다.
random1 = Random(411)
random2 = Random(416)
val1 = random1.random()
val2 = random2.random()
print(f'random 1 = random 2 : {val1 == val2}')
print(f'random 1 : {val1}, random 2 : {val2}')

# 만약 의사 랜덤 생성기의 상태 (시드) 를 알 경우, 공격자는 이 의사 랜덤의 값을 예측할 수 있습니다.
random2.seed(411)
val2 = random2.random()
print(f'random 1 = random 2 : {val1 == val2}')
print(f'random 1 : {val1}, random 2 : {val2}')

# 하드웨어 랜덤 생성기
systemRand = SystemRandom(411)
help(systemRand)
val1 = random1.random()
val2 = systemRand.random()
print(f'random 1 = hardware random : {val1 == val2}')
print(f'random 1 : {val1}, random 2 : {val2}')
