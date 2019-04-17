# this script is used to split large matsim dataset into smaller datasets based on city location

from lxml import etree, objectify
import os, sys
from qgis.core import *


def split_XML(source_dataset, target_dataset, ext, xform_reverse, is_all):

    with open(target_dataset, 'w') as xml_writer, open(source_dataset, 'r') as xml_reader:

        xml_writer.write('''<?xml version="1.0" encoding="UTF-8"?>\n''')
        xml_writer.write('''<!DOCTYPE population SYSTEM "http://www.matsim.org/files/dtd/population_v6.dtd">\n''')
        xml_writer.write('''<population desc="population written from streaming">\n''')
        xml_writer.write('''\n''')

        person_count = 0
        for event, person in etree.iterparse(source_dataset, tag="person"):
            if not is_all:
                plan = person[1] # all_7: plan=person[0], for the rest: plan=person[1]
            else:
                plan = person[0]
            num_trips = int((len(plan.getchildren()) - 1) / 2)
            for num in range(num_trips):
                from_activity = plan.getchildren()[2 * num]
                to_activity = plan.getchildren()[2 * num + 2]

                from_x = from_activity.attrib["x"]
                from_y = from_activity.attrib["y"]
                to_x = to_activity.attrib["x"]
                to_y = to_activity.attrib["y"]

                from_x = float(from_x)
                from_y = float(from_y)
                to_x = float(to_x)
                to_y = float(to_y)

                fromPoint_tr = xform_reverse.transform(from_x, from_y)
                toPoint_tr = xform_reverse.transform(to_x, to_y)

                if ext.contains(fromPoint_tr) or ext.contains(toPoint_tr):
                    print("{} th person.".format(person_count))
                    person_count = person_count + 1
                    obj_xml = etree.tostring(person,
                                             pretty_print=True,
                                             xml_declaration=False,
                                             encoding="utf-8").decode("utf-8")
                    xml_writer.write(obj_xml)
                    break
            person.clear()  # free memory for the person that is already processed`
        xml_writer.write('''</population>''')
        xml_writer.close()
        print("Total person count = {}".format(person_count))
    return


if __name__ == "__main__":
    # specify city information
    city_shapefile = "../cities/san_francisco/shp/downtown_taz.shp"
    flags_dict = {'all_7': True, '0.01': False, '0.05': False}
    dataset = '0.01'
    source_dataset = '../Caroline_NCST_Data/Scenario_1/matsim_input/plans_' + dataset + '.xml'
    target_dataset = '../cities/san_francisco/san_francisco_plans_' + dataset + '.xml'

    # supply path to qgis install location
    QgsApplication.setPrefixPath('/usr', True)

    # create a reference to the QgsApplication, setting the
    # second argument to False disables the GUI
    qgs = QgsApplication([], False)

    # load providers
    qgs.initQgis()
    layer = QgsVectorLayer(city_shapefile, "", "ogr")  # ../Caroline_NCST_Data/Communities_of_Concern_TAZ.shp
    if not layer.isValid():
        raise Exception("Layer failed to load!")

    # create projection
    crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
    crsDest = QgsCoordinateReferenceSystem("EPSG:32610")  # WGS 84 / UTM zone 10N
    xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
    xform_reverse = QgsCoordinateTransform(crsDest, crsSrc, QgsProject.instance())

    ext = layer.extent()

    features = layer.getFeatures()
    features_geometry = []
    for feature in features:
        # retrieve every feature with its geometry and attributes
        features_geometry.append(feature.geometry())

    split_XML(source_dataset, target_dataset, ext, xform_reverse, flags_dict[dataset]) # For 'plans_all_7', set to True; otherwise, set to False
