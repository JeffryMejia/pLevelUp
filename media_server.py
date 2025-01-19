from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password123':  # Simple credentials
            user = User(id=username)
            login_user(user)
            return redirect(url_for('dashboard'))
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # Handle file upload
        file = request.files.get('file')
        if file and file.filename:
            filepath = os.path.join('media', file.filename)
            file.save(filepath)
            flash(f"Archivo '{file.filename}' cargado con éxito.", "success")
        else:
            flash("No se seleccionó un archivo válido.", "error")

    # List files in the media folder
    files = os.listdir('media')
    files_list_html = ''.join(f'<li><a href="{url_for("media", filename=file)}">{file}</a></li>' for file in files)
    return render_template_string('''
        <h1>Dashboard</h1>
        <form id="upload-form" method="post" enctype="multipart/form-data">
            <input type="file" id="file" name="file" required>
            <button type="submit">Subir Archivo</button>
        </form>
        <div id="progress-container" style="display:none;">
            <p>Subiendo archivo...</p>
            <progress id="progress" value="0" max="100" style="width: 100%;"></progress>
        </div>
        <ul>
            {{ files }}
        </ul>
        <a href="{{ url_for('logout') }}">Logout</a>
        {% with messages = get_flashed_messages(with_categories=True) %}
        {% if messages %}
            <ul>
            {% for category, message in messages %}
                <li><strong>{{ category }}</strong>: {{ message }}</li>
            {% endfor %}
            </ul>
        {% endif %}
        {% endwith %}
        <script>
            const uploadForm = document.getElementById('upload-form');
            const fileInput = document.getElementById('file');
            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('progress');
            
            uploadForm.onsubmit = function(event) {
                event.preventDefault(); // Prevent form submission

                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append("file", file);

                // Show progress container
                progressContainer.style.display = 'block';

                // Upload the file using AJAX (XMLHttpRequest)
                const xhr = new XMLHttpRequest();
                xhr.open("POST", "{{ url_for('dashboard') }}", true);

                // Update progress bar
                xhr.upload.onprogress = function(event) {
                    if (event.lengthComputable) {
                        const percent = (event.loaded / event.total) * 100;
                        progressBar.value = percent;
                    }
                };

                // On complete
                xhr.onload = function() {
                    if (xhr.status == 200) {
                        alert("Archivo cargado con éxito.");
                    } else {
                        alert("Hubo un error al cargar el archivo.");
                    }
                    // Hide progress bar after completion
                    progressContainer.style.display = 'none';
                };

                // Send the request with the form data
                xhr.send(formData);
            };
        </script>
    ''', files=files_list_html)

@app.route('/media/<path:filename>')
@login_required
def media(filename):
    return send_from_directory('media', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
