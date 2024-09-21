from flask_restx import Resource, Namespace, abort
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from cloudinary.uploader import upload
from app.resources.api_models import *
from app.models import *
from app.extensions import db
from app.authorize import authorizations

ns_profile = Namespace('profile', authorizations=authorizations)
ns_author = Namespace('author', authorizations=authorizations)
ns_category = Namespace('category', description='Category operations', authorizations=authorizations)
ns_book = Namespace('books', description='Book operations', authorizations=authorizations)

ns_profile.decorators = [jwt_required()]
ns_author.decorators = [jwt_required()]
ns_category.decorators = [jwt_required()]
ns_book.decorators = [jwt_required()]

# Input profile
@ns_profile.route('/profile')
class ProfileAPIList(Resource):
    @ns_profile.doc(security="jsonWebToken")
    @ns_profile.marshal_list_with(profile_model)
    @jwt_required()
    def get(self):
        profiles = Profile.query.all()
        return profiles

    @ns_profile.doc(security="jsonWebToken")
    @ns_profile.expect(profile_input_model)
    @ns_profile.marshal_with(profile_model)
    @jwt_required()
    def post(self):
        data = ns_profile.payload
        profile = Profile(
            username=data["username"],
            email=data["email"],
            gender=data["gender"],  
            role=data["role"]
        )
        db.session.add(profile)
        db.session.commit()
        return profile, 201

# Update and delete search profile by id
@ns_profile.route('/profile/<int:id>')
class ProfileAPI(Resource):
    @ns_profile.doc(security="jsonWebToken")
    @ns_profile.marshal_with(profile_model)
    @jwt_required()
    def get(self, id):
        profile = Profile.query.get(id)
        if profile is None:
            return abort(404, message="Profile not found.")
        return profile

    @ns_profile.doc(security="jsonWebToken")
    @ns_profile.expect(profile_input_model)
    @ns_profile.marshal_with(profile_model)
    @jwt_required()
    def put(self, id):
        data = ns_profile.payload

        # Validate 'gender' field
        valid_genders = ["male", "female"]
        if "gender" in data and data["gender"].lower() not in valid_genders:
            return abort(400, message="Invalid value for 'gender'. Allowed values are 'male' or 'female'.")
        profile = Profile.query.get(id)

        if profile is None:
            # If the profile does not exist, create a new one
            profile = Profile(
                username = data["username"],
                email = data["email"],
                gender = data["gender"],
                role = data["role"],
                profile_image = data["profile_image"]
            )
            db.session.add(profile)
        else:
            # If the profile exists, update its fields
            profile.username = data.get("username", profile.username)
            profile.gender = data.get("gender", profile.gender)
            profile.role = data.get("role", profile.role)

        db.session.commit()
        return profile

    @ns_profile.doc(security="jsonWebToken")
    @jwt_required()
    def delete(self, id):
        profile = Profile.query.get(id)
        if profile is None:
            return abort(404, message="Profile not found.")

        db.session.delete(profile)
        db.session.commit()
        return {}, 204

@ns_book.route("/category")
class CategoryAPIList(Resource):
    @ns_book.doc(security="jsonWebToken")
    @ns_book.marshal_list_with(category_model)
    def get(self):
        return Category.query.all()

    @ns_book.doc(security="jsonWebToken")
    @ns_book.expect(category_input_model)
    @ns_book.marshal_with(category_model)
    def post(self):
        data = ns_book.payload
        category = Category(name=data["name"])
        db.session.add(category)
        db.session.commit()
        return category, 201

# Update and delete category by id
@ns_book.route('/category/<int:id>') 
class CategoryAPI(Resource):
    @ns_book.doc(security="jsonWebToken")
    @ns_book.marshal_with(category_model)
    def get(self, id):
        category = Category.query.get(id)
        if category is None:
            return abort(404, message="Category not found.")
        return category
    
    @ns_book.doc(security="jsonWebToken")
    @ns_book.expect(category_input_model)
    @ns_book.marshal_with(category_model)
    def put(self, id):
        data = ns_book.payload
        category = Category.query.get(id)

        if category is None:
            # If the category does not exist, create a new one
            category = Category(name=data["name"])
            db.session.add(category)
        else:
            # If the category exists, update its fields
            category.name = data.get("name", category.name)

        db.session.commit()
        return category
    
    @ns_book.doc(security="jsonWebToken")
    def delete(self, id):
        category = Category.query.get(id)
        if category is None:
            return abort(404, message="Category not found.")

        db.session.delete(category)
        db.session.commit()
        return {}, 204

