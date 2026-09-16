import sqlite3
from pathlib import Path
from datetime import datetime


# =====================================================
# DATABASE CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_FILE = BASE_DIR / "students.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():

    connection = sqlite3.connect(
        str(DATABASE_FILE),
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign keys
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def init_database():

    connection = get_connection()
    cursor = connection.cursor()

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

                face_embedding TEXT DEFAULT '',

                voice_embedding TEXT DEFAULT '',

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # =================================================
        # CHECK OLD STUDENT COLUMNS
        # =================================================

        cursor.execute(
            "PRAGMA table_info(students)"
        )

        student_columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        # Add face_embedding if missing
        if "face_embedding" not in student_columns:

            cursor.execute("""
                ALTER TABLE students
                ADD COLUMN face_embedding TEXT DEFAULT ''
            """)

        # Add voice_embedding if missing
        if "voice_embedding" not in student_columns:

            cursor.execute("""
                ALTER TABLE students
                ADD COLUMN voice_embedding TEXT DEFAULT ''
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

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # =================================================
        # SUBJECTS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                subject_code TEXT UNIQUE NOT NULL,

                name TEXT NOT NULL,

                section TEXT NOT NULL,

                teacher_id TEXT NOT NULL,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (teacher_id)
                    REFERENCES teachers(teacher_id)
                    ON DELETE CASCADE
            )
        """)

        # =================================================
        # SUBJECT STUDENTS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subject_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                student_id TEXT NOT NULL,

                subject_id INTEGER NOT NULL,

                enrolled_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(student_id, subject_id),

                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (subject_id)
                    REFERENCES subjects(id)
                    ON DELETE CASCADE
            )
        """)

        # =================================================
        # ATTENDANCE LOGS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                student_id TEXT NOT NULL,

                subject_id INTEGER NOT NULL,

                attendance_date TEXT NOT NULL,

                status TEXT NOT NULL
                    DEFAULT 'Present',

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(
                    student_id,
                    subject_id,
                    attendance_date
                ),

                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (subject_id)
                    REFERENCES subjects(id)
                    ON DELETE CASCADE
            )
        """)

        # =================================================
        # INDEXES
        # =================================================

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_subject_students_student
            ON subject_students(student_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_subject_students_subject
            ON subject_students(subject_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_attendance_student
            ON attendance_logs(student_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_attendance_subject
            ON attendance_logs(subject_id)
        """)

        connection.commit()

    except sqlite3.Error as e:

        connection.rollback()

        print(
            f"Database initialization error: {e}"
        )

        raise

    finally:

        connection.close()


# =====================================================
# STUDENT FUNCTIONS
# =====================================================

def create_student(
    student_id,
    name,
    email=""
):

    init_database()

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO students
            (
                student_id,
                name,
                email
            )
            VALUES (?, ?, ?)
            """,
            (
                str(student_id).strip(),
                str(name).strip(),
                str(email).strip()
            )
        )

        connection.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


# =====================================================
# UPDATE STUDENT EMBEDDINGS
# =====================================================

def update_student_embeddings(
    student_id,
    face_embedding=None,
    voice_embedding=None
):

    init_database()

    connection = get_connection()
    cursor = connection.cursor()

    try:

        updates = []
        values = []

        # ---------------------------------------------
        # FACE EMBEDDING
        # ---------------------------------------------

        if face_embedding is not None:

            updates.append(
                "face_embedding = ?"
            )

            values.append(
                face_embedding
            )

        # ---------------------------------------------
        # VOICE EMBEDDING
        # ---------------------------------------------

        if voice_embedding is not None:

            updates.append(
                "voice_embedding = ?"
            )

            values.append(
                voice_embedding
            )

        # ---------------------------------------------
        # NOTHING TO UPDATE
        # ---------------------------------------------

        if not updates:

            return False

        values.append(
            str(student_id).strip()
        )

        query = f"""
            UPDATE students

            SET {", ".join(updates)}

            WHERE student_id = ?
        """

        cursor.execute(
            query,
            tuple(values)
        )

        connection.commit()

        return cursor.rowcount > 0

    except sqlite3.Error as e:

        connection.rollback()

        print(
            f"Update embedding error: {e}"
        )

        return False

    finally:

        connection.close()


# =====================================================
# GET ALL STUDENTS
# =====================================================

def get_all_students():

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                student_id,
                name,
                email,
                face_embedding,
                voice_embedding,
                created_at

            FROM students

            ORDER BY id DESC
        """)

        students = cursor.fetchall()

        return [
            dict(student)
            for student in students
        ]

    finally:

        connection.close()


# =====================================================
# GET STUDENT
# =====================================================

def get_student(student_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                name,
                email,
                face_embedding,
                voice_embedding,
                created_at

            FROM students

            WHERE student_id = ?
            """,
            (
                str(student_id).strip(),
            )
        )

        student = cursor.fetchone()

        if student is None:

            return None

        return dict(student)

    finally:

        connection.close()


# =====================================================
# UPDATE STUDENT
# =====================================================

def update_student(
    student_id,
    name,
    email=""
):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE students

            SET
                name = ?,
                email = ?

            WHERE student_id = ?
            """,
            (
                str(name).strip(),
                str(email).strip(),
                str(student_id).strip()
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# =====================================================
# DELETE STUDENT
# =====================================================

def delete_student(student_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM students

            WHERE student_id = ?
            """,
            (
                str(student_id).strip(),
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# =====================================================
# TEACHER FUNCTIONS
# =====================================================

def check_teacher_exists(teacher_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id

            FROM teachers

            WHERE teacher_id = ?
            """,
            (
                str(teacher_id).strip(),
            )
        )

        teacher = cursor.fetchone()

        return teacher is not None

    finally:

        connection.close()


# =====================================================
# CREATE TEACHER
# =====================================================

def create_teacher(
    teacher_id,
    name,
    email="",
    password=""
):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO teachers
            (
                teacher_id,
                name,
                email,
                password
            )

            VALUES (?, ?, ?, ?)
            """,
            (
                str(teacher_id).strip(),
                str(name).strip(),
                str(email).strip(),
                str(password).strip()
            )
        )

        connection.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


# =====================================================
# TEACHER LOGIN
# =====================================================

def teacher_login(
    username,
    password
):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        username = str(
            username
        ).strip()

        password = str(
            password
        ).strip()

        cursor.execute(
            """
            SELECT
                id,
                teacher_id,
                name,
                email

            FROM teachers

            WHERE
                (
                    LOWER(teacher_id)
                    = LOWER(?)

                    OR

                    LOWER(name)
                    = LOWER(?)
                )

                AND password = ?
            """,
            (
                username,
                username,
                password
            )
        )

        teacher = cursor.fetchone()

        if teacher is None:

            return None

        return dict(teacher)

    finally:

        connection.close()


# =====================================================
# GET ALL TEACHERS
# =====================================================

def get_all_teachers():

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                teacher_id,
                name,
                email,
                created_at

            FROM teachers

            ORDER BY id DESC
        """)

        teachers = cursor.fetchall()

        return [
            dict(teacher)
            for teacher in teachers
        ]

    finally:

        connection.close()


# =====================================================
# GET TEACHER
# =====================================================

def get_teacher(teacher_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                teacher_id,
                name,
                email,
                created_at

            FROM teachers

            WHERE teacher_id = ?
            """,
            (
                str(teacher_id).strip(),
            )
        )

        teacher = cursor.fetchone()

        if teacher is None:

            return None

        return dict(teacher)

    finally:

        connection.close()


# =====================================================
# SUBJECT FUNCTIONS
# =====================================================

def create_subject(
    subject_code,
    name,
    section,
    teacher_id
):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO subjects
            (
                subject_code,
                name,
                section,
                teacher_id
            )

            VALUES (?, ?, ?, ?)
            """,
            (
                str(subject_code).strip(),
                str(name).strip(),
                str(section).strip(),
                str(teacher_id).strip()
            )
        )

        connection.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


# =====================================================
# GET ALL SUBJECTS
# =====================================================

def get_all_subjects():

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                subject_code,
                name,
                section,
                teacher_id,
                created_at

            FROM subjects

            ORDER BY subject_code ASC
        """)

        subjects = cursor.fetchall()

        return [
            dict(subject)
            for subject in subjects
        ]

    finally:

        connection.close()


