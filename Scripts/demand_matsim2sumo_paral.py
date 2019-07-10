from lxml import etree, objectify
import random
import numpy as np
import operator
import logging
from shutil import copyfile
import time

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib
import traci
import traci.constants as tc

from qgis.core import *

import parking as pk

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def parseXML(xmlfile, is_all):
    print('Starting parsing {}'.format(xmlfile))
    trips = []
    trip_id = 0
    with open(xmlfile) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding = 'utf-8'))
        # population = etree.parse(xmlfile).getroot()
        # for person in population.getchildren():
        for event, person in etree.iterparse(xmlfile, tag="person"):
            if len(person):
                if not is_all:
                    id = person.attrib["id"]
                    attributes = person[0]
                    attribute = attributes[0]
                    vot = attribute.text
                    plan = person[1]
                else:
                    id = person.attrib["id"]
                    vot = "0"
                    plan = person[0]

                num_trips = int((len(plan.getchildren())-1)/2)
                home_loc_x, home_loc_y = '', ''
                for num in range(num_trips):
                    trip = {}
                    from_activity = plan.getchildren()[2*num]
                    leg = plan.getchildren()[2*num+1]
                    to_activity = plan.getchildren()[2*num+2]

                    from_type = from_activity.attrib["type"]
                    from_x = from_activity.attrib["x"]
                    from_y = from_activity.attrib["y"]
                    from_end_time = from_activity.attrib["end_time"]

                    to_type = to_activity.attrib["type"]
                    to_x = to_activity.attrib["x"]
                    to_y = to_activity.attrib["y"]
                    try:
                        to_end_time = to_activity.attrib["end_time"]
                    except:
                        to_end_time = "00:00:00"

                    mode = leg.attrib["mode"]

                    # remove any unwanted modes
                    if mode in rm_modes:
                        continue

                    if from_type == 'home':
                        home_loc_x, home_loc_y = from_x, from_y

                    trip["person"] = id
                    trip["from_type"] = from_type
                    trip["from_x"] = from_x
                    trip["from_y"] = from_y
                    trip["to_type"] = to_type
                    trip["to_x"] = to_x
                    trip["to_y"] = to_y
                    trip["from_end_time"] = str(get_sec(from_end_time))
                    trip["to_end_time"] = str(get_sec(to_end_time))
                    trip["mode"] = mode
                    trip["vot"] = vot
                    trip["home_loc_x"] = home_loc_x
                    trip["home_loc_y"] = home_loc_y
                    trip["from_taz"] = ''
                    trip["to_taz"] = ''

                    # only include trips that are related to the ROI
                    from_x = float(trip["from_x"])
                    from_y = float(trip["from_y"])
                    to_x = float(trip["to_x"])
                    to_y = float(trip["to_y"])
                    fromPoint_tr = xform_reverse.transform(from_x, from_y)
                    fromPointGeometry = QgsGeometry.fromPointXY(fromPoint_tr)
                    toPoint_tr = xform_reverse.transform(to_x, to_y)
                    toPointGeometry = QgsGeometry.fromPointXY(toPoint_tr)
                    feature_index = 0
                    for feature in features_geometry:
                        if feature.contains(fromPointGeometry):
                            trip["from_taz"] = str(feature_index)
                        if feature.contains(toPointGeometry):
                            trip["to_taz"] = str(feature_index)
                        feature_index += 1
                        if trip["from_taz"] != '' or trip["to_taz"] != '':
                            trip["trip_id"] = str(trip_id)
                            trips.append(trip)
                            trip_id += 1
                            break
    print('Total trips: {}.'.format(trip_id))
    return trips

def generateTripElement(data):
    """
        Create a trip XML element
    """
    trip = objectify.Element("trip")
    trip.set("trip_id", data["trip_id"])
    trip.set("person", data["person"])
    trip.set("mode", data["mode"])
    trip.set("vot", data["vot"])
    trip.set("from_type", data["from_type"])
    trip.set("from_x", data["from_x"])
    trip.set("from_y", data["from_y"])
    trip.set("to_type", data["to_type"])
    trip.set("to_x", data["to_x"])
    trip.set("to_y", data["to_y"])
    trip.set("from_end_time", data["from_end_time"])
    trip.set("to_end_time", data["to_end_time"])
    trip.set("home_loc_x", data["home_loc_x"])
    trip.set("home_loc_y", data["home_loc_y"])
    trip.set("from_taz", data["from_taz"])
    trip.set("to_taz", data["to_taz"])
    return trip

