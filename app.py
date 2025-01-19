
from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, flash, Blueprint, render_template, request, redirect, url_for
from routes.dashboard import dashboard_bp
from routes.auth import auth_bp
from flask_login import LoginManager,UserMixin, login_user, logout_user, login_required
import os
import secrets


ckey = secrets.token_hex(16)
print(ckey)
app = Flask(__name__)
app.secret_key = ckey


login_manager = LoginManager()
login_manager.init_app(app)


# User authentication setup
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Ensure the media folder exists
if not os.path.exists('media'):
    os.makedirs('media')


# Register blueprints
app.register_blueprint(dashboard_bp)
# app.register_blueprint(auth_bp)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "password123":
            user = User(id=username)
            login_user(user)
            return redirect(url_for("dashboard.dashboard"))
    return render_template("login.html")
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if username == 'admin' and password == 'password123':  # Simple credentials
#             user = User(id=username)
#             login_user(user)
#             return redirect(url_for('dashboard'))
#     return 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Ensure the media folder exists
MEDIA_FOLDER = 'media'
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file and file.filename:
                filepath = os.path.join(MEDIA_FOLDER, file.filename)
                file.save(filepath)
                flash(f"Archivo '{file.filename}' cargado con éxito.", "success")
    return render_template('upload.html')


@app.route('/files', methods=['GET'])
@login_required
def list_files():
    files = os.listdir(MEDIA_FOLDER)
    return render_template('files.html', files=files)

    
@app.route('/media/<filename>')
@login_required
def media(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

@app.route('/view/<filename>')
@login_required
def view_file(filename):
    file_path = os.path.join(MEDIA_FOLDER, filename)
    if not os.path.exists(file_path):
        flash("El archivo no existe.", "error")
        return redirect(url_for('list_files'))
    return render_template('view_file.html', filename=filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


