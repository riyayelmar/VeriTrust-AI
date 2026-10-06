import cv2
import numpy as np
from insightface.app import FaceAnalysis


_face_app = None


def get_face_app():

    global _face_app

    if _face_app is None:

        _face_app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        _face_app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

    return _face_app


def load_image(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image.")

    return image


def get_face_embedding(image_path):

    image = load_image(image_path)

    app = get_face_app()

    faces = app.get(image)

    if not faces:
        return None

    # सर्वात मोठा detected face घ्या
    face = max(
        faces,
        key=lambda x:
        (x.bbox[2] - x.bbox[0]) *
        (x.bbox[3] - x.bbox[1])
    )

    embedding = face.embedding

    embedding = embedding / np.linalg.norm(
        embedding
    )

    return embedding


def compare_faces(reference_image, live_image):

    try:

        # Profile Photo
        reference_embedding = get_face_embedding(
            reference_image
        )

        if reference_embedding is None:

            return {
                "score": 0,
                "verified": False,
                "message":
                    "No face found in registered profile photo."
            }


        # Live Selfie
        live_embedding = get_face_embedding(
            live_image
        )

        if live_embedding is None:

            return {
                "score": 0,
                "verified": False,
                "message":
                    "No face found in live selfie."
            }


        # Cosine Similarity
        similarity = float(
            np.dot(
                reference_embedding,
                live_embedding
            )
        )


        # Display score
        score = ((similarity + 1) / 2) * 100

        score = round(
            max(0, min(100, score)),
            2
        )


        # Verification threshold
        threshold = 75


        if score >= threshold:

            return {
                "score": score,
                "verified": True,
                "message":
                    "Face matched successfully with registered profile photo."
            }


        return {
            "score": score,
            "verified": False,
            "message":
                "Face does not match with registered profile photo."
        }


    except Exception as e:

        return {
            "score": 0,
            "verified": False,
            "message":
                f"Face verification error: {str(e)}"
        }