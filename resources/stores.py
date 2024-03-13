from flask.views import MethodView
#request and respond
from flask_smorest import abort, Blueprint
from schemas import StoreSchema
#user authentication
from flask_jwt_extended import jwt_required, get_jwt
#Database
from models import StoreModel
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
#create a blueprint
blp = Blueprint('stores', __name__, description='operations on stores')

@blp.route('/store/<int:store_id>')
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store
    @jwt_required(fresh=True)
    def delete(self, store_id):
        #we only delete if user has admin priviledge
        jwt = get_jwt()
        if not jwt.get('is_admin'):
            abort(401, message='Admin priviledge required')
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {'message':'Store deleted'}

@blp.route('/store')
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))      #will return a list
    def get(self):
        return StoreModel.query.all()    
    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):       #schema will receive the request data in store_data
        #creating store object
        store = StoreModel(**store_data)
        #adding and commiting/save to database
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:      #for inconsistency in the data, for the constrains we set
            abort(400, message="A store with that name already exists")
        except SQLAlchemyError:
            abort(500, message="An error ocurred while receiving the store")
        return store    
