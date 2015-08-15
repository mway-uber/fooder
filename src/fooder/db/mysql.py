from __future__ import absolute_import
import copy
# ---
import clay
import sqlalchemy
from flask.ext.sqlalchemy import SQLAlchemy
# ---
from ..util.config import namespace as nsconfig
from ..util.logger import LOG


base_opts = {
    'host': 'localhost',
    'port': 3306,
    'username': 'root',
    'password': None,
    'database': None,
    'encoding': 'utf-8',
}

known_connections = {
    'default': base_opts.copy()
}

cfg = nsconfig(prefix=__name__)
connections = {}

def load_connections(key='{ns}.connections'.format(ns=__name__), uconns=None):
    LOG.debug('Loading user connections...')
    conns = clay.config.get(key) if uconns is None else uconns.copy()
    if conns is not None:
        try:
            for name, opts in conns.iteritems():
                if not name in known_connections:
                    known_connections[name] = {}
                known_connections[name].update(opts)
        except:
            LOG.error('Could not add user connections to the list of known connections')
            pass
    else:
        LOG.debug('No user connections found.')


def get_connection(name='default', overwrite=False, **kwargs):
    if not name in connections:
        opts = base_opts.copy()
        if name in known_connections:
            opts.update(known_connections[name].copy())
        opts.update(kwargs)

        connection_uri = 'mysql+mysqldb://{user}{pw}@{host}:{port}{db}'.format(
            # We can safely ignore key checking because we've merged on top of known dicts
            host=(opts['host'] or base_opts['host']),
            port=(opts['port'] or base_opts['port']),
            user=(opts['username'] or base_opts['username']),
            pw=(':{p}'.format(p=opts['password']) if opts['password'] else ''),
            db=('/{d}'.format(d=opts['database']) if opts['database'] else ''),
        )

        try:
            clay.app.config['SQLALCHEMY_DATABASE_URI'] = connection_uri
            connections[name] = SQLAlchemy(clay.app)

            # wait to overwrite in case sqlalchemy throws an error on connection
            if overwrite:
                LOG.debug('Overwriting connection {n} with user-defined options'.format(n=name))
                known_connections[name] = opts
        except:
            LOG.critical('Could not connect to database')
            connections[name] = None

    return connections[name]


clay.app.config['SQLALCHEMY_ECHO'] = cfg('enabled', False, prefix='debug')
load_connections()
get_connection()
