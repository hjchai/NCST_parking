from lxml import etree, objectify
import random
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

from parking import *

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def parseXML(xmlfile):
    trips = []
    trip_id = 0
    with open(xmlfile) as fobj:
        xml = fobj.read()
        xml = bytes(bytearray(xml, encoding = 'utf-8'))
        population = etree.parse(xmlfile).getroot()
        # print(population.tag)

        for person in population.getchildren():
            if len(person):
                # print(person)
                id = person.attrib["id"]
                # print(id)
                attributes = person[0]
                # print(attributes.tag)
                attribute = attributes[0]
                # print(attribute.tag)
                vot = attribute.text
                # print(vot)
                plan = person[1]
                selected = plan.attrib["selected"]
                # print(selected)
                num_trips = int((len(plan.getchildren())-1)/2)
                # print(num_trips)
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
                    to_end_time = to_activity.attrib["end_time"]

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

def createOriginalTrip(data):
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

def createOriginalTripXML(data, filename):
    """
       Create an XML file
    """
    xml = '''<?xml version="1.0" encoding="UTF-8"?><trips></trips>'''
    xml = bytes(bytearray(xml, encoding='utf-8'))

    root = objectify.fromstring(xml)

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

def createTrip(data, net, BBox, offset, ODs, parkingAreas):
    """
        Create a trip XML element
    """
    flag = True # set the flag to determin if closestedge is found or not
    radius = 1000
    trip = objectify.Element("trip")
    trip.set("id", data["trip_id"])
    trip.set("type", "passenger")
    trip.set("color", "1,1,0")

    point_from = Point(float(data["from_x"])+offset[0], float(data["from_y"])+offset[1])
    point_to = Point(float(data["to_x"])+offset[0], float(data["to_y"])+offset[1])
    polygon = Polygon([(BBox[0][0], BBox[0][1]), (BBox[1][0], BBox[0][1]), (BBox[1][0], BBox[1][1]), (BBox[0][0], BBox[1][1])])

    if polygon.contains(point_from) or polygon.contains(point_to):
        #print("This trip has at least one end in the ROI.")
        flag = True

        # trip going out polygon
        if polygon.contains(point_from) and not polygon.contains(point_to): # trip going out polygon
            from_edge = getClosestEdge(float(data["from_x"])+offset[0], float(data["from_y"])+offset[1], net, radius)
            from_edge_id = from_edge.getID()
            to_edge_id = ODs["destinations"][weighted_choice(ODs["destination_weights"])]
            if from_edge is None or from_edge_id in ODs["destinations"]:
                flag = False
                trip.set("from", "")
            else:
                trip.set("from", from_edge_id)
                etree.SubElement(trip, "stop")
                parkedEdge = getParkedEdge(to_edge_id, parkingAreas)
                trip.stop.set("parkingArea", parkingAreas[parkedEdge].attrib["id"])
                trip.stop.set("duration", "20")
            trip.set("to", to_edge_id)

        # trip going into polygon
        elif polygon.contains(point_to) and not polygon.contains(point_from):
            to_edge = getClosestEdge(float(data["to_x"]) + offset[0], float(data["to_y"]) + offset[1], net, radius)
            to_edge_id = to_edge.getID()
            if to_edge is None or to_edge_id in ODs["origins"]:
                flag = False
                trip.set("to", "")
            else:
                trip.set("to", to_edge_id)
                etree.SubElement(trip, "stop")
                parkedEdge = getParkedEdge(to_edge_id, parkingAreas)
                trip.stop.set("parkingArea", parkingAreas[parkedEdge].attrib["id"])
                trip.stop.set("duration", "20")
            from_edge_id = ODs["origins"][weighted_choice(ODs["origin_weights"])]
            trip.set("from", from_edge_id)

        # trip inside polygon
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
                trip.set("to", to_edge_id)
                etree.SubElement(trip, "stop")
                parkedEdge = getParkedEdge(to_edge_id, parkingAreas)
                trip.stop.set("parkingArea", parkingAreas[parkedEdge].attrib["id"])
                trip.stop.set("duration", "50")
    else:
        flag = False
    # Set departure time (in second) for this trip
    trip.set("depart", str(data["from_end_time"]))

    return trip, flag

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

