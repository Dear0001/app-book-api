from flask_restx import fields, reqparse
from app.extensions import *

user_model = api.model("UserModel", {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "password_hash": fields.String,
    "gender": fields.String,
    "role": fields.String,
})

login_model = api.model("LoginModel", {
    "username": fields.String,
    "password": fields.String
})

register_model = api.model("RegisterModel",{
    "username": fields.String,
    "email": fields.String,
    "password": fields.String,
    "gender": fields.String,
    "role": fields.String,
})

register_input_model = api.model("RegisterOutput",{
    "user": fields.Nested(user_model),
    "access_token": fields.String
})

profile_model = api.model("ProfileModel", {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "password_hash": fields.String,
    "gender": fields.String,
    "role": fields.String,
    "profile_image": fields.String,
})

profile_input_model = api.model("ProfileInputModel", {
    "username": fields.String(required=True),
    "email": fields.String(required=True),
    "password_hash": fields.String,
    "gender": fields.String,
    "role": fields.String,
    "profile_image": fields.String,
})

author_model = api.model("AuthorModel", {
    "id": fields.Integer,
    "author_name": fields.String,
    "author_decs": fields.String,
    "gender": fields.String,
    "author_image": fields.String,
})

author_input_model = api.model("AuthorInputModel", {
    "author_name": fields.String,
    "author_decs": fields.String,
    "gender": fields.String,
    "author_image": fields.String,
})

category_model = api.model("CategoryModel", {
    "id": fields.Integer,
    "name": fields.String,
})

category_input_model = api.model("CategoryInputModel", {
    "name": fields.String,
})

book_model = api.model("BookModel", {
    "id": fields.Integer,
    "title": fields.String,
    "description": fields.String,
    "price": fields.String,
    "publisher": fields.String,
    "category": fields.Nested(category_model),
    "author": fields.Nested(author_model),
    "book_image": fields.String,
    "book_pdf": fields.String,
})

book_input_model = api.model("BookInputModel", {
    "title": fields.String(required=True),
    "description": fields.String(required=True),
    "price": fields.String,
    "publisher": fields.String,
    "category_id": fields.Integer(required=True),
    "author_id": fields.Integer(required=True),
    "book_image": fields.String,
    "book_pdf": fields.String,
})

cart_model = api.model("CartModel", {
    "id" : fields.Integer,
    "user" : fields.Nested(user_model),
    "book": fields.Nested(book_model),
    "quantity" : fields.Integer,
})

cart_model_input = api.model("CartInputModel", {
    "user_id" : fields.Integer,
    "book_id" : fields.Integer,
    "quantity" : fields.Integer,
})

payment_model = api.model("PaymentModel", {
    'id': fields.Integer,
    'user': fields.Nested(user_model),
    'book': fields.Nested(book_model),
    'card_number': fields.String,
    'card_holder_name': fields.String,
    'expiration_date': fields.String,
    'cvv': fields.String,
    'price': fields.Float
})

payment_input_model = api.model("PaymentInputModel", {
    'user_id': fields.Integer(required=True, description='User ID'),
    'book_id': fields.Integer(required=True, description='Book ID'),
    'card_number': fields.String(required=True, description='Credit Card Number'),
    'card_holder_name': fields.String(required=True, description='Card Holder Name'),
    'expiration_date': fields.String(required=True, description='Expiration Date (MM/YY)'),
    'cvv': fields.String(required=True, description='CVV'),
    'price': fields.Float(required=True, description='Price'),
})

userbook_model = api.model("UserBook", {
    "id" : fields.Integer,
    "user" : fields.Nested(user_model),
    "book": fields.Nested(book_model)
})

userbook_model_input = api.model("UserInputBook", {
    "user_id" : fields.Integer,
    "book_id": fields.Integer
})

parser = reqparse.RequestParser()
parser.add_argument('user_id', type=int, help='User ID')
parser.add_argument('book_id', type=int, help='Book ID')
# image_model = api.model("ImageModel", {
#     "id": fields.Integer,
#     "file_path": fields.String
# })

# image_input_model = api.model("ImageInputModel", {
#     "file_path": fields.String(required=True)
# })

# pdf_model = api.model("PDFModel", {
#     "id": fields.Integer,
#     "file_path": fields.String
# })

# pdf_input_model = api.model("PDFInputModel", {
#     "file_path": fields.String(required=True)
# })
