from PyQt5.QtCore import *

layer = QgsProcessingUtils.mapLayerFromString("C:/Users/chaih/Desktop/NCST_parking/Caroline_NCST_Data/Communities_of_Concern_TAZ.shp", context)
layer.name()