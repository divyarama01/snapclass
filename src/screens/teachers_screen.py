import time
from io import BytesIO
from datetime import datetime

import streamlit as st
import qrcode
import numpy as np
import pandas as pd


# =========================================================
# UI IMPORTS
# =========================================================

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card

from src.components.dialog_create_subject import (
    create_subject_dialog
)

from src.components.dialog_add_photo import (
    add_photos_dialog
)

from src.components.dialog_voice_attendance import (
    voice_attendance_dialog
)

from src.components.dialog_attendance_results import (
    attendance_result_dialog
)


# =========================================================
# DATABASE IMPORTS - SQLITE
# =========================================================

from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
    get_subject_students,
    get_attendance_for_teacher
)


# =========================================================
# FACE PIPELINE
# =========================================================

from src.pipeline.face_pipeline import (
    predict_attendance
)


# =========================================================
# SHARE SUBJECT / QR DIALOG
# =========================================================

@st.dialog("Share Class Link")
def share_subject_dialog(
    subject_code,
    subject_name
):

    # -----------------------------------------------------
    # CREATE JOIN LINK
    # -----------------------------------------------------
    app_domain = "snapclass-main.streamlit.app"
    join_link = (
        f"http://10.116.8.46:8501/"
        f"?subject_code={subject_code}"
    )

    # -----------------------------------------------------
    # COLUMNS
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    # =====================================================
    # COPY LINK
    # =====================================================

    with col1:

        st.markdown("### Copy Link")

        st.code(
            join_link,
            language=None
        )

        st.markdown("### Subject Code")

        st.code(
            subject_code,
            language=None
        )

        st.info(
            "Share this link or subject code "
            "with your students."
        )

    # =====================================================
    # QR CODE
    # =====================================================

    with col2:

        st.markdown("### Scan to Join")

        try:

            qr = qrcode.QRCode(
                version=1,
                box_size=8,
                border=2
            )

            qr.add_data(join_link)

            qr.make(
                fit=True
            )

            qr_image = qr.make_image()

            buffer = BytesIO()

            qr_image.save(
                buffer,
                format="PNG"
            )

            buffer.seek(0)

            st.image(
                buffer,
                width=220
            )

            st.caption(
                f"Subject Code: {subject_code}"
            )

        except Exception as e:

            st.error(
                f"Unable to generate QR code: {e}"
            )


# =========================================================
# TEACHER MAIN SCREEN
# =========================================================

def teachers_screen():

    # -----------------------------------------------------
    # APPLY PAGE STYLE
    # -----------------------------------------------------

    style_background_dashboard()
    style_base_layout()

    # =====================================================
    # CHECK LOGIN
    # =====================================================

    if "teacher_data" in st.session_state:

        teacher_dashboard()

        return

    # =====================================================
    # LOGIN / REGISTER
    # =====================================================

    login_type = st.session_state.get(
        "teacher_login_type",
        "login"
    )

    if login_type == "register":

        teacher_screen_register()

    else:

        teacher_screen_login()


# =========================================================
# TEACHER DASHBOARD
# =========================================================

