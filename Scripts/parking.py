from lxml import etree, objectify

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
    fobj.close()

if __name__ == "__main__":
    parseParking('/home/huajun/Desktop/NCST_parking/cities/fairfield/on-parking.add.xml')