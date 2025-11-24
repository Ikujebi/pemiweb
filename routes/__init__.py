def register_routes(app):
    from .index_routes import register_index_routes
    from .compose_routes import register_compose_routes
    from .sent_routes import register_sent_routes
    from .logs_routes import register_logs_routes
    from .upload_csv_routes import register_upload_csv_routes
    from .upload_json_routes import register_upload_json_routes
    from .drafts_routes import register_drafts_routes

    register_index_routes(app)
    register_compose_routes(app)
    register_logs_routes(app)
    register_upload_csv_routes(app)
    register_upload_json_routes(app)
    register_drafts_routes(app)
    register_sent_routes(app)
