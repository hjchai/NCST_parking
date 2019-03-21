import pandas as pd
import numpy as np

file = open("../sfpark/sf.poly.xml", "w")
file.write('''<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo-sim.org/xsd/additional_file.xsd">\n''')
file.write("\n")

offSet = [-549867.32, -4179840.29]
poly_pts = pd.read_csv("roi_poly.csv")
x = poly_pts['X'] + offSet[0]#use 'X'
y = poly_pts['Y'] + offSet[1]
file.write('''<poly id="1" color="RED" fill="true" layer="0" shape="''')
for pt in zip(x, y):
    file.write(str(pt[0])+','+str(pt[1])+' ')
file.write('''"/>\n''')

file.write("\n")
file.write("</additional>")