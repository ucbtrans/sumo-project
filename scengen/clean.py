if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Scenario cleaner')
    parser.add_argument('-e', dest='edges_out', help='Edges output file')
    parser.add_argument('-l', dest='edgetypes_out', help='Edge types output file')
    parser.add_argument('-n', dest='nodes_out', help='Nodes output file')
    parser.add_argument('-o', dest='net_out', help='Net output file')
    parser.add_argument('-z', dest='taz_out', help='TAZ output file')
    parser.add_argument('-t', dest='trips_out', help='Trips output file')
    parser.add_argument('-f', dest='flows_out', help='Flows output file')
    parser.add_argument('-r', dest='routes_out', help='Routes output file')
    parser.add_argument('-v', dest='vtypes_out', help='Vehicle types output file')
    parser.add_argument('-m', dest='odmat_out', help='O/D matrix file')
    parser.add_argument('-c', dest='conf_out', help='Configuration file')
    parser.add_argument('-s', dest='name', help='Scenario name')
    args = parser.parse_args()

    try:
        args.edges_out = args.name + '.edg.xml'
        args.nodes_out = args.name + '.nod.xml'
        args.net_out = args.name + '.net.xml'
        args.taz_out = args.name + '.taz.xml'
        args.trips_out = args.name + '.trp.xml'
        args.flows_out = args.name + '.flw.xml'
        args.routes_out = args.name + '.rou.xml'
        args.vtypes_out = args.name + '.vty.xml'
        args.odmat_out = args.name + '.odm'
        args.conf_out = args.name + '.cfg.xml'
    except e:
        pass

    os.remove(args.edges_out)
#    os.remove(args.edgetypes_out)
    os.remove(args.nodes_out)
    os.remove(args.net_out)
    os.remove(args.taz_out)
    os.remove(args.trips_out)
    os.remove(args.flows_out)
    os.remove(args.routes_out)
    os.remove(args.vtypes_out)
    os.remove(args.odmat_out)
    os.remove(args.conf_out)
