
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

login_manager = LoginManager(auth_bp)
login_manager.init_app(auth_bp)


class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@auth_bp.route(["/login","/"], methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "password123":
            user = User(id=username)
            login_user(user)
            return redirect(url_for("dashboard.dashboard"))
    return render_template("login.html")
