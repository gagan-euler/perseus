import io
import os
import zipfile
from flask import Blueprint, send_file, jsonify

from perseus.blueprints.common import *

pull_bp = Blueprint("pull_bp",
                    __name__)

def _pull_version(version):
    apks = db.get_apks_for_version(version)
    if not apks:
        return jsonify({"error": f"No APKs found for version '{version}'"}), 404

    files_to_zip = []
    for apk in apks:
        filename = apk['filename']
        hashval = apk['hash']
        app_name = filename.rsplit('.', 1)[0]
        path = os.path.join(params.repository, app_name, f"{hashval}.apk")
        files_to_zip.append((path, filename))

    zip_data = zip_apks(files_to_zip)
    return send_file(zip_data,
                     mimetype='application/zip',
                     download_name=f"{version}.zip",
                     as_attachment=True)


def get_latest_version():
    with db._connect() as conn:
        row = conn.execute('''
            SELECT version FROM version_groups
            ORDER BY created_at DESC LIMIT 1
        ''').fetchone()
        return row[0] if row else None


def zip_apks(filepaths):
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in filepaths:
            print(path)
            if os.path.isfile(path[0]):
                zf.write(path[0], os.path.basename(path[0]))
    memory_file.seek(0)
    return memory_file


@pull_bp.route('/api/v1/pull', methods=['GET'])
def pull_latest():
    version = db.get_latest_version()
    if not version:
        return jsonify({"error": "No frozen versions found"}), 404

    return _pull_version(version)


@pull_bp.route('/api/v1/pull/<version>', methods=['GET'])
def get_latest_apks(version):
    return _pull_version(version)


@pull_bp.route('/api/v1/pull/<version>/<app_name>', methods=['GET'])
def get_specific_apk(version, app_name):
    if version != "latest":
        # Fetch hash for app_name in the specific version
        apk_hash = db.get_apk_hash_for_version(app_name, version)
        if not apk_hash:
            return jsonify({"error": f"No APK found for {app_name} in version {version}"}), 404
    else:
        # Fetch latest hash for app_name
        apk_hash = db.get_latest_apk_hash(app_name)
        if not apk_hash:
            return jsonify({"error": f"No latest APK found for {app_name}"}), 404

    apk_path = f"{params.repository}/{app_name}/{apk_hash}.apk"
    if not os.path.isfile(apk_path):
        return jsonify({"error": "APK file not found on server"}), 404

    return send_file(apk_path, as_attachment=True, download_name=f"{app_name}.apk")
