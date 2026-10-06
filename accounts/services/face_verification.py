import cv2
import numpy as np


def _load_face_detector():
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

    detector = cv2.CascadeClassifier(cascade_path)

    if detector.empty():
        raise RuntimeError(
            "Unable to load Haar Cascade face detector."
        )

    return detector


def _detect_faces(image, detector):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Improve detection for different lighting
    gray = cv2.equalizeHist(gray)

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    return faces, gray


def _get_largest_face(faces):
    if len(faces) == 0:
        return None

    return max(
        faces,
        key=lambda face: face[2] * face[3]
    )


def _crop_face(gray, face):
    x, y, w, h = face

    # Add small margin around face
    margin_x = int(w * 0.20)
    margin_y = int(h * 0.25)

    x1 = max(0, x - margin_x)
    y1 = max(0, y - margin_y)
    x2 = min(gray.shape[1], x + w + margin_x)
    y2 = min(gray.shape[0], y + h + margin_y)

    face_crop = gray[y1:y2, x1:x2]

    return face_crop


def _prepare_face(face):
    face = cv2.resize(
        face,
        (200, 200),
        interpolation=cv2.INTER_AREA
    )

    # CLAHE gives better lighting normalization
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    face = clahe.apply(face)

    # Slight blur removes camera noise
    face = cv2.GaussianBlur(
        face,
        (3, 3),
        0
    )

    return face


def _compare_faces(reference_face, selfie_face):
    """
    Compare normalized face images using
    multiple image similarity methods.
    """

    # -----------------------------------------
    # METHOD 1 - Correlation
    # -----------------------------------------

    correlation = cv2.compareHist(
        cv2.calcHist(
            [reference_face],
            [0],
            None,
            [256],
            [0, 256]
        ),
        cv2.calcHist(
            [selfie_face],
            [0],
            None,
            [256],
            [0, 256]
        ),
        cv2.HISTCMP_CORREL
    )

    correlation_score = max(
        0.0,
        min(
            100.0,
            ((correlation + 1.0) / 2.0) * 100.0
        )
    )

    # -----------------------------------------
    # METHOD 2 - Normalized pixel similarity
    # -----------------------------------------

    ref_float = reference_face.astype(np.float32)
    selfie_float = selfie_face.astype(np.float32)

    mse = np.mean(
        (ref_float - selfie_float) ** 2
    )

    pixel_score = 100.0 - (
        (mse / 65025.0) * 100.0
    )

    pixel_score = max(
        0.0,
        min(
            100.0,
            pixel_score
        )
    )

    # -----------------------------------------
    # METHOD 3 - Edge similarity
    # -----------------------------------------

    ref_edges = cv2.Canny(
        reference_face,
        50,
        150
    )

    selfie_edges = cv2.Canny(
        selfie_face,
        50,
        150
    )

    edge_difference = np.mean(
        cv2.absdiff(
            ref_edges,
            selfie_edges
        )
    )

    edge_score = 100.0 - (
        edge_difference / 255.0 * 100.0
    )

    edge_score = max(
        0.0,
        min(
            100.0,
            edge_score
        )
    )

    # -----------------------------------------
    # FINAL FACE SCORE
    # -----------------------------------------

    score = (
        correlation_score * 0.40
        + pixel_score * 0.35
        + edge_score * 0.25
    )

    return round(
        max(0.0, min(100.0, score)),
        2
    )


def verify_face(
    reference_image_path,
    selfie_image_path
):

    try:

        # -----------------------------------------
        # VALIDATE PATHS
        # -----------------------------------------

        if not reference_image_path:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": False,
                "message": "Profile photo is not available."
            }

        if not selfie_image_path:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": False,
                "message": "Selfie image is not available."
            }

        # -----------------------------------------
        # LOAD IMAGES
        # -----------------------------------------

        reference = cv2.imread(
            str(reference_image_path)
        )

        selfie = cv2.imread(
            str(selfie_image_path)
        )

        if reference is None:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": False,
                "message": "Unable to read profile photo."
            }

        if selfie is None:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": False,
                "message": "Unable to read selfie."
            }

        # -----------------------------------------
        # FACE DETECTOR
        # -----------------------------------------

        detector = _load_face_detector()

        # -----------------------------------------
        # DETECT FACES
        # -----------------------------------------

        reference_faces, reference_gray = _detect_faces(
            reference,
            detector
        )

        selfie_faces, selfie_gray = _detect_faces(
            selfie,
            detector
        )

        # -----------------------------------------
        # PROFILE PHOTO CHECK
        # -----------------------------------------

        if len(reference_faces) == 0:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": False,
                "message": "No face detected in profile photo."
            }

        # -----------------------------------------
        # SELFIE CHECK
        # -----------------------------------------

        if len(selfie_faces) == 0:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": False,
                "message": "No face detected in live selfie."
            }

        # Only one face allowed in selfie
        if len(selfie_faces) > 1:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": True,
                "message": (
                    "Multiple faces detected. "
                    "Please capture selfie with only one face."
                )
            }

        # -----------------------------------------
        # SELECT FACES
        # -----------------------------------------

        reference_face_box = _get_largest_face(
            reference_faces
        )

        selfie_face_box = _get_largest_face(
            selfie_faces
        )

        # -----------------------------------------
        # CROP FACE
        # -----------------------------------------

        reference_face = _crop_face(
            reference_gray,
            reference_face_box
        )

        selfie_face = _crop_face(
            selfie_gray,
            selfie_face_box
        )

        if reference_face.size == 0:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": False,
                "message": "Unable to crop face from profile photo."
            }

        if selfie_face.size == 0:

            return {
                "success": False,
                "verified": False,
                "score": 0.0,
                "face_detected": False,
                "message": "Unable to crop face from selfie."
            }

        # -----------------------------------------
        # PREPARE FACES
        # -----------------------------------------

        reference_face = _prepare_face(
            reference_face
        )

        selfie_face = _prepare_face(
            selfie_face
        )

        # -----------------------------------------
        # COMPARE
        # -----------------------------------------

        score = _compare_faces(
            reference_face,
            selfie_face
        )

        print("========== FACE SCORE DEBUG ==========")
        print("REFERENCE FACE DETECTED:", len(reference_faces))
        print("SELFIE FACE DETECTED:", len(selfie_faces))
        print("FINAL FACE SCORE:", score)
        print("======================================")

        # -----------------------------------------
        # VERIFICATION
        # -----------------------------------------

        verified = score >= 60.0

        if verified:

            message = (
                "Face matched successfully "
                "with the profile photo."
            )

        else:

            message = (
                "Live selfie does not match "
                "the profile photo."
            )

        return {

            "success": True,

            "verified": verified,

            "score": score,

            "face_detected": True,

            "message": message

        }

    except Exception as error:

        import traceback

        traceback.print_exc()

        return {

            "success": False,

            "verified": False,

            "score": 0.0,

            "face_detected": False,

            "message": str(error)

        }