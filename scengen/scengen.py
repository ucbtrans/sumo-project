from xml.etree import ElementTree

class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


    def distanseTo(self, point=None):
        import math
        point = Point() if point is None else point
        return math.sqrt((self.x - point.x)**2 + (self.y - point.y)**2)


    def vect(self, begin=None):
        begin = Point() if begin is None else begin
        return Point(self.x - begin.x, self.y - begin.y)


    def rotate(self, center=None, alpha=0.0):
        import numpy
        center = Point() if center is None else center
        cosalpha = numpy.cos(alpha)
        sinalpha = numpy.sin(alpha)
        rotationMatrix = numpy.matrix(
            [
                [cosalpha, -sinalpha],
                [sinalpha, cosalpha]
            ])
        v = self.vect(center)
        resv = rotationMatrix * numpy.matrix([[v.x], [v.y]])
        return Point(resv.item(0), resv.item(1))


    def angleTo(self, point, center=None):
        import math
        center = Point() if center is None else center
        v1 = self.vect(center)
        v2 = point.vect(center)
        return math.acos((v1.x*v2.x + v1.y*v2.y) / (v1.distanseTo() * v2.distanseTo()))



class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.p = Point(x, y)


    def __init__(self, id, point):
        self.id = id
        self.x = point.x
        self.y = point.y
        self.p = point


    def xml(self):
        elem = ElementTree.Element('node', {
            'id': str(self.id),
            'x': str(self.p.x),
            'y': str(self.p.y),
            'type': 'traffic_light'})
        return elem



class Edge:
    def __init__(self, id, node1, node2):
        self.id = id
        self.node1 = node1
        self.node2 = node2

    def createIntermediatePoints(self, accuracy):
        self.points = []
        angle = self.node1.p.angleTo(self.node2.p)
        for i in range(0, accuracy + 1):
            self.points.append(self.node1.p.rotate(alpha=i*angle/accuracy))



    def xml(self):
        attributeDict = {
            'id': self.id,
            'from': self.node1.id,
            'to': self.node2.id,
            'numLanes': '1',
            'speed': '50'}

        try:
            shapeStr = ''
            for point in self.points:
                shapeStr += str(point.x) + ',' + str(point.y) + ' '
            attributeDict['shape'] = shapeStr
        except AttributeError:
            pass

        return ElementTree.Element('edge', attributeDict)



class VehicleType:
    def __init__(self, id, accel, decel, sigma, length, maxSpeed):
        self.id = id
        self.accel = accel
        self.decel = decel
        self.sigma = sigma
        self.length = length
        self.maxSpeed = maxSpeed


    def xml(self):
        vtypeTag = ElementTree.Element('vType',
            {
                'id': self.id,
                'accel': str(self.accel),
                'decel': str(self.decel),
                'sigma': str(self.sigma),
                'length': str(self.length),
                'maxSpeed': str(self.maxSpeed)
            })
        return vtypeTag



class EdgeType:
    def __init__(self, id, priority=1, numLanes=1, speed=50):
        self.id = id
        self.priority = priority
        self.numLanes = numLanes
        self.speed = speed


    def xml():
        edgeTypeTag = ElementTree.Element('type',
            {
                'id': self.id,
                'priority': str(self.priority),
                'numLanes': str(numLanes),
                'speed': str(speed)
            })
        return edgeTypeTag



