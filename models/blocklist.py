from db import db

class BlocklistModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, unique=True, nullable=True)

    