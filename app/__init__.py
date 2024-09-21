from flask import Flask, jsonify
from flask_cors import CORS

from app.views.auth.auth import *
from app.views.main import *
from .config import Config
from .extensions import api, db, jwt, login_manager
from .models import *
from .resources import *


def create_app():
    app = Flask(__name__)
    CORS(app)
    config = Config()
    
    app.config.from_object(config)
    app.config['JWT_TOKEN_LOCATION'] = ["headers", "cookies"]
    app.config['SECRET_KEY'] = 'thisismysecretkeydontstealit'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = '07920ca637344a93a3403f4d062272f7'
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = None

    # app.config['UPLOAD_FOLDER'] = 'assets/'
   
    api.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    register_ns(api)
    
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main)
    # app.register_blueprint(api_bp)
    
    # @jwt.user_identity
    # def user_identity_lookup(user): 
    #     return user.id if user and hasattr(user, 'id') else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(username=identity).one_or_none()
    
    #additional claims
    @jwt.additional_claims_loader
    def make_addition_claims(identity):
        
        if identity == "admin":
            return {"is_user": True}
        return {"is_user": False}
    
    #jwt error handler
    @jwt.expired_token_loader
    def expires_token_callback(jwt_header, jwt_data):
        return jsonify({
                        "message": "Token has expired",
                        "error" : "token_expire"
                        }), 401
        
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
                        "message": "Signature verification failed",
                        "error" : "invalid_token"
                        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
                        "message": "Request doesn't contain valid token",
                        "error" : "authorization_header"
                        }), 401
        
    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header, jwt_data):
        jti = jwt_data['jti']
        
        token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()
        
        return token is not None 
        

    return app
