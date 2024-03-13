from flask.views import MethodView
#request and responses
from flask_smorest import abort, Blueprint
from schemas import ItemSchema, ItemUpdateSchema
#user authentication
from flask_jwt_extended import jwt_required
#database
from db import db
from models import ItemModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
#blueprint
blp = Blueprint('items', __name__, description='operations on items')

@blp.route('/item/<int:item_id>')
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item
    @jwt_required()
    @blp.arguments(ItemUpdateSchema)    
    @blp.response(200, ItemSchema)          #we don't use 'ItemUpdateSchema' because we want to send back all the data fro the item including id and store id
    def put(self, item_data, item_id):      #schema does the json request for us. Item_id must be at the end because is a URL argument
        item = ItemModel.query.get(item_id)
        if item:
            item.name = item_data['name']
            item.price = item_data['price']
        else:
            item = ItemModel(id=item_id, **item_data)
        db.session.add(item)
        db.session.commit()
        return item
    @jwt_required(fresh=True)
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {'message':'Item deleted'}

@blp.route('/item')
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))       #'many=True' will return a list of values
    def get(self):
        return ItemModel.query.all()
    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):         #we now have the json request done by Schema      
        #We are creating an object not saving it in the database. We put it as **kwargs so the data can be unpacked.
        item = ItemModel(**item_data)  
        #Here we save it into the database
        try:
            db.session.add(item)    
            db.session.commit()
        except IntegrityError:
            abort(400, message="An Item with that name already exist")
        except SQLAlchemyError:
            abort(500, message="An error ocurred while inserting the item")
        return item
