from app.extensions import db
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    gender = db.Column(db.String(10))
    role = db.Column(db.String)

    profile = db.relationship('Profile', back_populates='user')
    user_payments = db.relationship('Payment', back_populates='user')


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=True)
    create_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.jti}>"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Profile(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    gender = db.Column(db.String(10))
    role = db.Column(db.String)
    profile_image = db.Column(db.String(255), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='profile')


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(50), nullable=False, unique=True)
    author_decs = db.Column(db.String(200), nullable=False, unique=True)
    gender = db.Column(db.String)
    author_image = db.Column(db.String(255), nullable=False)

    # Define the one-to-many relationship with back_populates
    books = db.relationship('Book', back_populates='author')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    books = db.relationship('Book', back_populates='category')


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    publisher = db.Column(db.String(20), nullable=False)
    book_image = db.Column(db.String(255), nullable=False)
    book_pdf = db.Column(db.String(255), nullable=False)

    # Define the many-to-one relationship with Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='books')

    # Define the many-to-one relationship with Author
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', back_populates='books')

    # # Define the one-to-one relationship for Image
    # image_id = db.Column(db.Integer, db.ForeignKey('image_model.id'))
    # image = db.relationship('ImageModel', back_populates='book', uselist=False)

    # # Define the one-to-one relationship for PDF
    # pdf_id = db.Column(db.Integer, db.ForeignKey('pdf_model.id'))
    # pdf = db.relationship('PDFModel', back_populates='book', uselist=False)

    # Define the relationship with Payment
    book_payments = db.relationship('Payment', back_populates='book')


# class ImageModel(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     file_path = db.Column(db.String(255), nullable=False)

#     # Define the one-to-one relationship with back_populates
#     book = db.relationship('Book', back_populates='image', uselist=False)

# class PDFModel(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     file_path = db.Column(db.String(255), nullable=False)

#     # Define the one-to-one relationship with back_populates
#     book = db.relationship('Book', back_populates='pdf', uselist=False)    

class BookAuthor(db.Model):
    __tablename__ = 'book_author'

    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    author = db.relationship('Author', back_populates='books_association')
    book = db.relationship('Book', back_populates='authors_association')


Author.books_association = db.relationship('BookAuthor', back_populates='author')
Book.authors_association = db.relationship('BookAuthor', back_populates='book')


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Define the relationship with back_populates
    user = db.relationship('User', back_populates='cart')
    book = db.relationship('Book', back_populates='carts')


# Modify the User and Book models to include the relationships with Cart
User.cart = db.relationship('Cart', back_populates='user')
Book.carts = db.relationship('Cart', back_populates='book')


class UserBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    user = db.relationship('User', back_populates='books')
    book = db.relationship('Book', back_populates='users')


User.books = db.relationship('UserBook', back_populates='user')
Book.users = db.relationship('UserBook', back_populates='book')


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    card_holder_name = db.Column(db.String(100), nullable=False)
    expiration_date = db.Column(db.String(5), nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Define the relationship with User and Book
    user = db.relationship('User', back_populates='user_payments')
    book = db.relationship('Book', back_populates='book_payments')
