from lxml import etree, objectify
import random
import numpy as np
import operator

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

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from parking import parseParking

drop_off_duration = 20 # in second
on_off_parking_threshold = 7200 # 2 hours in seconds

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def parseXML(xmlfile, is_all):
    trips = []
    trip_id = 0
    with open(xmlfile) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding = 'utf-8'))
        population = etree.parse(xmlfile).getroot()
        # print(population.tag)

        for person in population.getchildren():
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

                    trip["trip_id"] = str(trip_id)
                    trip_id += 1
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
                    trips.append(trip)
    return trips

def generateTrip(data):
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
    return trip

def createAndSaveTripXML(data, filename):
    """
       Create an XML file
    """
    xml = '''<?xml version="1.0" encoding="UTF-8"?><trips></trips>'''
    xml = bytes(bytearray(xml, encoding='utf-8'))

    root = objectify.fromstring(xml)

    for trip in data:
        root.append(generateTrip(trip))

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

def createVehicle(data):
    """
        Create a vehicle XML element
    """
    vehicle= objectify.Element("trip")
    vehicle.set("person", data["person"])
    vehicle.set("mode", data["mode"])
    vehicle.set("vot", data["vot"])
    vehicle.set("from_type", data["from_type"])
    vehicle.set("from_x", data["from_x"])
    vehicle.set("from_y", data["from_y"])
    vehicle.set("to_type", data["to_type"])
    vehicle.set("to_x", data["to_x"])
    vehicle.set("to_y", data["to_y"])
    vehicle.set("from_end_time", data["from_end_time"])
    vehicle.set("to_end_time", data["to_end_time"])
    return vehicle

def createVehicleXML(data):
    """
       Create an XML file
    """
    xml = '''<?xml version="1.0" encoding="UTF-8"?><addNode></addNode>'''
    xml = bytes(bytearray(xml, encoding='utf-8'))

    root = objectify.fromstring(xml)
    root.set("id", "add_00")

    for trip in data:
        root.append(createOriginalTrip(trip))

    # remove lxml annotation
    objectify.deannotate(root)
    etree.cleanup_namespaces(root)

    # create the xml string
    obj_xml = etree.tostring(root,
                             pretty_print=True,
                             xml_declaration=True,
                             encoding="utf-8")

    try:
        with open("addNode.xml", "wb") as xml_writer:
            xml_writer.write(obj_xml)
        xml_writer.close()
        print("VehicleXML created successfully!")
    except IOError:
        pass

def getClosestEdge(x, y, net, radius):
    edges = net.getNeighboringEdges(x, y, radius)
    # pick the closest edge
    if len(edges) > 0:

        #distancesAndEdges = sorted([(dist, edge) for edge, dist in edges])
        #distancesAndEdges = [(dist, edge) for edge, dist in edges].sort(key = operator.itemgetter(0))

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

def getParkedEdge(to_edge_id, parkingAreas):
    # the destination edge has parkingarea
    if to_edge_id in parkingAreas:
        parkedEdge = to_edge_id
    # otherwise
    else:
        distance = float("inf")
        for parkingArea in parkingAreas:
            edge = parkingArea  # edge id
            tmp_dist = traci.simulation.getDistanceRoad(edge, 0, to_edge_id, 0, True)
            if tmp_dist < distance:
                distance = tmp_dist
                parkedEdge = edge
    return parkedEdge

