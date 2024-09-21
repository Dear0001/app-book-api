from flask_restx import Resource, Namespace, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.resources.api_models import *
from app.models import *
from app.extensions import db
from app.authorize import authorizations

ns_events = Namespace('events' , authorizations=authorizations)

ns_events.decorators = [jwt_required()]

@ns_events.route('/cart')
class EventListAPI(Resource):
    @ns_events.doc(security="jsonWebToken")
    @ns_events.marshal_list_with(cart_model)
    @jwt_required()
    def get(self):
        # Extract username from JWT token
        current_username = get_jwt_identity()

        # Get user object from the database
        user = User.query.filter_by(username=current_username).first()

        if not user:
            abort(404, message="User not found")

        # Retrieve cart items for the current user
        cart_items = Cart.query.filter_by(user_id=user.id).all()

        return cart_items, 200

    
    @ns_events.doc(security= "jsonWebToken")
    @ns_events.expect(cart_model_input)
    @ns_events.marshal_with(cart_model)
    @jwt_required()  # Ensure user is authenticated
    def post(self):
        add_cart_data = ns_events.payload

        # Extract username from JWT token
        current_username = get_jwt_identity()

        # Get user object from the database
        user = User.query.filter_by(username=current_username).first()

        # Extract book_id and quantity from the payload
        book_id = add_cart_data.get('book_id')
        quantity = add_cart_data.get('quantity')

        # Check if any of the required fields are missing
        if book_id is None or quantity is None:
            return {'message': 'Missing required fields in request payload'}, 400

        # Check if the user exists
        if not user:
            return {'message': 'User not found'}, 404

        # Check if the cart item already exists for the user and book
        existing_cart_item = Cart.query.filter_by(user_id=user.id, book_id=book_id).first()
        if existing_cart_item:
            # If the cart item already exists, update the quantity
            existing_cart_item.quantity += quantity
            db.session.commit()
            return existing_cart_item, 200
        else:
            # If the cart item doesn't exist, create a new one
            cart = Cart(
                user_id=user.id,
                book_id=book_id,
                quantity=quantity
            )
            db.session.add(cart)
            db.session.commit()
            return cart, 201
        
@ns_events.route('/cart/<int:id>')
class EventAPI(Resource):
    @ns_events.doc(security="jsonWebToken")
    @ns_events.marshal_with(cart_model)
    def get(self, id):
        cart = Cart.query.get(id)
        if not cart:
            abort(404, message="Cart item not found")
        return cart, 200

    @ns_events.doc(security="jsonWebToken")
    @ns_events.expect(cart_model_input)
    @ns_events.marshal_with(cart_model)
    def post(self, id):
        cart_data = ns_events.payload
        cart = Cart.query.get(id)
        if not cart:
            abort(404, message="Cart item not found")
    
    # Update the cart item with the provided data
        cart.user_id = cart_data.get("user_id", cart.user_id)
        cart.book_id = cart_data.get("book_id", cart.book_id)
        cart.quantity = cart_data.get("quantity", cart.quantity)
    
    # Commit the changes to the database
        db.session.commit()
    
        return cart, 200

            
    @ns_events.doc(security="jsonWebToken")
    @ns_events.expect(cart_model_input)
    @ns_events.marshal_with(cart_model)
    def put(self, id):
        cart_data = ns_events.payload
        cart = Cart.query.get(id)
        if not cart:
            abort(404, message="Cart item not found")
        cart.user_id = cart_data.get("user_id", cart.user_id)
        cart.book_id = cart_data.get("book_id", cart.book_id)
        cart.quantity = cart_data.get("quantity", cart.quantity)
        db.session.commit()
        return cart, 200

    @ns_events.doc(security="jsonWebToken")
    def delete(self, id):
        cart = Cart.query.get(id)
        if not cart:
            abort(404, message="Cart item not found")
        db.session.delete(cart)
        db.session.commit()
        return {}, 204  
    
