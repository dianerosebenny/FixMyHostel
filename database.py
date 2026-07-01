# ============================================================
#  database.py  —  Database Connection & Table Setup
#  This file handles connecting to MySQL and creating all
#  the tables your app needs (students, complaints, etc.)
# ============================================================

import mysql.connector   # Library to connect Python to MySQL
from flask import g      # 'g' is Flask's per-request storage (explained below)
import click             # For running commands in terminal

# ── YOUR MySQL SETTINGS ───────────────────────────────────
# Change these to match your MySQL setup on your laptop
DB_CONFIG = {
    "host":     "localhost",      # MySQL is running on your own computer
    "user":     "root",           # Your MySQL username (usually 'root' on localhost)
    "password": "diane2006",       # Your MySQL root password
    "database": "fixmyhostel"     # The database name we'll create
}

# ── Get a database connection ─────────────────────────────
# This function gives us a connection to MySQL.
# We store it in 'g' so we reuse the same connection per request
# instead of opening a new one every time.
def get_db():
    if "db" not in g:
        # Only connect if we haven't already for this request
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db

# ── Close connection after each request ───────────────────
def close_db(e=None):
    db = g.pop("db", None)     # Remove db from 'g'
    if db is not None:
        db.close()             # Close the MySQL connection properly

# ── Create all database tables ────────────────────────────
# This runs once when the server starts.
# If the tables already exist, MySQL ignores the command (safe).
def init_db():
    # We can't use get_db() here because we're not inside a request
    # So we make a direct connection just for setup
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = conn.cursor()

    # ── Create the database itself if it doesn't exist ────
    cursor.execute("CREATE DATABASE IF NOT EXISTS fixmyhostel")
    cursor.execute("USE fixmyhostel")

    # ── TABLE: students ───────────────────────────────────
    # Stores all registered students
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id          INT AUTO_INCREMENT PRIMARY KEY,  -- Unique number for each student
            first_name  VARCHAR(100) NOT NULL,           -- Student's first name
            last_name   VARCHAR(100) NOT NULL,           -- Student's last name
            college_id  VARCHAR(50)  UNIQUE NOT NULL,    -- e.g. CS2021045 (must be unique)
            hostel_block VARCHAR(50) NOT NULL,           -- e.g. Block A
            room_number VARCHAR(20)  NOT NULL,           -- e.g. A-204
            email       VARCHAR(150) UNIQUE NOT NULL,    -- College email
            password    VARCHAR(255) NOT NULL,           -- Hashed password (never store plain text!)
            case_id     VARCHAR(20)  UNIQUE NOT NULL,    -- Anonymous ID e.g. FMH-4821
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP  -- When they registered
        )
    """)

    # ── TABLE: complaints ─────────────────────────────────
    # Stores every complaint filed by students
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            case_id         VARCHAR(20) NOT NULL,        -- Links to student's case_id (anonymously)
            complaint_ref   VARCHAR(20) UNIQUE NOT NULL, -- Unique complaint ID e.g. FMH-9021
            type            VARCHAR(20) NOT NULL,        -- verbal / bullying / physical / sexual
            accused_type    VARCHAR(20) NOT NULL,        -- student / staff
            incident_date   DATE NOT NULL,               -- When it happened
            incident_time   TIME,                        -- Approximate time (optional)
            location        VARCHAR(100) NOT NULL,       -- e.g. Common Room
            hostel_block    VARCHAR(50)  NOT NULL,       -- e.g. Block B
            description     TEXT NOT NULL,               -- Student's description of incident
            prior_reports   VARCHAR(200),                -- Had they reported before?
            platform        VARCHAR(50),                 -- For cyberbullying: WhatsApp etc.
            evidence_desc   TEXT,                        -- Description of uploaded files
            status          VARCHAR(20) DEFAULT 'new',  -- new / review / action / closed
            routed_to       VARCHAR(50),                 -- Which admin role handles this
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE: witnesses ──────────────────────────────────
    # Each complaint can have multiple witnesses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS witnesses (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            complaint_ref VARCHAR(20) NOT NULL,          -- Which complaint this belongs to
            witness_desc  VARCHAR(200) NOT NULL          -- Name/description of witness
        )
    """)

    # ── TABLE: evidence_files ─────────────────────────────
    # Tracks uploaded evidence files for each complaint
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_files (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            complaint_ref VARCHAR(20) NOT NULL,          -- Which complaint
            filename      VARCHAR(255) NOT NULL,         -- Original file name
            saved_as      VARCHAR(255) NOT NULL,         -- Name we saved it as on disk
            uploaded_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE: messages ───────────────────────────────────
    # Anonymous messages between student and admin/investigator
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            complaint_ref VARCHAR(20) NOT NULL,          -- Which complaint
            sender        VARCHAR(20) NOT NULL,          -- 'student' or 'admin'
            content       TEXT NOT NULL,                 -- The message text
            sent_at       DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE: admins ─────────────────────────────────────
    # Stores admin accounts (warden, committee, icc)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            email      VARCHAR(150) UNIQUE NOT NULL,
            password   VARCHAR(255) NOT NULL,            -- Hashed password
            role       VARCHAR(20)  NOT NULL,            -- warden / committee / icc
            name       VARCHAR(100) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE: otp_codes ──────────────────────────────────
    # Temporary OTP codes for password reset
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            email      VARCHAR(150) NOT NULL,
            otp        VARCHAR(6)   NOT NULL,            -- The 6-digit code
            expires_at DATETIME NOT NULL,               -- Code expires after 10 minutes
            used       BOOLEAN DEFAULT FALSE            -- Has this OTP been used?
        )
    """)

    # ── TABLE: status_history ─────────────────────────────
    # Tracks every time a complaint's status changes (audit log)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_history (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            complaint_ref VARCHAR(20)  NOT NULL,
            changed_by    VARCHAR(100) NOT NULL,         -- Admin email who changed it
            old_status    VARCHAR(20)  NOT NULL,
            new_status    VARCHAR(20)  NOT NULL,
            changed_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()   # Save all these CREATE TABLE commands
    cursor.close()
    conn.close()
    print("✅ Database tables created / verified successfully.")