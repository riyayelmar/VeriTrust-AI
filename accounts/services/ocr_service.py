import re
import numpy as np
from PIL import (
    Image,
    ImageEnhance,
    ImageFilter
)

import pytesseract


# =========================================================
# TESSERACT CONFIGURATION
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# CLEAN OCR TEXT
# =========================================================

def clean_text(text):

    if not text:
        return ""

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"[ \t]+",
            " ",
            line
        )

        line = re.sub(
            r"^[^A-Za-z0-9]+",
            "",
            line
        )

        line = re.sub(
            r"[^A-Za-z0-9]+$",
            "",
            line
        )

        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# =========================================================
# NORMALIZE NAME
# Used only for comparison
# =========================================================

def normalize_name(name):

    if not name:
        return ""

    name = str(name).upper()

    name = re.sub(
        r"[^A-Z ]",
        " ",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip()


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def preprocess_image(image_path):

    image = Image.open(
        image_path
    ).convert("L")

    width, height = image.size

    image = image.resize(
        (
            width * 2,
            height * 2
        ),
        Image.Resampling.LANCZOS
    )

    image = ImageEnhance.Contrast(
        image
    ).enhance(1.8)

    image = image.filter(
        ImageFilter.SHARPEN
    )

    return image


# =========================================================
# AADHAAR NUMBER
# =========================================================

def extract_aadhaar_number(text):

    if not text:
        return None

    print(
        ">>> extract_aadhaar_number() CALLED"
    )

    # -----------------------------------------------------
    # 4-4-4 FORMAT
    # -----------------------------------------------------

    grouped_pattern = (
        r"(?<!\d)"
        r"\d{4}[ \t]+\d{4}[ \t]+\d{4}"
        r"(?!\d)"
    )

    matches = re.findall(
        grouped_pattern,
        text
    )

    print(
        ">>> GROUPED MATCHES:",
        matches
    )

    for match in matches:

        number = re.sub(
            r"\D",
            "",
            match
        )

        if len(number) == 12:

            print(
                ">>> AADHAAR CANDIDATE:",
                number
            )

            return number

    # -----------------------------------------------------
    # CONTINUOUS 12 DIGITS
    # -----------------------------------------------------

    continuous_pattern = (
        r"(?<!\d)"
        r"\d{12}"
        r"(?!\d)"
    )

    matches = re.findall(
        continuous_pattern,
        text
    )

    print(
        ">>> CONTINUOUS MATCHES:",
        matches
    )

    for match in matches:

        if len(match) == 12:
            return match

    return None


# =========================================================
# DATE OF BIRTH
# =========================================================

def extract_date_of_birth(text):

    if not text:
        return None

    # -----------------------------------------------------
    # ONLY DATE AFTER DOB LABEL
    # -----------------------------------------------------

    patterns = [

        (
            r"(?:DOB|D\.O\.B|DATE\s+OF\s+BIRTH)"
            r"\s*[:\-]?\s*"
            r"(\d{2}[/-]\d{2}[/-]\d{4})"
        ),

        (
            r"(?:DOB|D\.O\.B|DATE\s+OF\s+BIRTH)"
            r"\s*[:\-]?\s*"
            r"(\d{2}\.\d{2}\.\d{4})"
        ),

        (
            r"(?:DOB|D\.O\.B|DATE\s+OF\s+BIRTH)"
            r"\s*[:\-]?\s*"
            r"(\d{4}[/-]\d{2}[/-]\d{2})"
        ),

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1)

    # -----------------------------------------------------
    # FALLBACK VALID DATE
    # -----------------------------------------------------

    fallback_patterns = [

        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",

        r"\b\d{2}\.\d{2}\.\d{4}\b",

        r"\b\d{4}[/-]\d{2}[/-]\d{2}\b",

    ]

    for pattern in fallback_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group()

    return None


# =========================================================
# GENDER
# =========================================================

def extract_gender(text):

    if not text:
        return None

    upper_text = text.upper()

    if re.search(
        r"\bFEMALE\b",
        upper_text
    ):
        return "Female"

    if re.search(
        r"\bMALE\b",
        upper_text
    ):
        return "Male"

    return None


# =========================================================
# AADHAAR NAME
#
# Standard Aadhaar:
# Name is normally immediately before DOB.
# =========================================================

def extract_aadhaar_name(text):

    if not text:
        return None

    lines = [
        re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        for line in text.splitlines()

        if line.strip()
    ]

    unwanted = {
        "GOVERNMENT",
        "INDIA",
        "AADHAAR",
        "UNIQUE",
        "IDENTIFICATION",
        "AUTHORITY",
        "DOB",
        "DATE",
        "BIRTH",
        "MALE",
        "FEMALE",
        "YEAR",
        "ADDRESS",
        "VID",
        "HELP",
        "WWW",
        "UIDAI",
        "ENROLMENT",
        "ENROLLMENT",
    }

    # -----------------------------------------------------
    # FIND DOB LINE
    # -----------------------------------------------------

    dob_index = None

    for index, line in enumerate(lines):

        if re.search(
            r"\bDOB\b|D\.O\.B|DATE\s+OF\s+BIRTH",
            line,
            re.IGNORECASE
        ):

            dob_index = index
            break

    # -----------------------------------------------------
    # NAME = LINE IMMEDIATELY BEFORE DOB
    # -----------------------------------------------------

    if dob_index is not None and dob_index > 0:

        candidate = lines[
            dob_index - 1
        ]

        candidate = re.sub(
            r"[^A-Za-z ]",
            " ",
            candidate
        )

        candidate = re.sub(
            r"\s+",
            " ",
            candidate
        ).strip()

        words = candidate.split()

        if (
            2 <= len(words) <= 5
            and all(
                re.fullmatch(
                    r"[A-Za-z]+",
                    word
                )
                for word in words
            )
            and not any(
                word.upper() in unwanted
                for word in words
            )
        ):

            name = " ".join(
                words
            ).title()

            print(
                "EXTRACTED AADHAAR NAME:",
                name
            )

            return name

    return None


# =========================================================
# AADHAAR BACK ADDRESS
#
# IMPORTANT:
# This function receives IMAGE PATH,
# NOT OCR TEXT.
# =========================================================

def extract_aadhaar_address(image_path):

    try:

        image = Image.open(
            image_path
        ).convert("RGB")

        width, height = image.size

        # -------------------------------------------------
        # STANDARD AADHAAR BACK SIDE
        #
        # Left side = Address
        # Right side = QR
        # -------------------------------------------------

        left = int(width * 0.05)
        top = int(height * 0.43)
        right = int(width * 0.65)
        bottom = int(height * 0.78)

        address_crop = image.crop(
            (
                left,
                top,
                right,
                bottom
            )
        )

        # -------------------------------------------------
        # PREPROCESS ADDRESS CROP
        # -------------------------------------------------

        address_crop = address_crop.convert(
            "L"
        )

        address_crop = address_crop.resize(
            (
                address_crop.width * 3,
                address_crop.height * 3
            ),
            Image.Resampling.LANCZOS
        )

        address_crop = ImageEnhance.Contrast(
            address_crop
        ).enhance(2.0)

        address_crop = ImageEnhance.Sharpness(
            address_crop
        ).enhance(2.0)

        # -------------------------------------------------
        # OCR ONLY ADDRESS REGION
        # -------------------------------------------------

        text = pytesseract.image_to_string(
            address_crop,
            lang="eng",
            config="--psm 6"
        )

        print(
            "======================================"
        )

        print(
            "AADHAAR BACK ADDRESS OCR"
        )

        print(
            "======================================"
        )

        print(text)

        lines = [
            re.sub(
                r"\s+",
                " ",
                line
            ).strip()

            for line in text.splitlines()

            if line.strip()
        ]

        if not lines:
            return None

        # -------------------------------------------------
        # FIND ADDRESS LABEL
        # -------------------------------------------------

        address_start = None

        for index, line in enumerate(lines):

            if re.search(
                r"\bADDRESS\b",
                line,
                re.IGNORECASE
            ):

                address_start = index
                break

        if address_start is None:

            print(
                ">>> ADDRESS LABEL NOT FOUND"
            )

            return None

        # -------------------------------------------------
        # ADDRESS FIRST LINE
        # -------------------------------------------------

        first_line = re.sub(
            r"^.*?\bADDRESS\b\s*[:\-]?\s*",
            "",
            lines[address_start],
            flags=re.IGNORECASE
        ).strip()

        address_lines = []

        if first_line:
            address_lines.append(
                first_line
            )

        # -------------------------------------------------
        # NEXT ADDRESS LINES
        # -------------------------------------------------

        for line in lines[
            address_start + 1:
            address_start + 6
        ]:

            line = line.strip()

            if not line:
                continue

            # Stop at unrelated Aadhaar content
            if re.search(
                r"UNIQUE\s+IDENTIFICATION",
                line,
                re.IGNORECASE
            ):
                break

            if re.search(
                r"GOVERNMENT|INDIA|UIDAI|"
                r"WWW\.|HELP@|1947",
                line,
                re.IGNORECASE
            ):
                break

            address_lines.append(
                line
            )

        if not address_lines:
            return None

        # -------------------------------------------------
        # FINAL ADDRESS
        # -------------------------------------------------

        address = " ".join(
            address_lines
        )

        address = re.sub(
            r"\s+",
            " ",
            address
        ).strip()

        address = address.strip(
            " ,.-"
        )

        if len(address) < 10:
            return None

        print(
            "EXTRACTED AADHAAR ADDRESS:",
            address
        )

        return address

    except Exception as e:

        print(
            "AADHAAR ADDRESS ERROR:",
            str(e)
        )

        return None


# =========================================================
# PAN NUMBER
# =========================================================

def extract_pan_number(text):

    if not text:
        return None

    upper_text = text.upper()

    # -----------------------------------------------------
    # STANDARD PAN
    # ABCDE1234F
    # -----------------------------------------------------

    pattern = (
        r"(?<![A-Z0-9])"
        r"[A-Z]{5}[0-9]{4}[A-Z]"
        r"(?![A-Z0-9])"
    )

    match = re.search(
        pattern,
        upper_text
    )

    if match:
        return match.group()

    # -----------------------------------------------------
    # SPACED PAN
    # -----------------------------------------------------

    spaced_pattern = (
        r"([A-Z]{5})\s*"
        r"([0-9]{4})\s*"
        r"([A-Z])"
    )

    match = re.search(
        spaced_pattern,
        upper_text
    )

    if match:

        return (
            match.group(1)
            + match.group(2)
            + match.group(3)
        )

    return None


# =========================================================
# PAN NAME
#
# ONLY APPLICANT NAME
# Father's Name is NEVER returned.
# =========================================================
def extract_pan_name(text):

    if not text:
        return None

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # -------------------------------------------------
    # NORMALIZE OCR TEXT
    # -------------------------------------------------

    cleaned_lines = []

    for line in lines:

        line = re.sub(
            r"[^A-Za-z0-9:/\- ]",
            " ",
            line
        )

        line = re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        if line:
            cleaned_lines.append(line)

    lines = cleaned_lines

    # -------------------------------------------------
    # FIND FATHER'S NAME SECTION
    # -------------------------------------------------

    father_index = None

    for index, line in enumerate(lines):

        if re.search(
            r"FATHER'?S?\s*NAME|FATHER",
            line,
            re.IGNORECASE
        ):
            father_index = index
            break

    # -------------------------------------------------
    # FIND PAN NUMBER LINE
    # -------------------------------------------------

    pan_index = None

    for index, line in enumerate(lines):

        if re.search(
            r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
            line.upper()
        ):
            pan_index = index
            break

    # -------------------------------------------------
    # EXPLICIT NAME LABEL
    # Example:
    # Name: RIYA SANJAY YELMAR
    # -------------------------------------------------

    for index, line in enumerate(lines):

        match = re.search(
            r"\bNAME\s*[:\-]\s*(.+)$",
            line,
            re.IGNORECASE
        )

        if match:

            candidate = match.group(1)

            # Never accept Father's Name
            if re.search(
                r"FATHER",
                candidate,
                re.IGNORECASE
            ):
                continue

            candidate = re.sub(
                r"[^A-Za-z ]",
                " ",
                candidate
            )

            candidate = re.sub(
                r"\s+",
                " ",
                candidate
            ).strip()

            words = candidate.split()

            if (
                2 <= len(words) <= 5
                and all(
                    re.fullmatch(
                        r"[A-Za-z]+",
                        word
                    )
                    for word in words
                )
            ):
                return " ".join(words).title()

    # -------------------------------------------------
    # NAME LABEL ON ONE LINE
    # -------------------------------------------------

    for index, line in enumerate(lines):

        if re.fullmatch(
            r"NAME\s*:?",
            line,
            re.IGNORECASE
        ):

            if index + 1 >= len(lines):
                continue

            candidate = lines[index + 1]

            # Do not cross Father's Name section
            if re.search(
                r"FATHER",
                candidate,
                re.IGNORECASE
            ):
                continue

            candidate = re.sub(
                r"[^A-Za-z ]",
                " ",
                candidate
            )

            candidate = re.sub(
                r"\s+",
                " ",
                candidate
            ).strip()

            words = candidate.split()

            if (
                2 <= len(words) <= 5
                and all(
                    re.fullmatch(
                        r"[A-Za-z]+",
                        word
                    )
                    for word in words
                )
            ):
                return " ".join(words).title()

    # -------------------------------------------------
    # FALLBACK
    #
    # Search ONLY in the area before Father's Name.
    # Never use Father's Name itself.
    # -------------------------------------------------

    if father_index is not None:
        search_lines = lines[:father_index]
    else:
        search_lines = lines

    candidates = []

    for line in search_lines:

        if not line:
            continue

        # Numbers are not part of applicant name
        if re.search(r"\d", line):
            continue

        # Ignore PAN/header/card text
        if re.search(
            r"INCOME|TAX|DEPARTMENT|GOVT|"
            r"GOVERNMENT|INDIA|PERMANENT|"
            r"ACCOUNT|NUMBER|CARD|PAN|"
            r"DATE|DOB|FATHER|NAME",
            line,
            re.IGNORECASE
        ):
            continue

        candidate = re.sub(
            r"[^A-Za-z ]",
            " ",
            line
        )

        candidate = re.sub(
            r"\s+",
            " ",
            candidate
        ).strip()

        words = candidate.split()

        if not (
            2 <= len(words) <= 5
        ):
            continue

        if not all(
            re.fullmatch(
                r"[A-Za-z]+",
                word
            )
            for word in words
        ):
            continue

        candidates.append(candidate)

    print(
        "PAN NAME CANDIDATES:",
        candidates
    )

    if candidates:
        return candidates[-1].title()

    return None

# =========================================================
# AADHAAR FRONT OCR
#
# ONLY:
# Number
# Name
# DOB
# Gender
# =========================================================

def process_aadhaar_front(front_image_path):

    try:

        image = preprocess_image(
            front_image_path
        )

        text = pytesseract.image_to_string(
            image,
            lang="eng",
            config="--psm 6"
        )

        print(
            "======================================"
        )

        print(
            "AADHAAR FRONT OCR RAW TEXT"
        )

        print(
            "======================================"
        )

        print(text)

        aadhaar_number = (
            extract_aadhaar_number(
                text
            )
        )

        name = (
            extract_aadhaar_name(
                text
            )
        )

        date_of_birth = (
            extract_date_of_birth(
                text
            )
        )

        gender = (
            extract_gender(
                text
            )
        )

        print(
            "EXTRACTED AADHAAR:",
            aadhaar_number
        )

        print(
            "EXTRACTED NAME:",
            name
        )

        print(
            "EXTRACTED DOB:",
            date_of_birth
        )

        print(
            "EXTRACTED GENDER:",
            gender
        )

        return {

            "success":
                bool(aadhaar_number),

            "aadhaar_number":
                aadhaar_number,

            "name":
                name,

            "date_of_birth":
                date_of_birth,

            "gender":
                gender,

            "raw_text":
                text,
        }

    except Exception as e:

        print(
            "AADHAAR FRONT OCR ERROR:",
            str(e)
        )

        return {

            "success": False,

            "aadhaar_number": None,

            "name": None,

            "date_of_birth": None,

            "gender": None,

            "raw_text": "",
        }


# =========================================================
# AADHAAR COMPLETE
#
# FRONT + BACK
# =========================================================

def process_aadhaar_ocr(
    front_image_path,
    back_image_path=None
):

    try:

        # -------------------------------------------------
        # FRONT
        # -------------------------------------------------

        front_result = (
            process_aadhaar_front(
                front_image_path
            )
        )

        # -------------------------------------------------
        # BACK ADDRESS
        # -------------------------------------------------

        address = None

        if back_image_path:

            address = (
                extract_aadhaar_address(
                    back_image_path
                )
            )

        # -------------------------------------------------
        # FINAL RESULT
        # ONLY REQUIRED FIELDS
        # -------------------------------------------------

        result = {

            "success":
                front_result.get(
                    "success",
                    False
                ),

            "aadhaar_number":
                front_result.get(
                    "aadhaar_number"
                ),

            "name":
                front_result.get(
                    "name"
                ),

            "date_of_birth":
                front_result.get(
                    "date_of_birth"
                ),

            "gender":
                front_result.get(
                    "gender"
                ),

            "address":
                address,

            "raw_text":
                front_result.get(
                    "raw_text",
                    ""
                ),
        }

        print(
            "======================================"
        )

        print(
            "AADHAAR FINAL OCR RESULT"
        )

        print(
            "======================================"
        )

        print(
            "AADHAAR:",
            result["aadhaar_number"]
        )

        print(
            "NAME:",
            result["name"]
        )

        print(
            "DOB:",
            result["date_of_birth"]
        )

        print(
            "GENDER:",
            result["gender"]
        )

        print(
            "ADDRESS:",
            result["address"]
        )

        return result

    except Exception as e:

        print(
            "AADHAAR OCR ERROR:",
            str(e)
        )

        return {

            "success": False,

            "aadhaar_number": None,

            "name": None,

            "date_of_birth": None,

            "gender": None,

            "address": None,

            "raw_text": "",
        }


# =========================================================
# AADHAAR FRONT + BACK
#
# Keep this as alias for existing code
# =========================================================

def process_aadhaar_images(
    front_image_path,
    back_image_path=None
):

    return process_aadhaar_ocr(
        front_image_path,
        back_image_path
    )


# =========================================================
# PAN OCR
#
# ONLY:
# PAN Number
# Applicant Name
# =========================================================
def process_pan_ocr(image_path):
    try:

        image = Image.open(image_path).convert("RGB")

        width, height = image.size

        # =================================================
        # 1. FULL IMAGE OCR - PAN NUMBER
        # =================================================

        full_gray = image.convert("L")

        full_gray = full_gray.resize(
            (
                width * 2,
                height * 2
            ),
            Image.Resampling.LANCZOS
        )

        full_gray = ImageEnhance.Contrast(
            full_gray
        ).enhance(1.8)

        full_gray = full_gray.filter(
            ImageFilter.SHARPEN
        )

        full_text = pytesseract.image_to_string(
            full_gray,
            lang="eng",
            config="--psm 6"
        )

        full_text = clean_text(
            full_text
        )

        # =================================================
        # 2. EXACT APPLICANT NAME CROP
        # =================================================
        #
        # PAN card:
        # Name label is around y = 520
        # Applicant name is around y = 575-635
        #
        # We take ONLY applicant-name area.
        # Father's name is below this area.
        # =================================================

        name_crop = image.crop(
            (
                int(width * 0.04),
                int(height * 0.545),
                int(width * 0.45),
                int(height * 0.635)
            )
        )

        # =================================================
        # 3. GREEN CHANNEL
        # =================================================

        name_array = np.array(
            name_crop
        )

        green_channel = Image.fromarray(
            name_array[:, :, 1]
        )

        green_channel = green_channel.resize(
            (
                green_channel.width * 4,
                green_channel.height * 4
            ),
            Image.Resampling.LANCZOS
        )

        green_channel = ImageEnhance.Contrast(
            green_channel
        ).enhance(1.8)

        green_channel = green_channel.filter(
            ImageFilter.SHARPEN
        )

        # =================================================
        # 4. OCR NAME
        # =================================================

        name_text = pytesseract.image_to_string(
            green_channel,
            lang="eng",
            config="--psm 7"
        )

        name_text = clean_text(
            name_text
        )

        # =================================================
        # 5. EXTRACT PAN NUMBER
        # =================================================

        pan_number = extract_pan_number(
            full_text
        )

        # =================================================
        # 6. EXTRACT APPLICANT NAME
        # =================================================

        name = None

        if name_text:

            # Remove unwanted OCR characters
            candidate = re.sub(
                r"[^A-Za-z ]",
                " ",
                name_text
            )

            candidate = re.sub(
                r"\s+",
                " ",
                candidate
            ).strip()

            words = candidate.split()

            if (
                2 <= len(words) <= 5
                and all(
                    re.fullmatch(
                        r"[A-Za-z]+",
                        word
                    )
                    for word in words
                )
            ):
                name = " ".join(
                    words
                ).title()

        # =================================================
        # 7. CLEAN FINAL OCR OUTPUT
        # =================================================

        print()
        print("=" * 60)
        print("                 PAN OCR DATA")
        print("=" * 60)

        print(
            "PAN Number :",
            pan_number
        )

        print(
            "Name       :",
            name
        )

        print("=" * 60)
        print()

        # =================================================
        # 8. RETURN OCR RESULT
        # =================================================

        return {

            "success": True,

            "pan_number":
                pan_number,

            "name":
                name,

            "raw_text":
                full_text,

        }

    except Exception as error:

        print()
        print("=" * 60)
        print("                 PAN OCR ERROR")
        print("=" * 60)

        print(
            "Error:",
            str(error)
        )

        print("=" * 60)
        print()

        return {

            "success": False,

            "pan_number": None,

            "name": None,

            "raw_text": "",

            "error":
                str(error),

        }