def createTrip(data, net, BBox, offset, ODs, parkingAreas, type, duration):
    """
        Create a trip XML element
    """
    flag = True # set the flag to determin if closestedge is found or not
    radius = 1000
    trip = objectify.Element("trip")
    trip.set("id", data["trip_id"] + '_' + type)
    trip.set("type", "passenger")
    trip.set("color", "1,1,0")

    point_from = Point(float(data["from_x"])+offset[0], float(data["from_y"])+offset[1])
    point_to = Point(float(data["to_x"])+offset[0], float(data["to_y"])+offset[1])
    polygon = Polygon([(BBox[0][0], BBox[0][1]), (BBox[1][0], BBox[0][1]), (BBox[1][0], BBox[1][1]), (BBox[0][0], BBox[1][1])])

    # # set parking duration based on parking type
    # # on-street parking: duration = 20 seconds
    # # off-street parking: duration is between 2hrs to 6PM-start_time
    # if location is 'on':
    #     duration = 20
    # else:
    #     duration = np.random.randint(7200, max(7200, 64800 - int(data['from_end_time']))+1)

    stat = ''

    if polygon.contains(point_from) or polygon.contains(point_to):
        #print("This trip has at least one end in the ROI.")
        flag = True

        #### trip going out polygon:
        # if it is a drop off trip, then parking at to_edge_id for 20s, after that travel back to from node
        # if it is a on or off parking, do not assign parking as it is going to park somewhere outside the network
        ####
        if polygon.contains(point_from) and not polygon.contains(point_to): # trip going out polygon
            from_edge = getClosestEdge(float(data["from_x"])+offset[0], float(data["from_y"])+offset[1], net, radius)
            from_edge_id = from_edge.getID()
            to_edge_id = ODs["destinations"][weighted_choice(ODs["destination_weights"])]
            if from_edge is None or from_edge_id in ODs["destinations"]:
                flag = False
                trip.set("from", "")
            else:
                trip.set("from", from_edge_id)
                if type is 'drop-off':
                    etree.SubElement(trip, "stop")
                    parkedEdge = getParkedEdge(to_edge_id, parkingAreas)
                    trip.stop.set("parkingArea", parkingAreas[parkedEdge].attrib["id"])
                    trip.stop.set("duration", str(duration))
                stat = 'out'
            # need to make sure there is a path going back to from node
            if type is 'drop-off':
                trip.set("to", from_edge_id)
            else:
                trip.set("to", to_edge_id)

        #### trip going into polygon:
        #
        ####
        elif polygon.contains(point_to) and not polygon.contains(point_from):
            from_edge_id = ODs["origins"][weighted_choice(ODs["origin_weights"])]
            trip.set("from", from_edge_id)

            to_edge = getClosestEdge(float(data["to_x"]) + offset[0], float(data["to_y"]) + offset[1], net, radius)
            to_edge_id = to_edge.getID()
            if to_edge is None or to_edge_id in ODs["origins"]:
                flag = False
                trip.set("to", "")
            else:
                if type is 'drop-off':
                    trip.set("to", from_edge_id)
                else:
                    trip.set("to", to_edge_id)
                etree.SubElement(trip, "stop")
                try:
                    parkedEdge = getParkedEdge(to_edge_id, parkingAreas)
                except Exception as e:
                    print("Bug here!!!!"+str(e))
                trip.stop.set("parkingArea", parkingAreas[parkedEdge].attrib["id"])
                trip.stop.set("duration", str(duration))
                stat = 'into'

        #### trip inside polygon
        #
        ####
        else:
            from_edge = getClosestEdge(float(data["from_x"]) + offset[0], float(data["from_y"]) + offset[1], net,
                                       radius)
            from_edge_id = from_edge.getID()
            if from_edge is None or from_edge_id in ODs["destinations"]:
                flag = False
                trip.set("from", "")
            else:
                trip.set("from", from_edge_id)

            to_edge = getClosestEdge(float(data["to_x"]) + offset[0], float(data["to_y"]) + offset[1], net, radius)
            to_edge_id = to_edge.getID()
            if to_edge is None or to_edge_id in ODs["origins"]:
                flag = False
                trip.set("to", "")
            else:
                if type is 'drop-off':
                    trip.set("to", from_edge_id)
                else:
                    trip.set("to", to_edge_id)
                etree.SubElement(trip, "stop")
                parkedEdge = getParkedEdge(to_edge_id, parkingAreas)
                trip.stop.set("parkingArea", parkingAreas[parkedEdge].attrib["id"])
                trip.stop.set("duration", str(duration))
                stat = 'within'
    else:
        flag = False
    # Set departure time (in second) for this trip
    trip.set("depart", str(data["from_end_time"]))

    return trip, flag, stat

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

def createTripXML(city, trips_sorted, parkingAreas_on, parkingAreas_off, dataset, drop_off_percentage):
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
    BBox = net.getBBoxXY() #[(bottom_left_X, bottom_left_Y), (top_right_X, top_right_Y)]

    # read OD information
    ODFile = "../cities/" + city + "/" + city + ".od.xml"
    ODs = getOD(ODFile)

    count = 0
    out = 0
    into = 0
    within = 0
    for trip in trips_sorted:
        if trip["mode"] is 'walk':
            continue
        rnd = np.random.random()
        duration = int(trip["to_end_time"]) - int(trip["from_end_time"]) # trip duration
        # on-street drop-off
        if rnd <= drop_off_percentage:
            parkingAreas = parkingAreas_on
            type = 'drop-off'
            duration = 20
        else:
            # off-street parking
            if duration >= on_off_parking_threshold:
                parkingAreas = parkingAreas_off
                type = 'off'
            # on-street parking
            else:
                parkingAreas = parkingAreas_on
                type = 'on'
        trip, flag, stat = createTrip(trip, net, BBox, offset, ODs, parkingAreas, type, duration)

        if flag:
            root.append(trip)
        if count % 100 == 0:
            print("Trip: " + str(count))
        count += 1

        if stat is 'out':
            out = out + 1
        elif stat is 'into':
            into = into + 1
        else:
            within = within + 1

    print("Trips going out: {}".format(out))
    print("Trips coming in: {}".format(into))
    print("Trips within: {}".format(within))
    print("Total trips: {}".format(count))

    # remove lxml annotation
    objectify.deannotate(root)
    etree.cleanup_namespaces(root)

    # create the xml string
    obj_xml = etree.tostring(root,
                             pretty_print=True,
                             xml_declaration=True,
                             encoding="utf-8")

    try:
        with open('../cities/' + city + '/trip_' + dataset + '_with_' + str(drop_off_percentage) + '_drop-off.xml', "wb") as xml_writer:
            xml_writer.write(obj_xml)
        xml_writer.close()
        print("TripXML created successfully!")
    except IOError:
        pass

