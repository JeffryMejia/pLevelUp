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
        files = request.files.getlist('file')
        for file in files:
            if file and file.filename:
                filepath = os.path.join('media', file.filename)
                file.save(filepath)
                flash(f"Archivo '{file.filename}' cargado con éxito.", "success")
            else:
                flash("No se seleccionó un archivo válido.", "error")

    # List files in the media folder
    files = os.listdir('media')
    files_list_html = ''.join(f'<li><a href="{url_for("media", filename=file)}" target="_blank">{file}</a></li>' for file in files)
    
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 0;
                }
                header {
                    background-color: #333;
                    color: white;
                    padding: 15px 20px;
                    text-align: center;
                }
                .container {
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: white;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                }
                .btn {
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                .btn:hover {
                    background-color: #45a049;
                }
                .upload-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    margin-bottom: 30px;
                }
                #progress-container {
                    width: 100%;
                    margin-top: 20px;
                    display: none;
                }
                progress {
                    width: 100%;
                    height: 20px;
                    border-radius: 10px;
                }
                .file-list {
                    list-style-type: none;
                    padding: 0;
                }
                .file-list li {
                    margin: 10px 0;
                    font-size: 16px;
                }
                video {
                    width: 100%;
                    max-width: 600px;
                    margin-top: 20px;
                }
                .preview-container {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-bottom: 20px;
                }
                .preview-container img {
                    width: 150px;
                    height: 150px;
                    object-fit: cover;
                    border-radius: 8px;
                }
                footer {
                    text-align: center;
                    margin-top: 30px;
                    padding: 10px;
                    background-color: #333;
                    color: white;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>Dashboard</h1>
            </header>
            <div class="container">
                <div class="upload-container">
                    <form id="upload-form" method="post" enctype="multipart/form-data">
                        <input type="file" id="file" name="file" multiple required>
                        <button class="btn" type="submit">Subir Archivos</button>
                    </form>
                    <div id="preview-container" class="preview-container"></div>
                    <div id="progress-container">
                        <p>Subiendo archivo...</p>
                        <progress id="progress" value="0" max="100"></progress>
                        <p id="percent">0%</p>
                    </div>
                </div>
                <h2>Archivos Disponibles</h2>
                <ul class="file-list">
                    {{ files }}
                </ul>
                <a href="{{ url_for('logout') }}" class="btn">Logout</a>
            </div>
            <footer>
                <p>&copy; 2025 Multimedia Server</p>
            </footer>
            <script>
                const fileInput = document.getElementById('file');
                const previewContainer = document.getElementById('preview-container');
                const progressContainer = document.getElementById('progress-container');
                const progressBar = document.getElementById('progress');
                const percentText = document.getElementById('percent');
                const uploadForm = document.getElementById('upload-form');

                fileInput.addEventListener('change', function(event) {
                    previewContainer.innerHTML = '';
                    const files = event.target.files;

                    for (const file of files) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const fileUrl = e.target.result;
                            const fileType = file.type.split('/')[0];

                            let previewElement;
                            if (fileType === 'image') {
                                previewElement = document.createElement('img');
                                previewElement.src = fileUrl;
                            } else if (fileType === 'video') {
                                previewElement = document.createElement('video');
                                previewElement.src = fileUrl;
                                previewElement.controls = true;
                            }

                            const previewDiv = document.createElement('div');
                            previewDiv.appendChild(previewElement);
                            previewDiv.classList.add('preview');
                            previewContainer.appendChild(previewDiv);
                        };
                        reader.readAsDataURL(file);
                    }
                });

                uploadForm.onsubmit = function(event) {
                    event.preventDefault(); // Prevent form submission

                    const formData = new FormData();
                    const files = fileInput.files;
                    for (let i = 0; i < files.length; i++) {
                        formData.append('file', files[i]);
                    }

                    // Show progress container
                    progressContainer.style.display = 'block';

                    const xhr = new XMLHttpRequest();
                    xhr.open("POST", "{{ url_for('dashboard') }}", true);

                    // Update progress bar
                    xhr.upload.onprogress = function(event) {
                        if (event.lengthComputable) {
                            const percent = (event.loaded / event.total) * 100;
                            progressBar.value = percent;
                            percentText.textContent = `${Math.round(percent)}%`;
                        }
                    };

                    // On complete
                    xhr.onload = function() {
                        if (xhr.status == 200) {
                            alert("Archivos cargados con éxito.");
                        } else {
                            alert("Hubo un error al cargar los archivos.");
                        }
                        progressContainer.style.display = 'none';
                    };

                    xhr.send(formData);
                };
            </script>
        </body>
        </html>
    ''', files=files_list_html)

@app.route('/media/<path:filename>')
@login_required
def media(filename):
    return send_from_directory('media', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
