#!/usr/bin/python3.6
#_*_ coding: utf-8 _*_

from host import Host
from dom_utils import ConfigureVM, VMInstance

class TestDom(object):
    '''test create , delete, start, shutdwon vm'''
    def __init__(self):
        host = Host()
        conn = host.connect()
        self.conn = conn

    def create_vm(self):
        configure_instance = ConfigureVM()
        vm_xml = configure_instance.conf_vm(name='Centos7', img='/opt/vm_img/test.img', iso='/opt/iso/CentOS-7-x86_64-Minimal-1804.iso')
        vm_instance = VMInstance()
        dom = vm_instance.create_vm(conn=self.conn, vm_xml_file=vm_xml)
        if dom == -1:
            print('create vm failed')
        else:
            print('create vm succeed') 
            print('name: {}\nid: {}\nuuid: {}'.format(dom.name(), dom.ID(), dom.UUIDString()))

if __name__ == '__main__':
    test_instance = TestDom()
    test_instance.create_vm()