# def readFeaturesFromShape(shapefile):
#     # supply path to qgis install location
#     QgsApplication.setPrefixPath('/usr', True)
#
#     # create a reference to the QgsApplication, setting the
#     # second argument to False disables the GUI
#     qgs = QgsApplication([], False)
#
#     # load providers
#     qgs.initQgis()
#     layer = QgsVectorLayer(shapefile, "", "ogr")
#     if not layer.isValid():
#         print("Layer failed to load!")
#
#     # create projection
#     crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
#     crsDest = QgsCoordinateReferenceSystem("EPSG:32610")  # WGS 84 / UTM zone 10N
#     xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
#     xform_reverse = QgsCoordinateTransform(crsDest, crsSrc, QgsProject.instance())
#
#     features = layer.getFeatures()
#
#     count = 0
#     for feature in features:
#         # retrieve every feature with its geometry and attributes
#         feature = feature.geometry()
#
#     #qgs.exitQgis()
#
#     return features, xform, xform_reverse

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

def randomizeOriginDestination(trips_sorted, features, xform, xform_reverse):
    trips_sorted_randomized = trips_sorted
    count = 0
    for trip in trips_sorted_randomized:
        from_x = float(trip["from_x"])
        from_y = float(trip["from_y"])
        to_x = float(trip["to_x"])
        to_y = float(trip["to_y"])
        # fromPoint = QgsPoint(from_x, from_y)
        fromPoint_tr = xform_reverse.transform(from_x, from_y)
        fromPointGeometry = QgsGeometry.fromPointXY(fromPoint_tr)
        toPoint_tr = xform_reverse.transform(to_x, to_y)
        toPointGeometry = QgsGeometry.fromPointXY(toPoint_tr)
        # for from or to node falling inside a feature, we will randomly select a from or to coordinate for it
        for feature in features:
            if feature.contains(fromPointGeometry):
                point_rand = randomPointInFeature(feature)
                point_rand_tr = xform.transform(point_rand.x(), point_rand.y())
                trip["from_x"] = str(point_rand_tr.x())
                trip["from_y"] = str(point_rand_tr.y())
            if feature.contains(toPointGeometry):
                point_rand = randomPointInFeature(feature)
                point_rand_tr = xform.transform(point_rand.x(), point_rand.y())
                trip["to_x"] = str(point_rand_tr.x())
                trip["to_y"] = str(point_rand_tr.y())
        count += 1
        if count%100 is 0:
            print("Trip: {}.".format(count))

    return trips_sorted_randomized

def generateParkingRerouter(city, parkingAreas_on, parkingAreas_off, edges):
    edges_str = ''
    for edge in edges:
        edges_str = edges_str + edge.getID() + ' '
    edges_str = edges_str[:-1]

    with open("../cities/" + city + "/reroute_parking.xml", "w") as xml_writer:
        xml_writer.write('''<?xml version="1.0" encoding="UTF-8"?>\n''')
        xml_writer.write('''<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">\n''')
        for parkingAreas, rerouter_id in zip([parkingAreas_on, parkingAreas_off], ['rerouter_on', 'rerouter_off']):
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


if __name__ == "__main__":

    flags_dict = {'all_7': True, '0.01': False, '0.05': False}
    city = 'san_francisco'
    dataset = '0.01'

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

    parkingAreas_on = parseParking("../cities/" + city + "/on_parking.add.xml")
    parkingAreas_off = parseParking('../cities/' + city + '/off_parking.add.xml')
    net = sumolib.net.readNet('../cities/' + city + '/' + city + '.net.xml')
    edges = net.getEdges()
    generateParkingRerouter(city, parkingAreas_on, parkingAreas_off, edges)

    trips = parseXML('../cities/' + city + '/' + city + '_plans_' + dataset + '.xml', flags_dict[dataset]) # For 'plans_all_7', set to True; otherwise, set to False

    trips_sorted = sorted(trips, key=lambda k: k['from_end_time'])
    createAndSaveTripXML(trips_sorted, "originaltrip.xml")

    trips_sorted_randomized = randomizeOriginDestination(trips_sorted, features_geometry, xform, xform_reverse)
    createAndSaveTripXML(trips_sorted_randomized, "originaltrip_randomized.xml")

    # createVehicleXML(trips_sorted)
    drop_off_percentage = 0.25
    createTripXML(city, trips_sorted, parkingAreas_on, parkingAreas_off, dataset, drop_off_percentage)

    # close traci connection
    traci.close()
    # exit qgis
    qgs.exitQgis()
