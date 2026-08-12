import sqlite3
import os
import hashlib
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "quran_academy.db")

def hash_password(password):
    """Secure SHA-256 password hashing with salt."""
    salt = "AlHafizQuranAcademy2026SecuredSalt!@#"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # High Security Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Registrations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            course TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            level TEXT,
            icon TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Teachers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT,
            bio TEXT,
            icon TEXT,
            experience TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Admin Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed Default Users if empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("Student User", "student@alhafiz.com", hash_password("quran123"), "student"),
            ("Academy Administrator", "admin@alhafiz.com", hash_password("admin123"), "admin")
        ]
        cursor.executemany('''
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', default_users)

    # Seed Courses if empty
    cursor.execute('SELECT COUNT(*) FROM courses')
    if cursor.fetchone()[0] == 0:
        default_courses = [
            ("Quran With Tajweed", "Learn proper pronunciation and recitation rules with expert teachers.", "Flexible", "All Levels", "📖"),
            ("Hifz-ul-Quran", "Structured Quran memorization program with revision and monthly testing.", "Flexible", "Intermediate/Advanced", "🕌"),
            ("Noorani Qaida", "Foundational course for kids and beginners to learn Arabic alphabets.", "3-6 Months", "Beginner", "⭐"),
            ("Islamic Studies", "Learn fundamental Islamic knowledge, Fiqh, Seerah, Duas, and manners.", "Flexible", "All Levels", "🌙"),
            ("Quran Translation", "Understand the meaning and context of Quranic verses in Urdu & English.", "6-12 Months", "Intermediate", "📜"),
            ("Kids Quran Classes", "Interactive and fun online classes specialized for young children.", "Flexible", "Kids", "✨")
        ]
        cursor.executemany('''
            INSERT INTO courses (title, description, duration, level, icon)
            VALUES (?, ?, ?, ?, ?)
        ''', default_courses)

    # Seed Teachers if empty
    cursor.execute('SELECT COUNT(*) FROM teachers')
    if cursor.fetchone()[0] == 0:
        default_teachers = [
            ("Hafiz Allah Ditta", "Senior Quran & Tajweed Specialist", "Over 8 years of teaching Tajweed and Hifz to students worldwide.", "👳", "8+ Years"),
            ("Qaria Fatima", "Female Tajweed & Noorani Qaida Instructor", "Specialized in teaching young kids and female adult students with patience.", "🧕", "6+ Years"),
            ("Qari Muhammad Usama", "Hifz & Arabic Pronunciation Instructor", "Expert in memorization methodologies, revision techniques, and Qira'at.", "🧔", "7+ Years")
        ]
        cursor.executemany('''
            INSERT INTO teachers (name, role, bio, icon, experience)
            VALUES (?, ?, ?, ?, ?)
        ''', default_teachers)

    # Seed Admin User in legacy admin table
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', ('admin', 'admin123'))

    conn.commit()
    conn.close()

def register_user(name, email, password, role='student'):
    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', (name, email.lower().strip(), pwd_hash, role))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"success": True, "user_id": user_id, "name": name, "email": email.lower().strip(), "role": role}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "Email address already registered."}

def verify_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    cursor.execute('SELECT * FROM users WHERE email = ? AND password_hash = ?', (email.lower().strip(), pwd_hash))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            "success": True,
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    return {"success": False, "message": "Invalid Email or Password."}

def add_registration(name, age, phone, email, course, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO registrations (student_name, age, phone, email, course, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, age, phone, email, course, message))
    reg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reg_id

def get_all_registrations(status_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if status_filter and status_filter.lower() != 'all':
        cursor.execute('SELECT * FROM registrations WHERE status = ? ORDER BY id DESC', (status_filter,))
    else:
        cursor.execute('SELECT * FROM registrations ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_registration_status(reg_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE registrations SET status = ? WHERE id = ?', (status, reg_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_registration(reg_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM registrations WHERE id = ?', (reg_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM courses')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_teachers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teachers')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM registrations')
    total_reg = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = 'Pending'")
    pending_reg = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = 'Enrolled'")
    enrolled_reg = cursor.fetchone()[0]

    cursor.execute('SELECT course, COUNT(*) as count FROM registrations GROUP BY course ORDER BY count DESC LIMIT 1')
    top_course_row = cursor.fetchone()
    top_course = top_course_row['course'] if top_course_row else "Quran With Tajweed"

    conn.close()
    return {
        "total_registrations": total_reg,
        "pending_registrations": pending_reg,
        "enrolled_registrations": enrolled_reg,
        "popular_course": top_course
    }

def verify_admin(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

if __name__ == "__main__":
    init_db()
    print("Security Database initialized with SHA-256 password hashing & default users!")
