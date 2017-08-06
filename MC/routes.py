"""
SUMO route analysis routines.

"""


import sys
import numpy as np
import pickle


def group_by_route(route_file):
    '''
    
    '''
    
    routes = dict()
    
    veh = None
    route = None
    record = False
    
    with open(route_file, "r") as rf:
        for line in rf:
            if line.find("<vehicle id=") >= 0:
                parts = line.split('"')
                veh = parts[1]
                v_type = parts[5]
        
            if line.find("<route edges=") >= 0:
                route = line.split('"')[1]
                record = True
            
            if record:
                record = False
                try:
                    routes[route][0].append(veh)
                    routes[route][1].append(v_type)
                except:
                    routes[route] = ([veh], [v_type])
            
        rf.close()
        
    return routes



def check_route(r_buf, links):
    '''
    
    '''
    
    for l in links:
        if r_buf.find(l) < 0:
            return False
        
    return True



def get_trip_info(trip_file, assigned_vehicles):
    '''
    
    '''
    
    trip_info = dict()
    for k in assigned_vehicles.keys():
        trip_info[k] = dict()

    with open(trip_file, "r") as tf:
        for line in tf:
            if line.find("<tripinfo id=") < 0:
                continue
        
            parts = line.split('"')            
            veh = parts[1]
            data = [float(parts[3]), float(parts[13]), float(parts[21])]

            for k in assigned_vehicles.keys():
                if veh in assigned_vehicles[k][0]:
                    idx = assigned_vehicles[k][0].index(veh)
                    data.append(assigned_vehicles[k][1][idx])
                    trip_info[k][veh] = data
            
        tf.close()
        
    return trip_info



def print_trip_info(trip_info, tt_range):
    '''
    
    '''
    
    for k in trip_info.keys():
        v_list = trip_info[k].keys()
        sz = len(v_list)
        tt = np.zeros(sz)
        for i in range(sz):
            tt[i] = trip_info[k][v_list[i]][2]
        
        mn, mx = np.min(tt), np.max(tt)
        lb, ub = mn, mx
        if tt_range != None:
            lb, ub = tt_range[k][0], tt_range[k][1]
        
        r1, r2 = float(lb) / float(mn), float(ub) / float(mx)
        
        for v in trip_info[k].keys():
            d = trip_info[k][v]
            vtt = d[2]
            if vtt * r1 <= ub:
                vtt = vtt * r1
            else:
                vtt = vtt * r2
            
            print("{},{},{},{},{},{}".format(k, v, d[3], d[0], d[1], int(np.round(vtt))))
    
    return






#==============================================================================
# Main function - for standalone execution.
#==============================================================================

def main(argv):
    #print(__doc__)
    
    route_file = "network/moco_jtr_out.rou.xml"
    trip_file = "network/tripinfo.xml"
    alinks = ["116069075#0", "-50846720#10",  "-50846720#4", "-50846720#1.35", "-143009954"]
    blinks = ["116069075#0", "50846755#0", "50846755#2.0", "50846755#3.65"]
    
    tt_range = {'a': [306, 912], 'b': [253, 871]}
    assigned_vid = dict()
    assigned_vtype = dict()
    for k in tt_range.keys():
        assigned_vid[k] = []
        assigned_vtype[k] = []
    
    routes = group_by_route(route_file)
    
    for k in routes.keys():
        if len(routes[k][0]) < 5:
            continue
        if check_route(k, alinks):
            #print("A: {}, {}".format(k, routes[k]))
            assigned_vid['a'].extend(routes[k][0])
            assigned_vtype['a'].extend(routes[k][1])
        if check_route(k, blinks):
            #print("B: {}, {}".format(k, routes[k]))
            assigned_vid['b'].extend(routes[k][0])
            assigned_vtype['b'].extend(routes[k][1])
    
    assigned_vehicles = dict()
    for k in assigned_vid.keys():
        assigned_vehicles[k] = (assigned_vid[k], assigned_vtype[k])

    trip_info = get_trip_info(trip_file, assigned_vehicles)
    #tt_range = None       
    print_trip_info(trip_info, tt_range)
    
    return



if __name__ == "__main__":
    main(sys.argv)

