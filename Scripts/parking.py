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

def parkingToTAZs(features_geometry, parkingAreas, net, xform_reverse):
    TAZ_parking_dict = {}
    offset = net.getLocationOffset()
    index = 0
    parking_not_inside_taz_tey = []
    for feature_geometry in features_geometry:
        TAZ_parking_dict[str(index)] = []
        for key in parkingAreas:
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
            if feature_geometry.contains(midPointGeometry):
                TAZ_parking_dict[str(index)].append(parkingAreas[key])
            else:
                if key not in parking_not_inside_taz_tey:
                    parking_not_inside_taz_tey.append((key, midPointGeometry))
        index = index + 1
    for parking in parking_not_inside_taz_tey:
        dist = sys.maxsize
        feature_geometry_index = 0
        for feature_geometry in features_geometry:
            dist_tmp = feature_geometry.distance(parking[1])
            if dist_tmp < dist:
                dist = dist_tmp
                candidate_index = feature_geometry_index
            feature_geometry_index += 1
        TAZ_parking_dict[str(candidate_index)].append(parkingAreas[parking[0]])
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
    modes = []
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
                            modes.append(mode)
                            print(modes)


if __name__ == "__main__":
    # parseParking('/home/huajun/Desktop/NCST_parking/cities/fairfield/on-parking.add.xml')
    count, total_capacity = parkingStats('/home/huajun/Desktop/NCST_parking/cities/san_francisco/Scenario_Set_1/on_parking.add.xml')
    print(count, total_capacity)
    getAllModes('/home/huajun/Desktop/NCST_parking/cities/san_francisco/san_francisco_plans_all_7.xml')