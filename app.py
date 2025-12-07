# app.py
from flask import Flask, render_template
from dotenv import load_dotenv
from database import engine
from models import Base
from routes.upload_json_routes import register_upload_json_routes
from routes.sent_routes import register_sent_routes
from routes.drafts_routes import register_drafts_routes
from routes.logs_routes import register_logs_routes
from routes.compose_routes import register_compose_routes

load_dotenv()

# Create tables once (first run)
Base.metadata.create_all(bind=engine)

app = Flask(__name__)

register_upload_json_routes(app)
register_sent_routes(app)   
register_drafts_routes(app)   
register_logs_routes(app)   
register_compose_routes(app)   


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
