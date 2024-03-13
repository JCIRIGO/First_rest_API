from flask.views import MethodView
#request and response
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError
#user authentication
from flask_jwt_extended import jwt_required
#Database
from db import db
from models import TagModel, StoreModel, ItemModel, ItemsTagsModel
from schemas import TagSchema, TagAndItemSchema
#create a blueprint
blp = Blueprint('tags', __name__, description='operations on tags')

@blp.route('/store/<int:store_id>/tag')
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()     #'.tags' is lazy dynamic it is a query so we have to add '.all()'
    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.name == tag_data['name'], TagModel.store_id == store_id).first():
            abort (400, message='Tag already exists')
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)    
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))      #intersting way of using an error on a message
        return tag      

@blp.route('/item/<int:item_id>/tag/<int:tag_id>')
class LinkTagsToItems(MethodView):
    @jwt_required()
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        #Validation for existing link of tag and item
        if ItemsTagsModel.query.filter(ItemsTagsModel.tag_id == tag_id, ItemsTagsModel.item_id == item_id).first():
            abort(400, message='Tag already linked')   
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error ocurred while linking')
        return tag
    @jwt_required(fresh=True)
    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        #while TagModel.query.filter(ItemsTagsModel.tag_id == tag_id, ItemsTagsModel.item_id == item_id):
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))
        #except SQLAlchemyError:
        #    abort(500, message='An error ocurred while deleting')
        return {'message':'Item unlinked from tag', 'Item':item, 'Tag':tag}


@blp.route('/tag/<int:tag_id>')
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag   
    @jwt_required(fresh=True)
    @blp.response(202, description='Delete tag it not items linked', example={'message':'Tag deleted'})
    @blp.alt_response(404, description='Tag not found')
    @blp.alt_response(400, description='Tag assigned to items, not deleted')
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {'message':'Tag deleted'}
        abort(400, message='Tag assigned to items, not deleted')

#REMEMBER TO ADD VALIDATION TO THE TAG IF NAME IS SET AS UNIQUE=FALSE