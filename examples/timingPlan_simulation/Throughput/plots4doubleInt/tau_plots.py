import sys
import optparse
import subprocess
import random
import pdb
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.rcParams.update({'font.size': 40})
import math
import numpy as np
import scipy.io


a3_100 = np.loadtxt('2min3RCT_taus_100m',dtype=int)
t3_100 = np.loadtxt('2min3RCT_taus_time_100m',dtype=int)

a3_300 = np.loadtxt('2min3RCT_taus_300m',dtype=int)
t3_300 = np.loadtxt('2min3RCT_taus_time_300m',dtype=int)

a3_500 = np.loadtxt('2min3RCT_taus_500m',dtype=int)
t3_500 = np.loadtxt('2min3RCT_taus_time_500m',dtype=int)

a0_100 = np.loadtxt('2min0RCT_taus_100m',dtype=int)
t0_100 = np.loadtxt('2min0RCT_taus_time_100m',dtype=int)

a0_300 = np.loadtxt('2min0RCT_taus_300m',dtype=int)
t0_300 = np.loadtxt('2min0RCT_taus_time_300m',dtype=int)

a0_500 = np.loadtxt('2min0RCT_taus_500m',dtype=int)
t0_500 = np.loadtxt('2min0RCT_taus_time_500m',dtype=int)

ss = [1440]*len(t3_100)
ts = np.subtract(t3_100,120)


# 100m intersection
plt.figure(1)
m1, = plt.plot(np.subtract(t0_100,120),a0_100,label='RCT: 0s',linestyle='-',color='r',linewidth=3,marker='o',markersize=7)
m2, = plt.plot(np.subtract(t3_100,120),a3_100,label='RCT: 3s',linestyle='-',color='g',linewidth=3,marker='o',markersize=7)
ms, = plt.plot(ts,ss,label='Steady State',linestyle='--',color='k',linewidth=2)


plt.legend(handles=[m1,m2,ms],loc='lower left') #,fontsize=25)
plt.xlabel('Time (s)')
plt.ylabel('Throughput (veh/hr)')


plt.figure(2)
m1, = plt.plot(np.subtract(t0_500,120),a0_500,label='RCT: 0s',linestyle='-',color='r',linewidth=3,marker='o',markersize=7)
m2, = plt.plot(np.subtract(t3_500,120),a3_500,label='RCT: 3s',linestyle='-',color='g',linewidth=3,marker='o',markersize=7)
ms, = plt.plot(ts,ss,label='Steady State',linestyle='--',color='k',linewidth=2)


plt.legend(handles=[m1,m2,ms],loc='lower left') #,fontsize=25)
plt.xlabel('Time (s)')
plt.ylabel('Throughput (veh/hr)')






plt.show()
