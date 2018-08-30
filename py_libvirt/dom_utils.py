#!/usr/bin/python3.6
#_*_ coding: utf-8 _*_

import os
import uuid
import logging
import xml.etree.ElementTree as ET
 
format_str = '%(levelname)s: %(asctime)s %(message)s'
logging.basicConfig(filename='../log/dom_utils.log', level=logging.INFO, format=format_str)

def xml2root(filename=''):
    if not os.path.isfile(filename):
        logging.error('no suce configure file!')
    if not str(filename).split('.')[-1] == 'xml':
        logging.error('only xml file supported!')
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def root2xml(root):
    return ET.dump(root)

def configure_vm(conf_params=None):
    if not conf_params:
        logging.info('configure for nothing!')
        return 0
    root = xml2root('baseconfig.xml')
    devices = root[13]
    img_disk = devices[1]
    cd_disk = devices[2]
    interface = devices[9]

    name = root[0].text
    vm_uuid = root[1].text
    memory = root[2].text
    currentMemory = root[3].text
    vcpu = root[4].text
    mac = interface[0].attrib['address']
    img = img_disk[1].attrib['file']
    iso = cd_disk[1].attrib['file'] 

    print(name)
    print(vm_uuid)
    print(memory)
    print(currentMemory)
    print(vcpu)
    print(mac)
    print(img)
    print(iso)
    
    root[0].text = 'ArchLinux test'
    root[13][1][1].attrib['file'] = 'test mod img'
    print(root2xml(root))
