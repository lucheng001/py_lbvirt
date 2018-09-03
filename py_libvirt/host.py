#!/usr/bin/python3.6
#_*_ coding: utf-8 _*_

import libvirt
import logging

from common_utils import rsp_data

format_str = '%(levelname)s: %(asctime)s %(message)s'
logging.basicConfig(filename='../log/host.log', level=logging.INFO, format=format_str)


class Host(object):
    '''connect to qemu host machine'''
    def __init__(self, uri='qemu:///system'):
        self.uri = uri
        self.conn = None

    def connect(self, conn_type='default', read_only=False):
        conn_type_list = ['default', 'openauth']
        if not conn_type in conn_type_list:
            logging.error('error connection type!')
        if conn_type == 'openauth':
            pass
        elif conn_type == 'default':
            if read_only:
                conn = libvirt.openReadOnly(self.uri)
            conn = libvirt.open(self.uri)
        logging.info('connected to qemu host!')
        self.conn = conn
        return rsp_data(0, 'connected to qemu host', conn)

    def close(self):
        self.conn.close()
        logging.info('connection closed!')

    def info(self):
        return rsp_data(0, '', self.conn.getInfo())

    def domains(self):
        domains = self.conn.listAllDomains()
        domain_uuids = []
        domain_names = []
        for dom in domains:
            domain_names.append(dom.name())
            domain_uuids.append(dom.UUIDString())
        return rsp_data(0, '', dict(zip(domain_names, domain_uuids )))

    def dom_by_id(self, dom_id):
        if self.conn:
            try:
                dom = self.conn.lookupByID(dom_id)
                if dom:
                    return rsp_data(0, '', dom)
                return rsp_data(0, 'domain {} not found!'.format(dom_id), None)
            except Exception as e:
                return rsp_data(-1, 'get dom by id error:\n{}'.format(e), None)
        return rsp_data(-1, 'not qemu host connected!', None)

    def dom_by_name(self, dom_name):
        if self.conn:
            try:
                dom = self.conn.lookupByName(dom_name)
                if dom:
                    return rsp_data(0, '', dom)
                return rsp_data(0, 'domain {} not found!'.format(dom_name), None)
            except Exception as e:
                return rsp_data(-1, 'get dom by name error:\n{}'.format(e), None)
        return rsp_data(-1, 'not qemu host connected!', None)

if __name__ == '__main__':
    host = Host()
    conn = host.connect()
    print(host.info())
    host.close()

