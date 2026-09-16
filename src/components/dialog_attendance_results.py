import streamlit as st
import pandas as pd

from src.database.db import create_attendance


# =========================================================
# SHOW ATTENDANCE RESULT
# =========================================================

def show_attendance_result(df, logs):

    st.write(
        "Please review attendance before confirming."
    )

    # =====================================================
    # ATTENDANCE TABLE
    # =====================================================

    if df is not None and not df.empty:

        st.dataframe(
            df,
            hide_index=True,
            width="stretch"
        )

    else:

        st.warning(
            "No attendance results available."
        )

        return

    st.divider()

    # =====================================================
    # BUTTONS
    # =====================================================

    col1, col2 = st.columns(2)

    # =====================================================
    # DISCARD
    # =====================================================

    with col1:

        if st.button(
            "Discard",
            width="stretch",
            key="attendance_discard_btn"
        ):

            # Clear voice results
            st.session_state[
                "voice_attendance_results"
            ] = None

            # Clear photos
            st.session_state[
                "attendance_images"
            ] = []

            st.rerun()

    # =====================================================
    # CONFIRM & SAVE
    # =====================================================

    with col2:

        if st.button(
            "Confirm & Save",
            width="stretch",
            type="primary",
            key="attendance_confirm_save_btn"
        ):

            try:

                # -----------------------------------------
                # CHECK LOGS
                # -----------------------------------------

                if not logs:

                    st.warning(
                        "There is no attendance to save."
                    )

                    return

                # -----------------------------------------
                # SAVE ATTENDANCE
                # -----------------------------------------

                create_attendance(logs)

                # -----------------------------------------
                # SUCCESS MESSAGE
                # -----------------------------------------

                st.success(
                    "Attendance taken successfully!"
                )

                st.toast(
                    "Attendance saved successfully."
                )

                # -----------------------------------------
                # CLEAR SESSION DATA
                # -----------------------------------------

                st.session_state[
                    "attendance_images"
                ] = []

                st.session_state[
                    "voice_attendance_results"
                ] = None

                # -----------------------------------------
                # REFRESH
                # -----------------------------------------

                st.rerun()

            except Exception as e:

                st.error(
                    f"Unable to save attendance: {e}"
                )

                st.exception(e)


# =========================================================
# ATTENDANCE REPORT DIALOG
# =========================================================

@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):

    show_attendance_result(
        df,
        logs
    )