from __future__ import absolute_import
import datetime
import re
# ---
import sqlalchemy
# ---
from ..models import BaseModel
from ..models import db


# PROPERTY_MAP = {
#     'address': 'address',
#     'applicant': 'name',
#     'facilitytype': 'type',
#     'fooditems': 'menu',
#     'latitude': 'latitude',
#     'locationdescription': 'border_streets',
#     'longitude': 'longitude',
#     'permit': 'sf_permit_id',
#     'schedule': 'schedule_pdf',
# }

# SANITIZE_MAP = {
#     'address': lambda x: re.sub(r'\s0(\d)', r' \1', x),
#     'locationdescription': lambda x: re.sub(r'.*?\:\s*(.+?)\s*to\s*(.+?)\s*\(.*', r'\1 and \2', x),
#     'fooditems': lambda x: ','.join([s.strip(' .').lower() for s in x.split(':')]),
# }


class Vendor(BaseModel, db.Model):
    __tablename__   = 'vendors'
    id              = db.Column(db.Integer, primary_key=True)
    slug            = db.Column(db.String(64), default=BaseModel.slugify)
    type            = db.Column(db.String(32))
    name            = db.Column(db.String(128))
    address         = db.Column(db.String(128))
    border_streets  = db.Column(db.String(128))
    latitude        = db.Column(db.Float(16))
    longitude       = db.Column(db.Float(16))
    menu            = db.Column(db.Text)
    schedule_pdf    = db.Column(db.String(256))
    status          = db.Column(db.String(16))
    permit_status   = db.Column(db.String(16))
    sf_object_id    = db.Column(db.String(16), unique=True)
    sf_permit_id    = db.Column(db.String(16))
    created_at      = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at      = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    deleted_at      = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        # Do we want to sanitize at assignment time?
        #props = dict([(PROPERTY_MAP[t[0]], SANITIZE_MAP[t[0]](t[1]) if t[0] in SANITIZE_MAP else t[1]) for t in kwargs.items() if t[0] in PROPERTY_MAP])

        # Do we want to remap default property names internally instead of aliasing via the API's DQL?
        #props = dict([(PROPERTY_MAP[t[0]], t[1]) for t in kwargs.items() if t[0] in PROPERTY_MAP])
        #props = dict([(PROPERTY_MAP.get(t[0], t[0]), t[1]) for t in kwargs.items()])

        # Let's just keep it simple for now.
        props = kwargs.copy()
        super(Vendor, self).__init__(**props)
        self._sanitize()

    def _sanitize(self):
        if self.address:
            self.address = re.sub(r'\s0(\d)', r' \1', self.address)
        if self.border_streets:
            self.border_streets = re.sub(r'.*?\:\s*(.+?)\s*to\s*(.+?)\s*\(.*', r'\1 and \2', self.border_streets)
        if self.menu:
            self.menu = ','.join([s.strip(' .').lower() for s in self.menu.split(':')])
        else:
            self.__setattr__('menu', 'n/a')

    def save(self, commit=True):
        try:
            super(Vendor, self).save(commit=commit)
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