def createAndSaveTripXML(data, filename):
    """
       Create an XML file
    """
    xml = '''<?xml version="1.0" encoding="UTF-8"?><trips></trips>'''
    xml = bytes(bytearray(xml, encoding='utf-8'))

    root = objectify.fromstring(xml)

    for trip in data:
        root.append(generateTripElement(trip))

    # remove lxml annotation
    objectify.deannotate(root)
    etree.cleanup_namespaces(root)

    # create the xml string
    obj_xml = etree.tostring(root,
                             pretty_print=True,
                             xml_declaration=True,
                             encoding="utf-8")

    try:
        with open(filename, "wb") as xml_writer:
            xml_writer.write(obj_xml)
        xml_writer.close()
        print("{} created successfully!".format(filename))
    except IOError:
        pass

def getClosestEdge(x, y, net, radius):
    edges = net.getNeighboringEdges(x, y, radius)
    # pick the closest edge
    if len(edges) > 0:
        #### Sort Edge class object in python3 does not work properly.
        #### But works fine in python2.
        closestEdge, closestDist = edges[0]
        for edge, dist in edges:
            if dist < closestDist:
                closestDist, closestEdge = dist, edge
        return closestEdge

def weighted_choice(weights):
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i

def getParkedEdge(to_edge_id, parkingAreas, TAZ_parking):
    if TAZ_parking is None:
        # the destination edge has parkingarea
        if to_edge_id in parkingAreas:
            parkedEdge = to_edge_id
        # otherwise
        else:
            parkedEdge = random.choice(list(parkingAreas.keys()))
            # distance = float("inf")
            # for parkingArea in parkingAreas:
            #     edge = parkingArea  # edge id
            #     tmp_dist = traci.simulation.getDistanceRoad(edge, 0, to_edge_id, 0, True)
            #     if tmp_dist < distance:
            #         distance = tmp_dist
            #         parkedEdge = edge
    else:
        weights = []
        for parking in TAZ_parking:
            try:
                weights.append(int(parking["roadsideCapacity"]))
            except:
                print('error here.')
        i = weighted_choice(weights)
        # lane = TAZ_parking[i].attrib["lane"]
        parkedEdge = TAZ_parking[i]["edge_id"]
    return parkedEdge

def getOD(ODFile):
    origins = []
    origin_weights = []
    destinations = []
    destination_weights = []

    ods = etree.parse(ODFile).getroot()

    for od in ods.xpath('origin'):
        id = od.attrib["id"]
        weight = od.attrib["weight"]
        origins.append(id)
        origin_weights.append(float(weight))
    for od in ods.xpath('destination'):
        id = od.attrib["id"]
        weight = od.attrib["weight"]
        destinations.append(id)
        destination_weights.append(float(weight))
    return {"origins": origins, "origin_weights": origin_weights, "destinations": destinations, "destination_weights": destination_weights}

