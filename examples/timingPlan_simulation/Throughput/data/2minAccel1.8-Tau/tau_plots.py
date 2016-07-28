import sys
import optparse
import subprocess
import random
import pdb
import matplotlib.pyplot as plt
import math
import numpy as np
import scipy.io


a0 = np.loadtxt('2min0RCT_taus',dtype=int)
t0 = np.loadtxt('2min0RCT_taus_time',dtype=int)

a1 = np.loadtxt('2min1RCT_taus',dtype=int)
t1 = np.loadtxt('2min1RCT_taus_time',dtype=int)

a2 = np.loadtxt('2min2RCT_taus',dtype=int)
t2 = np.loadtxt('2min2RCT_taus_time',dtype=int)

a3 = np.loadtxt('2min3RCT_taus',dtype=int)
t3 = np.loadtxt('2min3RCT_taus_time',dtype=int)

a4 = np.loadtxt('2min4RCT_taus',dtype=int)
t4 = np.loadtxt('2min4RCT_taus_time',dtype=int)

a5 = np.loadtxt('2min5RCT_taus',dtype=int)
t5 = np.loadtxt('2min5RCT_taus_time',dtype=int)

plt.figure(1)
m0, = plt.plot(t0,a0,label='RCT=0')
#m1, = plt.plot(t1,a1,label='RCT=1')
#m2, = plt.plot(t2,a2,label='RCT=2')
m3, = plt.plot(t3,a3,label='RCT=3')
#m4, = plt.plot(t4,a4,label='RCT=4')
m5, = plt.plot(t5,a5,label='RCT=5')


plt.legend(handles=[m0,m3,m5],loc='upper left')
plt.xlabel("Time (s)")
plt.ylabel("Throughput per hr")

plt.title("Instantaneous Throughput vs time for 2 min cycle")
plt.axis([240,480,400,2000])
plt.show()
