import streamlit as st

from src.database.db import create_subject


# =========================================================
# CREATE SUBJECT DIALOG
# =========================================================

@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):

    st.write("Enter the details of the new subject.")

    # -----------------------------------------------------
    # SUBJECT CODE
    # -----------------------------------------------------

    subject_code = st.text_input(
        "Subject Code",
        placeholder="CS101",
        key="create_subject_code"
    )

    # -----------------------------------------------------
    # SUBJECT NAME
    # -----------------------------------------------------

    subject_name = st.text_input(
        "Subject Name",
        placeholder="Introduction to Computer Science",
        key="create_subject_name"
    )

    # -----------------------------------------------------
    # SECTION
    # -----------------------------------------------------

    section = st.text_input(
        "Section",
        placeholder="A",
        key="create_subject_section"
    )

    # -----------------------------------------------------
    # CREATE BUTTON
    # -----------------------------------------------------

    if st.button(
        "Create Subject Now",
        type="primary",
        width="stretch",
        key="create_subject_now_btn"
    ):

        subject_code = subject_code.strip()
        subject_name = subject_name.strip()
        section = section.strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not subject_code:
            st.warning("Please enter Subject Code.")
            return

        if not subject_name:
            st.warning("Please enter Subject Name.")
            return

        if not section:
            st.warning("Please enter Section.")
            return

        if not teacher_id:
            st.error("Teacher ID not found. Please login again.")
            return

        # -------------------------------------------------
        # CREATE SUBJECT
        # -------------------------------------------------

        try:

            result = create_subject(
                subject_code,
                subject_name,
                section,
                teacher_id
            )

            if result is None:
                st.error(
                    "Subject could not be created. "
                    "Subject code may already exist."
                )
                return

            st.success(
                "Subject created successfully! 🎉"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Error creating subject: {e}"
            )