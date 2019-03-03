if __name__ == "main":
    filename = "../cities/fairfield/fairfield.rerouter.xml"
    on_parking = "../cities/fairfield/on-parking.add.xml"
    off_parking = "../cities/fairfield/off-parking.add.xml"

    with open(filename, 'wb') as xml_writer:
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