def func(trip, on_closest, off_closest, drop_off_closest, net, offset, ODs,
         drop_off_percentage, parkingAreas_on, parkingAreas_off, parkingAreas_drop_off,
         TAZ_on_parking_dict, TAZ_off_parking_dict, TAZ_drop_off_parking_dict,
         TAZ_edge_dict, drop_off_only_percentage):#, parkingAreas_on, parkingAreas_off, parkingAreas_drop_off):
    rnd = np.random.random()
    duration = int(trip["to_end_time"]) - int(trip["from_end_time"])  # trip duration
    # on-street drop-off
    if rnd <= drop_off_percentage:
        parkingAreas = parkingAreas_drop_off
        TAZ_parking_dict = TAZ_drop_off_parking_dict
        type = 'drop-off'
        duration = 20
        closest = drop_off_closest
    else:
        if drop_off_only_percentage != 1.0:
            # off-street parking
            if duration >= 7200:
                duration = int(duration - min(random.uniform(0.1, 0.4) * duration, 7200)) # randomly substract driving time
                parkingAreas = parkingAreas_off
                TAZ_parking_dict = TAZ_off_parking_dict
                type = 'off'
                closest = off_closest
            # on-street parking
            else:
                duration = int(duration - min(random.uniform(0.1, 0.4) * duration, 1800)) # randomly substract driving time
                parkingAreas = parkingAreas_on
                TAZ_parking_dict = TAZ_on_parking_dict
                type = 'on'
                closest = on_closest
        else:
            duration = int(duration - min(random.uniform(0.1, 0.4) * duration, 7200))  # randomly substract driving time
            parkingAreas = parkingAreas_off
            TAZ_parking_dict = TAZ_off_parking_dict
            type = 'off'
            closest = off_closest
    """
            Create a trip XML element
        """
    flag = True  # set the flag to determin if closestedge is found or not
    radius = 200
    trip_element = {}
    trip_element["id"] = trip["trip_id"]
    trip_element["trip_type"] = type
    trip_element["type"] = "passenger"
    trip_element["color"] = "1,1,0"
    trip_element["from_taz"] = trip["from_taz"]
    trip_element["to_taz"] = trip["to_taz"]

    trip_element["stat"] = ''

    if trip["from_taz"] != '' or trip["to_taz"] != '':
        trip_element["flag"] = True

        #### trip going out polygon:
        # if it is a drop off trip, then parking at to_edge_id for 20s, after that travel back to from node
        # if it is a on or off parking, do not assign parking as it is going to park somewhere outside the network
        ####
        if trip["from_taz"] != '' and trip["to_taz"] == '':
            from_edge_id = random.choice(TAZ_edge_dict[trip["from_taz"]])
            to_edge_id = ODs["destinations"][weighted_choice(ODs["destination_weights"])]
            if from_edge_id in ODs["destinations"]:
                trip_element["flag"] = False
                trip_element["from"] = ""
            else:
                trip_element["from"] = from_edge_id
                if type is 'drop-off' and trip["to_type"] != 'home':
                    parkedEdge = getParkedEdge(to_edge_id, parkingAreas, None)
                    trip_element["stop"] = {"parkingArea": parkingAreas[parkedEdge],
                                            "duration": str(duration)}
                trip_element["stat"] = 'out'
            # need to make sure there is a path going back to from node
            if type is 'drop-off' and trip["to_type"] != 'home':
                trip_element["to"] = from_edge_id
            else:
                trip_element["to"] = to_edge_id
            trip_element["direction"] = "out"
        #### trip going into polygon:
        #
        ####
        elif trip["to_taz"] != '' and trip["from_taz"] == '':
            from_edge_id = ODs["origins"][weighted_choice(ODs["origin_weights"])]
            trip_element["from"] = from_edge_id
            to_edge_id = random.choice(TAZ_edge_dict[trip["to_taz"]])
            if to_edge_id in ODs["origins"]:
                trip_element["flag"] = False
                trip_element["to"] = ""
            else:
                if type is 'drop-off' and trip["to_type"] != 'home':
                    trip_element["to"] = from_edge_id
                else:
                    trip_element["to"] = to_edge_id
                if trip["to_type"] != 'home':
                    if TAZ_parking_dict[trip["to_taz"]] == []:
                        TAZ_parking = TAZ_parking_dict[str(closest[int(trip["to_taz"])])]
                    else:
                        TAZ_parking = TAZ_parking_dict[trip["to_taz"]]
                    parkedEdge = getParkedEdge(to_edge_id, parkingAreas, TAZ_parking)
                    trip_element["stop"] = {"parkingArea": parkingAreas[parkedEdge],
                                            "duration": str(duration)}
                trip_element["direction"] = "into"
                trip_element["stat"] = 'into'

        #### trip inside polygon
        #
        ####
        else:
            from_edge_id = random.choice(TAZ_edge_dict[trip["from_taz"]])
            if from_edge_id in ODs["destinations"]:
                trip_element["flag"] = False
                trip_element["from"] = ""
            else:
                trip_element["from"] = from_edge_id

            to_edge_id = random.choice(TAZ_edge_dict[trip["to_taz"]])
            if to_edge_id in ODs["origins"]:
                trip_element["flag"] = False
                trip_element["to"] = ""
            else:
                if type is 'drop-off' and trip["to_type"] != 'home':
                    trip_element["to"] = from_edge_id
                else:
                    trip_element["to"] = to_edge_id
                if trip["to_type"] != 'home':
                    if TAZ_parking_dict[trip["to_taz"]] == []:
                        TAZ_parking = TAZ_parking_dict[str(closest[int(trip["to_taz"])])]
                    else:
                        TAZ_parking = TAZ_parking_dict[trip["to_taz"]]
                    parkedEdge = getParkedEdge(to_edge_id, parkingAreas, TAZ_parking)
                    trip_element["stop"] = {"parkingArea": parkingAreas[parkedEdge],
                                            "duration": str(duration)}
                trip_element["direction"] = "within"
                trip_element["stat"] = 'within'
    else:
        trip_element["flag"] = False
    trip_element["depart"] = trip["from_end_time"]
    trip_element["end"] = trip["to_end_time"]
    if int(trip["trip_id"])%1000 == 0:
        print('{} is done'.format(trip["trip_id"]))

    return trip_element

