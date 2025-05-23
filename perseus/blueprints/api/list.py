from flask import Blueprint, jsonify

from perseus.blueprints.common import db

list_bp = Blueprint("list_bp", __name__)


@list_bp.route('/api/v1/versions', methods=['GET'])
def list_frozen_versions():
    """List all frozen versions ordered by timestamp."""
    with db._connect() as conn:
        versions = conn.execute('''
            SELECT version, timestamp 
            FROM version_groups 
            ORDER BY timestamp DESC
        ''').fetchall()
        
        return jsonify({
            'versions': [{'version': v[0], 'created_at': v[1]} for v in versions]
        })


@list_bp.route('/api/v1/apps', methods=['GET'])
def list_apps():
    """List all unique apps with their latest hashes and version tags."""
    with db._connect() as conn:
        # Get all unique apps with their latest APK info
        apps = conn.execute('''
            WITH LatestAPKs AS (
                SELECT 
                    filename,
                    hash,
                    timestamp,
                    ROW_NUMBER() OVER (PARTITION BY filename ORDER BY timestamp DESC) as rn
                FROM apk_versions
            )
            SELECT 
                la.filename,
                la.hash,
                la.timestamp,
                vg.version as version_tag
            FROM LatestAPKs la
            LEFT JOIN version_apks va ON va.apk_id = (
                SELECT id FROM apk_versions WHERE hash = la.hash
            )
            LEFT JOIN version_groups vg ON vg.id = va.version_id
            WHERE la.rn = 1
            ORDER BY la.filename
        ''').fetchall()
        
        return jsonify({
            'apps': [{
                'name': app[0].replace('.apk', ''),
                'latest_hash': app[1],
                'last_updated': app[2],
                'version_tag': app[3]
            } for app in apps]
        })


@list_bp.route('/api/v1/apps/all', methods=['GET'])
def list_all_app_versions():
    """List all apps that exist with all their versions."""
    with db._connect() as conn:
        apps = conn.execute('''
            SELECT 
                av.filename,
                av.hash,
                av.timestamp,
                av.message,
                vg.version as version_tag
            FROM apk_versions av
            LEFT JOIN version_apks va ON va.apk_id = av.id
            LEFT JOIN version_groups vg ON vg.id = va.version_id
            ORDER BY av.filename, av.timestamp DESC
        ''').fetchall()
        
        # Group by app name
        app_versions = {}
        for app in apps:
            app_name = app[0].replace('.apk', '')
            if app_name not in app_versions:
                app_versions[app_name] = []
            
            app_versions[app_name].append({
                'hash': app[1],
                'timestamp': app[2],
                'message': app[3],
                'version_tag': app[4]
            })
        
        return jsonify({
            'apps': [{
                'name': name,
                'versions': versions
            } for name, versions in app_versions.items()]
        }) 