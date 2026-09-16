import sqlite3
from pathlib import Path


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "students.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """Create and return a SQLite database connection."""

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_database():
    """Create all required database tables."""

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # =================================================
        # STUDENTS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # =================================================
        # TEACHERS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT DEFAULT '',
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # =================================================
        # SUBJECTS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id TEXT UNIQUE NOT NULL,
                subject_code TEXT NOT NULL,
                name TEXT NOT NULL,
                section TEXT DEFAULT '',
                teacher_id TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # =================================================
        # SUBJECT STUDENTS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subject_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, subject_id)
            )
        """)

        # =================================================
        # ATTENDANCE TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject_id TEXT NOT NULL,
                is_present INTEGER DEFAULT 0,
                attendance_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


# =========================================================
# STUDENT FUNCTIONS
# =========================================================

def create_student(student_id, name, email=""):
    """Create a new student."""

    init_database()

    conn = get_connection()

    try:
        student_id = str(student_id).strip()
        name = str(name).strip()
        email = str(email).strip()

        if not student_id or not name:
            return None

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students (
                student_id,
                name,
                email
            )
            VALUES (?, ?, ?)
        """, (
            student_id,
            name,
            email
        ))

        conn.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        conn.close()


def get_all_students():
    """Return all registered students."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                student_id,
                name,
                email,
                created_at
            FROM students
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_student(student_id):
    """Get one student by student ID."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                student_id,
                name,
                email,
                created_at
            FROM students
            WHERE student_id = ?
        """, (
            str(student_id).strip(),
        ))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()


def delete_student(student_id):
    """Delete a student."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM students
            WHERE student_id = ?
        """, (
            str(student_id).strip(),
        ))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


def update_student(student_id, name, email=""):
    """Update student information."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE students
            SET
                name = ?,
                email = ?
            WHERE student_id = ?
        """, (
            str(name).strip(),
            str(email).strip(),
            str(student_id).strip()
        ))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


# =========================================================
# TEACHER FUNCTIONS
# =========================================================

def check_teacher_exists(teacher_id):
    """Check whether a teacher already exists."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM teachers
            WHERE teacher_id = ?
        """, (
            str(teacher_id).strip(),
        ))

        return cursor.fetchone() is not None

    finally:
        conn.close()


def create_teacher(
    teacher_id,
    name,
    email="",
    password=""
):
    """Create a new teacher."""

    init_database()

    conn = get_connection()

    try:
        teacher_id = str(teacher_id).strip()
        name = str(name).strip()
        email = str(email).strip()
        password = str(password)

        if not teacher_id or not name or not password:
            return None

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO teachers (
                teacher_id,
                name,
                email,
                password
            )
            VALUES (?, ?, ?, ?)
        """, (
            teacher_id,
            name,
            email,
            password
        ))

        conn.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        conn.close()


def teacher_login(teacher_id, password):
    """Login teacher using ID and password."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                teacher_id,
                name,
                email
            FROM teachers
            WHERE teacher_id = ?
            AND password = ?
        """, (
            str(teacher_id).strip(),
            str(password)
        ))

        teacher = cursor.fetchone()

        if teacher is None:
            return None

        return dict(teacher)

    finally:
        conn.close()


# =========================================================
# SUBJECT FUNCTIONS
# =========================================================

def create_subjects(
    subject_id,
    subject_code,
    name,
    section="",
    teacher_id=""
):
    """Create a new subject."""

    init_database()

    conn = get_connection()

    try:
        subject_id = str(subject_id).strip()
        subject_code = str(subject_code).strip()
        name = str(name).strip()
        section = str(section).strip()
        teacher_id = str(teacher_id).strip()

        if not subject_id or not subject_code or not name:
            return None

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO subjects (
                subject_id,
                subject_code,
                name,
                section,
                teacher_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            subject_id,
            subject_code,
            name,
            section,
            teacher_id
        ))

        conn.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        conn.close()


def get_all_subjects():
    """Return all subjects."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                subject_id,
                subject_code,
                name,
                section,
                teacher_id,
                created_at
            FROM subjects
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_teacher_subjects(teacher_id):
    """Return subjects created by a teacher."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                subject_id,
                subject_code,
                name,
                section,
                teacher_id,
                created_at
            FROM subjects
            WHERE teacher_id = ?
            ORDER BY id DESC
        """, (
            str(teacher_id).strip(),
        ))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# =========================================================
