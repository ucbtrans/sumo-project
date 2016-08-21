import sys
import optparse
import subprocess
import random
import pdb
import matplotlib.pyplot as plt
import math
import numpy as np
import scipy.io


a2_10 = np.loadtxt('2min3RCT_taus_a1.0',dtype=int)
t2_10 = np.loadtxt('2min3RCT_taus_time_a1.0',dtype=int)

a2_15 = np.loadtxt('2min3RCT_taus_a1.5',dtype=int)
t2_15 = np.loadtxt('2min3RCT_taus_time_a1.5',dtype=int)

a2_26 = np.loadtxt('2min3RCT_taus_a2.6',dtype=int)
t2_26 = np.loadtxt('2min3RCT_taus_time_a2.6',dtype=int)

a1_10 = np.loadtxt('1min3RCT_taus_a1.0',dtype=int)
t1_10 = np.loadtxt('1min3RCT_taus_time_a1.0',dtype=int)

a1_15 = np.loadtxt('1min3RCT_taus_a1.5',dtype=int)
t1_15 = np.loadtxt('1min3RCT_taus_time_a1.5',dtype=int)

a1_26 = np.loadtxt('1min3RCT_taus_a2.6',dtype=int)
t1_26 = np.loadtxt('1min3RCT_taus_time_a2.6',dtype=int)

ss = [1440]*len(t2_10)
ts = np.subtract(t2_10,1200)

print '2 min cycle -----------'
print 'Max for a = 1.0: ' + str(max(a2_10))
print 'Max for a = 1.5: ' + str(max(a2_15))
print 'Max for a = 2.6: ' + str(max(a2_26))

print '1 min cycle -----------'
print 'Max for a = 1.0: ' + str(max(a1_10))
print 'Max for a = 1.5: ' + str(max(a1_15))
print 'Max for a = 2.6: ' + str(max(a1_26))


# compare all the 2min cycles with different accelerations
plt.figure(1)
m1, = plt.plot(np.subtract(t2_10,1200),a2_10,label=r'$a=1.0 \: m/s^2$',linestyle='-',color='r',linewidth=3,marker='o',markersize=7)
m2, = plt.plot(np.subtract(t2_15,1200),a2_15,label=r'$a=1.5 \: m/s^2$',linestyle='-',color='g',linewidth=3,marker='o',markersize=7)
m3, = plt.plot(np.subtract(t2_26,1200),a2_26,label=r'$a=2.6 \: m/s^2$',linestyle='-',color='b',linewidth=3,marker='o',markersize=7)
ms, = plt.plot(ts,ss,label=r'$Steady \: State$',linestyle='--',color='k',linewidth=2)


plt.legend(handles=[m1,m2,m3,ms],loc='best')


# compare all the 1min cycles with different accelerations
plt.figure(2)
m1, = plt.plot(np.subtract(t1_10,1200),a1_10,label=r'$a=1.0 \: m/s^2$',linestyle='-',color='r',linewidth=3,marker='o',markersize=7)
m2, = plt.plot(np.subtract(t1_15,1200),a1_15,label=r'$a=1.5 \: m/s^2$',linestyle='-',color='g',linewidth=3,marker='o',markersize=7)
m3, = plt.plot(np.subtract(t1_26,1200),a1_26,label=r'$a=2.6 \: m/s^2$',linestyle='-',color='b',linewidth=3,marker='o',markersize=7)
ms, = plt.plot(ts,ss,label='Steady State',linestyle='--',color='k',linewidth=2)


plt.legend(handles=[m1,m2,m3,ms],loc='best')


# compare the two diff cycles but same acceleration
plt.figure(3)
m1, = plt.plot(np.subtract(t1_10,1200),a1_10,label='1min cycle',linestyle='-',color='r',linewidth=3,marker='o',markersize=7)
m2, = plt.plot(np.subtract(t2_10,1200),a2_10,label='2min cycle',linestyle='-',color='g',linewidth=3,marker='o',markersize=7)
ms, = plt.plot(ts,ss,label='Steady State',linestyle='--',color='k',linewidth=2)


plt.legend(handles=[m1,m2,ms],loc='best')


plt.figure(4)
m1, = plt.plot(np.subtract(t1_15,1200),a1_15,label='1min cycle',linestyle='-',color='r',linewidth=3,marker='o',markersize=7)
m2, = plt.plot(np.subtract(t2_15,1200),a2_15,label='2min cycle',linestyle='-',color='g',linewidth=3,marker='o',markersize=7)
ms, = plt.plot(ts,ss,label='Steady State',linestyle='--',color='k',linewidth=2)

plt.legend(handles=[m1,m2,ms],loc='best')



plt.figure(5)
m1, = plt.plot(np.subtract(t1_26,1200),a1_26,label='1min cycle',linestyle='-',color='r',linewidth=3,marker='o',markersize=7)
m2, = plt.plot(np.subtract(t2_26,1200),a2_26,label='2min cycle',linestyle='-',color='g',linewidth=3,marker='o',markersize=7)
ms, = plt.plot(ts,ss,label='Steady State',linestyle='--',color='k',linewidth=2)


plt.legend(handles=[m1,m2,ms],loc='best')



plt.show()
