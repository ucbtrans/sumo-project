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
    
    files = ['1.pickle', '2.pickle']
    clr = ['ko-', 'bo-']
    legend = ['1', '2']
    
    sz = len(files)
    
    for i in range(sz):
        with open(files[i], 'rb') as f:
            data = pickle.load(f)
        f.close()
        
        plt.figure(1)
        plt.plot(data[0, :], data[1, :], clr[i])
        plt.xlabel('Time (minutes)')
        plt.ylabel('Vehicle Count')
        plt.legend(legend, loc='bottom, right')
        
    
    plt.show()
    



if __name__ == "__main__":
    main(sys.argv)

