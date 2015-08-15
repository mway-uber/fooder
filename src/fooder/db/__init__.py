from __future__ import absolute_import
# ---
from .mysql import connections as mysql_connections
from ..util.config import namespace as nsconfig


db = mysql_connections.get('default')
