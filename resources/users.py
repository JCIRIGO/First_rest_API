from flask.views import MethodView
#request and response
from flask_smorest import abort, Blueprint
from schemas import UserSchema
#user authentication
from passlib.hash import pbkdf2_sha256      #this is a hashing algorithm sort of encryption
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt,
    create_refresh_token,
    get_jwt_identity)
#Database 
from db import db
from models import UserModel, BlocklistModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
#Adittional functions
from datetime import timedelta
#create a blueprint
blp = Blueprint('Users','users', __name__, description='operations on users')

@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )
        try: 
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A user with that username already exist")
        except SQLAlchemyError:
            abort(500, message="An error ocurred while inserting the user")
        return {'message':'user created succesfully'}

@blp.route('/users')
class Users(MethodView):
    @blp.response(200, UserSchema(many=True))
    def get(self):
        return UserModel.query.all()

@blp.route('/user/<int:user_id>')
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    @jwt_required(fresh=True)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message':'User deleted'}, 200

@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data['username']).first()
        if pbkdf2_sha256.verify(user_data['password'], user.password):
            acces_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
                #we create a refresh token for less important uses
            return {'access_token': acces_token, 'refresh_token':refresh_token}
        else:
            abort(401, message='Invalid credentials')
    

#will take a refresh token and return a non-fresh access token
@blp.route('/refresh')
class UserRefreshToken(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False, expires_delta=timedelta(minutes=30))
        jti = get_jwt()["jti"]
        jwt = BlocklistModel(jti=jti)
        """ THIS IS IF WE WANT TO MAKE THE NON-FRESH TOKEN ONE USE
        try:       
            db.session.add(jwt)
            db.session.commit()
        except:
            abort(401, message='Error while commiting')
        """
        return {"non_fresh_access_token": new_token}, 200

@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        #we get the jti (jwt id) from the jwt
        jti = get_jwt()['jti']      #we could ise get_jwt().get('jti')
        jwt = BlocklistModel(jti=jti)
        try:       
            db.session.add(jwt)
            db.session.commit()
        except:
            abort(401, message='Error')
        return {'message':'Logged out'}
        """
        jti = get_jwt()['jti']      #we could ise get_jwt().get('jti')
        BLOCKLIST.add(jti)             #This is if we wanted to store it in a py file
        return {'message':'Logged out'}
        """
    