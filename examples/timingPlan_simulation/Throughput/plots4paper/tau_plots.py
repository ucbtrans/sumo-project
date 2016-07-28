import sys
import optparse
import subprocess
import random
import pdb
import matplotlib.pyplot as plt
import math
import numpy as np
import scipy.io


a2 = np.loadtxt('2min4RCT_taus',dtype=int)
t2 = np.loadtxt('2min4RCT_taus_time',dtype=int)

a1 = np.loadtxt('1min4RCT_taus',dtype=int)
t1 = np.loadtxt('1min4RCT_taus_time',dtype=int)

ss = [1440]*len(t1)
ts = np.subtract(t1,1200)


plt.figure(1)
m2, = plt.plot(np.subtract(t2,1200),a2,label='2min Cycle',linestyle='-',color='k')
m1, = plt.plot(np.subtract(t1,1200),a1,label='1min Cycle',linestyle='-.',color='k')
ms, = plt.plot(ts,ss,label='Steady State',linestyle='--',color='gray',linewidth=2)


plt.legend(handles=[m1,m2,ms],loc='best')
#plt.xlabel("Time (s)")
#plt.ylabel("Throughput per hr")

#plt.title("Instantaneous Throughput vs time for 2 min cycle")
#plt.axis([240,480,400,2000])
plt.show()
