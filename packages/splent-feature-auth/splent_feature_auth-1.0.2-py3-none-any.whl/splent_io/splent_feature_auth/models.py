from datetime import datetime

from flask_login import UserMixin
import pytz
from splent_io.splent_feature_profile.models import UserProfile
from splent_framework.db import db
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(256), unique=True, nullable=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(pytz.utc)
    )

    profile = db.relationship(UserProfile, backref="user", uselist=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "password" in kwargs:
            self.set_password(kwargs["password"])

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def temp_folder(self) -> str:
        import os
        from splent_framework.configuration.configuration import uploads_folder_name
        return os.path.join(uploads_folder_name(), "temp", str(self.id))
