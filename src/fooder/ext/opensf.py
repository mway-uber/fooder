from __future__ import absolute_import
import json
# ---
import requests
# ---
from .consumer import Consumer
from ..models import db
from ..models.vendors import Vendor
from ..util.config import namespace as nsconfig
from ..util.logger import LOG


cfg = nsconfig(prefix=__name__)
headers = { 'X-App-Token': cfg('token') }
consumer = Consumer(source=cfg('source'), model=Vendor, headers=headers)


def import_data():
    vendors = consumer.consume()
    mapped_vendors = { v.sf_object_id: v for v in vendors }
    existing_vendors = Vendor.query.filter(Vendor.sf_object_id.in_(mapped_vendors.keys())).all()

    for v in existing_vendors:
        mapped_vendors[v.sf_object_id] = v

    for v in mapped_vendors.values():
        db.session.add(v)
    db.session.commit()


def _update_existing(vendors):
    api_ids = [v.sf_object_id for v in vendors]
    return Vendor.query.filter(Vendor.sf_object_id.in_(api_ids)).all()


def _create_new(vendors):
    api_ids = [v.sf_object_id for v in vendors]
    return Vendor.query.filter(Vendor.sf_object_id.notin_(api_ids)).all()


#import_data()