# ENROLLMENT FUNCTIONS
# =========================================================

def enroll_student_to_subject(student_id, subject_id):
    """Enroll a student into a subject."""

    init_database()

    conn = get_connection()

    try:
        student_id = str(student_id).strip()
        subject_id = str(subject_id).strip()

        if not student_id or not subject_id:
            return False

        cursor = conn.cursor()

        # Check student
        cursor.execute("""
            SELECT id
            FROM students
            WHERE student_id = ?
        """, (
            student_id,
        ))

        if cursor.fetchone() is None:
            return False

        # Check subject
        cursor.execute("""
            SELECT id
            FROM subjects
            WHERE subject_id = ?
        """, (
            subject_id,
        ))

        if cursor.fetchone() is None:
            return False

        # Check existing enrollment
        cursor.execute("""
            SELECT id
            FROM subject_students
            WHERE student_id = ?
            AND subject_id = ?
        """, (
            student_id,
            subject_id
        ))

        if cursor.fetchone() is not None:
            return False

        # Enroll student
        cursor.execute("""
            INSERT INTO subject_students (
                student_id,
                subject_id
            )
            VALUES (?, ?)
        """, (
            student_id,
            subject_id
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def unenroll_student_to_subject(student_id, subject_id):
    """Remove student from a subject."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM subject_students
            WHERE student_id = ?
            AND subject_id = ?
        """, (
            str(student_id).strip(),
            str(subject_id).strip()
        ))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


# =========================================================
# GET STUDENT SUBJECTS
# =========================================================

def get_student_subjects(student_id):
    """Get all subjects in which a student is enrolled."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.id,
                s.subject_id,
                s.subject_code,
                s.name,
                s.section,
                s.teacher_id,
                s.created_at
            FROM subjects AS s
            INNER JOIN subject_students AS ss
                ON s.subject_id = ss.subject_id
            WHERE ss.student_id = ?
            ORDER BY s.name ASC
        """, (
            str(student_id).strip(),
        ))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# =========================================================
# GET SUBJECT STUDENTS
# =========================================================

def get_subject_students(subject_id):
    """Get all students enrolled in a subject."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.id,
                s.student_id,
                s.name,
                s.email
            FROM students AS s
            INNER JOIN subject_students AS ss
                ON s.student_id = ss.student_id
            WHERE ss.subject_id = ?
            ORDER BY s.name ASC
        """, (
            str(subject_id).strip(),
        ))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# =========================================================
# ATTENDANCE FUNCTIONS
# =========================================================

def create_attendance(
    student_id,
    subject_id,
    is_present
):
    """Create an attendance record."""

    init_database()

    conn = get_connection()

    try:
        student_id = str(student_id).strip()
        subject_id = str(subject_id).strip()

        if not student_id or not subject_id:
            return None

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attendance_logs (
                student_id,
                subject_id,
                is_present
            )
            VALUES (?, ?, ?)
        """, (
            student_id,
            subject_id,
            1 if is_present else 0
        ))

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def get_student_attendance(student_id):
    """Get attendance records for a student."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.id,
                a.student_id,
                a.subject_id,
                a.is_present,
                a.attendance_date,
                s.subject_code,
                s.name AS subject_name,
                s.section
            FROM attendance_logs AS a
            LEFT JOIN subjects AS s
                ON a.subject_id = s.subject_id
            WHERE a.student_id = ?
            ORDER BY a.attendance_date DESC
        """, (
            str(student_id).strip(),
        ))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_subject_attendance(subject_id):
    """Get attendance records for a subject."""

    init_database()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.id,
                a.student_id,
                s.name AS student_name,
                a.subject_id,
                a.is_present,
                a.attendance_date
            FROM attendance_logs AS a
            LEFT JOIN students AS s
                ON a.student_id = s.student_id
            WHERE a.subject_id = ?
            ORDER BY a.attendance_date DESC
        """, (
            str(subject_id).strip(),
        ))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# =========================================================
# INITIALIZE DATABASE ON IMPORT
# =========================================================

init_database()