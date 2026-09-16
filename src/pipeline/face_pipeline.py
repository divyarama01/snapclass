import dlib
import numpy as np
import face_recognition_models

from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


# =====================================================
# LOAD DLIB MODELS
# =====================================================

@st.cache_resource
def load_dlib_models():

    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


# =====================================================
# GET FACE EMBEDDINGS
# =====================================================

def get_face_embeddings(image_np):

    detector, sp, facerec = load_dlib_models()

    faces = detector(image_np, 1)

    encodings = []

    for face in faces:

        shape = sp(image_np, face)

        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(
            np.array(face_descriptor)
        )

    return encodings


# =====================================================
# TRAIN MODEL
# =====================================================

@st.cache_resource
def get_trained_model():

    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:

        embedding = student.get("face_embedding")

        if embedding:

            X.append(
                np.array(embedding, dtype=float)
            )

            y.append(
                student.get("student_id")
            )

    # No face embeddings found
    if len(X) == 0:
        return None

    # Only one student/class
    # SVC needs at least 2 classes
    if len(set(y)) < 2:

        return {
            "clf": None,
            "X": X,
            "y": y
        }

    clf = SVC(
        kernel="linear",
        probability=True,
        class_weight="balanced"
    )

    try:

        clf.fit(X, y)

    except ValueError as e:

        st.error(f"Model training error: {e}")

        return None

    return {
        "clf": clf,
        "X": X,
        "y": y
    }


# =====================================================
# TRAIN CLASSIFIER
# =====================================================

def train_classifier():

    st.cache_resource.clear()

    model_data = get_trained_model()

    return model_data is not None


# =====================================================
# PREDICT ATTENDANCE
# =====================================================

def predict_attendance(class_image_np):

    encodings = get_face_embeddings(
        class_image_np
    )

    detected_student = {}

    model_data = get_trained_model()

    # No trained model
    if not model_data:

        return (
            detected_student,
            [],
            len(encodings)
        )

    X_train = model_data["X"]
    y_train = model_data["y"]
    clf = model_data["clf"]

    all_students = sorted(
        list(set(y_train))
    )

    # No students
    if not all_students:

        return (
            detected_student,
            [],
            len(encodings)
        )

    # =================================================
    # CHECK EACH DETECTED FACE
    # =================================================

    for encoding in encodings:

        # ---------------------------------------------
        # Multiple students
        # ---------------------------------------------

        if len(all_students) >= 2 and clf is not None:

            predicted_id = clf.predict(
                [encoding]
            )[0]

        # ---------------------------------------------
        # Only one student
        # ---------------------------------------------

        else:

            predicted_id = all_students[0]

        # ---------------------------------------------
        # Find student's stored embedding
        # ---------------------------------------------

        try:

            student_index = y_train.index(
                predicted_id
            )

        except ValueError:

            continue

        student_embedding = X_train[
            student_index
        ]

        # ---------------------------------------------
        # Calculate distance
        # ---------------------------------------------

        best_match_score = np.linalg.norm(
            student_embedding - encoding
        )

        # ---------------------------------------------
        # Threshold
        # ---------------------------------------------

        resemblance_threshold = 0.6

        if best_match_score <= resemblance_threshold:

            detected_student[
                predicted_id
            ] = True

    return (
        detected_student,
        all_students,
        len(encodings)
    )