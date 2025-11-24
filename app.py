from flask import Flask
from routes import register_routes
from models import init_db  # Import the init_db function

app = Flask(__name__)

# Initialize database tables on app start
init_db()

# Register your routes
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)