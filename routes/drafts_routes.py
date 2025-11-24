from flask import render_template

def register_drafts_routes(app):
    @app.route("/drafts")
    def drafts():
        return render_template("drafts.html")