def createTripXML(data, parkingAreas):
    """
       Create an XML file
    """
    xml = '''<?xml version="1.0" encoding="UTF-8"?><routes></routes>'''
    xml = bytes(bytearray(xml, encoding='utf-8'))

    root = objectify.fromstring(xml)

    # read sumo network
    net = sumolib.net.readNet('../cities/fairfield/fairfield.net.xml')

    # map offset. sumolib net uses offset to convert utm to local coordinate
    offset = net.getLocationOffset()

    # get bounding box
    BBox = net.getBBoxXY() #[(bottom_left_X, bottom_left_Y), (top_right_X, top_right_Y)]

    # read OD information
    ODFile = "../cities/fairfield/fairfield.od.xml"
    ODs = getOD(ODFile)

    count = 0
    for trip in data:
        trip, flag = createTrip(trip, net, BBox, offset, ODs, parkingAreas)
        if flag:
            root.append(trip)
        if count % 100 == 0:
            print("Trip: " + str(count))
        count += 1

    # remove lxml annotation
    objectify.deannotate(root)
    etree.cleanup_namespaces(root)

    # create the xml string
    obj_xml = etree.tostring(root,
                             pretty_print=True,
                             xml_declaration=True,
                             encoding="utf-8")

    try:
        with open("../cities/fairfield/trip.xml", "wb") as xml_writer:
            xml_writer.write(obj_xml)
        xml_writer.close()
        print("TripXML created successfully!")
    except IOError:
        pass

def readFeaturesFromShape(shapefile):
    # supply path to qgis install location
    QgsApplication.setPrefixPath('/usr', True)

    # create a reference to the QgsApplication, setting the
    # second argument to False disables the GUI
    qgs = QgsApplication([], False)

    # load providers
    qgs.initQgis()
    layer = QgsVectorLayer(shapefile, "", "ogr")
    if not layer.isValid():
        print("Layer failed to load!")

    # create projection
    crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
    crsDest = QgsCoordinateReferenceSystem("EPSG:32610")  # WGS 84 / UTM zone 10N
    xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
    xform_reverse = QgsCoordinateTransform(crsDest, crsSrc, QgsProject.instance())

    features = layer.getFeatures()

    count = 0
    for feature in features:
        # retrieve every feature with its geometry and attributes
        feature = feature.geometry()

    #qgs.exitQgis()

    return features, xform, xform_reverse

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
        tmp_geom = QgsGeometry.fromPointXY(pt)
        if tmp_geom.contains(pt):
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


if __name__ == "__main__":
    traci.start(["sumo", "-c", "../cities/fairfield/fairfield.sumo.cfg"]) #initialize connect to traci

    # supply path to qgis install location
    QgsApplication.setPrefixPath('/usr', True)

    # create a reference to the QgsApplication, setting the
    # second argument to False disables the GUI
    qgs = QgsApplication([], False)

    # load providers
    qgs.initQgis()
    layer = QgsVectorLayer("selected_fairfield.shp", "", "ogr") # ../Caroline_NCST_Data/Communities_of_Concern_TAZ.shp
    if not layer.isValid():
        print("Layer failed to load!")

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

    parkingAreas = parseParking('../cities/fairfield/on-parking.add.xml')

    trips = parseXML('../Caroline_NCST_Data/Scenario_1/matsim_input/plans_0.01.xml')

    trips_sorted = sorted(trips, key=lambda k: k['from_end_time'])
    createOriginalTripXML(trips_sorted, "originaltrip.xml")

    trips_sorted_randomized = randomizeOriginDestination(trips_sorted, features_geometry, xform, xform_reverse)
    createOriginalTripXML(trips_sorted_randomized, "originaltrip_randomized.xml")

    # createVehicleXML(trips_sorted)
    createTripXML(trips_sorted, parkingAreas)
    traci.close()
    qgs.exitQgis()