def createTripXML(city, trips_sorted, parkingAreas_on, parkingAreas_off, parkingAreas_drop_off,
                  dataset, drop_off_percentage, scenario_dir, drop_off_only_percentage):
    """
       Create an XML file
    """
    xml = '''<?xml version="1.0" encoding="UTF-8"?><routes></routes>'''
    xml = bytes(bytearray(xml, encoding='utf-8'))

    root = objectify.fromstring(xml)

    # read sumo network
    net = sumolib.net.readNet('../cities/' + city + '/' + city + '.net.xml')

    # map offset. sumolib net uses offset to convert utm to local coordinate
    offset = net.getLocationOffset()

    # get bounding box
    # BBox = net.getBBoxXY() #[(bottom_left_X, bottom_left_Y), (top_right_X, top_right_Y)]

    # read OD information
    ODFile = "../cities/" + city + "/" + city + ".od.xml"
    ODs = getOD(ODFile)

    on_closest, off_closest, drop_off_closest = pk.closestTazWithParking(TAZ_on_parking_dict, TAZ_off_parking_dict, TAZ_drop_off_parking_dict, features_geometry)
    out, into, within = 0, 0, 0

    parkingAreas_on_ids, parkingAreas_off_ids, parkingAreas_drop_off_ids = {}, {}, {}
    for key in parkingAreas_on.keys():
        parkingAreas_on_ids[key] = parkingAreas_on[key].attrib["id"]
    for key in parkingAreas_off.keys():
        parkingAreas_off_ids[key] = parkingAreas_off[key].attrib["id"]
    for key in parkingAreas_drop_off.keys():
        parkingAreas_drop_off_ids[key] = parkingAreas_drop_off[key].attrib["id"]
    TAZ_on_parking_dict_ids, TAZ_off_parking_dict_ids, TAZ_drop_off_parking_dict_ids = {}, {}, {}
    for key in TAZ_on_parking_dict.keys():
        TAZ_on_parking_dict_ids[key] = [{"edge_id": parkingArea.attrib["lane"].split('_')[0],
                                         "roadsideCapacity": parkingArea.attrib["roadsideCapacity"]}for parkingArea in TAZ_on_parking_dict[key]]
    for key in TAZ_off_parking_dict.keys():
        TAZ_off_parking_dict_ids[key] = [{"edge_id": parkingArea.attrib["lane"].split('_')[0],
                                          "roadsideCapacity": parkingArea.attrib["roadsideCapacity"]} for parkingArea in TAZ_off_parking_dict[key]]
    for key in TAZ_drop_off_parking_dict.keys():
        TAZ_drop_off_parking_dict_ids[key] = [{"edge_id": parkingArea.attrib["lane"].split('_')[0],
                                               "roadsideCapacity": parkingArea.attrib["roadsideCapacity"]} for parkingArea in TAZ_drop_off_parking_dict[key]]

    from functools import partial
    from multiprocessing import Pool, get_context
    sys.setrecursionlimit(10000000)

    p = get_context('spawn').Pool(processes=12)
    result = p.map(partial(func, on_closest=on_closest, off_closest=off_closest,
                          drop_off_closest=drop_off_closest, net=net,
                          offset=offset, ODs=ODs, drop_off_percentage=drop_off_percentage,
                          parkingAreas_on=parkingAreas_on_ids,
                          parkingAreas_off=parkingAreas_off_ids, parkingAreas_drop_off=parkingAreas_drop_off_ids,
                          TAZ_on_parking_dict=TAZ_on_parking_dict_ids, TAZ_off_parking_dict=TAZ_off_parking_dict_ids,
                          TAZ_drop_off_parking_dict=TAZ_drop_off_parking_dict_ids,
                          TAZ_edge_dict=TAZ_edge_dict,
                          drop_off_only_percentage=drop_off_only_percentage), trips_sorted)
    p.close()
    p.join()
    trips = []
    for trip in result:
        if trip["flag"] == False:
            continue
        else:
            trips.append(trip)
            if trip["stat"] == 'into':
                into += 1
            elif trip["stat"] == 'out':
                out += 1
            elif trip["stat"] == 'within':
                within += 1
            else:
                print("wrong direction type!")
    trips_sorted = sorted(trips, key=lambda k: k["depart"])
    trips_sorted_elements = dictToElements(trips_sorted)
    for trip in trips_sorted_elements:
        if True:
            root.append(trip)
        else:
            continue
    print("Trips going out: {}".format(out))
    print("Trips coming in: {}".format(into))
    print("Trips within: {}".format(within))
    print("Total trips: {}".format(len(trips)))

    # remove lxml annotation
    objectify.deannotate(root)
    etree.cleanup_namespaces(root)

    # create the xml string
    obj_xml = etree.tostring(root,
                             pretty_print=True,
                             xml_declaration=True,
                             encoding="utf-8")

    try:
        with open(scenario_dir + '/trip_' + dataset + '_with_' + str(drop_off_percentage) + '_drop-off_'
                  + '{:.1f}'.format(drop_off_only_percentage) + '_drop-off_only.xml', "wb") as xml_writer:
            xml_writer.write(obj_xml)
        xml_writer.close()
        print("TripXML created successfully!")
    except IOError:
        pass

