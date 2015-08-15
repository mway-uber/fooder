from __future__ import absolute_import
import os
import signal
import sys
import time
# ---
import clay
import pymongo
import redis
import sqlalchemy
from flask_restful import Api
# ---
from .db import db
from .util.config import namespace as nsconfig
from .util.logger import LOG
from .ext.consumer import Consumer, ConsumerRequest


# if clay.config.get('debug.enabled', False):
#     db.create_all()


cfg         = nsconfig(prefix=__name__)
__version__ = cfg('version', 'dev')
api         = Api(app=clay.app, prefix='/api/{v}'.format(v=__version__))
LOG.debug('API bootstrapped under namespace {ns}'.format(ns=api.prefix))


for resource, routes in cfg('routes', {}).iteritems():
    for route in routes:
        try:
            parts = str(route['resource']).split('.')
            mod = __import__('.'.join(parts[:-1]), fromlist=[parts[-1]])
            api.add_resource(getattr(mod, parts[-1]), route['path'])
            LOG.info('Mounted {h} at {p}'.format(h=parts[-1], p=route['path']))
        except ImportError as e:
            LOG.warn('Could not load resource: {r}'.format(r=route['resource']))