# =====================================================
# GET TEACHER SUBJECTS
# =====================================================

def get_teacher_subjects(teacher_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                s.id,
                s.subject_code,
                s.name,
                s.section,
                s.teacher_id,
                s.created_at,

                (
                    SELECT COUNT(*)

                    FROM subject_students ss

                    WHERE ss.subject_id = s.id

                ) AS total_students,

                (
                    SELECT COUNT(
                        DISTINCT attendance_date
                    )

                    FROM attendance_logs al

                    WHERE al.subject_id = s.id

                ) AS total_classes

            FROM subjects s

            WHERE s.teacher_id = ?

            ORDER BY s.id DESC
            """,
            (
                str(teacher_id).strip(),
            )
        )

        subjects = cursor.fetchall()

        return [
            dict(subject)
            for subject in subjects
        ]

    finally:

        connection.close()


# =====================================================
# GET SUBJECT BY CODE
# =====================================================

def get_subject(subject_code):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                subject_code,
                name,
                section,
                teacher_id,
                created_at

            FROM subjects

            WHERE LOWER(subject_code)
                  = LOWER(?)
            """,
            (
                str(subject_code).strip(),
            )
        )

        subject = cursor.fetchone()

        if subject is None:

            return None

        return dict(subject)

    finally:

        connection.close()


