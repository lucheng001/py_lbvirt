#!/usr/bin/python3.6
#_*_ coding: utf-8 _*_

import libvirt
import logging

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
        return conn

    def close(self):
        self.conn.close()
        logging.info('connection closed!')

    def info(self):
        return self.conn.getInfo()

    def domains(self):
        domains = self.conn.listAllDomains()
        domain_uuids = []
        domain_names = []
        for dom in domains:
            domain_names.append(dom.name())
            domain_uuids.append(dom.UUIDString())
        return dict(zip(domain_names, domain_uuids ))

if __name__ == '__main__':
    host = Host()
    conn = host.connect()
    print(host.info())
    host.close()

