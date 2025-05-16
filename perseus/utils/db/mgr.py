import sqlite3

from perseus.config.backend import Parameters


class DatabaseManager:
    def __init__(self):
        self._params = Parameters()
        self.db_path = self._params.db
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS apk_versions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                filename TEXT,
                                hash TEXT UNIQUE,
                                message TEXT,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS version_groups (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                version TEXT UNIQUE,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS version_apks (
                                version_id INTEGER,
                                apk_id INTEGER,
                                PRIMARY KEY (version_id, apk_id),
                                FOREIGN KEY(version_id) REFERENCES version_groups(id),
                                FOREIGN KEY(apk_id) REFERENCES apk_versions(id)
                            )''')

    def insert_apk(self, filename, apk_hash, message):
        with self._connect() as conn:
            conn.execute('''INSERT OR IGNORE INTO apk_versions (filename, hash, message)
                            VALUES (?, ?, ?)''',
                         (filename, apk_hash, message))
            conn.commit()

    def create_version_group(self, version):
        with self._connect() as conn:
            conn.execute('''INSERT OR IGNORE INTO version_groups (version) VALUES (?)''', (version,))
            conn.commit()

    def assign_apk_to_version(self, apk_hash, version):
        with self._connect() as conn:
            apk_id = conn.execute('SELECT id FROM apk_versions WHERE hash = ?', (apk_hash,)).fetchone()
            version_id = conn.execute('SELECT id FROM version_groups WHERE version = ?', (version,)).fetchone()

            if not apk_id or not version_id:
                raise ValueError('APK hash or version does not exist')

            conn.execute('''INSERT OR IGNORE INTO version_apks (version_id, apk_id)
                            VALUES (?, ?)''',
                         (version_id[0], apk_id[0]))
            conn.commit()

    def get_apks_for_version(self, version):
        with self._connect() as conn:
            rows = conn.execute('''
                SELECT av.filename, av.hash, av.message, av.timestamp
                FROM apk_versions av
                JOIN version_apks va ON av.id = va.apk_id
                JOIN version_groups vg ON vg.id = va.version_id
                WHERE vg.version = ?
                ORDER BY av.timestamp DESC
            ''', (version,)).fetchall()
        return [{
            'filename': row[0],
            'hash': row[1],
            'message': row[2],
            'timestamp': row[3]
        } for row in rows]

    def get_latest_apk_by_name(self, apk_name):
        with self._connect() as conn:
            cursor = conn.execute('''
                SELECT hash FROM apk_versions
                WHERE filename = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (apk_name,))
            row = cursor.fetchone()
            if row:
                return {"hash": row[0]}
            return None

    def freeze_version(self, version):
        with self._connect() as conn:
            # Create version group if it doesn't exist
            conn.execute('''INSERT OR IGNORE INTO version_groups (version) VALUES (?)''', (version,))
            version_id = conn.execute('SELECT id FROM version_groups WHERE version = ?', (version,)).fetchone()[0]

            # Remove any existing APKs assigned to this version
            conn.execute('DELETE FROM version_apks WHERE version_id = ?', (version_id,))

            # Get latest APKs per filename
            latest_apks = conn.execute('''
                SELECT filename, hash, id FROM (
                    SELECT filename, hash, id, timestamp,
                           RANK() OVER (PARTITION BY filename ORDER BY timestamp DESC) as rank
                    FROM apk_versions
                ) WHERE rank = 1
            ''').fetchall()

            # Insert latest into the version group
            for _, apk_hash, apk_id in latest_apks:
                conn.execute('''INSERT INTO version_apks (version_id, apk_id)
                                VALUES (?, ?)''',
                             (version_id, apk_id))
            conn.commit()

    def get_latest_version(self):
        with self._connect() as conn:
            result = conn.execute(
                "SELECT version FROM version_groups ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()
            return result[0] if result else None