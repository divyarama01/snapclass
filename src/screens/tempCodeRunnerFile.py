import time
import streamlit as st

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card

from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects
)

from components.dialog_enroll import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog


# =========================================================
# TEACHER MAIN SCREEN
# =========================================================

def teachers_screen():

    style_background_dashboard()
    style_base_layout()

    # -----------------------------------------------------
    # TEACHER ALREADY LOGGED IN
    # -----------------------------------------------------

    if "teacher_data" in st.session_state:
        teacher_dashboard()

    # -----------------------------------------------------
    # LOGIN SCREEN
    # -----------------------------------------------------

    elif (
        "teacher_login_type" not in st.session_state
        or st.session_state["teacher_login_type"] == "login"
    ):
        teacher_screen_login()

    # -----------------------------------------------------
    # REGISTER SCREEN
    # -----------------------------------------------------

    elif st.session_state["teacher_login_type"] == "register":
        teacher_screen_register()


# =========================================================
# TEACHER DASHBOARD
# =========================================================

def teacher_dashboard():

    teacher_data = st.session_state.get(
        "teacher_data",
        {}
    )

    # -----------------------------------------------------
    # HEADER + WELCOME
    # -----------------------------------------------------

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    with c1:
        header_dashboard()

    with c2:

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

            st.session_state["is_logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state["teacher_login_type"] = "login"
            st.session_state["current_teacher_tab"] = "take_attendance"

            st.rerun()

    st.space()

    # =====================================================
    # DEFAULT TAB
    # =====================================================

    if "current_teacher_tab" not in st.session_state:
        st.session_state["current_teacher_tab"] = "take_attendance"

    # =====================================================
    # DASHBOARD BUTTONS
    # =====================================================

    tab1, tab2, tab3 = st.columns(3)

    # -----------------------------------------------------
    # TAKE ATTENDANCE
    # -----------------------------------------------------

    with tab1:

        if st.session_state["current_teacher_tab"] == "take_attendance":
            button_type = "primary"
        else:
            button_type = "tertiary"

        if st.button(
            "Take Attendance",
            type=button_type,
            width="stretch",
            key="take_attendance_btn"
        ):

            st.session_state["current_teacher_tab"] = "take_attendance"
            st.rerun()

    # -----------------------------------------------------
    # MANAGE SUBJECTS
    # -----------------------------------------------------

    with tab2:

        if st.session_state["current_teacher_tab"] == "manage_subjects":
            button_type = "primary"
        else:
            button_type = "tertiary"

        if st.button(
            "Manage Subjects",
            type=button_type,
            width="stretch",
            key="manage_subjects_btn"
        ):

            st.session_state["current_teacher_tab"] = "manage_subjects"
            st.rerun()

    # -----------------------------------------------------
    # ATTENDANCE RECORDS
    # -----------------------------------------------------

    with tab3:

        if st.session_state["current_teacher_tab"] == "attendance_records":
            button_type = "primary"
        else:
            button_type = "tertiary"

        if st.button(
            "Attendance Records",
            type=button_type,
            width="stretch",
            key="attendance_records_btn"
        ):

            st.session_state["current_teacher_tab"] = "attendance_records"
            st.rerun()

    st.divider()

    # =====================================================
    # SHOW SELECTED TAB
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

    footer_dashboard()


# =========================================================
# TAKE ATTENDANCE TAB
# =========================================================

def teacher_tab_take_attendance():

    st.header(
        "Take AI Attendance"
    )

    st.info(
        "AI Attendance section is ready."
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

    # -----------------------------------------------------
    # GET TEACHER ID
    # -----------------------------------------------------

    teacher_id = teacher_data.get(
        "teacher_id"
    )

    st.header(
        "Manage Subjects"
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
    # SUBJECT HEADER
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Subjects",
            width="stretch"
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

        for sub in subjects:

            # -------------------------------------------------
            # SUBJECT DATA
            # -------------------------------------------------

            subject_name = sub.get(
                "name",
                "Unknown Subject"
            )

            subject_code = sub.get(
                "subject_code",
                ""
            )

            section = sub.get(
                "section",
                ""
            )

            # -------------------------------------------------
            # SUBJECT STATS
            # -------------------------------------------------

            stats = [
                (
                    "🫂 Students",
                    sub.get("total_students", 0)
                ),
                (
                    "⏱️ Classes",
                    sub.get("total_classes", 0)
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
                    key=f"share_{code}",
                    icon=":material/share:"
                ):

                    st.info(
                        f"Subject Code: {code}"
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
            "NO SUBJECT FOUND. CREATE ONE ABOVE."
        )


# =========================================================
# ATTENDANCE RECORDS TAB
# =========================================================

def teacher_tab_attendance_records():

    st.header(
        "Attendance Records"
    )

    st.info(
        "Attendance Records section is ready."
    )


# =========================================================
# TEACHER LOGIN FUNCTION
# =========================================================

def login_teacher(
    username,
    password
):

    # -----------------------------------------------------
    # REMOVE EXTRA SPACES
    # -----------------------------------------------------

    username = username.strip()
    password = password.strip()

    # -----------------------------------------------------
    # EMPTY FIELDS
    # -----------------------------------------------------

    if not username or not password:
        return False

    try:

        teacher = teacher_login(
            username,
            password
        )

        if teacher:

            st.session_state["user_role"] = "teacher"

            st.session_state["teacher_data"] = teacher

            st.session_state["is_logged_in"] = True

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

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    with c1:
        header_dashboard()

    # -----------------------------------------------------
    # BACK BUTTON
    # -----------------------------------------------------

    with c2:

        if st.button(
            "Go back to Home",
            type="secondary",
            width="stretch",
            key="teacher_login_back_btn"
        ):

            st.session_state["teacher_login_type"] = "login"

            st.session_state["login_type"] = None

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

    st.space()

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

            st.session_state["teacher_login_type"] = "register"

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
    # REMOVE EXTRA SPACES
    # -----------------------------------------------------

    teacher_username = teacher_username.strip()
    teacher_name = teacher_name.strip()
    teacher_pass = teacher_pass.strip()
    teacher_pass_confirm = teacher_pass_confirm.strip()

    # -----------------------------------------------------
    # CHECK EMPTY FIELDS
    # -----------------------------------------------------

    if not teacher_username:
        return False, "Username is required."

    if not teacher_name:
        return False, "Name is required."

    if not teacher_pass:
        return False, "Password is required."

    if not teacher_pass_confirm:
        return False, "Please confirm your password."

    # -----------------------------------------------------
    # CHECK PASSWORD
    # -----------------------------------------------------

    if teacher_pass != teacher_pass_confirm:

        return False, "Passwords do not match."

    # -----------------------------------------------------
    # CHECK USERNAME
    # -----------------------------------------------------

    try:

        if check_teacher_exists(
            teacher_username
        ):

            return False, "Username already taken."

    except Exception as e:

        return False, f"Database error: {e}"

    # -----------------------------------------------------
    # CREATE TEACHER
    # -----------------------------------------------------

    try:

        result = create_teacher(
            teacher_id=teacher_username,
            name=teacher_name,
            email="",
            password=teacher_pass
        )

        if result is None:

            return False, (
                "Teacher account could not be created."
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

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    with c1:
        header_dashboard()

    # -----------------------------------------------------
    # BACK BUTTON
    # -----------------------------------------------------

    with c2:

        if st.button(
            "Go back to Home",
            type="secondary",
            width="stretch",
            key="teacher_register_back_btn"
        ):

            st.session_state["teacher_login_type"] = "login"

            st.session_state["login_type"] = None

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

    st.space()

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

            success, message = register_teacher(
                teacher_username,
                teacher_name,
                teacher_pass,
                teacher_pass_confirm
            )

            if success:

                st.success(
                    message
                )

                time.sleep(1)

                st.session_state["teacher_login_type"] = "login"

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

            st.session_state["teacher_login_type"] = "login"

            st.rerun()

    footer_dashboard()