def teacher_dashboard():

    # -----------------------------------------------------
    # GET TEACHER DATA
    # -----------------------------------------------------

    teacher_data = st.session_state.get(
        "teacher_data",
        {}
    )

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    col1, col2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    with col1:

        header_dashboard()

    with col2:

        teacher_name = teacher_data.get(
            "name",
            "Teacher"
        )

        st.subheader(
            f"Welcome, {teacher_name}"
        )

        # -------------------------------------------------
        # LOGOUT
        # -------------------------------------------------

        if st.button(
            "Logout",
            type="secondary",
            width="stretch",
            key="teacher_logout_btn"
        ):

            st.session_state.pop(
                "teacher_data",
                None
            )

            st.session_state[
                "is_logged_in"
            ] = False

            st.session_state[
                "user_role"
            ] = None

            st.session_state[
                "teacher_login_type"
            ] = "login"

            st.session_state[
                "current_teacher_tab"
            ] = "take_attendance"

            st.session_state[
                "attendance_images"
            ] = []

            st.session_state[
                "voice_attendance_results"
            ] = None

            st.rerun()

    # =====================================================
    # DEFAULT TAB
    # =====================================================

    if (
        "current_teacher_tab"
        not in st.session_state
    ):

        st.session_state[
            "current_teacher_tab"
        ] = "take_attendance"

    # =====================================================
    # DASHBOARD TABS
    # =====================================================

    tab1, tab2, tab3 = st.columns(3)

    # =====================================================
    # TAKE ATTENDANCE
    # =====================================================

    with tab1:

        if (
            st.session_state[
                "current_teacher_tab"
            ]
            == "take_attendance"
        ):

            button_type = "primary"

        else:

            button_type = "tertiary"

        if st.button(
            "Take Attendance",
            type=button_type,
            width="stretch",
            key="take_attendance_btn"
        ):

            st.session_state[
                "current_teacher_tab"
            ] = "take_attendance"

            st.rerun()

    # =====================================================
    # MANAGE SUBJECTS
    # =====================================================

    with tab2:

        if (
            st.session_state[
                "current_teacher_tab"
            ]
            == "manage_subjects"
        ):

            button_type = "primary"

        else:

            button_type = "tertiary"

        if st.button(
            "Manage Subjects",
            type=button_type,
            width="stretch",
            key="manage_subjects_btn"
        ):

            st.session_state[
                "current_teacher_tab"
            ] = "manage_subjects"

            st.rerun()

    # =====================================================
    # ATTENDANCE RECORDS
    # =====================================================

    with tab3:

        if (
            st.session_state[
                "current_teacher_tab"
            ]
            == "attendance_records"
        ):

            button_type = "primary"

        else:

            button_type = "tertiary"

        if st.button(
            "Attendance Records",
            type=button_type,
            width="stretch",
            key="attendance_records_btn"
        ):

            st.session_state[
                "current_teacher_tab"
            ] = "attendance_records"

            st.rerun()

    st.divider()

    # =====================================================
    # SHOW CURRENT TAB
    # =====================================================

    current_tab = st.session_state.get(
        "current_teacher_tab",
        "take_attendance"
    )

    if current_tab == "take_attendance":

        teacher_tab_take_attendance()

    elif current_tab == "manage_subjects":

        teacher_tab_manage_subjects()

    elif current_tab == "attendance_records":

        teacher_tab_attendance_records()

    # =====================================================
    # FOOTER
    # =====================================================

    footer_dashboard()


# =========================================================
# TAKE ATTENDANCE TAB
# =========================================================