def dictToElements(trips):
    trip_elements = []
    for trip_dict in trips:
        trip_element = objectify.Element("trip")
        for key in trip_dict.keys():
            if key != "stop":
                try:
                    trip_element.set(key, str(trip_dict[key]))
                except:
                    print("key is {}".format(key))
            else:
                etree.SubElement(trip_element, "stop")
                trip_element.stop.set("parkingArea", trip_dict[key]["parkingArea"])
                trip_element.stop.set("duration", trip_dict[key]["duration"])
        trip_elements.append(trip_element)
    return trip_elements

def randomPointInFeature(feature):
    bounds = feature.boundingBox()
    xmin = bounds.xMinimum()
    xmax = bounds.xMaximum()
    ymin = bounds.yMinimum()
    ymax = bounds.yMaximum()
    p = 0
    while p < 1:
        x_coord = random.uniform(xmin, xmax)
        y_coord = random.uniform(ymin, ymax)
        pt = QgsPointXY(x_coord, y_coord)
        #tmp_geom = QgsGeometry.fromPointXY(pt)
        if feature.contains(pt):
            p += 1
            return pt

# randomly shift the point in feature a little bit
def randomizeOriginDestination(trips_sorted, features, xform, xform_reverse):
    trips_sorted_randomized = []
    count = 0
    for trip in trips_sorted:
        if trip["from_taz"] != '':
            point_rand = randomPointInFeature(features[int(trip["from_taz"])])
            point_rand_tr = xform.transform(point_rand.x(), point_rand.y())
            trip["from_x"] = str(point_rand_tr.x())
            trip["from_y"] = str(point_rand_tr.y())
        if trip["to_taz"] != '':
            point_rand = randomPointInFeature(features[int(trip["to_taz"])])
            point_rand_tr = xform.transform(point_rand.x(), point_rand.y())
            trip["to_x"] = str(point_rand_tr.x())
            trip["to_y"] = str(point_rand_tr.y())
        count += 1
        if count % 1000 is 0:
            print("Randomizing trip: {}.".format(count))

        trips_sorted_randomized.append(trip)

    return trips_sorted_randomized

