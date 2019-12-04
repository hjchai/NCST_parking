import sys
sys.path.append("/usr/share/qgis/python")
print(sys.path)

from qgis.core import * # python-qgis only works with python3.6.
import numpy as np

city = 'sf_residential'
file = open('../cities/' + city + '/' + city + '.poly.xml', 'w')
file.write('''<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo-sim.org/xsd/additional_file.xsd">\n''')
file.write("\n")

offSet = QgsPointXY(-549867.32, -4179840.29)
#offSet = QgsPointXY(-440044.55, -4068040.52)

# supply path to qgis install location
QgsApplication.setPrefixPath('/usr', True)

# create a reference to the QgsApplication, setting the
# second argument to False disables the GUI
qgs = QgsApplication([], False)

# load providers
qgs.initQgis()

# Write your code here to load some layers, use processing algorithms, etc.
layer = QgsVectorLayer('../cities/' + city + '/shp/' + city + '.shp', "selected_taz", "ogr")
if not layer.isValid():
    print("Layer failed to load!")

# create projection
crsSrc = QgsCoordinateReferenceSystem("EPSG:4326") # WGS 84
crsDest = QgsCoordinateReferenceSystem("EPSG:32610") # WGS 84 / UTM zone 10N
xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())

features = layer.getFeatures()

for feature in features:
    # retrieve every feature with its geometry and attributes
    print("Feature ID: ", feature.id())
    # fetch geometry
    # show some information about the feature geometry
    geom = feature.geometry()
    geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())

    if geom.type() == QgsWkbTypes.PointGeometry:
        # the geometry type can be of single or multi type
        if geomSingleType:
            x = geom.asPoint()
            print("Point: ", x)
        else:
            x = geom.asMultiPoint()
            print("MultiPoint: ", x)
    elif geom.type() == QgsWkbTypes.LineGeometry:
        if geomSingleType:
            x = geom.asPolyline()
            print("Line: ", x, "length: ", geom.length())
        else:
            x = geom.asMultiPolyline()
            print("MultiLine: ", x, "length: ", geom.length())
    elif geom.type() == QgsWkbTypes.PolygonGeometry:
        if geomSingleType:
            x = geom.asPolygon()
            print("Polygon: ", x, "Area: ", geom.area())
        else:
            x = geom.asMultiPolygon()
            print("MultiPolygon: ", x, "Area: ", geom.area())
            color = np.random.rand(3,)
            file.write('''<poly id="''' + str(feature.id()) + '''" color="''' + str(color[0]) + ',' +
                       str(color[1]) + ',' + str(color[2]) + '''" fill="true" layer="0" shape="''')
            for point in x[0][0]:
                pt_tr = xform.transform(point.x(), point.y())
                print(pt_tr)
                file.write(str(pt_tr.x() + offSet.x()) + ',' + str(pt_tr.y() + offSet.y()) + ' ')
            file.write('''"/>\n''')
    else:
        print("Unknown or invalid geometry")
    # fetch attributes
    attrs = feature.attributes()
    # attrs is a list. It contains all the attribute values of this feature
    print(attrs)


# When your script is complete, call exitQgis() to remove the
# provider and layer registries from memory
qgs.exitQgis()

file.write("\n")
file.write("</additional>")
# =======
# from PyQt5.QtCore import *
#
# layer = QgsProcessingUtils.mapLayerFromString("C:/Users/chaih/Desktop/NCST_parking/Caroline_NCST_Data/Communities_of_Concern_TAZ.shp", context)
# layer.name()