def teacher_tab_take_attendance():

    # -----------------------------------------------------
    # GET TEACHER DATA
    # -----------------------------------------------------

    teacher_data = st.session_state.get(
        "teacher_data",
        {}
    )

    teacher_id = teacher_data.get(
        "teacher_id"
    )

    # -----------------------------------------------------
    # CHECK TEACHER ID
    # -----------------------------------------------------

    if teacher_id is None:

        st.error(
            "Teacher ID not found."
        )

        return

    # -----------------------------------------------------
    # PAGE TITLE
    # -----------------------------------------------------

    st.header(
        "Take AI Attendance"
    )

    # =====================================================
    # INITIALIZE PHOTOS
    # =====================================================

    if (
        "attendance_images"
        not in st.session_state
    ):

        st.session_state[
            "attendance_images"
        ] = []

    # =====================================================
    # LOAD SUBJECTS
    # =====================================================

    try:

        subjects = get_teacher_subjects(
            teacher_id
        )

    except Exception as e:

        st.error(
            f"Unable to load subjects: {e}"
        )

        return

    # =====================================================
    # NO SUBJECT
    # =====================================================

    if not subjects:

        st.warning(
            "You haven't created any subjects yet! "
            "Please create one to begin."
        )

        return

    # =====================================================
    # SUBJECT OPTIONS
    # =====================================================

    subject_options = {}

    for subject in subjects:

        subject_name = subject.get(
            "name",
            "Unknown Subject"
        )

        subject_code = subject.get(
            "subject_code",
            ""
        )

        # Support both subject_id and id
        subject_id = subject.get(
            "subject_id",
            subject.get("id")
        )

        label = (
            f"{subject_name} - "
            f"{subject_code}"
        )

        subject_options[
            label
        ] = subject_id

    # =====================================================
    # SUBJECT + ADD PHOTOS
    # =====================================================

    col1, col2 = st.columns(
        [3, 1]
    )

    # -----------------------------------------------------
    # SELECT SUBJECT
    # -----------------------------------------------------

    with col1:

        selected_subject_label = st.selectbox(
            "Select Subject",
            options=list(
                subject_options.keys()
            ),
            key="attendance_subject_select"
        )

    # -----------------------------------------------------
    # ADD PHOTOS
    # -----------------------------------------------------

    with col2:

        if st.button(
            "Add Photos",
            type="primary",
            width="stretch",
            key="add_attendance_photos_btn"
        ):

            add_photos_dialog()

    # =====================================================
    # GET SELECTED SUBJECT
    # =====================================================

    selected_subject_id = subject_options.get(
        selected_subject_label
    )

    st.divider()

    # =====================================================
    # CHECK PHOTOS
    # =====================================================

    has_photos = bool(
        st.session_state.get(
            "attendance_images",
            []
        )
    )

    # =====================================================
    # SHOW ADDED PHOTOS
    # =====================================================

    if has_photos:

        st.header(
            "Added Photos"
        )

        gallery_cols = st.columns(4)

        for idx, img in enumerate(
            st.session_state[
                "attendance_images"
            ]
        ):

            with gallery_cols[
                idx % 4
            ]:

                st.image(
                    img,
                    width="stretch",
                    caption=f"Photo {idx + 1}"
                )

    # =====================================================
    # ACTION BUTTONS
    # =====================================================

    c1, c2, c3 = st.columns(3)

    # =====================================================
    # CLEAR ALL PHOTOS
    # =====================================================

    with c1:

        if st.button(
            "Clear all photos",
            width="stretch",
            type="tertiary",
            icon=":material/delete:",
            disabled=not has_photos,
            key="clear_all_photos_btn"
        ):

            st.session_state[
                "attendance_images"
            ] = []

            st.rerun()

    # =====================================================
    # RUN FACE ANALYSIS
    # =====================================================

    with c2:

        if st.button(
            "Run Face Analysis",
            width="stretch",
            type="secondary",
            icon=":material/analytics:",
            disabled=not has_photos,
            key="run_face_analysis_btn"
        ):

            with st.spinner(
                "Deep scanning classroom photos..."
            ):

                # =========================================
                # DETECT STUDENTS
                # =========================================

                all_detected_ids = {}

                for idx, img in enumerate(
                    st.session_state[
                        "attendance_images"
                    ]
                ):

                    try:

                        img_np = np.array(
                            img.convert("RGB")
                        )

                        detected, _, _ = (
                            predict_attendance(
                                img_np
                            )
                        )

                        if detected:

                            for sid in detected.keys():

                                student_id = str(
                                    sid
                                ).strip()

                                all_detected_ids.setdefault(
                                    student_id,
                                    []
                                ).append(
                                    f"Photo {idx + 1}"
                                )

                    except Exception as e:

                        st.error(
                            f"Face analysis failed for "
                            f"Photo {idx + 1}: {e}"
                        )

                # =========================================
                # LOAD ENROLLED STUDENTS FROM SQLITE
                # =========================================

                try:

                    enrolled_students = (
                        get_subject_students(
                            selected_subject_id
                        )
                    )

                except Exception as e:

                    st.error(
                        "Unable to load enrolled students: "
                        f"{e}"
                    )

                    return

                # =========================================
                # NO ENROLLED STUDENTS
                # =========================================

                if not enrolled_students:

                    st.warning(
                        "No students enrolled in this course."
                    )

                    return

                # =========================================
                # CREATE RESULTS
                # =========================================

                results = []

                attendance_to_log = []

                current_timestamp = (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                current_date = (
                    datetime.now().strftime(
                        "%Y-%m-%d"
                    )
                )

                # =========================================
                # CHECK EVERY ENROLLED STUDENT
                # =========================================

                for student in enrolled_students:

                    student_id = student.get(
                        "student_id"
                    )

                    student_name = student.get(
                        "name",
                        "Unknown Student"
                    )

                    if student_id is None:

                        continue

                    student_id = str(
                        student_id
                    ).strip()

                    sources = (
                        all_detected_ids.get(
                            student_id,
                            []
                        )
                    )

                    is_present = (
                        len(sources) > 0
                    )

                    # -------------------------------------
                    # RESULT
                    # -------------------------------------

                    results.append(
                        {
                            "Name": student_name,
                            "ID": student_id,
                            "Source": (
                                ", ".join(sources)
                                if is_present
                                else "-"
                            ),
                            "Status": (
                                "Present"
                                if is_present
                                else "Absent"
                            )
                        }
                    )

                    # -------------------------------------
                    # ATTENDANCE LOG
                    # -------------------------------------

                    attendance_to_log.append(
                        {
                            "student_id": student_id,
                            "subject_id": selected_subject_id,
                            "attendance_date": current_date,
                            "timestamp": current_timestamp,
                            "status": (
                                "Present"
                                if is_present
                                else "Absent"
                            ),
                            "source": (
                                "Face"
                                if is_present
                                else "-"
                            )
                        }
                    )

                # =========================================
                # SHOW ATTENDANCE RESULTS
                # =========================================

                if results:

                    result_df = pd.DataFrame(
                        results
                    )

                    # Save in session also
                    st.session_state[
                        "face_attendance_results"
                    ] = (
                        result_df,
                        attendance_to_log
                    )

                    attendance_result_dialog(
                        result_df,
                        attendance_to_log
                    )

                else:

                    st.warning(
                        "No attendance results were generated."
                    )

    # =====================================================
    # VOICE ATTENDANCE
    # =====================================================

    with c3:

        if st.button(
            "Use Voice Attendance",
            type="primary",
            width="stretch",
            icon=":material/mic:",
            key="voice_attendance_btn"
        ):

            voice_attendance_dialog(
                selected_subject_id
            )

    # =====================================================
    # PHOTO STATUS
    # =====================================================

    photo_count = len(
        st.session_state.get(
            "attendance_images",
            []
        )
    )

    if photo_count == 0:

        st.info(
            "No classroom photos added yet. "
            "Click 'Add Photos' to capture or "
            "upload classroom photos."
        )

    else:

        st.success(
            f"{photo_count} classroom photo(s) "
            "ready for AI attendance."
        )

    # =====================================================
    # SELECTED SUBJECT
    # =====================================================

    st.caption(
        f"Selected Subject: "
        f"{selected_subject_label}"
    )


# =========================================================
# MANAGE SUBJECTS TAB
# =========================================================

def teacher_tab_manage_subjects():

    # -----------------------------------------------------
    # GET TEACHER DATA
    # -----------------------------------------------------

    teacher_data = st.session_state.get(
        "teacher_data",
        {}
    )

    teacher_id = teacher_data.get(
        "teacher_id"
    )

    st.header(
        "Manage Subjects"
    )

    # =====================================================
    # CHECK TEACHER ID
    # =====================================================

    if teacher_id is None:

        st.error(
            "Teacher ID not found."
        )

        return

    # =====================================================
    # SUBJECT HEADER
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Subjects"
        )

    with col2:

        if st.button(
            "Create New Subject",
            width="stretch",
            key="create_new_subject_btn"
        ):

            create_subject_dialog(
                teacher_id
            )

    # =====================================================
    # GET SUBJECTS
    # =====================================================

    try:

        subjects = get_teacher_subjects(
            teacher_id
        )

    except Exception as e:

        st.error(
            f"Unable to load subjects: {e}"
        )

        return

    # =====================================================
    # SHOW SUBJECTS
    # =====================================================

    if subjects:

        for subject in subjects:

            # -------------------------------------------------
            # SUBJECT DATA
            # -------------------------------------------------

            subject_name = subject.get(
                "name",
                "Unknown Subject"
            )

            subject_code = subject.get(
                "subject_code",
                ""
            )

            section = subject.get(
                "section",
                ""
            )

            # -------------------------------------------------
            # SUBJECT STATS
            # -------------------------------------------------

            stats = [

                (
                    "🫂 Students",
                    subject.get(
                        "total_students",
                        0
                    )
                ),

                (
                    "⏱️ Classes",
                    subject.get(
                        "total_classes",
                        0
                    )
                )
            ]

            # -------------------------------------------------
            # SHARE BUTTON
            # -------------------------------------------------

            def share_btn(
                code=subject_code,
                name=subject_name
            ):

                if st.button(
                    f"Share Code: {name}",
                    key=f"share_subject_{code}",
                    icon=":material/share:"
                ):

                    share_subject_dialog(
                        subject_code=code,
                        subject_name=name
                    )

            # -------------------------------------------------
            # SUBJECT CARD
            # -------------------------------------------------

            subject_card(
                name=subject_name,
                code=subject_code,
                section=section,
                stats=stats,
                footer_callback=share_btn
            )

    else:

        st.info(
            "NO SUBJECT FOUND. "
            "CREATE ONE ABOVE."
        )


