from functools import partial
from multiprocessing import Pool
import numpy as np
import time

def func(a, b, d):
    # tmp = 0
    # for i in range(100000):
    #     tmp += i
    if a == 1:
        return
    return a+b+d

p = Pool(processes=24)
c = np.arange(10000)
start = time.time()
result = p.map(partial(func, b=1, d=2), c)
p.close()
end = time.time()
print('Pool uses {} seconds.'.format(end-start))
print(result)
result = []
start = time.time()
for i in c:
    # tmp = 0
    # for i in range(100000):
    #     tmp += i
    result.append(i+1)
end = time.time()
print('Iterative uses {} seconds.'.format(end-start))