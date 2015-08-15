from __future__ import absolute_import
import json
# ---
import requests
# ---
from ..models import BaseModel
from ..util.config import namespace as nsconfig
from ..util.logger import LOG


"""
Consumer.
- if arbiter, use to process results (callable)
- if no arbiter, return [Model(**result), ...]
"""
class Consumer(object):
    def __init__(self, arbiter=None, model=None, request=None, source=None, **reqopts):
        super(Consumer, self).__init__()
        self._arbiter = arbiter
        self._model = model
        self._request = request
        self._source = source
        self._reqopts = reqopts

    def consume(self, timeout=0):
        if not callable(self._arbiter):
            if self._model and self._model.__base__ is not BaseModel:
                LOG.error('{name} has no associated model or arbiter, aborting')
                raise ConsumerClientError('No associated model or arbiter')

        if not self._request:
            if not self._source:
                LOG.error('{name} has no available data source'.format(name=self))
                raise ConsumerClientError('No provided data source URL or request')
            self._request = ConsumerRequest(url=self._source, **self._reqopts)

        data = self._request.get()
        if self._arbiter:
            return self._arbiter(data)
        else:
            try:
                return [self._model(**d) for d in data]
            except Exception as e:
                raise ConsumerDataError('bad instantiation: {e}'.format(e=e.message))

    def _process_response(self, resp):
        pass


# instead of needing to perpetually re-issue requests with explicit URLs,
# let's wrap requests.Session so we can also reuse the same request
# e.g., req = ConsumerRequest(url='http://foo.bar/baz') for persistence,
#    or req = ConsumerRequest(); req.get('http://foo.bar/baz') for transience
class ConsumerRequest(requests.Session):
    def __init__(self, url=None, headers=None, timeout=0):
        super(ConsumerRequest, self).__init__()
        self.url = url
        if headers:
            try:
                self.headers.update(headers)
            except:
                pass

    def get(self, url=None, *args, **kwargs):
        req_url = url if url else self.url
        resp = super(ConsumerRequest, self).get(req_url, *args, **kwargs)

        ctype_parts = resp.headers.get('Content-Type', '').split(';')
        ctype = ctype_parts[0] if len(ctype_parts) > 0 else None

        if ctype != 'application/json':
            LOG.error('Underlying ConsumerRequest returned bad content type ({t}) from {u}'.format(t=ctype, u=req_url))
            raise ConsumerDataError('Invalid content type returned: {t}'.format(t=ctype))

        return resp.json()

class ConsumerClientError(Exception):
    pass

class ConsumerDataError(Exception):
    pass