# =====================================================
# GET SUBJECT BY ID
# =====================================================

def get_subject_by_id(subject_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                subject_code,
                name,
                section,
                teacher_id,
                created_at

            FROM subjects

            WHERE id = ?
            """,
            (
                subject_id,
            )
        )

        subject = cursor.fetchone()

        if subject is None:

            return None

        return dict(subject)

    finally:

        connection.close()


# =====================================================
# DELETE SUBJECT
# =====================================================

def delete_subject(subject_code):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM subjects

            WHERE subject_code = ?
            """,
            (
                str(subject_code).strip(),
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# =====================================================
# ENROLL STUDENT TO SUBJECT
# =====================================================

def enroll_student_to_subject(
    student_id,
    subject_id
):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        student_id = str(
            student_id
        ).strip()

        # ---------------------------------------------
        # CHECK STUDENT
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT student_id

            FROM students

            WHERE student_id = ?
            """,
            (
                student_id,
            )
        )

        student = cursor.fetchone()

        if student is None:

            return False

        # ---------------------------------------------
        # CHECK SUBJECT
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT id

            FROM subjects

            WHERE id = ?
            """,
            (
                subject_id,
            )
        )

        subject = cursor.fetchone()

        if subject is None:

            return False

        # ---------------------------------------------
        # CHECK EXISTING ENROLLMENT
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT id

            FROM subject_students

            WHERE
                student_id = ?
                AND subject_id = ?
            """,
            (
                student_id,
                subject_id
            )
        )

        existing = cursor.fetchone()

        if existing is not None:

            return False

        # ---------------------------------------------
        # ENROLL STUDENT
        # ---------------------------------------------

        cursor.execute(
            """
            INSERT INTO subject_students
            (
                student_id,
                subject_id
            )

            VALUES (?, ?)
            """,
            (
                student_id,
                subject_id
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


# =====================================================
# UNENROLL STUDENT
# =====================================================

def unenroll_student_to_subject(
    student_id,
    subject_id
):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM subject_students

            WHERE
                student_id = ?
                AND subject_id = ?
            """,
            (
                str(student_id).strip(),
                subject_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# =====================================================
# GET STUDENT SUBJECTS
# =====================================================

def get_student_subjects(student_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                s.id,
                s.subject_code,
                s.name,
                s.section,
                s.teacher_id,
                s.created_at,
                ss.enrolled_at

            FROM subjects s

            INNER JOIN subject_students ss
                ON s.id = ss.subject_id

            WHERE ss.student_id = ?

            ORDER BY s.name ASC
            """,
            (
                str(student_id).strip(),
            )
        )

        subjects = cursor.fetchall()

        return [
            dict(subject)
            for subject in subjects
        ]

    finally:

        connection.close()


# =====================================================
# GET SUBJECT STUDENTS
# =====================================================

def get_subject_students(subject_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                st.id,
                st.student_id,
                st.name,
                st.email,
                st.face_embedding,
                st.voice_embedding,
                ss.enrolled_at

            FROM students st

            INNER JOIN subject_students ss
                ON st.student_id = ss.student_id

            WHERE ss.subject_id = ?

            ORDER BY st.name ASC
            """,
            (
                subject_id,
            )
        )

        students = cursor.fetchall()

        return [
            dict(student)
            for student in students
        ]

    finally:

        connection.close()


# =====================================================
# MARK ATTENDANCE
# =====================================================

def mark_attendance(
    student_id,
    subject_id,
    attendance_date,
    status="Present"
):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        student_id = str(
            student_id
        ).strip()

        status = str(
            status
        ).strip().capitalize()

        if status not in (
            "Present",
            "Absent",
            "Late"
        ):

            status = "Present"

        # ---------------------------------------------
        # CHECK ENROLLMENT
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT id

            FROM subject_students

            WHERE
                student_id = ?
                AND subject_id = ?
            """,
            (
                student_id,
                subject_id
            )
        )

        enrollment = cursor.fetchone()

        if enrollment is None:

            return False

        # ---------------------------------------------
        # SAVE ATTENDANCE
        # ---------------------------------------------

        cursor.execute(
            """
            INSERT INTO attendance_logs
            (
                student_id,
                subject_id,
                attendance_date,
                status
            )

            VALUES (?, ?, ?, ?)

            ON CONFLICT(
                student_id,
                subject_id,
                attendance_date
            )

            DO UPDATE SET
                status = excluded.status
            """,
            (
                student_id,
                subject_id,
                str(
                    attendance_date
                ).strip(),
                status
            )
        )

        connection.commit()

        return True

    except sqlite3.Error as e:

        connection.rollback()

        print(
            f"Attendance database error: {e}"
        )

        return False

    finally:

        connection.close()


# =====================================================
# CREATE MULTIPLE ATTENDANCE RECORDS
# =====================================================

def create_attendance(logs):

    """
    Save multiple attendance records.

    logs format:

    {
        "student_id": "101",
        "subject_id": 1,
        "attendance_date": "2026-09-16",
        "status": "Present"
    }
    """

    if not logs:

        return False

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        saved_count = 0

        for log in logs:

            # -----------------------------------------
            # STUDENT ID
            # -----------------------------------------

            student_id = str(
                log.get(
                    "student_id",
                    ""
                )
            ).strip()

            # -----------------------------------------
            # SUBJECT ID
            # -----------------------------------------

            subject_id = log.get(
                "subject_id"
            )

            # -----------------------------------------
            # STATUS
            # -----------------------------------------

            status = str(
                log.get(
                    "status",
                    "Present"
                )
            ).strip().capitalize()

            if status not in (
                "Present",
                "Absent",
                "Late"
            ):

                status = "Present"

            # -----------------------------------------
            # ATTENDANCE DATE
            # -----------------------------------------

            attendance_date = log.get(
                "attendance_date"
            )

            if not attendance_date:

                timestamp = log.get(
                    "timestamp"
                )

                if timestamp:

                    attendance_date = str(
                        timestamp
                    )[:10]

                else:

                    attendance_date = (
                        datetime.now().strftime(
                            "%Y-%m-%d"
                        )
                    )

            attendance_date = str(
                attendance_date
            ).strip()

            # -----------------------------------------
            # VALIDATION
            # -----------------------------------------

            if not student_id:

                continue

            if subject_id is None:

                continue

            # -----------------------------------------
            # CHECK ENROLLMENT
            # -----------------------------------------

            cursor.execute(
                """
                SELECT id

                FROM subject_students

                WHERE
                    student_id = ?
                    AND subject_id = ?
                """,
                (
                    student_id,
                    subject_id
                )
            )

            enrollment = cursor.fetchone()

            if enrollment is None:

                print(
                    f"Student {student_id} "
                    f"is not enrolled in "
                    f"subject {subject_id}"
                )

                continue

            # -----------------------------------------
            # INSERT / UPDATE ATTENDANCE
            # -----------------------------------------

            cursor.execute(
                """
                INSERT INTO attendance_logs
                (
                    student_id,
                    subject_id,
                    attendance_date,
                    status
                )

                VALUES (?, ?, ?, ?)

                ON CONFLICT(
                    student_id,
                    subject_id,
                    attendance_date
                )

                DO UPDATE SET
                    status = excluded.status
                """,
                (
                    student_id,
                    subject_id,
                    attendance_date,
                    status
                )
            )

            saved_count += 1

        connection.commit()

        return saved_count > 0

    except sqlite3.Error as e:

        connection.rollback()

        print(
            f"Create attendance error: {e}"
        )

        return False

    finally:

        connection.close()


# =====================================================
# GET STUDENT ATTENDANCE
# =====================================================

def get_student_attendance(student_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                al.id,
                al.student_id,
                al.subject_id,
                al.attendance_date,
                al.status,
                al.created_at,

                s.subject_code,
                s.name AS subject_name,
                s.section

            FROM attendance_logs al

            LEFT JOIN subjects s
                ON al.subject_id = s.id

            WHERE al.student_id = ?

            ORDER BY
                al.attendance_date DESC
            """,
            (
                str(student_id).strip(),
            )
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# =====================================================
# GET SUBJECT ATTENDANCE
# =====================================================

def get_subject_attendance(subject_id):

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                al.id,

                al.student_id,

                st.name AS student_name,

                al.subject_id,

                al.attendance_date,

                al.status,

                al.created_at,

                sub.subject_code,

                sub.name AS subject_name,

                sub.section

            FROM attendance_logs al

            INNER JOIN students st
                ON al.student_id = st.student_id

            INNER JOIN subjects sub
                ON al.subject_id = sub.id

            WHERE al.subject_id = ?

            ORDER BY
                al.attendance_date DESC,
                st.name ASC
            """,
            (
                subject_id,
            )
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# =====================================================
# GET ATTENDANCE FOR TEACHER
# =====================================================

def get_attendance_for_teacher(teacher_id):

    """
    Get attendance records for all subjects
    belonging to a particular teacher.
    """

    init_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                al.id,

                al.student_id,

                al.subject_id,

                al.attendance_date,

                al.status,

                al.created_at,

                st.name AS student_name,

                st.email AS student_email,

                sub.subject_code,

                sub.name AS subject_name,

                sub.section,

                sub.teacher_id

            FROM attendance_logs al

            INNER JOIN subjects sub
                ON al.subject_id = sub.id

            LEFT JOIN students st
                ON al.student_id = st.student_id

            WHERE sub.teacher_id = ?

            ORDER BY
                al.attendance_date DESC,
                al.created_at DESC,
                st.name ASC
            """,
            (
                str(teacher_id).strip(),
            )
        )

        rows = cursor.fetchall()

        records = []

        for row in rows:

            status = str(
                row["status"] or "Absent"
            ).strip().capitalize()

            # -----------------------------------------
            # TIMESTAMP
            # -----------------------------------------

            timestamp = (
                row["created_at"]
                or row["attendance_date"]
            )

            # -----------------------------------------
            # RECORD
            # -----------------------------------------

            records.append(
                {
                    "id": row["id"],

                    "student_id": (
                        row["student_id"]
                    ),

                    "student_name": (
                        row["student_name"]
                        or "Unknown Student"
                    ),

                    "student_email": (
                        row["student_email"]
                        or ""
                    ),

                    "subject_id": (
                        row["subject_id"]
                    ),

                    "subject_code": (
                        row["subject_code"]
                        or "N/A"
                    ),

                    "subject_name": (
                        row["subject_name"]
                        or "Unknown Subject"
                    ),

                    "section": (
                        row["section"]
                        or ""
                    ),

                    "teacher_id": (
                        row["teacher_id"]
                    ),

                    "attendance_date": (
                        row["attendance_date"]
                    ),

                    "status": status,

                    "created_at": (
                        row["created_at"]
                    ),

                    "timestamp": timestamp,

                    # Compatibility with
                    # older UI code
                    "is_present": (
                        status == "Present"
                    )
                }
            )

        return records

    except sqlite3.Error as e:

        print(
            f"Error loading teacher attendance: {e}"
        )

        return []

    finally:

        connection.close()


# =====================================================
# ATTENDANCE SUMMARY
# =====================================================

def get_student_attendance_summary(
    student_id,
    subject_id=None
):

    init_database()

    connection = get_connection()

    try:

        if subject_id is not None:

            cursor = connection.execute(
                """
                SELECT

                    COUNT(*) AS total_classes,

                    SUM(
                        CASE
                            WHEN status = 'Present'
                            THEN 1
                            ELSE 0
                        END
                    ) AS present_count,

                    SUM(
                        CASE
                            WHEN status = 'Absent'
                            THEN 1
                            ELSE 0
                        END
                    ) AS absent_count,

                    SUM(
                        CASE
                            WHEN status = 'Late'
                            THEN 1
                            ELSE 0
                        END
                    ) AS late_count

                FROM attendance_logs

                WHERE
                    student_id = ?
                    AND subject_id = ?
                """,
                (
                    str(student_id).strip(),
                    subject_id
                )
            )

        else:

            cursor = connection.execute(
                """
                SELECT

                    COUNT(*) AS total_classes,

                    SUM(
                        CASE
                            WHEN status = 'Present'
                            THEN 1
                            ELSE 0
                        END
                    ) AS present_count,

                    SUM(
                        CASE
                            WHEN status = 'Absent'
                            THEN 1
                            ELSE 0
                        END
                    ) AS absent_count,

                    SUM(
                        CASE
                            WHEN status = 'Late'
                            THEN 1
                            ELSE 0
                        END
                    ) AS late_count

                FROM attendance_logs

                WHERE student_id = ?
                """,
                (
                    str(student_id).strip(),
                )
            )

        result = cursor.fetchone()

        if result is None:

            return {
                "total_classes": 0,
                "present_count": 0,
                "absent_count": 0,
                "late_count": 0,
                "attendance_percentage": 0.0
            }

        data = dict(result)

        total = (
            data.get(
                "total_classes"
            )
            or 0
        )

        present = (
            data.get(
                "present_count"
            )
            or 0
        )

        absent = (
            data.get(
                "absent_count"
            )
            or 0
        )

        late = (
            data.get(
                "late_count"
            )
            or 0
        )

        percentage = (
            (present / total) * 100
            if total > 0
            else 0.0
        )

        return {
            "total_classes": total,
            "present_count": present,
            "absent_count": absent,
            "late_count": late,
            "attendance_percentage": round(
                percentage,
                2
            )
        }

    finally:

        connection.close()


# =====================================================
# ATTENDANCE PERCENTAGE
# =====================================================

def get_attendance_percentage(
    student_id,
    subject_id
):

    summary = get_student_attendance_summary(
        student_id,
        subject_id
    )

    return summary[
        "attendance_percentage"
    ]


# =====================================================
# INITIALIZE DATABASE WHEN FILE LOADS
# =====================================================

init_database()