# -*- encoding: utf-8 -*-

from pupylib.PupyModule import PupyArgumentParser
from pupylib.PupyOutput import Table

usage = 'list exposed objects/methods'
parser = PupyArgumentParser(description=usage)

def do(server, handler, config, modargs):
    for client in server.get_clients(handler.default_filter):
        objects = []
        with client.conn._conn._local_objects._lock:
            objects.extend(
                {'OID': id(klass), 'Object': repr(klass), 'Refs': refcnt}
                for klass, refcnt in client.conn._conn._local_objects._dict.itervalues()
            )
        handler.display(Table(
            objects,
            headers=['OID', 'Object', 'Refs'],
            caption=client.short_name()
        ))