def generateParkingRerouter(city, parkingAreas_on, parkingAreas_off, parkingAreas_drop_off, edges):
    edges_str = ''
    for edge in edges:
        edges_str = edges_str + edge.getID() + ' '
    edges_str = edges_str[:-1]

    with open("../cities/" + city + "/reroute_parking.xml", "w") as xml_writer:
        xml_writer.write('''<?xml version="1.0" encoding="UTF-8"?>\n''')
        xml_writer.write('''<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">\n''')
        for parkingAreas, rerouter_id in zip([parkingAreas_on, parkingAreas_off, parkingAreas_drop_off], ['rerouter_on', 'rerouter_off', 'rerouter_drop_off']):
            rerouter = objectify.Element("rerouter")
            rerouter.set("id", rerouter_id)
            rerouter.set("edges", edges_str)

            interval = objectify.Element("interval")
            interval.set("begin", "0")
            interval.set("end", "100000")

            for parkingArea in parkingAreas:
                parkingAreaID = parkingAreas[parkingArea].attrib["id"]
                parkingAreaOBJ = objectify.Element("parkingAreaReroute")
                parkingAreaOBJ.set("id", parkingAreaID)
                interval.append(parkingAreaOBJ)
            rerouter.append(interval)
            objectify.deannotate(rerouter)
            etree.cleanup_namespaces(rerouter)
            obj_xml = etree.tostring(rerouter,
                                     pretty_print=True,
                                     xml_declaration=False,
                                     encoding="utf-8").decode("utf-8")
            xml_writer.write(obj_xml)
        xml_writer.write('''</additional>''')
    xml_writer.close()
    print('Generate parking rerouting done.')