@ns_author.route('/author')
class AuthorAPIList(Resource):
    @ns_author.doc(security="jsonWebToken")
    @ns_author.marshal_list_with(author_model)
    def get(self):
        return Author.query.all()
    
    # Add the necessary decorators, expect, and marshal_with for creating an author
    @ns_author.doc(security="jsonWebToken")
    @ns_author.expect(author_input_model)
    @ns_author.marshal_with(author_model)
    def post(self):
        data = ns_author.payload
        author = Author(
            author_name=data["author_name"],
            author_decs=data["author_decs"],
            gender=data["gender"]
        )
        db.session.add(author)
        db.session.commit()
        return author, 201

# Define update and delete author by ID endpoint
@ns_author.route('/author/<int:id>')
class AuthorAPI(Resource):
    @ns_author.doc(security="jsonWebToken")
    @ns_author.marshal_with(author_model)
    def get(self, id):
        author = Author.query.get(id)
        if author is None:
            return abort(404, message="Author not found.")
        return author

    @ns_author.doc(security="jsonWebToken")
    @ns_author.expect(author_input_model)
    @ns_author.marshal_with(author_model)
    def put(self, id):
        data = ns_author.payload
        author = Author.query.get(id)

        if author is None:
            # If the author does not exist, create a new one
            author = Author(
                author_name=data["author_name"],
                author_decs=data["author_decs"],
                gender=data["gender"]
            )
            db.session.add(author)
        else:
            # If the author exists, update its fields
            author.author_name = data.get("author_name", author.author_name)
            author.author_decs = data.get("author_decs", author.author_decs)
            author.gender = data.get("gender", author.gender)

        db.session.commit()
        return author

    @ns_author.doc(security="jsonWebToken")
    def delete(self, id):
        author = Author.query.get(id)
        if author is None:
            return abort(404, message="Author not found.")

        db.session.delete(author)
        db.session.commit()
        return {}, 204
    
@ns_book.route("/book")
class BookResource(Resource):
    @ns_book.doc(security="jsonWebToken")
    @ns_book.marshal_list_with(book_model)
    def get(self):
        books = Book.query.all()
        return books

    @ns_book.doc(security="jsonWebToken")
    @ns_book.expect(book_input_model)
    @ns_book.marshal_with(book_model)
    def post(self):
        data = ns_book.payload

        # Check if the provided author_id exists
        author = Author.query.get(data["author_id"])
        if author is None:
            return abort(400, message="Author not found.")

        # Check if the provided category_id exists
        category = Category.query.get(data["category_id"])
        if category is None:
            return abort(400, message="Category not found.")

        # Upload image to Cloudinary if available
        image_url = None
        if 'image_file' in data:
            image_file = data['image_file']
            upload_result = upload(image_file)
            image_url = upload_result['secure_url']

        # Upload PDF to Cloudinary if available
        pdf_url = None
        if 'pdf_file' in data:
            pdf_file = data['pdf_file']
            upload_result = upload(pdf_file)
            pdf_url = upload_result['secure_url']

        # Create a new book with the specified author, category, image, and pdf
        book = Book(
            title=data["title"],
            description=data["description"],
            price=data["price"],
            publisher=data['publisher'],
            category_id=data["category_id"],
            author_id=data["author_id"],
            book_image=image_url,
            book_pdf=pdf_url,
        )

        db.session.add(book)
        db.session.commit()

        return book, 201

@ns_book.route('/book/<string:title>')
class BookSearch(Resource):
    @ns_book.doc(security= "jsonWebToken")
    @ns_book.marshal_with(book_model)
    def get(self, title):
        # Perform a case-insensitive search for books by title
        books = Book.query.filter(func.lower(Book.title) == func.lower(title)).all()
        
        if not books:
            return abort(404, message="No books found with the given title.")
        
        return books

