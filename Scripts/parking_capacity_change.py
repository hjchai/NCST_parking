import numpy as np
from lxml import etree, objectify


def park_cap_change(path, xmlfile, perc=0.1):
    additional = etree.parse(path + xmlfile).getroot()
    for parkingarea in additional.getchildren():
        print(parkingarea.attrib['roadsideCapacity'])
        parkingarea.attrib['roadsideCapacity'] = str(int(np.ceil(float(parkingarea.attrib['roadsideCapacity']) * perc)))
        print(parkingarea.attrib['roadsideCapacity'])

    with open(path + str(perc) +'_'+xmlfile, "w") as f_obj:
        parkingAreas_on_xml = etree.tostring(additional, pretty_print=True, xml_declaration=False,
                                         encoding="utf-8").decode("utf-8")
        f_obj.write(parkingAreas_on_xml)


path = '/home/huajun/Desktop/NCST_parking/cities/san_francisco/Scenario_Set_2/'
park_cap_change(path,'drop_off_parking.add.xml')
park_cap_change(path,'off_parking.add.xml')