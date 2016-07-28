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


a0 = np.loadtxt('2min0RCT_taus_a1.5',dtype=int)
t0 = np.loadtxt('2min0RCT_taus_time_a1.5',dtype=int)

a3 = np.loadtxt('2min3RCT_taus_a1.5',dtype=int)
t3 = np.loadtxt('2min3RCT_taus_time_a1.5',dtype=int)

a5 = np.loadtxt('2min5RCT_taus_a1.5',dtype=int)
t5 = np.loadtxt('2min5RCT_taus_time_a1.5',dtype=int)


ss = [1440]*len(t0)
ts = np.subtract(t0,1200)

print '2 min cycle -----------'
print 'Max for RCT 0: ' + str(max(a0))
print 'Max for RCT 3: ' + str(max(a3))
print 'Max for RCT 5: ' + str(max(a5))





# compare all the 2min cycles with different accelerations
plt.figure(1)
m1, = plt.plot(np.subtract(t0,1200),a0,label='RCT: 0s',linestyle='-',color='r',linewidth=3,marker='o',markersize=7)
m2, = plt.plot(np.subtract(t3,1200),a3,label='RCT: 3s',linestyle='-',color='g',linewidth=3,marker='o',markersize=7)
m3, = plt.plot(np.subtract(t5,1200),a5,label='RCT: 5s',linestyle='-',color='b',linewidth=3,marker='o',markersize=7)
ms, = plt.plot(ts,ss,label='Steady State',linestyle='--',color='k',linewidth=2)


plt.legend(handles=[m1,m2,m3,ms],loc='best')#,fontsize=25)
plt.xlabel('Time (s)')
plt.ylabel('Throughput (veh/hr)')





plt.show()
