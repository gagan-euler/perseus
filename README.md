# Perseus Backend

Perseus is a powerful APK management system that allows you to store, version, and distribute Android application packages (APKs). It provides a RESTful API interface for pushing, pulling, and managing APK versions.

## Features

- **APK Storage**: Securely store APK files with SHA256 hash verification
- **Version Management**: Create and manage frozen versions of your APKs
- **Version Tagging**: Tag specific APK combinations as releases
- **RESTful API**: Simple and intuitive HTTP API interface

## Installation

1. Ensure you have Python 3.13 or higher installed
2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd perseus-backend
   ```
3. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
4. Install Gunicorn (for production deployment):
   ```bash
   pip install gunicorn
   ```

### Setting up as a System Service

1. Create a systemd service file at `/etc/systemd/system/perseus.service`:

```ini
[Unit]
Description=Perseus Gunicorn Service
After=network.target

[Service]
User=<your-user>
WorkingDirectory=/path/to/perseus
ExecStart=/usr/bin/gunicorn --workers 2 --bind <ip-address>:<port> perseus:app
Restart=on-failure
Environment=PYTHONUNBUFFERED=1
Type=simple

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:
```bash
sudo systemctl enable perseus
sudo systemctl start perseus
```

3. Check service status:
```bash
sudo systemctl status perseus
```

Replace the following placeholders:
- `<your-user>`: System user to run the service
- `/path/to/perseus`: Absolute path to your Perseus installation
- `<ip-address>`: IP address to bind to (e.g., 0.0.0.0 for all interfaces)
- `<port>`: Port number to run the service on

## Configuration

Create a configuration file at `/srv/perseus/perseus.conf` or use the default configuration:

```ini
[repository]
name = /srv/perseus

[network]
ip_address = 0.0.0.0
port = 5000
```

## API Endpoints

### Push Operations
- `POST /api/v1/push`
  - Upload a new APK file
  - Request: multipart/form-data with 'file' and optional 'message'
  - Response: Returns hash and path of stored APK

### Pull Operations
- `GET /api/v1/pull`
  - Download latest frozen version of all APKs
- `GET /api/v1/pull/<version>`
  - Download specific version of all APKs
- `GET /api/v1/pull/<version>/<app_name>`
  - Download specific version of a single app

### Version Management
- `GET /api/v1/freeze/<version>`
  - Create a new frozen version using latest APKs
- `GET /api/v1/versions`
  - List all frozen versions with timestamps

### App Management
- `GET /api/v1/apps`
  - List all apps with their latest hashes and version tags
  - Returns: App names, latest hashes, timestamps, and version tags
- `GET /api/v1/apps/all`
  - List all apps with their complete version history
  - Returns: Detailed version history including hashes, timestamps, and messages

### Status
- `GET /`
  - Basic server status check
- `GET /api/v1/status`
  - API status check

## Example Usage

### Uploading an APK
```bash
curl -X POST -F "file=@myapp.apk" -F "message=New feature release" http://localhost:5000/api/v1/push
```

### Creating a Frozen Version
```bash
curl http://localhost:5000/api/v1/freeze/1.0.0
```

### Downloading Latest Version
```bash
curl http://localhost:5000/api/v1/pull
```

### Listing All Apps
```bash
curl http://localhost:5000/api/v1/apps
```

## Database Schema

The system uses SQLite with the following main tables:
- `apk_versions`: Stores APK metadata (filename, hash, message)
- `version_groups`: Manages frozen versions
- `version_apks`: Maps APKs to version groups

## Development

### Requirements
- Python 3.13+
- Poetry for dependency management
- SQLite3

### Project Structure
```
perseus/
├── app.py              # Main application entry point
├── blueprints/         # API route definitions
│   └── api/
│       ├── default.py  # Basic status endpoints
│       ├── push.py     # Upload operations
│       ├── pull.py     # Download operations
│       └── list.py     # Listing operations
├── config/             # Configuration management
└── utils/
    └── db/            # Database operations
```

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.