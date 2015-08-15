from __future__ import absolute_import
# ---
from ._base import BaseResource, BaseRepositoryResource
from ..models import db
from ..models.vendors import Vendor


FIELD_WHITELIST = [
    'type', 'name', 'slug', 'location', 'address', 'border_streets', 'latitude', 'longitude',
    'menu', 'schedule_pdf', 'status', 'created_at', 'updated_at'
]


class VendorRepositoryService(BaseRepositoryResource):
    def get(self):
        vendors = Vendor.query.all()
        return [{ key: str(val) for key, val in v.__dict__.items() if key in FIELD_WHITELIST } for v in vendors]
