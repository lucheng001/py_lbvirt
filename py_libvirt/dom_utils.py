#!/usr/bin/python3.6
#_*_ coding: utf-8 _*_

import os
import uuid
import random
import subprocess
import logging
import xml.etree.ElementTree as ET

from common_utils import rsp_data
 
format_str = '%(levelname)s: %(asctime)s %(message)s'
logging.basicConfig(filename='../log/dom_utils.log', level=logging.INFO, format=format_str)

def xml2tree(filename=''):
    if not os.path.isfile(filename):
        logging.error('no suce configure file!')
    if not str(filename).split('.')[-1] == 'xml':
        logging.error('only xml file supported!')
    tree = ET.parse(filename)
    return rsp_data(0, '', tree) 

def tree2xml(tree):
    ramdom_id = str(uuid.uuid1())[0:8]
    xml_file = '../tmp/{}.xml'.format(ramdom_id)
    tree.write(xml_file)
    return rsp_data(0, '', xml_file)

def random_mac():
	mac = [ 0x00, 0x16, 0x3e,
		random.randint(0x00, 0x7f),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff) ]
	return rsp_data(0, '', ':'.join(map(lambda x: "%02x" % x, mac)))

def create_img(name=None, img_size=None, vm_type='qcow2'):
    args = ['qemu-img', 'create', '-f', vm_type, name, img_size]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if not stderr:
        logging.info('create vm img success for {}'.format(name))
        return rsp_data(0, '', name)
    return rsp_data(-1, 'failed to create cm img', None)


class ConfigureVM(object):
    def __init__(self, conf_file='./xml/baseconfig.xml'):
        tree = xml2tree(conf_file)['data']
        root = tree.getroot()
        self.tree = tree
        self.root = root
        pass

    def conf_vm(self, name=None, memory=None, vcpu=None, img=None, iso=None):
        if name:
            self.root[0].text = name
        if memory:
            self.root[2].text = memory
            self.root[3].text = memory
        if vcpu:
            self.root[4].text = str(vcpu)
        if img:
            self.root[13][1][1].attrib['file'] = img
        if iso:
            self.root[13][2][1].attrib['file'] = iso
        self.root[1].text = str(uuid.uuid1())
        self.root[13][9][0].attrib['address'] = random_mac()['data']
        return rsp_data(0, '', tree2xml(self.tree)['data'])


class VMInstance(object):
    def __init__(self, instance=None):
        self.dom = instance
        pass

    def create_vm(self, conn=None, vm_xml_file=None):
        if not vm_xml_file or not os.path.isfile(vm_xml_file):
            logging.error('no vm xml file found!')
            return rsp_data(-1, 'no vm xml file found', None)
        if not conn:
            logging.error('no alivable qemu server!')
            return rsp_data(-1, 'no alivable qemu server', None)
        try:
            vm_xml = open(vm_xml_file, 'r').read()
            os.remove(vm_xml_file)
            try:
                dom = conn.defineXML(vm_xml)
            except Exception as e:
                return rsp_data(-1, 'define domain failed\n{}'.format(e), None)
            #dom = conn.createXML(vm_xml, 0)
            logging.info('define domain succeed')
            if dom == None:
                logging.error('failed to create new vm!\n{}'.format(vm_xml))
                return rsp_data(-1, 'failed to define a domain from an xml definition', None)
            if dom.create() < 0:
                return rsp_data(0, 'create cm succeed but not boot guest domain', dom)
            logging.info('create new vm success!')
            self.dom = dom
            return rsp_data(0, 'create new vm succeed and booted', dom)
        except Exception as e:
            logging.error('create new vm failed!\n{}'.format(e))
            return rsp_data(-1, 'create new vm failed\n{}'.format(e), None)

    def remove_vm(self):
        pass

    def vm_vnc_info(self):
        args = ['virsh', 'vncdisplay', self.dom.UUIDString()]
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if not stderr:
            return rsp_data(0, '', stdout)
        return rsp_data(-1, '', None)