# =========================================================
# ATTENDANCE RECORDS TAB
# =========================================================

def teacher_tab_attendance_records():

    st.header(
        "Attendance Records"
    )

    # -----------------------------------------------------
    # GET TEACHER DATA
    # -----------------------------------------------------

    teacher_data = st.session_state.get(
        "teacher_data",
        {}
    )

    teacher_id = teacher_data.get(
        "teacher_id"
    )

    if teacher_id is None:

        st.error(
            "Teacher ID not found."
        )

        return

    # -----------------------------------------------------
    # LOAD RECORDS
    # -----------------------------------------------------

    try:

        records = get_attendance_for_teacher(
            teacher_id
        )

    except Exception as e:

        st.error(
            f"Unable to load attendance records: {e}"
        )

        return

    # -----------------------------------------------------
    # NO RECORDS
    # -----------------------------------------------------

    if not records:

        st.info(
            "No attendance records found yet."
        )

        return

    # -----------------------------------------------------
    # PREPARE DATA
    # -----------------------------------------------------

    data = []

    for record in records:

        # =================================================
        # DATE / TIME
        # =================================================

        timestamp = (
            record.get("timestamp")
            or record.get("created_at")
            or record.get("attendance_date")
        )

        formatted_time = "N/A"

        if timestamp:

            try:

                timestamp_string = str(
                    timestamp
                )

                # Remove microseconds if present
                timestamp_string = (
                    timestamp_string
                    .split(".")[0]
                )

                parsed_datetime = (
                    datetime.fromisoformat(
                        timestamp_string
                    )
                )

                formatted_time = (
                    parsed_datetime.strftime(
                        "%Y-%m-%d %I:%M %p"
                    )
                )

            except Exception:

                formatted_time = str(
                    timestamp
                )

        # =================================================
        # SUBJECT INFORMATION
        # =================================================

        subject_data = record.get(
            "subjects"
        )

        subject_code = (
            record.get("subject_code")
            or record.get("code")
        )

        subject_name = (
            record.get("subject_name")
            or record.get("name")
        )

        # If nested subject data exists
        if isinstance(
            subject_data,
            dict
        ):

            subject_code = (
                subject_code
                or subject_data.get(
                    "subject_code"
                )
                or subject_data.get(
                    "code"
                )
            )

            subject_name = (
                subject_name
                or subject_data.get(
                    "name"
                )
            )

        # =================================================
        # STATUS
        # =================================================

        status = str(
            record.get(
                "status",
                ""
            )
        ).strip().capitalize()

        # -------------------------------------------------
        # Backward compatibility
        # -------------------------------------------------

        if not status:

            old_present_value = record.get(
                "is_present"
            )

            if old_present_value is not None:

                status = (
                    "Present"
                    if bool(
                        old_present_value
                    )
                    else "Absent"
                )

            else:

                status = "Absent"

        is_present = (
            status == "Present"
        )

        # =================================================
        # STUDENT INFORMATION
        # =================================================

        student_id = record.get(
            "student_id",
            ""
        )

        student_name = (
            record.get("student_name")
            or record.get("name")
            or "Unknown Student"
        )

        # =================================================
        # APPEND ROW
        # =================================================

        data.append(
            {
                "Timestamp": timestamp,
                "Time": formatted_time,
                "Student": student_name,
                "Student ID": str(student_id),
                "Subject": (
                    subject_name
                    or "Unknown Subject"
                ),
                "Subject Code": (
                    subject_code
                    or "N/A"
                ),
                "Status": status,
                "is_present": is_present
            }
        )

    # -----------------------------------------------------
    # CHECK DATA
    # -----------------------------------------------------

    if not data:

        st.info(
            "No attendance records available."
        )

        return

    # =====================================================
    # CREATE DATAFRAME
    # =====================================================

    df = pd.DataFrame(
        data
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    summary = (
        df.groupby(
            [
                "Time",
                "Subject",
                "Subject Code"
            ],
            dropna=False
        )
        .agg(
            Present_Count=(
                "is_present",
                "sum"
            ),
            Total_Count=(
                "is_present",
                "count"
            )
        )
        .reset_index()
    )

    # =====================================================
    # ATTENDANCE STATS
    # =====================================================

    summary[
        "Attendance Stats"
    ] = (
        "✅ "
        + summary[
            "Present_Count"
        ].astype(str)
        + "/"
        + summary[
            "Total_Count"
        ].astype(str)
        + " Students"
    )

    # =====================================================
    # SORT RECORDS
    # =====================================================

    display_df = (
        summary[
            [
                "Time",
                "Subject",
                "Subject Code",
                "Attendance Stats"
            ]
        ]
        .sort_values(
            by="Time",
            ascending=False
        )
    )

    # =====================================================
    # DISPLAY SUMMARY
    # =====================================================

    st.subheader(
        "Attendance Summary"
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )

    # =====================================================
    # DETAILED RECORDS
    # =====================================================

    st.divider()

    st.subheader(
        "Detailed Attendance Records"
    )

    detailed_df = df[
        [
            "Time",
            "Student",
            "Student ID",
            "Subject",
            "Subject Code",
            "Status"
        ]
    ].copy()

    st.dataframe(
        detailed_df,
        width="stretch",
        hide_index=True
    )


# =========================================================
# TEACHER LOGIN FUNCTION
# =========================================================

def login_teacher(
    username,
    password
):

    # -----------------------------------------------------
    # CLEAN INPUT
    # -----------------------------------------------------

    username = str(
        username
    ).strip()

    password = str(
        password
    ).strip()

    # -----------------------------------------------------
    # CHECK EMPTY
    # -----------------------------------------------------

    if not username or not password:

        return False

    # =====================================================
    # DATABASE LOGIN
    # =====================================================

    try:

        teacher = teacher_login(
            username,
            password
        )

        if teacher:

            st.session_state[
                "user_role"
            ] = "teacher"

            st.session_state[
                "teacher_data"
            ] = teacher

            st.session_state[
                "is_logged_in"
            ] = True

            return True

        return False

    except Exception as e:

        st.error(
            f"Login error: {e}"
        )

        return False


# =========================================================
# TEACHER LOGIN SCREEN
# =========================================================

def teacher_screen_login():

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    col1, col2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    with col1:

        header_dashboard()

    # -----------------------------------------------------
    # BACK BUTTON
    # -----------------------------------------------------

    with col2:

        if st.button(
            "Go back to Home",
            type="secondary",
            width="stretch",
            key="teacher_login_back_btn"
        ):

            st.session_state[
                "teacher_login_type"
            ] = "login"

            st.session_state[
                "login_type"
            ] = None

            st.rerun()

    # =====================================================
    # LOGIN TITLE
    # =====================================================

    st.markdown(
        """
        <h2 style="text-align:center;">
            Login using password
        </h2>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # USERNAME
    # =====================================================

    teacher_username = st.text_input(
        "Enter username",
        placeholder="ananyaroy",
        key="teacher_username_login"
    )

    # =====================================================
    # PASSWORD
    # =====================================================

    teacher_pass = st.text_input(
        "Enter password",
        type="password",
        placeholder="Enter password",
        key="teacher_password_login"
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    # =====================================================
    # LOGIN BUTTON
    # =====================================================

    with btnc1:

        if st.button(
            "Login",
            width="stretch",
            key="teacher_login_btn"
        ):

            if login_teacher(
                teacher_username,
                teacher_pass
            ):

                st.toast(
                    "Welcome back! 👋"
                )

                time.sleep(1)

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    # =====================================================
    # REGISTER BUTTON
    # =====================================================

    with btnc2:

        if st.button(
            "Register Instead",
            type="primary",
            width="stretch",
            key="teacher_register_btn"
        ):

            st.session_state[
                "teacher_login_type"
            ] = "register"

            st.rerun()

    footer_dashboard()


# =========================================================
# REGISTER TEACHER FUNCTION
# =========================================================

def register_teacher(
    teacher_username,
    teacher_name,
    teacher_pass,
    teacher_pass_confirm
):

    # -----------------------------------------------------
    # CLEAN INPUT
    # -----------------------------------------------------

    teacher_username = (
        str(teacher_username).strip()
    )

    teacher_name = (
        str(teacher_name).strip()
    )

    teacher_pass = (
        str(teacher_pass).strip()
    )

    teacher_pass_confirm = (
        str(teacher_pass_confirm).strip()
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    if not teacher_username:

        return False, (
            "Username is required."
        )

    if not teacher_name:

        return False, (
            "Name is required."
        )

    if not teacher_pass:

        return False, (
            "Password is required."
        )

    if not teacher_pass_confirm:

        return False, (
            "Please confirm your password."
        )

    # =====================================================
    # PASSWORD CHECK
    # =====================================================

    if teacher_pass != teacher_pass_confirm:

        return False, (
            "Passwords do not match."
        )

    # =====================================================
    # CHECK USERNAME
    # =====================================================

    try:

        if check_teacher_exists(
            teacher_username
        ):

            return False, (
                "Username already taken."
            )

    except Exception as e:

        return False, (
            f"Database error: {e}"
        )

    # =====================================================
    # CREATE TEACHER
    # =====================================================

    try:

        result = create_teacher(
            teacher_id=teacher_username,
            name=teacher_name,
            email="",
            password=teacher_pass
        )

        if result is None:

            return False, (
                "Teacher account could not "
                "be created."
            )

        return True, (
            "Teacher account created successfully!"
        )

    except Exception as e:

        return False, (
            f"Registration error: {e}"
        )


# =========================================================
# TEACHER REGISTER SCREEN
# =========================================================

def teacher_screen_register():

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    col1, col2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    with col1:

        header_dashboard()

    # -----------------------------------------------------
    # BACK BUTTON
    # -----------------------------------------------------

    with col2:

        if st.button(
            "Go back to Home",
            type="secondary",
            width="stretch",
            key="teacher_register_back_btn"
        ):

            st.session_state[
                "teacher_login_type"
            ] = "login"

            st.session_state[
                "login_type"
            ] = None

            st.rerun()

    # =====================================================
    # REGISTER TITLE
    # =====================================================

    st.markdown(
        """
        <h2 style="text-align:center;">
            Register your teacher profile
        </h2>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # USERNAME
    # =====================================================

    teacher_username = st.text_input(
        "Enter username",
        placeholder="ananyaroy",
        key="teacher_username_register"
    )

    # =====================================================
    # NAME
    # =====================================================

    teacher_name = st.text_input(
        "Enter name",
        placeholder="Anaya Roy",
        key="teacher_name_register"
    )

    # =====================================================
    # PASSWORD
    # =====================================================

    teacher_pass = st.text_input(
        "Enter password",
        type="password",
        placeholder="Enter password",
        key="teacher_password_register"
    )

    # =====================================================
    # CONFIRM PASSWORD
    # =====================================================

    teacher_pass_confirm = st.text_input(
        "Confirm your password",
        type="password",
        placeholder="Enter password",
        key="teacher_password_confirm_register"
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    # =====================================================
    # REGISTER NOW
    # =====================================================

    with btnc1:

        if st.button(
            "Register Now",
            width="stretch",
            key="teacher_register_now_btn"
        ):

            success, message = (
                register_teacher(
                    teacher_username,
                    teacher_name,
                    teacher_pass,
                    teacher_pass_confirm
                )
            )

            if success:

                st.success(
                    message
                )

                time.sleep(1)

                st.session_state[
                    "teacher_login_type"
                ] = "login"

                st.rerun()

            else:

                st.error(
                    message
                )

    # =====================================================
    # LOGIN INSTEAD
    # =====================================================

    with btnc2:

        if st.button(
            "Login Instead",
            type="primary",
            width="stretch",
            key="teacher_login_instead_btn"
        ):

            st.session_state[
                "teacher_login_type"
            ] = "login"

            st.rerun()

    footer_dashboard()