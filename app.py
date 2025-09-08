from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
# Import your forms from the forms.py
from forms import CafeForm, RegisterForm, LoginForm, CommentForm
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
csrf = CSRFProtect(app)

# For emoji in db
app.config['MYSQL_CHARSET'] = 'utf8mb4'
app.config['MYSQL_COLLATION'] = 'utf8mb4_unicode_ci'


# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes_wifi.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURE TABLES
# Create a User TABLE for all your registered users. 
class User(UserMixin, db.Model):
    __tablename__='users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    
    #This will act like a List of Cafes objects attached to each User. 
    #The "author" refers to the author property in the Cafes class.
    cafe = relationship("Cafes", back_populates="author")
    
    #*******Add parent relationship*******#
    #"comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")
    
class Cafes(db.Model):
    __tablename__ = "cafe"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'))

    #foreign_keys argument, which is a Column or list of Column objects which indicate those columns to be considered “foreign”, 
    # or in other words, the columns that contain a value referring to a parent table. 
    # Create reference to the User object. The "cafe" refers to the posts property in the User class.
    author = relationship("User", back_populates="cafe")

    cafe_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    open: Mapped[str] = mapped_column(String(250), nullable=False)
    close: Mapped[str] = mapped_column(Text, nullable=False)
    coffee_rating:Mapped[str] = mapped_column(String(250), nullable=False)
    wifi_rating:Mapped[str] = mapped_column(String(250), nullable=False)
    power_rating:Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    
    #***************Parent Relationship*************#
    comments = relationship("Comment", back_populates="comment_post")

class Comment(db.Model):
    __tablename__='comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    #*******Add child relationship*******#
    #"users.id" The users refers to the tablename of the Users class.
    #"comments" refers to the comments property in the User class.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments") # asta are atribut: 'comment_author.name'
    
    #***************Child Relationship*************#
    cafe_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("cafe.id"))
    comment_post = relationship("Cafes", back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False) 

with app.app_context():
    db.create_all()


# Hash the user's password when creating a new user and add it to data base:
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.cancel.data: 
        return redirect(url_for('get_all_cafes'))
    if form.validate_on_submit():
        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
            )
        new_user = User(
            email = form.email.data,
            password = hash_and_salted_password,
            name = form.name.data
            )
        db.session.add(new_user)
        db.session.commit()
        #This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for('get_all_cafes', current_user=current_user))
    return render_template("register.html", form=form)


# Retrieve a user from the database based on their email. 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.cancel.data:
        return redirect(url_for('get_all_cafes'))
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email==form.email.data))
        user = result.scalar()
        if not user :
            flash("That email does not exist, please try again! Or register!")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, form.password.data):
            flash("Password incorrect, please try again!")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_cafes'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_cafes'))


@app.route('/')
def get_all_cafes():
    # Get page number from query params (default = 1)
    page = request.args.get('page', 1, type=int)
    # Cafes per page  
    per_page = 3  
    pagination = Cafes.query.paginate(page=page, per_page=per_page, error_out=False)
    # page = request.args.get('page', 1, type=int)
    next_url = url_for('get_all_cafes', page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('get_all_cafes', page=pagination.prev_num) \
        if pagination.has_prev else None
    return render_template("index.html", all_cafes=pagination.items,
                           next_url=next_url, prev_url=prev_url, current_user=current_user)


# Logged-in users can comment on posts
@app.route("/cafe/<int:cafe_id>", methods=["GET", "POST"])
def show_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafes, cafe_id)
    # Add the CommentForm to the route
    comment_form = CommentForm()
    if comment_form.cancel.data: 
        return render_template("view_cafe.html", cafe=requested_cafe, current_user=current_user)
    if request.args.get('is_comment'):
        is_comment = request.args.get('is_comment')
        # What to be written in the text area.
        comment_form.body.data = 'Type your comment..'
        return render_template('view_cafe.html', 
                                   cafe=requested_cafe, 
                                   current_user=current_user, 
                                   form=comment_form, 
                                   is_comment=is_comment)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for('login'))
        new_comment = Comment(
                            text=comment_form.body.data,
                            comment_author = current_user,
                            comment_post = requested_cafe
                            )
        db.session.add(new_comment)
        db.session.commit()
        return render_template("view_cafe.html", cafe=requested_cafe, current_user=current_user)
    return render_template("view_cafe.html", cafe=requested_cafe, current_user=current_user)


