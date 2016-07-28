"""
IDM equilibrium analysis...

Equilibrium condition: 
   1  -  (v/v_max)**delta  -  ((g_min + v*tau) / gap)**2  =  0

"""

import sys
import numpy as np
import matplotlib.pyplot as plt








#==============================================================================
# Main function.
#==============================================================================
def main(argv):
    print(__doc__)
    
    l = 5 # meters
    g_min = 4 # meters
    v_max = 30 # m/s
    tau = 2.05 # seconds
    delta = 4 # acceleration exponent 
    
    dv = 0.1
    

    speed = []
    gap = []
    headway = []
    
    v = 0
    while v < v_max:
        g = (g_min + v*tau) / np.sqrt(1 - float(v/v_max)**delta)
        speed.append(v)
        gap.append(g)
        if v < dv:
            headway.append(tau)
        else:
            headway.append((g+l)/v)
            
        print(g, v, headway[-1])
        v += dv
    
    
    if True:
        plt.figure()
        plt.plot(gap, speed, 'k')
        plt.plot(gap, speed, 'o')
        plt.xlabel('Gap')
        plt.ylabel('Speed')
        
        plt.figure()
        plt.plot(speed, headway, 'k')
        plt.plot(speed, headway, 'o')
        plt.xlabel('Speed')
        plt.ylabel('Headway')
        plt.show()





if __name__ == "__main__":
    main(sys.argv)

