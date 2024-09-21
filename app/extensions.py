from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api,Resource
from flask_jwt_extended import JWTManager
from flask import Blueprint
from app.authorize import authorizations
from flask_login import LoginManager


api = Api(version='1.0', title= "ELibrary" , description="Test API" , authorizations=authorizations)

@api.route('/swagger')
class SwaggerResource(Resource):
    def get(self):
        return api.swagger_ui()
    
db = SQLAlchemy()
jwt = JWTManager()
login_manager = LoginManager()