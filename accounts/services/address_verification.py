import re

from django.utils import timezone

from difflib import SequenceMatcher

from .ocr_service import extract_text_from_image



# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    # Common OCR replacements
    text = text.replace("|", " ")
    text = text.replace("\n", " ")

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# BUILD USER ENTERED ADDRESS
# =========================================================

def build_address_text(address):

    parts = [
        address.house_no,
        address.street,
        address.area,
        address.city,
        address.district,
        address.state,
        address.pincode,
    ]

    return " ".join(
        str(part)
        for part in parts
        if part
    )


# =========================================================
# FIELD SIMILARITY
# =========================================================

def field_similarity(value, extracted_text):

    value = normalize_text(
        value
    )

    extracted = normalize_text(
        extracted_text
    )

    if not value or not extracted:
        return 0.0

    # -----------------------------------------------------
    # EXACT PHRASE MATCH
    # -----------------------------------------------------

    if value in extracted:
        return 100.0

    # -----------------------------------------------------
    # TOKEN MATCH
    # -----------------------------------------------------

    value_tokens = value.split()

    extracted_tokens = extracted.split()

    if not value_tokens:
        return 0.0

    matched_tokens = 0

    for token in value_tokens:

        if token in extracted_tokens:
            matched_tokens += 1

    token_score = (
        matched_tokens
        /
        len(value_tokens)
    ) * 100

    # -----------------------------------------------------
    # FUZZY MATCH
    # -----------------------------------------------------

    fuzzy_score = SequenceMatcher(
        None,
        value,
        extracted
    ).ratio() * 100

    return round(
        max(
            token_score,
            fuzzy_score
        ),
        2
    )


# =========================================================
# CALCULATE ADDRESS MATCH SCORE
# =========================================================

def calculate_address_match_score(
    entered_address,
    extracted_text
):

    if not extracted_text:
        return 0.0

    # -----------------------------------------------------
    # WEIGHTS
    #
    # Total = 100
    # -----------------------------------------------------

    weights = {
        "pincode": 30,
        "city": 20,
        "state": 15,
        "district": 10,
        "area": 10,
        "street": 10,
        "house_no": 5,
    }

    field_values = {
        "pincode": entered_address.pincode,
        "city": entered_address.city,
        "state": entered_address.state,
        "district": entered_address.district,
        "area": entered_address.area,
        "street": entered_address.street,
        "house_no": entered_address.house_no,
    }

    final_score = 0.0

    for field_name, weight in weights.items():

        value = field_values.get(
            field_name
        )

        if not value:
            continue

        score = field_similarity(
            value,
            extracted_text
        )

        # Weighted contribution
        final_score += (
            score * weight / 100
        )

    return round(
        min(final_score, 100),
        2
    )


# =========================================================
# EXTRACT ADDRESS FROM OCR TEXT
# =========================================================

def extract_address_from_text(text):

    if not text:
        return ""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return ""

    # -----------------------------------------------------
    # ADDRESS KEYWORDS
    # -----------------------------------------------------

    address_keywords = [
        "address",
        "residential address",
        "permanent address",
        "correspondence address",
        "present address",
    ]

    # -----------------------------------------------------
    # STOP KEYWORDS
    # -----------------------------------------------------

    stop_keywords = [
        "date of birth",
        "dob",
        "gender",
        "mobile",
        "phone",
        "email",
        "signature",
        "authority",
        "uidai",
    ]

    address_lines = []

    address_started = False

    # -----------------------------------------------------
    # METHOD 1
    # FIND ADDRESS SECTION
    # -----------------------------------------------------

    for line in lines:

        normalized_line = normalize_text(
            line
        )

        # Start address section
        if any(
            keyword in normalized_line
            for keyword in address_keywords
        ):

            address_started = True

            cleaned_line = re.sub(
                r"^(address|residential address|permanent address|correspondence address|present address)\s*[:\-]?\s*",
                "",
                line,
                flags=re.IGNORECASE
            )

            if cleaned_line.strip():

                address_lines.append(
                    cleaned_line.strip()
                )

            continue

        if address_started:

            if any(
                keyword in normalized_line
                for keyword in stop_keywords
            ):

                break

            address_lines.append(
                line
            )

    if address_lines:

        return " ".join(
            address_lines
        ).strip()


    # -----------------------------------------------------
    # METHOD 2
    # FIND PINCODE
    # -----------------------------------------------------

    pincode_pattern = r"\b\d{6}\b"

    for index, line in enumerate(lines):

        if re.search(
            pincode_pattern,
            line
        ):

            start = max(
                0,
                index - 4
            )

            end = min(
                len(lines),
                index + 2
            )

            possible_address = (
                lines[start:end]
            )

            return " ".join(
                possible_address
            ).strip()


    # -----------------------------------------------------
    # METHOD 3
    # OCR TEXT FALLBACK
    # -----------------------------------------------------

    return " ".join(
        lines
    ).strip()


