from __future__ import absolute_import
import uuid
# ---
from ..db import db


class BaseModel(object):
    @classmethod
    def slugify(klass):
        return str(uuid.uuid4())

    def save(self, commit=True, rollback_on_error=True):
        db.session.add(self)

        if commit:
            try:
                db.session.commit()
            except:
                if rollback_on_error:
                    db.session.rollback()
