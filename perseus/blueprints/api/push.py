import hashlib
import os

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from perseus.blueprints.common import *

push_bp = Blueprint("push_bp",
                    __name__)


def calculate_sha256(file_stream):
    hasher = hashlib.sha256()
    for chunk in iter(lambda: file_stream.read(4096), b""):
        hasher.update(chunk)
    file_stream.seek(0)
    return hasher.hexdigest()


def save_apk(file, apk_hash, app_name):
    app_dir = os.path.join(params.repository, app_name)
    os.makedirs(app_dir, exist_ok=True)
    final_path = os.path.join(str(app_dir), f"{apk_hash}.apk")
    if not os.path.exists(final_path):
        file.save(final_path)
    return final_path


@push_bp.route('/api/v1/push', methods=['POST'])
def push_apk():
    # Get the uploaded file and message
    uploaded_file = request.files.get('file')
    message = request.form.get('message', '')

    # If no file is uploaded, return an error
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    # Secure the filename and check if it's an APK file
    filename = secure_filename(uploaded_file.filename)
    if not filename.lower().endswith('.apk'):
        return jsonify({"error": "Only APK files are allowed"}), 400

    # Calculate the SHA256 hash of the APK file
    apk_hash = calculate_sha256(uploaded_file.stream)

    # Check if the APK already exists in the database by its hash
    with db._connect() as conn:
        existing_apk = conn.execute(
            "SELECT id, hash FROM apk_versions WHERE hash = ?", (apk_hash,)
        ).fetchone()

    # If the APK already exists, return the existing record's ID and hash
    if existing_apk:
        return jsonify({
            "status": "APK already exists",
        }), 200

    # If it's a new APK, save the file and insert it into the database
    app_name = filename.rsplit('.', 1)[0]
    final_path = save_apk(uploaded_file, apk_hash, app_name)

    # Insert the new APK into the database
    db.insert_apk(filename, apk_hash, message)

    return jsonify({
        "status": "success",
        "hash": apk_hash,
        "path": final_path
    }), 200


@push_bp.route('/api/v1/freeze/<version>', methods=['GET'])
def freeze_release(version):
    # Initialize the DatabaseManager
    db_manager = DatabaseManager()

    # Call the freeze_version method to freeze the latest APKs
    response = db_manager.freeze_version(version)

    return jsonify(response)