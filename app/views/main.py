from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import * 
from app.extensions import db
from cloudinary.uploader import upload
from app.views.auth.form import *
from google_drive import upload_file

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/author', methods=['GET', 'POST'])
@login_required
def author():
    username = current_user.username
    form = AuthorForm()
    if form.validate_on_submit():
        author_name = form.author_name.data
        author_decs = form.author_decs.data
        gender = form.gender.data
        author_image = form.author_image.data
        
        # Upload image to Cloudinary
        cloudinary_response = upload(author_image)
        author_image_url = cloudinary_response['secure_url']

        new_author = Author(author_name=author_name,
                            author_decs=author_decs,
                            gender=gender, 
                            author_image=author_image_url)
        db.session.add(new_author)
        db.session.commit()
        flash('Author added successfully', 'success')
        return redirect(url_for('main.author'))
    
    authors = Author.query.all()
    return render_template('author.html', authors=authors, form=form, username=username)

@main.route('/author/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_author(id):
    author = Author.query.get_or_404(id)
    form = AuthorForm(obj=author)
    if form.validate_on_submit():
        form.populate_obj(author)
        
        # Check if a new image is uploaded
        if 'author_image' in request.files:
            author_image = form.author_image.data
            cloudinary_response = upload(author_image)
            author.author_image = cloudinary_response['secure_url']
        
        db.session.commit()
        flash('Author updated successfully', 'success')
        return redirect(url_for('main.author'))
    return render_template('edit_author.html', form=form, author=author)

@main.route('/author/delete/<int:id>', methods=['POST'])
@login_required
def delete_author(id):
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    flash('Author deleted successfully', 'success')
    return redirect(url_for('main.author'))

@main.route('/category', methods=['GET', 'POST'])
@login_required
def category():
    username = current_user.username
    form = CategoryForm()
    
    # Create operation
    if form.validate_on_submit():
        name = form.name.data
        
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully', 'success')
        return redirect(url_for('main.category'))
    
    # Read operation
    categories = Category.query.all()
    
    # Update operation
    if request.method == 'POST':
        if 'edit_category' in request.form:
            category_id = request.form.get('category_id')
            new_name = request.form.get('new_name')
            category = Category.query.get(category_id)
            if category:
                category.name = new_name
                db.session.commit()
                flash('Category updated successfully', 'success')
                return redirect(url_for('main.category'))
        
        # Delete operation
        elif 'delete_category' in request.form:
            category_id = request.form.get('category_id')
            category = Category.query.get(category_id)
            if category:
                db.session.delete(category)
                db.session.commit()
                flash('Category deleted successfully', 'success')
                return redirect(url_for('main.category'))
    
    return render_template('category.html', form=form, username=username, categories=categories)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.username
    form = ProfileForm()

    if form.validate_on_submit():
        try:
            username = form.username.data
            email = form.email.data
            gender = form.gender.data
            role = form.role.data
            profile_image = form.profile_image.data

            if profile_image and allowed_file(profile_image.filename):
                cloudinary_response = upload(profile_image)
                cloudinary_url = cloudinary_response['secure_url']

                profile = User.query.filter_by(username=username).first()
                if profile:
                    profile.email = email
                    profile.gender = gender
                    profile.role = role
                    profile.profile_image = cloudinary_url
                else:
                    profile = User(
                        username=username,
                        email=email,
                        gender=gender,
                        role=role,
                        profile_image=cloudinary_url
                    )
                db.session.add(profile)
                db.session.commit()

                flash('Profile created/updated successfully', 'success')
                return redirect(url_for('main.profile'))
            else:
                flash('Invalid profile image file extension', 'error')
        except Exception as e:
            flash('Error creating/updating profile: {}'.format(str(e)), 'error')

    profiles = User.query.all()

    if request.method == 'POST':
        if 'edit_profile' in request.form:
            profile_id = request.form.get('profile_id')
            new_username = request.form.get('new_username')
            new_email = request.form.get('new_email')
            new_gender = request.form.get('new_gender')
            new_role = request.form.get('new_role')
            new_profile_image = request.files.get('new_profile_image')

            if new_profile_image and allowed_file(new_profile_image.filename):
                cloudinary_response = upload(new_profile_image)
                new_cloudinary_url = cloudinary_response['secure_url']

                profile = User.query.get(profile_id)
                if profile:
                    profile.username = new_username
                    profile.email = new_email
                    profile.gender = new_gender
                    profile.role = new_role
                    profile.profile_image = new_cloudinary_url
                    db.session.commit()
                    flash('Profile updated successfully', 'success')
                    return redirect(url_for('main.profile'))
            else:
                flash('Invalid profile image file extension', 'error')

    return render_template('profile.html', form=form, profiles=profiles, username=username)

@main.route('/profile/delete/<int:id>', methods=['POST'])
@login_required
def delete_profile():
    profile = Profile.query.get_or_404(id)
    db.session.delete(profile)
    db.session.commit()
    flash('Profile deleted successfully', 'success')
    return redirect(url_for('main.profile'))


@main.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    username = current_user.username
    form = BookForm()
    if form.validate_on_submit():
        # Retrieve form data
        title = form.title.data
        description = form.description.data
        price = form.price.data
        publisher = form.publisher.data
        author_id = form.author.data
        category_id = form.category.data
        book_image = form.image.data 
        book_pdf = form.file.data
                
        # Check if all required fields are present
        if title and description and price and publisher and author_id and category_id and book_image and book_pdf:
            # Handle file uploads (image and book file)
            if allowed_file(book_image.filename) and allowed_file(book_pdf.filename):
                # Upload image to Cloudinary
                cloudinary_response_image = upload(book_image)
                image_url = cloudinary_response_image['secure_url']
                
                # Upload PDF to Google Drive and get secure URL
                pdf_url = upload_file(book_pdf)
                
                # Create a new book entry
                new_book = Book(
                    title=title,
                    description=description,
                    price=price,
                    publisher=publisher,
                    category_id=category_id,
                    author_id=author_id,
                    book_image=image_url,
                    book_pdf=pdf_url  # Store PDF URL in the database
                )
                
                # Add the new book to the database session
                db.session.add(new_book)
                # Commit changes to the database
                db.session.commit()

                flash('Book added successfully', 'success')
                return redirect(url_for('main.book')) 
            else:
                flash('Invalid file extension for image or book file', 'error')
        else:
            flash('Please fill in all the required fields', 'error')

    books = Book.query.all()
    authors = Author.query.all()
    categories = Category.query.all()
    
    return render_template('book.html', form=form, books=books, authors=authors, categories=categories, username=username)

@main.route('/book/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        form.populate_obj(book)
        db.session.commit()
        flash('Book updated successfully', 'success')
        return redirect(url_for('main.book'))
    return render_template('edit_book.html', form=form, book=book)

@main.route('/book/delete/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully', 'success')
    return redirect(url_for('main.book'))

@main.route('/dashboard')
@login_required
def dashboard():
    username = current_user.username
    return render_template('dashboard.html', username=username)

    
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
