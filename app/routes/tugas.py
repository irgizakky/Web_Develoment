from flask import Blueprint, render_template

tugas_bp = Blueprint("tugas", __name__)

@tugas_bp.route("/")
def list_tugas():
    return render_template("tugas_list.html")