if __name__ == "__main__":

    drop_off_duration = 20  # in second
    on_off_parking_threshold = 7200  # 2 hours in seconds
    rm_modes = ['walk', 'bike']
    flags_dict = {'all_7': True, '0.01': False, '0.05': False}
    city = 'san_francisco'
    dataset = '0.01'
    scenario_dir = "../cities/" + city + "/Scenario_Set_2"
    drop_off_only_percentages = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] # percentage of on-street parking dedicated to drop-off only
    drop_off_percentages = [0.5] #[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] # percentage of drop-off trips
    capacity_increase = 0.25 # capacity increase of remaining off-street parking structures

    traci.start(["sumo", "-c", "../cities/" + city + "/dummy.sumo.cfg"]) #initialize connect to traci using a dummy sumo cfg file

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

    # read in all trips for later processing
    start = time.time()
    trips = parseXML('../cities/' + city + '/' + city + '_plans_' + dataset + '.xml',
                     flags_dict[dataset])  # For 'plans_all_7', set to True; otherwise, set to False
    print('Parsing xml takes {} seconds.'.format(time.time() - start))
    createAndSaveTripXML(trips, "../cities/" + city + "/originaltrip.xml")

    # copy original on street parking into drop-off parking
    if not os.path.exists(scenario_dir):
        os.makedirs(scenario_dir)
        os.makedirs(scenario_dir + '/results')
        os.makedirs(scenario_dir + 'plots')
    copyfile("../cities/" + city + "/on_parking.add.xml", scenario_dir + "/drop_off_parking.add.xml")
    parkingAreas_drop_off = pk.parseParking(
        scenario_dir + "/drop_off_parking.add.xml")  # parking spots that are used for drop-off traffic

    for drop_off_only_percentage in drop_off_only_percentages:
        if scenario_dir[-1] == '1':
            # on-street
            copyfile("../cities/" + city + "/on_parking.add.xml", scenario_dir + "/on_parking.add.xml")
            parkingAreas_on = pk.parseParking(
                scenario_dir + "/on_parking.add.xml")  # parking spots that are used for both drop-off traffic and on-street parking traffic
            # off-street
            copyfile("../cities/" + city + "/off_parking.add.xml", scenario_dir + "/off_parking.add.xml")
            parkingAreas_off = pk.parseParking(
                scenario_dir + '/off_parking.add.xml')  # parking spots that are used for off street parking
        elif scenario_dir[-1] == '2':
            # on-street
            parkingAreas_on_OBJ = pk.splitDropoffAndOnParking("../cities/" + city + "/on_parking.add.xml", drop_off_only_percentage)
            with open(scenario_dir + "/on_parking_" + '{:.1f}'.format(1 - drop_off_only_percentage) + ".add.xml", "w") as f_obj:
                parkingAreas_on_xml = etree.tostring(parkingAreas_on_OBJ, pretty_print=True, xml_declaration=False, encoding="utf-8").decode("utf-8")
                f_obj.write(parkingAreas_on_xml)
            parkingAreas_on = pk.parseParking(
                scenario_dir + "/on_parking_" + '{:.1f}'.format(1 - drop_off_only_percentage) + ".add.xml") # parking spots that are used for both drop-off traffic and on-street parking traffic
            # off-street
            copyfile("../cities/" + city + "/off_parking.add.xml", scenario_dir + "/off_parking.add.xml")
            parkingAreas_off = pk.parseParking(
                scenario_dir + '/off_parking.add.xml')  # parking spots that are used for off street parking
        elif scenario_dir[-1] == '3':
            # on-street
            copyfile("../cities/" + city + "/on_parking.add.xml", scenario_dir + "/on_parking.add.xml")
            parkingAreas_on = pk.parseParking(
                scenario_dir + "/on_parking.add.xml")  # parking spots that are used for both drop-off traffic and on-street parking traffic
            # off-street
            # todo: scenario 3
            parkingAreas_off = pk.parseParking('../cities/' + city + '/off_parking.add.xml') # parking spots that are used for off street parking
        else:
            raise Exception('Wrong Scenario Directory!')

        print('Import parking data done.')

        net = sumolib.net.readNet('../cities/' + city + '/' + city + '.net.xml')
        edges = net.getEdges()
        on_edges = set(parkingAreas_on.keys())
        off_egdes = set(parkingAreas_off.keys())
        drop_off_edges = set(parkingAreas_drop_off.keys())
        edges_with_parking_id = list((on_edges.union(off_egdes)).union(drop_off_edges))
        edges_with_parking = []
        for id in edges_with_parking_id:
            edges_with_parking.append(net.getEdge(id))

        generateParkingRerouter(city, parkingAreas_on, parkingAreas_off, parkingAreas_drop_off, edges_with_parking)

        TAZ_on_parking_dict = pk.parkingToTAZs(features_geometry, parkingAreas_on, net, xform_reverse)
        TAZ_drop_off_parking_dict = pk.parkingToTAZs(features_geometry, parkingAreas_drop_off, net, xform_reverse)
        TAZ_off_parking_dict = pk.parkingToTAZs(features_geometry, parkingAreas_off, net, xform_reverse)
        print('Parking to TAZ done.')
        TAZ_edge_dict = pk.edgeToTAZs(edges, features_geometry, net, xform_reverse)

        for drop_off_percentage in drop_off_percentages:
            start = time.time()
            createTripXML(city, trips, parkingAreas_on, parkingAreas_off, parkingAreas_drop_off,
                          dataset, drop_off_percentage, scenario_dir, drop_off_only_percentage)
            print('Total running time = {} seconds.'.format(time.time() - start))

    # close traci connection
    traci.close()
    # exit qgis
    qgs.exitQgis()