@ns_book.route('/book/<int:id>')
class BookAPI(Resource):
    @ns_book.doc(security="jsonWebToken")
    @ns_book.marshal_with(book_model)
    def get(self, id):
        # Retrieve the book by its ID and load its related author and category information
        book = Book.query.options(db.joinedload(Book.author), db.joinedload(Book.category)).get(id)
        if book is None:
            return abort(404, message="Book not found.")
        return book
    
    
    @ns_book.doc(security="jsonWebToken")
    @ns_book.expect(book_input_model)
    @ns_book.marshal_with(book_model)  
    def put(self, id):
        data = ns_book.payload
        book = Book.query.get(id)

        if book is None:
            return abort(404, message="Book not found.")

        # Check if the provided author_id exists
        author = Author.query.get(data["author_id"])
        if author is None:
            return abort(400, message="Author not found.")

        # Check if the provided category_id exists
        category = Category.query.get(data["category_id"])
        if category is None:
            return abort(400, message="Category not found.")

        # Update book fields
        book.title = data.get("title", book.title)
        book.description = data.get("description", book.description)
        book.price = data.get("price", book.price)
        book.publisher = data.get("publisher", book.publisher)
        book.category_id = data.get("category_id", book.category_id)
        book.author_id = data.get("author_id", book.author_id)

        # Update image if available
        if 'image_file' in data:
            image_file = data['image_file']
            upload_result = upload(image_file)
            book.book_image = upload_result['secure_url']

        # Update PDF if available
        if 'pdf_file' in data:
            pdf_file = data['pdf_file']
            upload_result = upload(pdf_file)
            book.book_pdf = upload_result['secure_url']

        db.session.commit()
        return book

    @ns_book.doc(security="jsonWebToken")
    def delete(self, id):
        book = Book.query.get(id)
        if book is None:
            return abort(404, message="Book not found.")

        db.session.delete(book)
        db.session.commit()
        return {}, 204


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt','png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Assuming you have defined the ImageModel in your models

# @ns_book.route('/image')
# class ImageResource(Resource):
#     @ns_book.doc(security="jsonWebToken")
#     @ns_book.expect(image_input_model)
#     @ns_book.marshal_with(image_model)
#     def post(self):
#         try:
#             file = request.files['file']

#             if 'file' not in request.files:
#                 return abort(400, message="No file part")
#             if file.filename == '':
#                 return abort(400, message="No selected file")

#             if file and allowed_file(file.filename):
#                 cloudinary_response = upload(file)
#                 cloudinary_url = cloudinary_response['secure_url']

#                 image = ImageModel(file_path=cloudinary_url)
#                 db.session.add(image)
#                 db.session.commit()

#                 return {"message": "Image uploaded successfully", "file_path": cloudinary_url}, 201

#             return abort(400, message="Invalid file extension")
#         except Exception as e:
#             return abort(500, message="Error uploading the image: {}".format(str(e)))
        
#     @ns_book.doc(security="jsonWebToken")
#     @ns_book.marshal_with(image_model)
#     def get(self):
#         images = ImageModel.query.all()
#         return images

# @ns_book.route('/pdf')
# class PDFResource(Resource):
#     @ns_book.doc(security="jsonWebToken")
#     @ns_book.expect(pdf_input_model)
#     @ns_book.marshal_with(pdf_model)
#     def post(self):
#         try:
#             file = request.files['file']

#             if 'file' not in request.files:
#                 return abort(400, message="No file part")
#             if file.filename == '':
#                 return abort(400, message="No selected file")

#             if file and allowed_file(file.filename):
#                 cloudinary_response = upload(file)
#                 cloudinary_url = cloudinary_response['secure_url']

#                 pdf = PDFModel(file_path=cloudinary_url)
#                 db.session.add(pdf)
#                 db.session.commit()

#                 return {"message": "PDF uploaded successfully", "file_path": cloudinary_url}, 201

#             return abort(400, message="Invalid file extension")
#         except Exception as e:
#             return abort(500, message="Error uploading the PDF: {}".format(str(e)))
    
#     @ns_book.doc(security="jsonWebToken")
#     @ns_book.marshal_with(pdf_model)
#     def get(self):
#         pdfs = PDFModel.query.all()
#         return pdfs
