from flask import render_template

def register_index_routes(app):
    @app.route("/")
    def index():
        """
        Render the main WebMail page with:
        - Single message form (POST to /upload_json)
        - Bulk message form (POST to /upload_csv)
        - Sidebar navigation to other pages
        """
        return render_template("index.html")
