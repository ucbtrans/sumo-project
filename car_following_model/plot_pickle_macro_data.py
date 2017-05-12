"""
Plot point measurements from pickle...

"""




import sys
import matplotlib.pyplot as plt
import pickle






#==============================================================================
# Main function.
#==============================================================================
def main(argv):
    print(__doc__)
    
    files = ['a_08.pickle', 'a_15.pickle', 'a_25.pickle']
    legend = ['a = 0.8 m/s^2', 'a = 1.5 m/s^2', 'a = 2.5 m/s^2']
    clr = ['k', 'b', 'm']
    sz = len(files)
    
    lnk = 70
    tt = [0, 60]
    cap1 = [1440, 1440]
    #cap2 = [2400, 2400]
    
    for i in range(sz):
        with open(files[i], 'rb') as f:
            links = pickle.load(f)
        f.close()
        
        plt.figure(1)
        plt.plot(links[lnk].time, links[lnk].speed, clr[i])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Speed (m/s)')
        plt.legend(legend, loc='bottom, right')
        
        plt.figure(2)
        plt.plot(links[lnk].time, links[lnk].density, clr[i])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Density (vpm)')
        plt.legend(legend, loc='bottom, right')
        
        plt.figure(3)
        plt.plot(links[lnk].time, links[lnk].flow, clr[i])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Flow (vph)')
        plt.legend(legend, loc='bottom, right')

        
    plt.plot(tt, cap1, 'r')
    #plt.plot(tt, cap2, 'r')
    
    plt.show()
    



if __name__ == "__main__":
    main(sys.argv)

