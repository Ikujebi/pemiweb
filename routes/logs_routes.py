from flask import render_template
from models import SessionLocal, SendLog

def register_logs_routes(app):
    @app.route("/logs")
    def logs():
        db = SessionLocal()
        logs_list = db.query(SendLog).all()
        db.close()
        return render_template("logs.html", logs=logs_list)
