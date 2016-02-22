#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import re
import codecs
import json
import timeit


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
ADDRESS = ["housenumber", "street", "postcode", "city"]
OSMFILE = "hyderabad_india.osm"
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]
mapping = { " St": " Street",
            "Ave": "Avenue",
            " rd": " Road",
            " rd ": " Road",
            "Rd": "Road",
            " Rd": " Road",
            "Rd,": " Road",
            "road":"Road",
            "ln": "Lane",
            "Ln": "Lane",
            "Apts": "Apartments",
            " st ": " Street",
            "RD": "Road",
            "Jn": "Junction"
          }

def update_name(name, mapping):
    '''
    This function is used to update/clean the tag attribute values that has key as "name"
    :param name: attribute values to be udpated/cleaned
    :param mapping: Predefined dictionary to compare the attribute values
    :return: updated/cleaned attribute values.
    '''
    for i in mapping:
        match = re.search(r'\b' +i+ r'\b', name)
        if match:
            #regular expression used to compare and substitute Mapping values.
            name = re.sub(i,mapping[i],name)
    return name

def shape_element(element):
    '''
    This method is used to set all the tag attributes to the predefined dictionary "node".
    It also has two nested dictionaries "created" and "address".
    :param element: XML file
    :return: node dictionary.
    '''
    node = {}
    if element.tag == "node" or element.tag == "way" :
        created = {}
        address = {}
        node_refs = []
        try:
            POS = []
            POS = [float(element.attrib['lat']),float(element.attrib['lon'])]
        except:
            pass
        node["pos"] = POS
        node["id"] = element.attrib["id"]
        node["type"] = element.tag
        node["visible"] = element.get("visible")
        for elem in element.iter("tag"):
            if elem.attrib['k'] == "amenity":
                node["amenity"] = clean_amenity(elem.attrib['v'])
            elif elem.attrib['k'] == "name":
                if len(elem.attrib['v']) > 1:
                    node["name"] = update_name(elem.attrib['v'], mapping)
            else:
                pass
        for i in element.attrib.keys():
            if i in CREATED:
                created[i] = element.attrib[i]
                node["created"] = created
        for addr in element:
            if addr.tag == "tag":
                if re.match(problemchars,addr.get('k')):
                    continue
                elif re.search(r'\w+:\w+:\w+', addr.get('k')):
                    pass
                elif addr.attrib['k'].startswith('addr'):
                    if addr.attrib['k'] == 'addr:postcode':
                        node["address"] = update_postalcode(addr.attrib['v'])
                    address[addr.get('k')[5:]] = addr.get('v')
                    node['address'] = address
                else:
                    pass
            else:
                if addr.tag == 'nd':
                    node_refs.append(addr.attrib['ref'])
                else:
                    pass
        if node_refs:
            node['node_refs'] = node_refs
        return node
    else:
        return None

def clean_amenity(val_amenity):
    '''
    This method is used to clean the amenity value in tag element.
    :param val_amenity: attribute value of the key "amenity"
    :return: cleaned value
    '''
    return re.sub(r'_'," ", val_amenity)

def update_postalcode(val_postalcode):
    '''
    This method is used to clean postalcode value.
    It removes any spaces between the digits in the postal code.
    :param val_postalcode:
    :return: cleaned postalcode
    '''
    return re.sub(r" ","", val_postalcode)

def process_map(file_in, pretty = True):
    '''
    # This function is used for Json conversion.
    :param file_in: OSM file
    :param pretty: True
    :return: clean JSON object.
    '''

    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():

    data = process_map(OSMFILE, True)

if __name__ == "__main__":
    test()