# =========================================================
# VERIFY SINGLE ADDRESS DOCUMENT
# =========================================================

def verify_address_document(proof):

    address = (
        proof.address_verification
    )

    # -----------------------------------------------------
    # FILE CHECK
    # -----------------------------------------------------

    if not proof.file:

        proof.verification_status = (
            "needs_review"
        )

        proof.verification_message = (
            "No document file was found."
        )

        proof.address_match_score = 0

        proof.verified_at = (
            timezone.now()
        )

        proof.save()

        return "needs_review"


    # -----------------------------------------------------
    # OCR
    # -----------------------------------------------------

    try:

        extracted_text = (
            extract_text_from_image(
                proof.file.path
            )
        )

    except Exception as error:

        print(
            "Address OCR Error:",
            error
        )

        extracted_text = ""


    # -----------------------------------------------------
    # OCR FAILED
    # -----------------------------------------------------

    if not extracted_text:

        proof.extracted_text = ""

        proof.extracted_address = ""

        proof.address_match_score = 0

        proof.verification_status = (
            "needs_review"
        )

        proof.verification_message = (
            "Unable to extract readable text "
            "from the uploaded document."
        )

        proof.verified_at = (
            timezone.now()
        )

        proof.save()

        return "needs_review"


    # -----------------------------------------------------
    # SAVE FULL OCR TEXT
    # -----------------------------------------------------

    proof.extracted_text = (
        extracted_text
    )


    # -----------------------------------------------------
    # EXTRACT ADDRESS
    # -----------------------------------------------------

    extracted_address = (
        extract_address_from_text(
            extracted_text
        )
    )

    proof.extracted_address = (
        extracted_address
    )


    # -----------------------------------------------------
    # ADDRESS EXTRACTION FAILED
    # -----------------------------------------------------

    if not extracted_address:

        proof.address_match_score = 0

        proof.verification_status = (
            "needs_review"
        )

        proof.verification_message = (
            "Address could not be extracted "
            "from the uploaded document."
        )

        proof.verified_at = (
            timezone.now()
        )

        proof.save()

        return "needs_review"


    # -----------------------------------------------------
    # CALCULATE MATCH SCORE
    # -----------------------------------------------------

    score = (
        calculate_address_match_score(
            address,
            extracted_address
        )
    )

    proof.address_match_score = (
        score
    )


    # -----------------------------------------------------
    # FINAL DOCUMENT DECISION
    # -----------------------------------------------------

    if score >= 85:

        proof.verification_status = (
            "verified"
        )

        proof.verification_message = (
            f"Address verified successfully. "
            f"Match score: {score}%."
        )


    elif score >= 60:

        proof.verification_status = (
            "needs_review"
        )

        proof.verification_message = (
            f"Address partially matched. "
            f"Match score: {score}%. "
            f"Manual review is required."
        )


    else:

        proof.verification_status = (
            "rejected"
        )

        proof.verification_message = (
            f"Address mismatch detected. "
            f"Match score: {score}%."
        )


    # -----------------------------------------------------
    # VERIFIED TIME
    # -----------------------------------------------------

    proof.verified_at = (
        timezone.now()
    )

    proof.save()

    return (
        proof.verification_status
    )


