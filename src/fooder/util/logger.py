from __future__ import absolute_import
import logging
import sys
# ---
import clay
# ---
from .config import namespace as nsconfig


cfg = nsconfig(prefix=__name__)
LOG = logging.getLogger(__name__)
_debug = cfg('enabled', False, prefix='debug')
_loghdlr = None
_logfile = cfg('file')

if not _logfile and _debug:
    _loghdlr = logging.StreamHandler(stream=sys.stdout)
else:
    _loghdlr = logging.FileHandler(
        (_logfile or '{name}.log').format(name=__name__),
        mode=cfg('filemode', 'a'),
    )

_loghdlr.setFormatter(logging.Formatter(cfg('format', logging.BASIC_FORMAT)))
LOG.setLevel(cfg('level', 'DEBUG' if _debug else 'WARN'))
LOG.handlers = [_loghdlr]
LOG.propagate = 0
