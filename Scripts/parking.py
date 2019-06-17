from lxml import etree, objectify
from qgis.core import *
import sys
import numpy as np

def parseParking(xmlfile):
    parkingAreas = {}
    with open(xmlfile) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding='utf-8'))
        additional = etree.parse(xmlfile).getroot()

        #print(additional.tag)

        for parkingArea in additional.getchildren():

            #print(parkingArea)

            lane = parkingArea.attrib['lane']
            edge = lane.split('_')[0]
            parkingAreas[edge] = parkingArea
    return parkingAreas

def splitDropoffAndOnParking(total_parking_xml, drop_off_only_percentage):
    root = etree.parse(total_parking_xml).getroot()
    additional = objectify.Element("additional")
    for parking in root.getchildren():
        if np.random.random() < 1 - drop_off_only_percentage:
            additional.append(parking)
    return additional


def edgeToTAZs(edges, features_geometry, net, xform_reverse):
    TAZ_edge_dict = {}
    offset = net.getLocationOffset()
    for i in range(len(features_geometry)):
        TAZ_edge_dict[str(i)] = []
    for edge in edges:
        index = 0
        edge_id = edge.getID()
        edge_from_node = edge.getFromNode()
        edge_to_node = edge.getToNode()
        from_coord = edge_from_node.getCoord()
        to_coord = edge_to_node.getCoord()
        from_x = from_coord[0] - offset[0]
        from_y = from_coord[1] - offset[1]
        to_x = to_coord[0] - offset[0]
        to_y = to_coord[1] - offset[1]
        mid_coord = ((from_x + to_x) / 2, (from_y + to_y) / 2)
        mid_coord_tr = xform_reverse.transform(mid_coord[0], mid_coord[1])
        midPointGeometry = QgsGeometry.fromPointXY(mid_coord_tr)
        for feature_geometry in features_geometry:
            if feature_geometry.contains(midPointGeometry):
                TAZ_edge_dict[str(index)].append(edge_id)
                break
            else:
                index += 1
                continue
        if index == len(features_geometry):
            print('Edge {} is not within boundary.'.format(edge_id))

    return TAZ_edge_dict

def parkingToTAZs(features_geometry, parkingAreas, net, xform_reverse):
    TAZ_parking_dict = {}
    offset = net.getLocationOffset()
    for i in range(len(features_geometry)):
        TAZ_parking_dict[str(i)] = []
    for key in parkingAreas:
        index = 0
        parking_edge_id = key
        parking_edge = net.getEdge(parking_edge_id)
        edge_from_node = parking_edge.getFromNode()
        edge_to_node = parking_edge.getToNode()
        from_coord = edge_from_node.getCoord()
        to_coord = edge_to_node.getCoord()
        from_x = from_coord[0] - offset[0]
        from_y = from_coord[1] - offset[1]
        to_x = to_coord[0] - offset[0]
        to_y = to_coord[1] - offset[1]
        mid_coord = ((from_x + to_x)/2, (from_y + to_y)/2)
        mid_coord_tr = xform_reverse.transform(mid_coord[0], mid_coord[1])
        midPointGeometry = QgsGeometry.fromPointXY(mid_coord_tr)
        for feature_geometry in features_geometry:
            if feature_geometry.contains(midPointGeometry):
                TAZ_parking_dict[str(index)].append(parkingAreas[key])
            else:
                index += 1
                continue
                # if key not in parking_not_inside_taz_tey:
                #     parking_not_inside_taz_tey.append((key, midPointGeometry))
        if index == len(features_geometry):
            print('Parkingarea {} is not within boundary.'.format(parking_edge_id))
    # for parking in parking_not_inside_taz_tey:
    #     dist = sys.maxsize
    #     feature_geometry_index = 0
    #     for feature_geometry in features_geometry:
    #         dist_tmp = feature_geometry.distance(parking[1])
    #         if dist_tmp < dist:
    #             dist = dist_tmp
    #             candidate_index = feature_geometry_index
    #         feature_geometry_index += 1
    #     TAZ_parking_dict[str(candidate_index)].append(parkingAreas[parking[0]])
    return TAZ_parking_dict

