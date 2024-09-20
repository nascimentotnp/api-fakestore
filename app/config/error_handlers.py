
from flask import render_template


def register_error_handlers(app):
    @app.errorhandler(403)
    def access_forbidden(error):
        return render_template('home/page-403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('home/page-404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('home/page-500.html'), 500
