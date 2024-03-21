#-------SETUP-------
#new libraries needed
from flask import Flask, jsonify
from flask_smorest import Api
import os
from flask_jwt_extended import JWTManager
#database
from db import db
from models import BlocklistModel
from flask_migrate import Migrate, upgrade
#importing our blueprints
from resources.items import blp as ItemsBlueprint
from resources.stores import blp as StoresBlueprint
from resources.tags import blp as TagsBlueprint
from resources.users import blp as UsersBlueprint

def create_app(db_url=None):
    app = Flask(__name__)

    #app config
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    #app documentation 
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    #Database
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    def apply_migrations():
        with app.app_context():
            upgrade()
    apply_migrations()

    api = Api(app)

    #Create JWT secret key
    app.config["JWT_SECRET_KEY"] = "jose"
            #we should use 'str(secrets.SystemRandom().getrandbits(128))' instead
    jwt = JWTManager(app)

    #we check if a jwt is on the list of blocked jwts and if so we deny access
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = BlocklistModel.query.filter(BlocklistModel.jti == jwt_payload['jti']).first()
        if jti is None:
            return False
        return True
    
    #to modify the message if on blocklist
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return(
            jsonify({'description':'The token has been revoked','error':'token_revoked'}),
            401
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return(
            jsonify(
                {
                    "description":"The token is not fresh",
                    "error":"Fresh token required"
                }
            ),
            401
        )

    #we can add any additional information we want to a jwt in the payload
    #in this case we give admin priviledge to the id=1
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {'is_admin':True}
        return {'is_admin':False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return(
            jsonify({'message':'The token has expired','error':'token_expired'}),
            401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(
            jsonify({'message':'Signature verification failed','error':'invalid_token'}),
            401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify({'description':'Missing access token', 'error':'Authorization_required'}),
            401
        )

    """ This is deleted because we flask-migrate will create our tables now
    #Create tables before our first request
    with app.app_context():
        db.create_all()
    """
        
    api.register_blueprint(ItemsBlueprint)
    api.register_blueprint(StoresBlueprint)
    api.register_blueprint(TagsBlueprint)
    api.register_blueprint(UsersBlueprint)

    return app
