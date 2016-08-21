import sys
import optparse
import subprocess
import random
import pdb
import matplotlib.pyplot as plt
import math
import numpy as np
import scipy.io


a0 = np.loadtxt('2min0RCT_taus_1.0',dtype=int)
t0 = np.loadtxt('2min0RCT_taus_time_1.0',dtype=int)

a1 = np.loadtxt('2min0RCT_taus_1.8',dtype=int)
t1 = np.loadtxt('2min0RCT_taus_time_1.8',dtype=int)

a2 = np.loadtxt('2min0RCT_taus_2.6',dtype=int)
t2 = np.loadtxt('2min0RCT_taus_time_2.6',dtype=int)



plt.figure(1)
m0, = plt.plot(t0,a0,label='a=1.0')
m1, = plt.plot(t1,a1,label='a=1.8')
m2, = plt.plot(t2,a2,label='a=2.6')


plt.legend(handles=[m0,m1,m2],loc='best')
plt.xlabel("Time (s)")
plt.ylabel("Throughput per hr")

plt.title("Instantaneous Throughput vs time for 2 min cycle and RCT = 0")
plt.axis([240,480,400,2000])
plt.show()
