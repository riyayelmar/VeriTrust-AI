import re
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(value):
    """
    Normalizes text only for comparison.
    Example:
    'Riya  Sanjay Yelmar' -> 'RIYA SANJAY YELMAR'
    """
    if value is None:
        return ""

    value = str(value).upper().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^A-Z0-9 ]", "", value)

    return value.strip()


# =========================================================
# EXACT TEXT COMPARISON
# =========================================================

def compare_text(value_one, value_two):
    """
    Exact normalized comparison.

    Match     = 100
    Mismatch  = 0
    Missing   = 0
    """

    first = normalize_text(value_one)
    second = normalize_text(value_two)

    if not first or not second:
        return 0.0

    return 100.0 if first == second else 0.0

def normalize_address_text(value):
    if value is None:
        return ""

    value = str(value).upper().strip()

    value = re.sub(r"[^A-Z0-9 ]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def compare_address(ocr_address, api_address):
    """
    Compare OCR address string with API structured address dictionary.

    API address can contain fields such as:
    dist, state, po, loc, vtc, subdist, street,
    house, landmark and zip.

    No personal data is hardcoded.
    """

    ocr = normalize_address_text(ocr_address)

    if not ocr or not api_address:
        return 0.0

    # If API address is already a string
    if isinstance(api_address, str):
        api = normalize_address_text(api_address)

        if not api:
            return 0.0

        return 100.0 if api in ocr or ocr in api else 0.0

    # API structured address
    if isinstance(api_address, dict):

        important_fields = [
            "dist",
            "state",
            "po",
            "loc",
            "vtc",
            "subdist",
            "street",
            "house",
            "landmark",
            "zip",
        ]

        values = []

        for field in important_fields:

            value = api_address.get(field)

            if value not in [None, ""]:
                normalized_value = normalize_address_text(value)

                if normalized_value:
                    values.append(normalized_value)

        if not values:
            return 0.0

        matched = 0

        for value in values:

            if value in ocr:
                matched += 1

        if matched == len(values):
            return 100.0

        return round(
            (matched / len(values)) * 100,
            2
        )

    return 0.0
# =========================================================
# DATE NORMALIZATION
# =========================================================

def normalize_date(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    value = str(value).strip()

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


# =========================================================
# EXACT DATE COMPARISON
# =========================================================

def compare_dates(value_one, value_two):
    date_one = normalize_date(value_one)
    date_two = normalize_date(value_two)

    if date_one is None or date_two is None:
        return 0.0

    return 100.0 if date_one == date_two else 0.0

def calculate_name_similarity(value_one, value_two):
    """
    Dynamic OCR name similarity.
    No hardcoded names.
    """

    first = normalize_text(value_one)
    second = normalize_text(value_two)

    if not first or not second:
        return 0.0

    if first == second:
        return 100.0

    # Character-level Levenshtein distance
    previous = list(range(len(second) + 1))

    for i, char_one in enumerate(first, start=1):

        current = [i]

        for j, char_two in enumerate(second, start=1):

            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (
                0 if char_one == char_two else 1
            )

            current.append(
                min(
                    insert_cost,
                    delete_cost,
                    replace_cost
                )
            )

        previous = current

    distance = previous[-1]
    max_length = max(len(first), len(second))

    if max_length == 0:
        return 0.0

    similarity = (
        1 - (distance / max_length)
    ) * 100

    return round(similarity, 2)

# =========================================================
# RECURSIVE API VALUE FINDER
# =========================================================

def find_value(data, possible_keys):

    if isinstance(data, dict):

        for key, value in data.items():

            if str(key).lower() in [
                str(k).lower() for k in possible_keys
            ]:
                if value not in [None, ""]:
                    return value

            result = find_value(value, possible_keys)

            if result not in [None, ""]:
                return result

    elif isinstance(data, list):

        for item in data:

            result = find_value(item, possible_keys)

            if result not in [None, ""]:
                return result

    return None


# =========================================================
# EXTRACT AADHAAR API DATA
# =========================================================

def extract_aadhaar_api_data(response_data):

    if not response_data:
        return {
            "name": None,
            "date_of_birth": None,
            "address": None,
        }

    return {
        "name": find_value(
            response_data,
            [
                "name",
                "full_name",
                "fullname",
                "applicant_name",
            ]
        ),

        "date_of_birth": find_value(
            response_data,
            [
                "dob",
                "date_of_birth",
                "dateOfBirth",
                "birth_date",
            ]
        ),

        "address": find_value(
            response_data,
            [
                "address",
                "full_address",
                "address_line",
            ]
        ),
    }


# =========================================================
# AADHAAR EXACT MATCH SCORE
# =========================================================

def calculate_aadhaar_match_score(
    ocr_name,
    ocr_date_of_birth,
    ocr_address,
    api_name,
    api_date_of_birth,
    api_address,
):
  

    name_score = compare_text(
        ocr_name,
        api_name
    )

    dob_score = compare_dates(
        ocr_date_of_birth,
        api_date_of_birth
    )

    address_score = compare_address(
        ocr_address,
        api_address
    )

    # STRICT EXACT MATCH
    if (
        name_score == 100.0
        and dob_score == 100.0
        and address_score == 100.0
    ):
        return Decimal("100.00")

    return Decimal("0.00")


# =========================================================
# EXTRACT PAN API DATA
# =========================================================
def extract_pan_api_data(response_data):

    if not response_data:
        return {
            "pan_number": None,
            "name": None,
        }

    pan_number = find_value(
        response_data,
        [
            "pan",
            "pan_number",
            "panNumber",
            "pan_no",
            "panNo",
            "pan_card_number",
            "panCardNumber",
        ]
    )

    name = find_value(
        response_data,
        [
            "name",
            "full_name",
            "fullname",
            "applicant_name",
            "applicantName",
            "pan_holder_name",
            "panHolderName",
        ]
    )

    return {
        "pan_number": pan_number,
        "name": name,
    }


def calculate_pan_match_score(
    ocr_pan,
    ocr_name,
    api_response
):
    api_data = extract_pan_api_data(
        api_response
    )

    api_pan = api_data.get("pan_number")
    api_name = api_data.get("name")

    pan_match = compare_text(
        ocr_pan,
        api_pan
    )

    name_similarity = calculate_name_similarity(
        ocr_name,
        api_name
    )

    print("========== PAN MATCH DEBUG ==========")
    print("PAN API DATA FOUND:", bool(api_pan))
    print("PAN API NAME FOUND:", bool(api_name))
    print("PAN NUMBER MATCH:", pan_match)
    print("PAN NAME SIMILARITY:", name_similarity)
    print("=====================================")

    # PAN number must be exact
    if pan_match != 100.0:
        return Decimal("0.00")

    # Exact name
    if normalize_text(ocr_name) == normalize_text(api_name):
        return Decimal("100.00")

    # OCR can contain small recognition errors.
    # API name is used only as verified reference.
    if name_similarity >= 90.0:
        return Decimal("100.00")

    return Decimal("0.00")

def calculate_final_identity_score(identity):

    aadhaar_score = Decimal("0.00")
    pan_score = Decimal("0.00")
    selfie_score = Decimal("0.00")

    if (
        identity.aadhaar_status or ""
    ).upper() == "VERIFIED":

        aadhaar_score = Decimal(
            str(
                identity.aadhaar_match_score or 0
            )
        )

    if (
        identity.pan_status or ""
    ).upper() == "VERIFIED":

        pan_score = Decimal(
            str(
                identity.pan_match_score or 0
            )
        )

    if (
        identity.selfie_status or ""
    ).upper() == "VERIFIED":

        selfie_score = Decimal(
            str(
                identity.selfie_match_score or 0
            )
        )

    final_score = (
        aadhaar_score * Decimal("0.40")
        +
        pan_score * Decimal("0.30")
        +
        selfie_score * Decimal("0.30")
    )

    return final_score.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )