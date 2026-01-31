import os
from flask import Flask, jsonify
from flask_cors import CORS
from models import db

def create_app():
    app = Flask(__name__)
    CORS(app) # Enable Cross-Origin Resource Sharing for React frontend

    # Database Configuration (SQLite for local prototype)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crypto_investigation.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Log database location
    print(f"[INFO] Database configured: {db_path}")

    # Register Blueprints (Routes)
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create Database Tables if they don't exist
    with app.app_context():
        db.create_all()
        print(f"[INFO] Database tables initialized")

    @app.route('/')
    def index():
        return jsonify({"status": "Cybercrime Investigation System Backend Running", "version": "1.0"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
