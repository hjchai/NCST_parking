from lxml import etree, objectify
import random
import numpy as np
import operator
import logging

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

class Converter:

    def __init__(self, city ):
        self.city = city
        self.drop_off_percentage = 0
        traci.start(["sumo", "-c", "../cities/" + self.city + "/dummy.sumo.cfg"])
        # supply path to qgis install location
        QgsApplication.setPrefixPath('/usr', True)

        # create a reference to the QgsApplication, setting the
        # second argument to False disables the GUI
        qgs = QgsApplication([], False)

        # load providers
        qgs.initQgis()
        layer = QgsVectorLayer("../cities/" + self.city + "/shp/" + self.city + ".shp", "", "ogr")
        if not layer.isValid():
            raise Exception("Layer failed to load!")

        # create projection
        crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
        crsDest = QgsCoordinateReferenceSystem("EPSG:32610")  # WGS 84 / UTM zone 10N
        self.xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        self.xform_reverse = QgsCoordinateTransform(crsDest, crsSrc, QgsProject.instance())

        self.features = layer.getFeatures()
        self.features_geometry = []
        for feature in self.features:
            # retrieve every feature with its geometry and attributes
            self.features_geometry.append(feature.geometry())
        self.parkingAreas_on = parseParking("../cities/" + self.city + "/on_parking.add.xml")
        self.parkingAreas_off = parseParking('../cities/' + self.city + '/off_parking.add.xml')
        self.net = sumolib.net.readNet('../cities/' + self.city + '/' + self.city + '.net.xml')
        #edges = self.net.getEdges()

    def set_drop_off_percent(self, percent):
        self.drop_off_percentage = percent

    def generateParkingRerouter(self):
        edges = self.net.getEdges()
        edges_str = ''
        for edge in edges:
            edges_str = edges_str + edge.getID() + ' '
        edges_str = edges_str[:-1]

        with open("../cities/" + self.city + "/reroute_parking.xml", "w") as xml_writer:
            xml_writer.write('''<?xml version="1.0" encoding="UTF-8"?>\n''')
            xml_writer.write(
                '''<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">\n''')
            for parkingAreas, rerouter_id in zip([self.parkingAreas_on, self.parkingAreas_off], ['rerouter_on', 'rerouter_off']):
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

    def randomizeOriginDestination(self, trips_sorted):
        trips_sorted_randomized = []
        count = 0
        for trip in trips_sorted:
            if trip["mode"] == "walk":
                continue
            from_x = float(trip["from_x"])
            from_y = float(trip["from_y"])
            to_x = float(trip["to_x"])
            to_y = float(trip["to_y"])
            # fromPoint = QgsPoint(from_x, from_y)
            fromPoint_tr = self.xform_reverse.transform(from_x, from_y)
            fromPointGeometry = QgsGeometry.fromPointXY(fromPoint_tr)
            toPoint_tr = self.xform_reverse.transform(to_x, to_y)
            toPointGeometry = QgsGeometry.fromPointXY(toPoint_tr)
            # for from or to node falling inside a feature, we will randomly select a from or to coordinate for it
            for feature in self.features:
                if feature.contains(fromPointGeometry):
                    point_rand = randomPointInFeature(feature)
                    point_rand_tr = self.xform.transform(point_rand.x(), point_rand.y())
                    trip["from_x"] = str(point_rand_tr.x())
                    trip["from_y"] = str(point_rand_tr.y())
                if feature.contains(toPointGeometry):
                    point_rand = randomPointInFeature(feature)
                    point_rand_tr = xform.transform(point_rand.x(), point_rand.y())
                    trip["to_x"] = str(point_rand_tr.x())
                    trip["to_y"] = str(point_rand_tr.y())
            count += 1
            if count % 100 is 0:
                print("Trip: {}.".format(count))

            trips_sorted_randomized.append(trip)

        return trips_sorted_randomized

if __name__ == "__main__":
    flags_dict = {'all_7': True, '0.01': False, '0.05': False}
    city = 'fairfield'
    dataset = '0.01'

    x = Converter(city)
    x.generateParkingRerouter()

    trips = parseXML('../cities/' + city + '/' + city + '_plans_' + dataset + '.xml',
                     flags_dict[dataset])  # For 'plans_all_7', set to True; otherwise, set to False
    trips_sorted = sorted(trips, key=lambda k: k['from_end_time'])
    createAndSaveTripXML(trips_sorted, "../cities/" + city + "/originaltrip.xml")

    trips_sorted_randomized = randomizeOriginDestination(trips_sorted, features_geometry, xform, xform_reverse)
    createAndSaveTripXML(trips_sorted_randomized, "../cities/" + city + "/originaltrip_with_randomizedOD.xml")

    # createVehicleXML(trips_sorted)
    drop_off_percentage = 0.25
    createTripXML(city, trips_sorted_randomized, parkingAreas_on, parkingAreas_off, dataset, drop_off_percentage)