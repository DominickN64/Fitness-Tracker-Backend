from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .database import collection
from bson import ObjectId
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)

@auth.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        userdata = collection.find_one({"email":email})
        
        
        if userdata:
            user = User(str(userdata["_id"]))
            if check_password_hash(userdata["password"], password):
                login_user(user, remember=True)
                flash('Logged in successfully', category='success')
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password, try again", category='error')
        else:
            flash("Account does not exist under that email.", category='error')
            


    return render_template("login.html", user = current_user)





@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out")
    return redirect(url_for("auth.login"))




@auth.route("/sign-up", methods = ["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user = collection.find_one({"email":email})
        if user:
            flash("Account with that email already exists", category="error")

        elif len(email) == 0:
            flash("Fill in email", category="error")
        elif len(firstName)==0:
            flash("Fill in first name", category="error")
        elif len(password1) == 0:
            flash("Fill in password", category="error")
        elif len(password2) == 0:
            flash("Fill in password confirmation", category="error")
        elif password1 != password2:
            flash("Passwords don't match", category="error")
        else:
            
            result = collection.insert_one({
            "email":email,
            "firstName":firstName,
            "password":generate_password_hash(password1, method='scrypt'),
            "notes":[]
            })
            

            
            new_user = User(str(result.inserted_id))
            flash("Account created", category="success")
            login_user(new_user, remember=True)
            return redirect(url_for("views.home"))
    

    
    
    return render_template("sign_up.html", user = current_user)


@auth.route("/settings/changePassword", methods = [ "POST"])
def changePassword():
    if request.method == "POST":
        password = request.form.get("password")
        if len(password) < 1:
            flash("Please enter a password")
        else:
            hashed_password = generate_password_hash(password, method='scrypt')
            collection.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {"password": hashed_password}})
            

            flash('Password changed successfully!')
        return redirect(url_for('views.settings'))