@ns_events.route('/payment')
class PaymentAPI(Resource):
    @ns_events.doc(security="jsonWebToken")
    @ns_events.marshal_with(payment_model)
    def get(self):
        payments = Payment.query.all()
        return payments

    @ns_events.doc(security="jsonWebToken")
    @ns_events.expect(payment_input_model)
    @ns_events.marshal_with(payment_model)
    def post(self):
        payment_data = ns_events.payload
        payment = Payment(
            user_id=payment_data["user_id"],
            book_id=payment_data["book_id"],
            price=payment_data["price"],
            card_number=payment_data["card_number"],
            card_holder_name=payment_data["card_holder_name"],
            expiration_date=payment_data["expiration_date"],
            cvv=payment_data["cvv"]
        )
        db.session.add(payment)
        db.session.commit()
        return payment, 201

@ns_events.route('/payment/<int:id>')
class PaymentDetailAPI(Resource):
    @ns_events.doc(security="jsonWebToken")
    @ns_events.marshal_with(payment_model)
    def get(self, id):
        payment = Payment.query.get(id)
        if not payment:
            abort(404, message="Payment not found")
        return payment

    @ns_events.doc(security="jsonWebToken")
    @ns_events.expect(payment_input_model)
    @ns_events.marshal_with(payment_model)
    def put(self, id):
        payment_data = ns_events.payload
        payment = Payment.query.get(id)
        if not payment:
            abort(404, message="Payment not found")
        payment.user_id = payment_data.get("user_id", payment.user_id)
        payment.book_id = payment_data.get("book_id", payment.book_id)
        payment.price = payment_data.get("price", payment.price)
        payment.card_number = payment_data.get("card_number", payment.card_number)
        payment.card_holder_name = payment_data.get("card_holder_name", payment.card_holder_name)
        payment.expiration_date = payment_data.get("expiration_date", payment.expiration_date)
        payment.cvv = payment_data.get("cvv", payment.cvv)
        db.session.commit()
        return payment

    @ns_events.doc(security="jsonWebToken")
    def delete(self, id):
        payment = Payment.query.get(id)
        if not payment:
            abort(404, message="Payment not found")
        db.session.delete(payment)
        db.session.commit()
        return {}, 204
    
@ns_events.route('/userbook')
class UserBookAPI(Resource):
    @ns_events.doc(security="jsonWebToken")
    @ns_events.marshal_with(userbook_model)
    @jwt_required()
    def get(self):
        current_username = get_jwt_identity()
        user = User.query.filter_by(username=current_username).first()
        if not user:
            abort(404, message="User not found")

        userbooks = UserBook.query.filter_by(user_id=user.id).all()
        if not userbooks:
            abort(404, message="No UserBook entries found for the user")

        return userbooks

    @ns_events.doc(security="jsonWebToken")
    @ns_events.expect(userbook_model_input)
    @ns_events.marshal_with(userbook_model)
    @jwt_required()
    def post(self):
        userbook_data = ns_events.payload

        # Extract username from JWT token
        current_username = get_jwt_identity()

        # Get user object from the database
        user = User.query.filter_by(username=current_username).first()

        # Extract book_id from the payload
        book_id = userbook_data.get('book_id')

        # Check if book_id is present
        if book_id is None:
            return {'message': 'Missing book_id in request payload'}, 400

        # Check if the user exists
        if not user:
            return {'message': 'User not found'}, 404

        # Check if the user already has the book in their userbook entries
        existing_userbook = UserBook.query.filter_by(user_id=user.id, book_id=book_id).first()
        if existing_userbook:
            return {'message': 'User already has this book in their userbook entries'}, 400

        # Create a new userbook entry
        userbook = UserBook(
            user_id=user.id,
            book_id=book_id
        )
        db.session.add(userbook)
        db.session.commit()

        return userbook, 200
    
@ns_events.route('/userbook/<int:id>')
class UserBookDetailAPI(Resource):
    @ns_events.doc(security="jsonWebToken")
    def delete(self, id):
        userbook = UserBook.query.get(id)
        if not userbook:
            abort(404, message="UserBook entry not found")
        db.session.delete(userbook)
        db.session.commit()
        return {}, 204

