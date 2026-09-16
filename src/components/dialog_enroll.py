import streamlit as st

from src.database.db import (
    get_subject,
    enroll_student_to_subject,
)


# =========================================================
# ENROLL STUDENT IN SUBJECT
# =========================================================

@st.dialog("Enroll in Subject")
def enroll_subject_dialog(student_id=None):

    st.write(
        "Enter the subject code provided by your teacher."
    )

    # =====================================================
    # SUBJECT CODE INPUT
    # =====================================================

    subject_code = st.text_input(
        "Subject Code",
        placeholder="CS204",
        key="enroll_subject_code",
    )

    st.caption(
        "Example: CS204"
    )

    # =====================================================
    # ENROLL BUTTON
    # =====================================================

    if st.button(
        "Enroll Now",
        type="primary",
        width="stretch",
        key="enroll_now_btn",
    ):

        # =================================================
        # CLEAN SUBJECT CODE
        # =================================================

        subject_code = subject_code.strip()

        # =================================================
        # CHECK SUBJECT CODE
        # =================================================

        if not subject_code:

            st.warning(
                "⚠️ Please enter Subject Code."
            )

            return

        # =================================================
        # CHECK STUDENT ID
        # =================================================

        if not student_id:

            student_data = st.session_state.get(
                "student_data",
                {},
            )

            if isinstance(
                student_data,
                dict,
            ):

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
                )

        # =================================================
        # VALIDATE STUDENT ID
        # =================================================

        if not student_id:

            st.error(
                "❌ Student ID not found. "
                "Please login again."
            )

            return

        student_id = str(
            student_id
        ).strip()

        # =================================================
        # FIND SUBJECT
        # =================================================

        try:

            subject = get_subject(
                subject_code
            )

        except Exception as e:

            st.error(
                f"❌ Could not find subject: {e}"
            )

            return

        # =================================================
        # SUBJECT NOT FOUND
        # =================================================

        if subject is None:

            st.error(
                f"❌ Subject '{subject_code}' not found."
            )

            st.info(
                "Please check the subject code "
                "provided by your teacher."
            )

            return

        # =================================================
        # GET SUBJECT ID
        # =================================================

        try:

            subject_id = subject["id"]

        except (
            KeyError,
            TypeError,
        ):

            st.error(
                "❌ Subject ID could not be found "
                "in the database."
            )

            return

        if subject_id is None:

            st.error(
                "❌ Invalid Subject ID."
            )

            return

        # =================================================
        # ENROLL STUDENT
        # =================================================

        try:

            success = enroll_student_to_subject(
                student_id,
                subject_id,
            )

        except Exception as e:

            st.error(
                f"❌ Enrollment failed: {e}"
            )

            return

        # =================================================
        # ENROLLMENT SUCCESS
        # =================================================

        if success:

            st.success(
                f"🎉 Successfully enrolled in "
                f"{subject.get('name', subject_code)}!"
            )

            st.info(
                f"Subject Code: {subject.get('subject_code', subject_code)}"
            )

            # Close dialog and refresh dashboard
            time_to_refresh = 0.5

            import time

            time.sleep(
                time_to_refresh
            )

            st.rerun()

        # =================================================
        # ALREADY ENROLLED / FAILED
        # =================================================

        else:

            st.warning(
                "⚠️ You are already enrolled in this "
                "subject or enrollment failed."
            )