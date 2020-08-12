import numpy as np
from matplotlib import pyplot as plt
import time

arr = np.random.rand(10,10)
fig = plt.figure()
plt.pcolor(arr)
print('starting post')
time.sleep(5)
print('ending post')
plt.savefig('someFigure.png')