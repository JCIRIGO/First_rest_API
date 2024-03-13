from db import db

class TagModel(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)   #if we set to True will mean that each tag will be unique so two stores can't have the same tags so we'll set to false and add validation
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), unique=False, nullable=False)    
    #One to many relationship
    stores = db.relationship('StoreModel', back_populates='tags')
    #Many to many relationship
    items = db.relationship('ItemModel', back_populates='tags', secondary='items_tags')
            #secondary will gives us the relationship we stablished in 'items_tags.py'
            # so we get the items that are related to this tag id