def closestTazWithParking(on_dict, off_dict, dropoff_dict, geo_features):
    on_close = np.zeros(len(on_dict)).astype(int)
    off_close = np.zeros(len(off_dict)).astype(int)
    dropoff_close = np.zeros(len(dropoff_dict)).astype(int)
    for key, pa in on_dict.items():
        if pa != []:
            on_close[int(key)] = key
        else:
            origin_pt = geo_features[int(key)].centroid()
            dist = float("inf")
            target = NULL
            for i in range(len(on_dict)):
                if on_dict[str(i)] == []:
                    continue
                dest_pt = geo_features[i].centroid()
                dist_tmp = origin_pt.distance(dest_pt)
                if dist_tmp < dist:
                    dist = dist_tmp
                    target = i
            on_close[int(key)] = target

    for key, pa in off_dict.items():
        if pa != []:
            off_close[int(key)] = key
        else:
            origin_pt = geo_features[int(key)].centroid()
            dist = float("inf")
            target = NULL
            for i in range(len(off_dict)):
                if off_dict[str(i)] == []:
                    continue
                dest_pt = geo_features[i].centroid()
                dist_tmp = origin_pt.distance(dest_pt)
                if dist_tmp < dist:
                    dist = dist_tmp
                    target = i
            off_close[int(key)] = target

    for key, pa in dropoff_dict.items():
        if pa != []:
            dropoff_close[int(key)] = key
        else:
            origin_pt = geo_features[int(key)].centroid()
            dist = float("inf")
            target = NULL
            for i in range(len(off_dict)):
                if dropoff_dict[str(i)] == []:
                    continue
                dest_pt = geo_features[i].centroid()
                dist_tmp = origin_pt.distance(dest_pt)
                if dist_tmp < dist:
                    dist = dist_tmp
                    target = i
            dropoff_close[int(key)] = target

    return on_close, off_close, dropoff_close

def parkingStats(parkingXML):
    with open(parkingXML) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding='utf-8'))
        additional = etree.parse(parkingXML).getroot()

        #print(additional.tag)
        count = 0
        total_capacity = 0
        for parkingArea in additional.getchildren():
            count += 1
            total_capacity += int(parkingArea.attrib['roadsideCapacity'])
        return count, total_capacity

def getAllModes(tripXML):
    modes = {}
    count = 0
    with open(tripXML) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding='utf-8'))
        population = etree.parse(tripXML).getroot()
        for person in population:
            if len(person):
                plan = person[0]
                for child in plan.getchildren():
                    if child.tag == 'leg':
                        mode = child.attrib['mode']
                        if mode not in modes:
                            modes[mode] = 1
                            print(modes)
                        else:
                            modes[mode] += 1
                            count += 1
                            # print(count)
    print(modes)

def getTripStats(tripXML):
    types = {'on': 0, 'drop_off': 0, 'off': 0}
    direct = {'into': 0, 'out': 0, 'within': 0}
    with open(tripXML) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding='utf-8'))
        routes = etree.parse(tripXML).getroot()
        for trip in routes:
            trip_id = trip.attrib['id']
            direction = trip.attrib["direction"]
            type = trip_id.split('_')[1]
            if type == 'on':
                types['on'] += 1
            elif type == 'drop-off':
                types['drop_off'] += 1
            else:
                types['off'] += 1
            if direction == 'into':
                direct['into'] += 1
            elif direction == 'out':
                direct['out'] += 1
            else:
                direct['within'] += 1
    print(types, direct)

if __name__ == "__main__":
    city = 'san_francisco'
    # parseParking('/home/huajun/Desktop/NCST_parking/cities/fairfield/on-parking.add.xml')
    count, total_capacity = parkingStats('/home/huajun/Desktop/NCST_parking/cities/san_francisco/Scenario_Set_1/on_parking.add.xml')
    print(count, total_capacity)
    # getAllModes('/home/huajun/Desktop/NCST_parking/cities/san_francisco/san_francisco_plans_all_7.xml')
    # getTripStats('/home/huajun/Desktop/NCST_parking/cities/san_francisco/Scenario_Set_1/trip_all_7_with_0.5_drop-off.xml')

    # supply path to qgis install location
    QgsApplication.setPrefixPath('/usr', True)

    # create a reference to the QgsApplication, setting the
    # second argument to False disables the GUI
    qgs = QgsApplication([], False)

    # load providers
    qgs.initQgis()
    layer = QgsVectorLayer("../cities/" + city + "/shp/" + city + ".shp", "", "ogr")
    if not layer.isValid():
        raise Exception("Layer failed to load!")

    # create projection
    crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
    crsDest = QgsCoordinateReferenceSystem("EPSG:32610")  # WGS 84 / UTM zone 10N
    xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
    xform_reverse = QgsCoordinateTransform(crsDest, crsSrc, QgsProject.instance())

    features = layer.getFeatures()
    features_geometry = []
    for feature in features:
        # retrieve every feature with its geometry and attributes
        features_geometry.append(feature.geometry())

    import os, sys
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    import sumolib
    # read sumo network
    net = sumolib.net.readNet('../cities/' + city + '/' + city + '.net.xml')
    edges = net.getEdges()

    import time

    start = time.time()
    TAZ_edge_dict = edgeToTAZs(edges, features_geometry, net, xform_reverse)
    print('Single thread takes {} seconds.'.format(time.time() - start))

