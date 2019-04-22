from lxml import etree, objectify
from qgis.core import *
import sys

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







if __name__ == "__main__":
    parseParking('/home/huajun/Desktop/NCST_parking/cities/fairfield/on-parking.add.xml')