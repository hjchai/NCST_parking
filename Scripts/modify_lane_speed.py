from lxml import etree

if __name__ == "__main__":

    speed_map = {"highway.residential":     "11.18",
                 "highway.secondary":       "11.18",
                 "highway.tertiary":        "11.18",
                 "highway.unclassified":    "11.18",
                 "highway.primary":         "11.18",
                 "highway.living_street":   "11.18",
                 "highway.motorway":        "29.06"}

    # original_net = "../cities/san_francisco/san_francisco.net.xml"
    # modified_net = "../cities/san_francisco/san_francisco_mod.net.xml"
    original_net = "../cities/fairfield/fairfield.net.xml"
    modified_net = "../cities/fairfield/fairfield_mod.net.xml"

    net_et = etree.parse(original_net).getroot()

    type_map = []

    for child in net_et.getchildren():
        if child.tag == "edge":
            if "function" in child.attrib: # it is a internal edge
                continue
            else: # normal edge
                if "type" in child.attrib: # it is an edge with type attribute
                    if child.attrib["type"] not in type_map:
                        type_map.append(child.attrib["type"])
                    for lane in child.getchildren():
                        if child.attrib["type"] in speed_map:
                            lane.attrib["speed"] = speed_map[child.attrib["type"]]
    net_str = etree.tostring(net_et, pretty_print=True, xml_declaration=False, encoding="utf-8").decode("utf-8")
    with open(modified_net, 'w') as f_obj:
        f_obj.write(net_str)