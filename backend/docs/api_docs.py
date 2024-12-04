from flask import Blueprint, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import os

# Configuration Swagger UI
SWAGGER_URL = '/api/docs'
API_URL = '/static/openapi.yml'

# Blueprint pour la documentation
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Nutrition Tracking API"
    }
)

# Blueprint pour servir le fichier OpenAPI
docs_blueprint = Blueprint('docs', __name__)

@docs_blueprint.route('/static/openapi.yml')
def serve_openapi_spec():
    """Sert le fichier de spécification OpenAPI"""
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(docs_dir, 'openapi.yml')

def setup_docs(app):
    """Configure la documentation API dans l'application"""
    app.register_blueprint(swagger_ui_blueprint)
    app.register_blueprint(docs_blueprint)

    # Configuration CORS pour la documentation
    @app.after_request
    def after_request(response):
        if request.path.startswith(SWAGGER_URL):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
