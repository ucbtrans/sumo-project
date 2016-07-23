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
    
    files = ['acc_0.pickle', 'acc_50.pickle', 'acc_100.pickle']
    files = ['a_08.pickle', 'a_15.pickle', 'a_25.pickle']
    legend = ['No ACC', '50% ACC', '100% ACC']
    legend = ['a = 0.8 m/s^2', 'a = 1.5 m/s^2', 'a = 2.5 m/s^2']
    clr = ['ko-', 'bo-', 'mo-']
    sz = len(files)
    
    tt = [0, 60]
    cap1 = [1440, 1440]
    cap2 = [2400, 2400]
    
    for i in range(sz):
        with open(files[i], 'rb') as f:
            time = pickle.load(f)
            time2 = pickle.load(f)
            dx = pickle.load(f)
            dv = pickle.load(f)
            speed = pickle.load(f)
            accel = pickle.load(f)
            flow1 = pickle.load(f)
        
        plt.figure(1)
        plt.plot(time, dx, clr[i])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Distance to Leader (meters)')
        plt.legend(legend, loc='bottom, right')
        
        plt.figure(2)
        plt.plot(time, dv, clr[i])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Speed Difference (m/s)')
        plt.legend(legend)
        
        plt.figure(3)
        plt.plot(time, speed, clr[i])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Speed (m/s)')
        plt.legend(legend, loc='bottom, right')
        
        plt.figure(4)
        plt.plot(time, accel, clr[i])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Acceleration (m/s^2)')
        plt.legend(legend)
        
        plt.figure(5)
        plt.plot(time2, flow1, clr[i])
        plt.xlabel('Time (seconds)')
        plt.ylabel('Flow (vph)')
        plt.legend(legend)

        
    plt.plot(tt, cap1, 'r')
    #plt.plot(tt, cap2, 'r')
    
    plt.show()
    



if __name__ == "__main__":
    main(sys.argv)

