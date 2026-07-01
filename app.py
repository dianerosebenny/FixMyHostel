# ============================================================
#  app.py  —  FixMyHostel Backend (Main Entry Point)
#  This is the "heart" of your backend. It starts the server
#  and connects all the route files together.
# ============================================================

from flask import Flask                        # Flask is the web framework
from flask_cors import CORS                    # Allows your HTML pages to talk to this server
from database import init_db                   # Our function to set up the database tables
from routes.auth import auth_bp                # Student login/register routes
from routes.complaints import complaints_bp    # Complaint filing & fetching routes
from routes.admin import admin_bp              # Admin panel routes
import os

# ── Create the Flask app ──────────────────────────────────
app = Flask(__name__)

# ── Secret key (used to secure sessions/cookies) ──────────
# In a real production app, use a long random string here
app.secret_key = "fixmyhostel_secret_2026"

# ── Allow Cross-Origin Requests ───────────────────────────
# This lets your HTML files (opened in browser) talk to this
# Python server running on localhost:5000
CORS(app, supports_credentials=True)

# ── Folder where uploaded evidence files will be saved ────
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)      # Create the folder if it doesn't exist
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # Max file size: 20MB

# ── Register all route "blueprints" ───────────────────────
# A blueprint is just a group of related routes (URLs)
app.register_blueprint(auth_bp,       url_prefix="/api")       # /api/register, /api/login
app.register_blueprint(complaints_bp, url_prefix="/api")       # /api/complaints
app.register_blueprint(admin_bp,      url_prefix="/api/admin") # /api/admin/login, etc.

# ── Initialize the database (create tables if not exist) ──
with app.app_context():
    init_db()

# ── Start the server ──────────────────────────────────────
if __name__ == "__main__":
    print("✅ FixMyHostel backend is running at http://localhost:5000")
    app.run(debug=True, port=5000)
    # debug=True means the server auto-restarts when you change code