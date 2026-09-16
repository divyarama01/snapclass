import time

import streamlit as st
from PIL import Image
import numpy as np


# =========================================================
# UI
# =========================================================

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
)

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard


# =========================================================
# FACE PIPELINE
# =========================================================

from src.pipeline.face_pipeline import (
    get_face_embeddings,
)


# =========================================================
# VOICE PIPELINE
# =========================================================

from src.pipeline.voice_pipeline import (
    get_voice_embedding,
)


# =========================================================
# DATABASE
# =========================================================

from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject,
)


# =========================================================
# COMPONENTS
# =========================================================

# IMPORTANT:
# Student enrollment comes from dialog_enroll.py
from src.components.dialog_enroll import (
    enroll_subject_dialog,
)

from src.components.subject_card import (
    subject_card,
)


# =========================================================
# STUDENT REGISTRATION
# =========================================================

def register_student():

    st.markdown("## 📝 Register New Profile")

    st.write(
        "Create your student profile using your face and optional voice."
    )

    st.divider()

    # =====================================================
    # FACE CAMERA
    # =====================================================

    st.markdown("### 📷 Capture Face")

    camera_image = st.camera_input(
        "Position your face in the center",
        key="student_camera",
    )

    if camera_image is not None:

        st.success(
            "✅ Face photo captured successfully."
        )

        try:

            image = Image.open(
                camera_image
            ).convert("RGB")

            st.image(
                image,
                caption="Captured Face",
                use_container_width=True,
            )

        except Exception as e:

            st.error(
                f"❌ Unable to process camera image: {e}"
            )

            return

    st.divider()

    # =====================================================
    # STUDENT DETAILS
    # =====================================================

    st.markdown("### 👨‍🎓 Student Details")

    with st.form(
        "student_registration_form"
    ):

        student_id = st.text_input(
            "Student ID",
            placeholder="STU001",
        )

        name = st.text_input(
            "Student Name",
            placeholder="Enter your full name",
        )

        email = st.text_input(
            "Email",
            placeholder="student@example.com",
        )

        st.markdown(
            "### 🎤 Optional: Voice Enrollment"
        )

        voice_audio = st.audio_input(
            "Record your voice",
        )

        submitted = st.form_submit_button(
            "Register New Profile",
            width="stretch",
        )

    # =====================================================
    # SUBMIT CHECK
    # =====================================================

    if not submitted:
        return

    # =====================================================
    # CLEAN INPUT
    # =====================================================

    student_id = student_id.strip()
    name = name.strip()
    email = email.strip()

    # =====================================================
    # VALIDATION
    # =====================================================

    if not student_id:

        st.error(
            "❌ Please enter Student ID."
        )

        return

    if not name:

        st.error(
            "❌ Please enter Student Name."
        )

        return

    if camera_image is None:

        st.error(
            "📷 Please capture your face first."
        )

        return

    # =====================================================
    # CHECK EXISTING STUDENT
    # =====================================================

    try:

        students = get_all_students() or []

        student_exists = any(
            str(
                student.get(
                    "student_id",
                    "",
                )
            ).strip().lower()
            == student_id.lower()
            for student in students
            if isinstance(student, dict)
        )

        if student_exists:

            st.error(
                f"❌ Student ID '{student_id}' already exists."
            )

            return

    except Exception as e:

        st.error(
            f"❌ Could not check existing students: {e}"
        )

        return

    # =====================================================
    # FACE EMBEDDING
    # =====================================================

    try:

        image = Image.open(
            camera_image
        ).convert("RGB")

        image_np = np.array(image)

        face_embedding = get_face_embeddings(
            image_np
        )

        if face_embedding is None:

            st.error(
                "❌ Face not detected. "
                "Please capture a clear photo."
            )

            return

        st.success(
            "✅ Face detected successfully."
        )

    except Exception as e:

        st.error(
            f"❌ Face processing failed: {e}"
        )

        return

    # =====================================================
    # VOICE EMBEDDING
    # =====================================================

    voice_embedding = None

    if voice_audio is not None:

        try:

            voice_bytes = voice_audio.getvalue()

            if voice_bytes:

                voice_embedding = get_voice_embedding(
                    voice_bytes
                )

                if voice_embedding is not None:

                    st.success(
                        "✅ Voice enrollment completed."
                    )

                else:

                    st.warning(
                        "⚠️ Voice embedding could not be created."
                    )

        except Exception as e:

            st.warning(
                f"⚠️ Voice enrollment skipped: {e}"
            )

    # =====================================================
    # CREATE STUDENT
    # =====================================================

    try:

        result = create_student(
            student_id=student_id,
            name=name,
            email=email,
        )

    except Exception as e:

        st.error(
            f"❌ Student registration failed: {e}"
        )

        return

    # =====================================================
    # REGISTRATION RESULT
    # =====================================================

    if result:

        # -------------------------------------------------
        # SAVE STUDENT SESSION
        # -------------------------------------------------

        st.session_state["student_data"] = {
            "student_id": student_id,
            "name": name,
            "email": email,
        }

        # Keep separate student_id also
        st.session_state["student_id"] = student_id

        st.session_state["is_logged_in"] = True

        st.session_state["user_role"] = "student"

        # -------------------------------------------------
        # SUCCESS MESSAGE
        # -------------------------------------------------

        st.success(
            f"🎉 Student '{name}' registered successfully!"
        )

        st.success(
            "✅ Face enrollment completed."
        )

        if voice_embedding is not None:

            st.success(
                "✅ Voice enrollment completed."
            )

        st.info(
            f"Student ID: {student_id}"
        )

        time.sleep(1)

        st.session_state[
            "show_student_registration"
        ] = False

        st.rerun()

    else:

        st.error(
            "❌ Student registration failed."
        )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard():

    # =====================================================
    # GET STUDENT DATA
    # =====================================================

    student_data = st.session_state.get(
        "student_data",
        {},
    )

    if not isinstance(
        student_data,
        dict,
    ):

        student_data = {}

    # =====================================================
    # STUDENT NAME
    # =====================================================

    student_name = str(
        student_data.get(
            "name",
            "Student",
        )
        or "Student"
    ).strip()

    if not student_name:

        student_name = "Student"

    # =====================================================
    # STUDENT ID
    # =====================================================

    student_id = (
        student_data.get(
            "student_id"
        )
        or student_data.get(
            "id"
        )
        or student_data.get(
            "studentId"
        )
        or st.session_state.get(
            "student_id"
        )
    )

    if student_id is not None:

        student_id = str(
            student_id
        ).strip()

    # =====================================================
    # PAGE STYLE
    # =====================================================

    style_background_dashboard()

    style_base_layout()

    # =====================================================
    # HEADER
    # =====================================================

    col1, col2 = st.columns(
        [2, 1],
        vertical_alignment="center",
    )

    with col1:

        header_dashboard()

    with col2:

        st.subheader(
            f"Welcome, {student_name}"
        )

        # -------------------------------------------------
        # LOGOUT
        # -------------------------------------------------

        if st.button(
            "Logout",
            type="secondary",
            width="stretch",
            key="student_logout_btn",
        ):

            # Clear student session
            st.session_state.pop(
                "student_data",
                None,
            )

            st.session_state.pop(
                "student_id",
                None,
            )

            st.session_state[
                "is_logged_in"
            ] = False

            st.session_state[
                "user_role"
            ] = None

            st.session_state[
                "student_login_type"
            ] = "login"

            st.session_state[
                "show_student_registration"
            ] = False

            st.rerun()

    st.divider()

    # =====================================================
    # SUBJECT HEADER
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.header(
            "Your Enrolled Subjects"
        )

    with col2:

        # -------------------------------------------------
        # ENROLL BUTTON
        # -------------------------------------------------

        if st.button(
            "Enroll in Subject",
            type="primary",
            width="stretch",
            key="student_enroll_subject_btn",
        ):

            if not student_id:

                st.error(
                    "❌ Student ID not found. "
                    "Please login again."
                )

            else:

                # Open actual enrollment dialog
                enroll_subject_dialog(
                    student_id=student_id
                )

    st.divider()

    # =====================================================
    # LOAD SUBJECTS AND ATTENDANCE
    # =====================================================

    subjects = []

    logs = []

    if student_id:

        try:

            with st.spinner(
                "Loading your data..."
            ):

                subjects = get_student_subjects(
                    student_id
                )

                logs = get_student_attendance(
                    student_id
                )

                if subjects is None:
                    subjects = []

                if logs is None:
                    logs = []

        except Exception as e:

            st.error(
                f"❌ Unable to load subjects or attendance: {e}"
            )

            subjects = []

            logs = []

    else:

        st.warning(
            "⚠️ Student ID not found in session."
        )

    # =====================================================
    # ATTENDANCE STATS
    # =====================================================

    stats_map = {}

    for log in logs:

        if not isinstance(
            log,
            dict,
        ):

            continue

        subject_id = log.get(
            "subject_id"
        )

        if subject_id is None:
            continue

        subject_id = str(
            subject_id
        ).strip()

        if not subject_id:
            continue

        if subject_id not in stats_map:

            stats_map[subject_id] = {
                "total": 0,
                "attended": 0,
            }

        stats_map[
            subject_id
        ]["total"] += 1

        try:

            is_present = int(
                log.get(
                    "is_present",
                    0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            is_present = 0

        if is_present == 1:

            stats_map[
                subject_id
            ]["attended"] += 1

    # =====================================================
    # SHOW SUBJECTS
    # =====================================================

    if not subjects:

        st.info(
            "📚 You are not enrolled in any subject yet."
        )

    else:

        cols = st.columns(2)

        for index, subject in enumerate(
            subjects
        ):

            if not isinstance(
                subject,
                dict,
            ):

                continue

            # -------------------------------------------------
            # GET SUBJECT ID
            # -------------------------------------------------

            sid = (
                subject.get("subject_id")
                or subject.get("id")
            )

            if sid is None:
                continue

            sid = str(
                sid
            ).strip()

            if not sid:
                continue

            # -------------------------------------------------
            # ATTENDANCE DATA
            # -------------------------------------------------

            stats = stats_map.get(
                sid,
                {
                    "total": 0,
                    "attended": 0,
                },
            )

            # -------------------------------------------------
            # UNENROLL FUNCTION
            # -------------------------------------------------

            def unenroll_button(
                subject_id=sid
            ):

                if st.button(
                    "Unenroll from this course",
                    type="secondary",
                    width="stretch",
                    key=f"unenroll_{subject_id}",
                ):

                    try:

                        success = (
                            unenroll_student_to_subject(
                                student_id,
                                subject_id,
                            )
                        )

                        if success:

                            st.success(
                                "✅ Successfully unenrolled."
                            )

                            time.sleep(0.5)

                            st.rerun()

                        else:

                            st.warning(
                                "⚠️ Student was not enrolled "
                                "in this subject."
                            )

                    except Exception as e:

                        st.error(
                            f"❌ Could not unenroll: {e}"
                        )

            # -------------------------------------------------
            # SUBJECT CARD
            # -------------------------------------------------

            with cols[index % 2]:

                subject_card(
                    name=subject.get(
                        "name",
                        "Unknown Subject",
                    ),

                    code=subject.get(
                        "subject_code",
                        "N/A",
                    ),

                    section=subject.get(
                        "section",
                        "N/A",
                    ),

                    stats=[
                        (
                            "📆",
                            "Total",
                            stats["total"],
                        ),
                        (
                            "✅",
                            "Attended",
                            stats["attended"],
                        ),
                    ],

                    footer_callback=unenroll_button,
                )

    st.divider()

    # =====================================================
    # STUDENT REGISTRATION
    # =====================================================

    st.markdown(
        "### 📝 Student Registration"
    )

    st.write(
        "Register a new student profile for attendance."
    )

    if st.button(
        "📝 Register New Profile",
        type="primary",
        width="stretch",
        key="student_register_profile_btn",
    ):

        st.session_state[
            "show_student_registration"
        ] = True

        st.rerun()

    # =====================================================
    # SHOW REGISTRATION FORM
    # =====================================================

    if st.session_state.get(
        "show_student_registration",
        False,
    ):

        st.divider()

        register_student()

        st.divider()

        if st.button(
            "← Back to Dashboard",
            type="secondary",
            width="stretch",
            key="student_back_dashboard_btn",
        ):

            st.session_state[
                "show_student_registration"
            ] = False

            st.rerun()

    # =====================================================
    # REGISTERED STUDENTS
    # =====================================================

    st.divider()

    st.markdown(
        "### 👨‍🎓 Registered Students"
    )

    try:

        students = get_all_students()

        if students is None:
            students = []

    except Exception as e:

        students = []

        st.error(
            f"❌ Unable to load students: {e}"
        )

    # =====================================================
    # NO STUDENTS
    # =====================================================

    if not students:

        st.info(
            "No students registered yet."
        )

    # =====================================================
    # STUDENT LIST
    # =====================================================

    else:

        for student in students:

            if not isinstance(
                student,
                dict,
            ):

                continue

            with st.container(
                border=True
            ):

                registered_student_name = student.get(
                    "name",
                    "Unknown Student",
                )

                registered_student_id = student.get(
                    "student_id",
                    "N/A",
                )

                student_email = student.get(
                    "email",
                    "",
                )

                st.subheader(
                    registered_student_name
                )

                st.write(
                    f"**Student ID:** {registered_student_id}"
                )

                if student_email:

                    st.write(
                        f"**Email:** {student_email}"
                    )

    # =====================================================
    # FOOTER
    # =====================================================

    try:

        footer_dashboard()

    except Exception:

        pass


# =========================================================
# STUDENT SCREEN
# =========================================================

def student_screen():

    # =====================================================
    # DEFAULT SESSION VALUE
    # =====================================================

    if "show_student_registration" not in st.session_state:

        st.session_state[
            "show_student_registration"
        ] = False

    # =====================================================
    # CHECK STUDENT SESSION
    # =====================================================

    student_data = st.session_state.get(
        "student_data"
    )

    valid_student_session = False

    if isinstance(
        student_data,
        dict,
    ):

        current_student_id = (
            student_data.get("student_id")
            or student_data.get("id")
            or student_data.get("studentId")
        )

        if current_student_id:

            valid_student_session = bool(
                str(
                    current_student_id
                ).strip()
            )

    # =====================================================
    # LOGIN REQUIRED
    # =====================================================

    if not valid_student_session:

        # Remove invalid student data
        st.session_state.pop(
            "student_data",
            None,
        )

        student_login()

        return

    # =====================================================
    # SHOW DASHBOARD
    # =====================================================

    student_dashboard()


# =========================================================
# STUDENT LOGIN
# =========================================================

def student_login():

    st.markdown(
        "## 🔐 Student Login"
    )

    st.write(
        "Enter your registered Student ID to continue."
    )

    student_id_input = st.text_input(
        "Enter Student ID",
        placeholder="STU001",
        key="student_login_id_input",
    )

    if st.button(
        "Login",
        type="primary",
        width="stretch",
        key="student_login_btn",
    ):

        # -------------------------------------------------
        # CLEAN INPUT
        # -------------------------------------------------

        student_id_input = (
            student_id_input.strip()
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not student_id_input:

            st.warning(
                "Please enter Student ID."
            )

            return

        # -------------------------------------------------
        # LOAD STUDENTS
        # -------------------------------------------------

        try:

            students = (
                get_all_students()
                or []
            )

        except Exception as e:

            st.error(
                f"❌ Could not load students: {e}"
            )

            return

        # -------------------------------------------------
        # FIND STUDENT
        # -------------------------------------------------

        student = None

        for item in students:

            if not isinstance(
                item,
                dict,
            ):

                continue

            saved_id = str(
                item.get(
                    "student_id",
                    "",
                )
            ).strip()

            if (
                saved_id.lower()
                == student_id_input.lower()
            ):

                student = item

                break

        # -------------------------------------------------
        # STUDENT NOT FOUND
        # -------------------------------------------------

        if student is None:

            st.error(
                f"❌ Student ID '{student_id_input}' "
                "not found. Please register first."
            )

            return

        # -------------------------------------------------
        # GET STUDENT INFORMATION
        # -------------------------------------------------

        saved_student_id = str(
            student.get(
                "student_id",
                student_id_input,
            )
        ).strip()

        saved_name = str(
            student.get(
                "name",
                "Student",
            )
            or "Student"
        ).strip()

        saved_email = str(
            student.get(
                "email",
                "",
            )
            or ""
        ).strip()

        # -------------------------------------------------
        # SAVE SESSION
        # -------------------------------------------------

        st.session_state[
            "student_data"
        ] = {
            "student_id": saved_student_id,
            "name": saved_name,
            "email": saved_email,
        }

        st.session_state[
            "student_id"
        ] = saved_student_id

        st.session_state[
            "is_logged_in"
        ] = True

        st.session_state[
            "user_role"
        ] = "student"

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        st.success(
            f"Welcome, {saved_name}! 🎉"
        )

        time.sleep(0.5)

        st.rerun()