class Flow:
    def __init__(self, begin, end, vtype, flowmat, n, edges):
        self.begin = begin
        self.end = end
        self.flowmat = flowmat
        self.n = n
        self.edges = edges
        self.vtype = vtype


    def OFormat(self):
        return []


    def VFormat(self):
        strs = [self.vtype
            , Flow.__secondToHourMinute(self.begin) + ' ' + Flow.__secondToHourMinute(self.end)
            , str(1.0)
            , str(self.n)]

        tazsstr = ''
        for i in range(0, self.n):
            tazsstr += 'taz-'+str(i) + ' '

        strs.append(tazsstr)

        for i in range(0, self.n):
            tmp = ''
            for j in range(0, self.n):
                tmp += str(self.flowmat[i][j]) + ' '
            strs.append(tmp)

        return strs


    def __secondToHourMinute(sec):
        return str(sec//3600) + '.' + str((sec%3600)//60)



class RoundaboutScenario:
    def __init__(self, roundaboutJson):
        root = roundaboutJson['roundabout']
        self.n = int(root['n'])
        self.radius = int(root['radius'])
        self.begin = int(root['begin'])
        self.end = int(root['end'])
        self.accuracy = int(root['accuracy'])

        self.__generateNodes()
        self.__generateEdges()

        self.vtypes = dict((
            (record['id'],
            VehicleType(
                record['id'],
                record['accel'],
                record['decel'],
                record['sigma'],
                record['length'],
                record['maxSpeed']))
            for record in root['vtypes']))

        self.flows = []
        for record in root['flow_records']:
            begin = record['begin']
            end = record['end']
            vtype = record['vtype']
            jsonFlowMat = record['flowmat']
            flowMat = [[jsonFlowMat[i][j] for j in range(0, self.n)] for i in range(0, self.n)]
            self.flows.append(Flow(begin, end, vtype, flowMat, self.n, self.edges))


    def __generateNodes(self):
        import numpy
        alpha = 2 * numpy.pi / self.n
        self.nodes = dict((
            ('ra-node-' + str(i),
                Node(
                    id = 'ra-node-' + str(i),
                    point = Point(self.radius, 0.0).rotate(alpha=i*alpha)))
            for i in range(0, self.n)))
        self.nodes.update(dict((
            ('out-node-' + str(i),
                Node(
                    id = 'out-node-' + str(i),
                    point = Point(2 * self.radius, 0.0).rotate(alpha=i*alpha)))
            for i in range(0, self.n))))


    def __generateEdges(self):
        self.edges = {}
        for i in range(0, self.n):
            edgeId = 'ra-edge-' + str(i) + '-' + str((i+1)%self.n)
            self.edges[edgeId] = Edge(
                edgeId,
                self.nodes['ra-node-' + str(i)],
                self.nodes['ra-node-' + str((i+1)%self.n)])
            self.edges[edgeId].createIntermediatePoints(self.accuracy)

            edgeId = 'out-edge-' + str(i)
            self.edges[edgeId] = Edge(
                edgeId,
                self.nodes['ra-node-' + str(i)],
                self.nodes['out-node-' + str(i)])

            edgeId = 'in-edge-' + str(i)
            self.edges[edgeId] = Edge(
                edgeId,
                self.nodes['out-node-' + str(i)],
                self.nodes['ra-node-' + str(i)])


    def nodes(self):
        return self.nodes.values()


    def edges(self):
        return self.edges.values()


    def flows(self):
        return self.flows


    def vtypes(self):
        return self.vtypes.values()


    def nodesXml(self):
        nodesTag = ElementTree.Element('nodes')
        
        for id, node in self.nodes.items():
            nodesTag.append(node.xml())

        return ElementTree.ElementTree(nodesTag)


    def edgesXml(self):
        edgesTag = ElementTree.Element('edges')

        for id, edge in self.edges.items():
            edgesTag.append(edge.xml())

        roundaboutStr = ''
        for i in range(0, self.n):
            roundaboutStr += 'ra-edge-' + str(i) + '-' + str((i+1)%self.n) + ' '
        #for id, edge in self.edges.items():
        #    if edge.id.startswith('ra-edge'):
        #        roundaboutStr += edge.id + ' '
        nodeStr = ''
        for i in range(0, self.n):
            nodeStr += 'ra-node-'+str(i) + ' '
        roundaboutTag = ElementTree.SubElement(edgesTag, 'roundabout',
            { 'edges': roundaboutStr, 'nodes': nodeStr })

        return ElementTree.ElementTree(edgesTag)


    def tazXml(self):
        tazsTag = ElementTree.Element('tazs')
        for i in range(0, self.n):
            elem = ElementTree.SubElement(tazsTag, 'taz', {'id': 'taz-'+str(i)})
            ElementTree.SubElement(elem, 'tazSource',
                {'id': 'in-edge-'+str(i), 'weight': str(1)})
            ElementTree.SubElement(elem, 'tazSink',
                {'id': 'out-edge-'+str(i), 'weight': str(1)})
        return ElementTree.ElementTree(tazsTag)


    def flowVFormat(self):
        strs = ['$VMR']
        for flow in self.flows:
            strs.extend(flow.VFormat())
        return strs


    def configXml(self, netName, flowName, vtypesName):
        confTag = ElementTree.Element('configuration')

        inputTag = ElementTree.SubElement(confTag, 'input')
        ElementTree.SubElement(inputTag, 'net-file', { 'value': netName + ' ' + vtypesName})
#        ElementTree.SubElement(inputTag, 'type-files', { 'value' : vtypesName })
        ElementTree.SubElement(inputTag, 'route-files', { 'value': flowName })

        timeTag = ElementTree.SubElement(confTag, 'time')
        ElementTree.SubElement(timeTag, 'begin', { 'value': str(self.begin) })
        ElementTree.SubElement(timeTag, 'end', { 'value': str(self.end) })

        return ElementTree.ElementTree(confTag)


    def vTypesXml(self):
        routesTag = ElementTree.Element('routes')

        for id, vtype in self.vtypes.items():
            routesTag.append(vtype.xml())

        return ElementTree.ElementTree(routesTag)



if __name__ == '__main__':
    import argparse
    import json
    import os

    parser = argparse.ArgumentParser(description='Scenario generator')
    parser.add_argument('-i', dest='roundabout', help='Roundabout JSON file')
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
        args.roundabout = args.name + '.json'
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

    jsonFile = open(args.roundabout)
    scenario = RoundaboutScenario(json.load(jsonFile))
    jsonFile.close()

    nodesXml = scenario.nodesXml()
    edgesXml = scenario.edgesXml()
    vTypesXml = scenario.vTypesXml()
    tazXml = scenario.tazXml()

    nodesXml.write(args.nodes_out)
    edgesXml.write(args.edges_out)
    vTypesXml.write(args.vtypes_out)
    tazXml.write(args.taz_out)

    os.system('netconvert'
        + ' --node-files ' + args.nodes_out
        + ' --edge-files ' + args.edges_out
        + ' --output-file ' + args.net_out
        + ' --no-turnarounds')

    # Use OD2TRIPS and DUAROUTER to convert O/D matrices to SUMO trips
    # and then to SUMO flows
    odmatFile = open(args.odmat_out, 'w')
    odmatFile.writelines('\n'.join(scenario.flowVFormat()))
    odmatFile.close()

    os.system('od2trips'
        + ' -n ' + args.taz_out
#        + ' --taz-files=' + args.taz_out
        + ' --od-matrix-files ' + args.odmat_out
        + ' --output-file ' + args.trips_out
        + ' --flow-output ' + args.flows_out)

    os.system('duarouter'
        + ' -n ' + args.net_out
        + ' -d ' + args.taz_out
#        + ' -d ' + args.vtypes_out
        + ' -f ' + args.flows_out
        + ' -o ' + args.routes_out)

    confXml = scenario.configXml(args.net_out, args.routes_out, args.vtypes_out)
    confXml.write(args.conf_out)

    print('Now you can run simulation using \"sumo[-gui] -c ' + args.conf_out + '\"')
