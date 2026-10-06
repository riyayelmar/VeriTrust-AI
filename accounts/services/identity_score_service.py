from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone


def calculate_final_identity_score(identity):

    aadhaar_score = Decimal("0.00")
    pan_score = Decimal("0.00")
    selfie_score = Decimal("0.00")

    # -----------------------------------------
    # AADHAAR
    # -----------------------------------------

    if (
        identity.aadhaar_status
        and identity.aadhaar_status.upper() == "VERIFIED"
    ):
        aadhaar_score = Decimal(
            str(identity.aadhaar_match_score or 0)
        )

    # -----------------------------------------
    # PAN
    # -----------------------------------------

    if (
        identity.pan_status
        and identity.pan_status.upper() == "VERIFIED"
    ):
        pan_score = Decimal(
            str(identity.pan_match_score or 0)
        )

    # -----------------------------------------
    # SELFIE
    # -----------------------------------------

    if (
        identity.selfie_status
        and identity.selfie_status.upper() == "VERIFIED"
    ):
        selfie_score = Decimal(
            str(identity.selfie_match_score or 0)
        )

    # -----------------------------------------
    # FINAL WEIGHTED SCORE
    # -----------------------------------------

    final_score = (
        aadhaar_score * Decimal("0.40")
        + pan_score * Decimal("0.30")
        + selfie_score * Decimal("0.30")
    )

    return final_score.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def update_final_identity_status(identity):

    # -----------------------------------------
    # Keep VERIFIED component scores consistent
    # -----------------------------------------

    if identity.aadhaar_status == "VERIFIED":
        identity.aadhaar_match_score = Decimal("100.00")

    if identity.pan_status == "VERIFIED":
        identity.pan_match_score = Decimal("100.00")

    if identity.selfie_status == "VERIFIED":
        identity.selfie_match_score = Decimal("100.00")

    # -----------------------------------------
    # FINAL SCORE
    # -----------------------------------------

    score = calculate_final_identity_score(identity)

    identity.verification_score = score

    aadhaar_status = (
        identity.aadhaar_status or "PENDING"
    ).upper()

    pan_status = (
        identity.pan_status or "PENDING"
    ).upper()

    selfie_status = (
        identity.selfie_status or "PENDING"
    ).upper()

    # -----------------------------------------
    # FAILED
    # -----------------------------------------

    if (
        aadhaar_status == "FAILED"
        or pan_status == "FAILED"
        or selfie_status == "FAILED"
    ):

        identity.verification_status = "FAILED"

        identity.verification_message = (
            "Identity verification failed because "
            "one or more verification checks failed."
        )

        identity.verified_at = None

    # -----------------------------------------
    # NEEDS REVIEW
    # -----------------------------------------

    elif (
        aadhaar_status == "NEEDS_REVIEW"
        or pan_status == "NEEDS_REVIEW"
        or selfie_status == "NEEDS_REVIEW"
    ):

        identity.verification_status = "NEEDS_REVIEW"

        identity.verification_message = (
            "Identity verification requires manual review."
        )

        identity.verified_at = None

    # -----------------------------------------
    # PROCESSING / PENDING
    # -----------------------------------------

    elif (
        aadhaar_status != "VERIFIED"
        or pan_status != "VERIFIED"
        or selfie_status != "VERIFIED"
    ):

        identity.verification_status = "PROCESSING"

        identity.verification_message = (
            "Identity verification is still in progress. "
            "Aadhaar, PAN and Live Selfie verification "
            "must be completed."
        )

        identity.verified_at = None

    # -----------------------------------------
    # ALL VERIFIED
    # -----------------------------------------

    else:

        identity.verification_score = Decimal("100.00")

        identity.verification_status = "VERIFIED"

        identity.verification_message = (
            "Identity verification completed successfully."
        )

        if not identity.verified_at:
            identity.verified_at = timezone.now()

    return identity