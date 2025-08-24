# # auth.py
# from flask import Blueprint, request, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_jwt_extended import create_access_token
# from config import PREDEFINED_DOCTOR_IDS
# from extensions import db  # Use db from extensions.py

# bp = Blueprint("auth", __name__, url_prefix="/auth")

# # ---------------- Register ----------------
# @bp.post("/register")
# def register():
#     data = request.json or {}
#     name = data.get("name", "").strip()
#     doctor_uid = data.get("doctor_id", "").strip()   # match frontend field
#     password = data.get("password", "").strip()

#     if doctor_uid not in PREDEFINED_DOCTOR_IDS:
#         return jsonify({"error": "Doctor ID not authorized"}), 400
#     if not name or not doctor_uid or not password:
#         return jsonify({"error": "Missing fields"}), 400

#     if db.doctors.find_one({"doctor_uid": doctor_uid}):
#         return jsonify({"error": "Doctor already registered"}), 400

#     new_doctor = {
#         "name": name,
#         "doctor_uid": doctor_uid,
#         "password_hash": generate_password_hash(password)
#     }
#     db.doctors.insert_one(new_doctor)

#     return jsonify({"message": "Registered"}), 201


# # ---------------- Login ----------------
# @bp.post("/login")
# def login():
#     data = request.json or {}
#     doctor_uid = data.get("doctor_id", "").strip()  # match frontend
#     password = data.get("password", "").strip()

#     if not doctor_uid or not password:
#         return jsonify({"error": "Missing fields"}), 400

#     doctor = db.doctors.find_one({"doctor_uid": doctor_uid})
#     if not doctor or not check_password_hash(doctor["password_hash"], password):
#         return jsonify({"error": "Invalid credentials"}), 401

#     access_token = create_access_token(identity={
#         "doctor_uid": doctor["doctor_uid"],
#         "name": doctor["name"]
#     })

#     return jsonify({
#         "access_token": access_token,
#         "doctor": {
#             "doctor_uid": doctor["doctor_uid"],
#             "name": doctor["name"]
#         }
#     }), 200

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from flask_jwt_extended import create_access_token
from flask_cors import cross_origin

bp = Blueprint("auth", __name__, url_prefix="/auth")

# REGISTER
@bp.route("/register", methods=["POST", "OPTIONS"])
@cross_origin(origin='http://localhost:5173', headers=['Content-Type','Authorization'])
def register():
    if request.method == "OPTIONS":
        return '', 200

    try:
        data = request.get_json()
        doctor_id = data.get("doctor_id")
        password = data.get("password")

        if not doctor_id or not password:
            return jsonify({"error": "Doctor ID and password required"}), 400

        # Check if doctor ID already exists
        if db.doctors.find_one({"doctor_uid": doctor_id}):
            return jsonify({"error": "Doctor ID already exists"}), 409

        # Hash password and save doctor
        hashed_pw = generate_password_hash(password)
        db.doctors.insert_one({
            "doctor_uid": doctor_id,
            "password_hash": hashed_pw
        })

        return jsonify({"message": "Registered successfully"}), 201

    except Exception as e:
        print("Register Error:", str(e))
        return jsonify({"error": "Internal server error"}), 500


# LOGIN
@bp.route("/login", methods=["POST", "OPTIONS"])
@cross_origin(origin='http://localhost:5173', headers=['Content-Type','Authorization'])
def login():
    if request.method == "OPTIONS":
        return '', 200

    try:
        data = request.get_json()
        doctor_id = data.get("doctor_id")
        password = data.get("password")

        if not doctor_id or not password:
            return jsonify({"error": "Doctor ID and password required"}), 400

        doctor = db.doctors.find_one({"doctor_uid": doctor_id})
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        if not check_password_hash(doctor["password_hash"], password):
            return jsonify({"error": "Invalid password"}), 401

        token = create_access_token(identity=doctor_id)
        return jsonify({"access_token": token}), 200

    except Exception as e:
        print("Login Error:", str(e))
        return jsonify({"error": "Internal server error"}), 500
