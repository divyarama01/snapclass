import streamlit as st
import pandas as pd
from datetime import datetime

from src.pipeline.voice_pipeline import process_bulk_audio
from src.database.db import get_subject_students
from src.components.dialog_attendance_results import show_attendance_result


# =========================================================
# VOICE ATTENDANCE DIALOG
# =========================================================

@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):

    st.write(
        "Record classroom audio and analyze student voices "
        "to mark attendance."
    )

    st.divider()

    # =====================================================
    # RECORD AUDIO
    # =====================================================

    st.markdown("### 🎙️ Record Classroom Audio")

    audio_data = st.audio_input(
        "Record classroom audio",
        key="classroom_voice_audio"
    )

    if audio_data is not None:

        st.audio(
            audio_data,
            format="audio/wav"
        )

    # =====================================================
    # ANALYZE AUDIO
    # =====================================================

    if st.button(
        "Analyze Audio",
        width="stretch",
        type="primary",
        key="analyze_voice_audio_btn"
    ):

        if audio_data is None:

            st.warning(
                "Please record classroom audio first."
            )

            return

        with st.spinner(
            "Analyzing classroom audio..."
        ):

            try:

                # =========================================
                # GET ENROLLED STUDENTS
                # =========================================

                enrolled_students = get_subject_students(
                    selected_subject_id
                )

                if not enrolled_students:

                    st.warning(
                        "No students are enrolled in this subject."
                    )

                    return

                # =========================================
                # PREPARE VOICE CANDIDATES
                # =========================================

                candidates_dict = {}

                for student in enrolled_students:

                    student_id = student.get(
                        "student_id"
                    )

                    voice_embedding = student.get(
                        "voice_embedding"
                    )

                    if student_id is None:
                        continue

                    if not voice_embedding:
                        continue

                    student_id = str(
                        student_id
                    ).strip()

                    candidates_dict[
                        student_id
                    ] = voice_embedding

                if not candidates_dict:

                    st.warning(
                        "No enrolled student has a "
                        "registered voice embedding."
                    )

                    return

                # =========================================
                # READ AUDIO
                # =========================================

                audio_bytes = audio_data.read()

                if not audio_bytes:

                    st.warning(
                        "Unable to read recorded audio."
                    )

                    return

                # =========================================
                # PROCESS AUDIO
                # =========================================

                detected_scores = process_bulk_audio(
                    audio_bytes,
                    candidates_dict
                )

                if detected_scores is None:

                    detected_scores = {}

                # =========================================
                # CREATE ATTENDANCE RESULTS
                # =========================================

                results = []

                attendance_to_log = []

                current_timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                current_date = datetime.now().strftime(
                    "%Y-%m-%d"
                )

                for student in enrolled_students:

                    student_id = str(
                        student.get(
                            "student_id",
                            ""
                        )
                    ).strip()

                    student_name = student.get(
                        "name",
                        "Unknown Student"
                    )

                    # -------------------------------------
                    # GET SCORE
                    # -------------------------------------

                    score = detected_scores.get(
                        student_id,
                        0.0
                    )

                    # Handle pipelines returning integer IDs
                    if score == 0.0 and student_id.isdigit():

                        score = detected_scores.get(
                            int(student_id),
                            0.0
                        )

                    try:

                        score = float(score)

                    except (
                        TypeError,
                        ValueError
                    ):

                        score = 0.0

                    # -------------------------------------
                    # PRESENT / ABSENT
                    # -------------------------------------

                    is_present = score > 0

                    results.append(
                        {
                            "Name": student_name,
                            "ID": student_id,
                            "Source": (
                                "Voice"
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

                    if is_present:

                        attendance_to_log.append(
                            {
                                "student_id": student_id,
                                "subject_id": selected_subject_id,
                                "attendance_date": current_date,
                                "status": "Present",
                                "timestamp": current_timestamp,
                                "source": "Voice"
                            }
                        )

                # =========================================
                # DATAFRAME
                # =========================================

                df_results = pd.DataFrame(
                    results
                )

                # =========================================
                # SAVE IN SESSION STATE
                # =========================================

                st.session_state[
                    "voice_attendance_results"
                ] = (
                    df_results,
                    attendance_to_log
                )

                st.success(
                    "Voice analysis completed successfully."
                )

            except Exception as e:

                st.error(
                    f"Voice attendance analysis failed: {e}"
                )

                st.exception(e)

    # =====================================================
    # SHOW PREVIOUS RESULTS
    # =====================================================

    voice_results = st.session_state.get(
        "voice_attendance_results"
    )

    if voice_results is not None:

        st.divider()

        df_results, logs = voice_results

        if not df_results.empty:

            show_attendance_result(
                df_results,
                logs
            )

        else:

            st.warning(
                "No attendance results available."
            )