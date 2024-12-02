from flask import Flask
from flask_cors import CORS
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)  # Enable CORS for all routes


    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    from app.routes import api
    app.register_blueprint(api)

    return app
