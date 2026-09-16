import streamlit as st
from PIL import Image


# =========================================================
# ADD PHOTOS DIALOG
# =========================================================

@st.dialog("Capture or Upload Photos")
def add_photos_dialog():

    st.write(
        "Add classroom photos to scan for attendance"
    )

    # =====================================================
    # SESSION STATE
    # =====================================================

    if "photo_tab" not in st.session_state:
        st.session_state["photo_tab"] = "camera"

    if "attendance_images" not in st.session_state:
        st.session_state["attendance_images"] = []

    # =====================================================
    # CAMERA / UPLOAD BUTTONS
    # =====================================================

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # CAMERA BUTTON
    # -----------------------------------------------------

    with col1:

        if st.button(
            "📷 Camera",
            width="stretch",
            key="dialog_camera_tab"
        ):

            st.session_state["photo_tab"] = "camera"

            st.rerun()

    # -----------------------------------------------------
    # UPLOAD BUTTON
    # -----------------------------------------------------

    with col2:

        if st.button(
            "📁 Upload Photos",
            width="stretch",
            key="dialog_upload_tab"
        ):

            st.session_state["photo_tab"] = "upload"

            st.rerun()

    st.divider()

    # =====================================================
    # CAMERA
    # =====================================================

    if st.session_state["photo_tab"] == "camera":

        st.subheader("Take Classroom Photo")

        camera_photo = st.camera_input(
            "Take snapshot",
            key="dialog_camera_input"
        )

        if camera_photo is not None:

            try:

                image = Image.open(
                    camera_photo
                ).copy()

                st.session_state[
                    "attendance_images"
                ].append(image)

                st.success(
                    "Photo captured successfully!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Unable to process photo: {e}"
                )

    # =====================================================
    # UPLOAD
    # =====================================================

    elif st.session_state["photo_tab"] == "upload":

        st.subheader(
            "Upload Classroom Photos"
        )

        uploaded_files = st.file_uploader(
            "Choose image files",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            accept_multiple_files=True,
            key="dialog_upload_files"
        )

        if uploaded_files:

            for uploaded_file in uploaded_files:

                try:

                    image = Image.open(
                        uploaded_file
                    ).copy()

                    # -------------------------------------
                    # Prevent duplicate upload
                    # -------------------------------------

                    file_key = (
                        f"{uploaded_file.name}_"
                        f"{uploaded_file.size}"
                    )

                    if (
                        "uploaded_photo_keys"
                        not in st.session_state
                    ):

                        st.session_state[
                            "uploaded_photo_keys"
                        ] = []

                    if (
                        file_key
                        not in
                        st.session_state[
                            "uploaded_photo_keys"
                        ]
                    ):

                        st.session_state[
                            "attendance_images"
                        ].append(image)

                        st.session_state[
                            "uploaded_photo_keys"
                        ].append(file_key)

                except Exception as e:

                    st.error(
                        f"Unable to process "
                        f"{uploaded_file.name}: {e}"
                    )

    # =====================================================
    # SHOW PHOTOS
    # =====================================================

    photos = st.session_state[
        "attendance_images"
    ]

    if photos:

        st.divider()

        st.subheader(
            f"Photos Added: {len(photos)}"
        )

        for start in range(
            0,
            len(photos),
            3
        ):

            columns = st.columns(3)

            row_photos = photos[
                start:start + 3
            ]

            for index, image in enumerate(
                row_photos
            ):

                photo_index = start + index

                with columns[index]:

                    st.image(
                        image,
                        width="stretch"
                    )

                    if st.button(
                        "Remove",
                        key=f"remove_photo_{photo_index}"
                    ):

                        st.session_state[
                            "attendance_images"
                        ].pop(photo_index)

                        st.rerun()

        # =================================================
        # CLEAR ALL
        # =================================================

        st.divider()

        if st.button(
            "Clear All Photos",
            width="stretch",
            key="clear_all_photos_btn"
        ):

            st.session_state[
                "attendance_images"
            ] = []

            st.session_state[
                "uploaded_photo_keys"
            ] = []

            st.rerun()

    # =====================================================
    # DONE
    # =====================================================

    st.divider()

    if st.button(
        "Done",
        type="primary",
        width="stretch",
        key="dialog_done_btn"
    ):

        st.rerun()