from db import db

class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship('ItemModel', back_populates='store', lazy='dynamic', cascade='all, delete')    
        #Lazy dynamic stablishes that the data of items will be fetched only when called, so we can save resources
        #Cascade, delete will delete all the child. If it wasnt there the child would deassociate and have its 
        #foreign key assigned to none. We can also use 'delete-orphan' if the related row is deassociated from the parent
    tags = db.relationship('TagModel', back_populates='stores', lazy='dynamic', cascade='all, delete')
