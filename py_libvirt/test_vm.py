#!/usr/bin/python3.6
#_*_ coding: utf-8 _*_

from host import Host
from dom_utils import ConfigureVM, VMInstance, create_img

class TestDom(object):
    '''test create , delete, start, shutdwon vm'''
    def __init__(self):
        host = Host()
        conn = host.connect()
        self.conn = conn

    def create_vm(self):
        configure_instance = ConfigureVM()
        img = create_img(name='/opt/vm_img/test.img', img_size='8G')
        vm_xml = configure_instance.conf_vm(name='Centos7', img=img, iso='/opt/iso/CentOS-7-x86_64-Minimal-1804.iso')
        vm_instance = VMInstance()
        dom = vm_instance.create_vm(conn=self.conn, vm_xml_file=vm_xml)
        if dom == -1:
            print('create vm failed')
        else:
            print('create vm succeed') 
            print('name: {}\nid: {}\nuuid: {}'.format(dom.name(), dom.ID(), dom.UUIDString()))
            print(vm_instance.vm_vnc_info())

if __name__ == '__main__':
    test_instance = TestDom()
    test_instance.create_vm()