# A decorator so only an admin user can create a new cafe
def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        # if a user is logged in
        if current_user.is_authenticated:  
        # If id is not 1 then return abort with 403 error
            if current_user.id != 1:
                return abort(403)
        # Otherwise continue with the route function
        else:    
            return abort(403)    
        return function(*args, **kwargs)
    return decorated_function

# A decorator so only an admin user can create new posts
@app.route("/new-cafe", methods=["GET", "POST"])
@admin_only
def add_new_cafe():
    form = CafeForm()
    if form.cancel.data: 
        return redirect(url_for('get_all_cafes', current_user=current_user))
    if form.validate_on_submit():
        new_cafe = Cafes(
            cafe_name=form.cafe_name.data,
            location=form.location.data,
            open=form.open.data,
            close=form.close.data,
            coffee_rating=form.coffee_rating.data,
            wifi_rating=form.wifi_rating.data,
            power_rating=form.power_rating.data,
            img_url=form.img_url.data,
            author_id = current_user.id
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("get_all_cafes"))
    return render_template("add.html", form=form, current_user=current_user)


# A decorator so only an admin user can edit a post 
@app.route("/edit-cafe/<int:cafe_id>", methods=["GET", "POST"])
@admin_only
def edit_cafe(cafe_id):
    cafe_to_edit = db.get_or_404(Cafes, cafe_id)
    edit_form = CafeForm(
        cafe_name = cafe_to_edit.cafe_name,
        location = cafe_to_edit.location,
        open = cafe_to_edit.open,
        close = cafe_to_edit.close,
        coffee_rating = cafe_to_edit.coffee_rating,
        wifi_rating = cafe_to_edit.wifi_rating,
        power_rating = cafe_to_edit.power_rating,
        img_url = cafe_to_edit.img_url
    ) 
    if edit_form.validate_on_submit():
        
        cafe_to_edit.cafe_name = edit_form.cafe_name.data 
        cafe_to_edit.location = edit_form.location.data
        cafe_to_edit.open = edit_form.open.data
        cafe_to_edit.author = current_user 
        cafe_to_edit.close = edit_form.close.data
        cafe_to_edit.coffee_rating=edit_form.coffee_rating.data
        cafe_to_edit.wifi_rating=edit_form.wifi_rating.data
        cafe_to_edit.power_rating=edit_form.power_rating.data
        cafe_to_edit.img_url=edit_form.img_url.data

        db.session.commit()
        return redirect(url_for('show_cafe', cafe_id=cafe_id, current_user=current_user))
    elif edit_form.cancel.data: 
        return redirect(url_for('show_cafe', cafe_id=cafe_id, current_user=current_user))
    return render_template("edit.html", form=edit_form, cafe=cafe_to_edit, current_user=current_user)


# Decorator so only an admin user can delete a cafe
@app.route("/delete/<int:cafe_id>")

@admin_only
def delete_cafe(cafe_id):
    cafe_to_delete = db.get_or_404(Cafes, cafe_id)
    if cafe_to_delete.comments:
        flash("You need to delete all comments before deleting a cafe!")
        return render_template("view_cafe.html", cafe=cafe_to_delete, current_user=current_user)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_cafes'))

@app.route("/delete/<int:cafe_id>/<int:comment_id>")
@admin_only
def delete_comment(comment_id, cafe_id):
    comment_to_delete = db.get_or_404(Comment, comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for('show_cafe', cafe_id=cafe_id, current_user=current_user))

@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)