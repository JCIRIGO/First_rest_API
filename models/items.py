from db import db

class ItemModel(db.Model):
    __tablename__ = 'items'     #create a table called items for all the object of this class

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)     #nullable=False means we can't create an item without name
    description = db.Column(db.String(), unique=False, nullable=True)
    price = db.Column(db.Float(2), nullable=False, unique=False)    #unique=False means different items can have the same price
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), unique=False, nullable=False)     #this stablish that the item id needs to match with the a store id otherwise it will not accept it
    #One to many
    store = db.relationship('StoreModel', back_populates='items')   
        #this stablishes a relationship so we can have 'StoreModel' data and/or methods as part of this class. But only if it matches with the store_id stablished by the foreign key
        #Back populates stablishes that store data can have the same with items
    #Many to many
    tags = db.relationship('TagModel', back_populates='items', secondary='items_tags')
        #we put a secondary relationship to where we have the many to many table 
