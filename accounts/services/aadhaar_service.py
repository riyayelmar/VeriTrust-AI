import os
import requests


API_BASE_URL = (
    "https://uat.valentinaheartcare.com"
)


API_USERNAME = os.getenv(
    "KYC_API_USERNAME",
    "OtpService"
)


API_PASSWORD = os.getenv(
    "KYC_API_PASSWORD",
    ""
)


REQUEST_TIMEOUT = 30


# =====================================================
# COMMON REQUEST
# =====================================================

def make_aadhaar_request(endpoint, payload):

    url = (
        f"{API_BASE_URL}"
        f"{endpoint}"
    )

    try:

        response = requests.post(
            url,
            json=payload,
            auth=(
                API_USERNAME,
                API_PASSWORD
            ),
            timeout=REQUEST_TIMEOUT
        )

        try:
            data = response.json()

        except ValueError:
            data = {
                "message": response.text
            }

        return {
            "success": response.ok,
            "status_code": response.status_code,
            "data": data
        }

    except requests.RequestException as error:

        return {
            "success": False,
            "status_code": 0,
            "data": {
                "message": str(error)
            }
        }

# =====================================================
# GENERATE AADHAAR OTP
# =====================================================

def generate_aadhaar_otp(
    aadhaar_number
):

    payload = {

        "aadhaar_number":
            aadhaar_number

    }

    return make_aadhaar_request(

        "/api/kyc/aadhaar/generate-otp",

        payload
    )


# =====================================================
# SUBMIT AADHAAR OTP
# =====================================================

def submit_aadhaar_otp(request_id, otp):

    payload = {
        "request_id": request_id,
        "otp": otp,
    }

    print("========== AADHAAR OTP SUBMIT ==========")
    print("REQUEST ID PRESENT:", bool(request_id))
    print("OTP PRESENT:", bool(otp))
    print("=========================================")

    return make_aadhaar_request(
        "/api/kyc/aadhaar/submit-otp",
        payload
    )