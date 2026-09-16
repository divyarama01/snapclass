import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teachers_screen import teachers_screen
from src.screens.student_screen import student_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog

def main():

    # Login type initialize
    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    # -------------------------------------------------
    # Page title
    # -------------------------------------------------

    st.set_page_config(
        page_title="SnapClass-Making Attendance faster using AI",
        page_icon="🎓https://i.ibb.co/YTYGn5qV/logo.png",
        layout="wide"
    )

    # -------------------------------------------------
    # Application routing
    # -------------------------------------------------

    login_type = st.session_state.get("login_type")

    if login_type == "teacher":

        teachers_screen()

    elif login_type == "student":

        student_screen()

    else:

        home_screen()


if __name__ == "__main__":
    join_code = st.query_params.get('join-code')
    if join_code:
        if st.session_state.login_type != 'student':
            st.sessio_state.login_type = 'student'
            st.rerun()
        if st.sessiom_state.get('is_logged_in') and st.session_state.get('user_role') == 'student': 
            auto_enroll_dialog(join_code)   
    main()