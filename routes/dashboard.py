
from flask import Blueprint, render_template, request, redirect, url_for, flash
import os

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")

if not os.path.exists("media"):
    os.makedirs("media")

@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        files = request.files.getlist("file")
        for file in files:
            if file and file.filename:
                filepath = os.path.join("media", file.filename)
                file.save(filepath)
                flash(f"Archivo '{file.filename}' cargado con éxito.", "success")

    files = os.listdir("media")
    return render_template("dashboard.html", files=files)
