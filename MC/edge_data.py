"""
Extract edge data from SUMO output.

"""


import sys
import numpy as np
import matplotlib.pyplot as plt
import pickle



def get_input_details(config_file):
    '''
    Extract name of the edge data output and output period.
    '''
    
    period = -1
    data_file = "edgedata.xml"
    
    with open(config_file, "r") as cf:
        for line in cf:
            if line.find("<edgeData id=") >= 0:
                period = float(line[line.find("freq="):].split('"')[1])
                data_file = line[line.find("file="):].split('"')[1]
        cf.close()
    
    return data_file, period



def get_edge_data(data_file, edge_id, param, period=-1, time_units="minutes"):
    '''
    Extract time series for given parameter for the given edge.
    
    :param data_file:
        Name (string) of the file with edge output data.
    :param edge_id:
        String containing edge ID.
    :param param:
        String containing name of parameter to extract.
    :param period:
        Optional float parameter indicating aggregation period of the parameter values.
        -1 means the full simulation period.
    :param time_units:
        String indicating how time should be represented - seconds, minutes or hours.
        
    
    :return param_series:
        2D numpy array, where
        + param_series[0] row represents time;
        + param_series[1] row represents parameter values.
    '''
    
    time_scales = {'seconds': 1.0, 'minutes': 1.0/60.0, 'hours': 1.0/3600.0}
    factor = 1.0 / 60.0
    try:
        factor = time_scales[time_units]
    except:
        factor = time_scales['minutes']
    
    
    edge_buf = "<edge id=\"{}\"".format(edge_id)
    data = []
    time = []
    t = -1
    
    with open(data_file, "r") as df:
        for line in df:
            if line.find("<interval begin=") >= 0:
                t = factor * float(line[line.find("end="):].split('"')[1])
            
            if line.find(edge_buf) >= 0:
                v = float(line[line.find(param + "="):].split('"')[1])
                time.append(t)
                data.append(v)
            
        df.close()
    
    param_series = np.vstack((np.array(time), np.array(data)))
    
    return param_series
    






#==============================================================================
# Main function - for standalone execution.
#==============================================================================

def main(argv):
    #print(__doc__)
    
    sz = len(argv)
    fn = "flows" # file to store results
    param = "left" # number of vehicles leaving the edge over a time interval
    edge_id = "116069075#1.338" # Montrose Road edge ending at Tildenwood intersection
    prefix = "network/"
    add_config = "moco.det.xml"

    if sz > 1:
        fn = argv[1]
    if sz > 2:
        param = argv[2]
    if sz > 3:
        edge_id = argv[3]
        
        
    data_file, period = get_input_details(prefix + add_config)
    data_file = prefix + data_file
    
    flow_series = get_edge_data(data_file, edge_id, param, period=period, time_units="minutes")
    
    with open(fn + ".pickle", 'wb') as f:
        pickle.dump(flow_series, f)
    f.close()
    
    plt.plot(flow_series[0, :], flow_series[1, :], 'b')
    
    return



if __name__ == "__main__":
    main(sys.argv)

