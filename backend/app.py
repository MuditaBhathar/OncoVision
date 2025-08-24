from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from extensions import db_client, db
from auth import bp as auth_bp
from patients import bp as patients_bp
from pymongo import MongoClient

def create_app():
    global db_client, db  # Move this to the top

    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow CORS for React frontend
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    JWTManager(app)

    # Initialize MongoDB
    db_client = MongoClient(Config.MONGO_URI)
    db = db_client["oncoVisionDB"]

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