# =========================================================
# FINAL ADDRESS STATUS
# =========================================================

def calculate_final_address_status(
    address_verification
):

    proofs = (
        address_verification.proofs.all()
    )

    documents = proofs.filter(
        proof_type="document"
    )

    building_photos = proofs.filter(
        proof_type="building_photo"
    )

    videos = proofs.filter(
        proof_type="surrounding_video"
    )


    # =====================================================
    # REQUIRED ADDRESS DATA
    # =====================================================

    required_address_fields = [
        address_verification.house_no,
        address_verification.street,
        address_verification.area,
        address_verification.city,
        address_verification.district,
        address_verification.state,
        address_verification.pincode,
    ]

    if not all(
        required_address_fields
    ):

        address_verification.status = (
            "pending"
        )

        address_verification.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return "pending"


    # =====================================================
    # GPS CHECK
    # =====================================================

    if (
        address_verification.latitude is None
        or
        address_verification.longitude is None
    ):

        address_verification.location_verified = (
            False
        )

        address_verification.status = (
            "pending"
        )

        address_verification.save(
            update_fields=[
                "location_verified",
                "status",
                "updated_at",
            ]
        )

        return "pending"


    # =====================================================
    # DOCUMENT COUNT
    # =====================================================

    if documents.count() < 2:

        address_verification.status = (
            "pending"
        )

        address_verification.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return "pending"


    # =====================================================
    # BUILDING PHOTOS
    # =====================================================

    if building_photos.count() < 2:

        address_verification.status = (
            "pending"
        )

        address_verification.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return "pending"


    # =====================================================
    # VIDEO
    # =====================================================

    if videos.count() < 1:

        address_verification.status = (
            "pending"
        )

        address_verification.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return "pending"


    # =====================================================
    # VERIFY DOCUMENT STATUS
    # =====================================================

    document_scores = []

    for proof in documents:

        # -------------------------------------------------
        # REJECTED DOCUMENT
        # -------------------------------------------------

        if (
            proof.verification_status
            == "rejected"
        ):

            address_verification.location_verified = (
                False
            )

            address_verification.status = (
                "rejected"
            )

            address_verification.save(
                update_fields=[
                    "location_verified",
                    "status",
                    "updated_at",
                ]
            )

            return "rejected"


        # -------------------------------------------------
        # NEEDS REVIEW / PENDING
        # -------------------------------------------------

        if (
            proof.verification_status
            != "verified"
        ):

            address_verification.location_verified = (
                False
            )

            address_verification.status = (
                "needs_review"
            )

            address_verification.save(
                update_fields=[
                    "location_verified",
                    "status",
                    "updated_at",
                ]
            )

            return "needs_review"


        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        if (
            proof.address_match_score
            is not None
        ):

            document_scores.append(
                float(
                    proof.address_match_score
                )
            )


    # =====================================================
    # TWO VERIFIED SCORES REQUIRED
    # =====================================================

    if len(
        document_scores
    ) < 2:

        address_verification.status = (
            "pending"
        )

        address_verification.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return "pending"


    # =====================================================
    # AVERAGE SCORE
    # =====================================================

    average_score = (
        sum(document_scores)
        /
        len(document_scores)
    )

    average_score = round(
        average_score,
        2
    )


    # =====================================================
    # FINAL DECISION
    # =====================================================

    if average_score >= 85:

        address_verification.location_verified = (
            True
        )

        address_verification.status = (
            "verified"
        )


    elif average_score >= 60:

        address_verification.location_verified = (
            False
        )

        address_verification.status = (
            "needs_review"
        )


    else:

        address_verification.location_verified = (
            False
        )

        address_verification.status = (
            "rejected"
        )


    address_verification.save(
        update_fields=[
            "location_verified",
            "status",
            "updated_at",
        ]
    )

    return (
        address_verification.status
    )