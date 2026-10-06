import requests

from requests.auth import HTTPBasicAuth


# =========================================================
# API CONFIGURATION
# =========================================================

BASE_URL = "https://uat.valentinaheartcare.com"

API_USERNAME = "OtpService"

API_PASSWORD = "YOUR_API_PASSWORD"


AUTH = HTTPBasicAuth(
    API_USERNAME,
    API_PASSWORD
)


TIMEOUT = 30


# =========================================================
# SEND MOBILE OTP
# =========================================================

def send_mobile_otp(mobile, source="web"):

    try:

        url = (
            f"{BASE_URL}"
            f"/api/otp/send"
        )

        payload = {
            "mobile": mobile,
            "source": source
        }

        response = requests.post(
            url,
            json=payload,
            auth=AUTH,
            timeout=TIMEOUT
        )

        try:

            data = response.json()

        except Exception:

            data = {
                "message": response.text
            }

        return {

            "success":
                response.status_code in [200, 201],

            "status_code":
                response.status_code,

            "data":
                data,

            "message":
                data.get(
                    "message",
                    "OTP request completed."
                )
        }

    except requests.RequestException as error:

        return {

            "success": False,

            "status_code": 500,

            "data": {},

            "message": str(error)
        }


# =========================================================
# VERIFY MOBILE OTP
# =========================================================

def verify_mobile_otp(
    mobile,
    otp,
    source="web"
):

    try:

        url = (
            f"{BASE_URL}"
            f"/api/otp/verify"
        )

        payload = {
            "mobile": mobile,
            "otp": otp,
            "source": source
        }

        response = requests.post(
            url,
            json=payload,
            auth=AUTH,
            timeout=TIMEOUT
        )

        try:

            data = response.json()

        except Exception:

            data = {
                "message": response.text
            }

        return {

            "success":
                response.status_code in [200, 201],

            "status_code":
                response.status_code,

            "data":
                data,

            "message":
                data.get(
                    "message",
                    "OTP verification completed."
                )
        }

    except requests.RequestException as error:

        return {

            "success": False,

            "status_code": 500,

            "data": {},

            "message": str(error)
        }


# =========================================================
# GENERATE AADHAAR OTP
# =========================================================

def generate_aadhaar_otp(
    aadhaar_number
):

    try:

        url = (
            f"{BASE_URL}"
            f"/api/kyc/aadhaar/generate-otp"
        )

        payload = {
            "aadhaar_number":
                aadhaar_number
        }

        response = requests.post(
            url,
            json=payload,
            auth=AUTH,
            timeout=TIMEOUT
        )

        try:

            data = response.json()

        except Exception:

            data = {
                "message": response.text
            }

        return {

            "success":
                response.status_code in [200, 201],

            "status_code":
                response.status_code,

            "data":
                data,

            "request_id":
                data.get(
                    "request_id"
                ),

            "message":
                data.get(
                    "message",
                    "Aadhaar OTP request completed."
                )
        }

    except requests.RequestException as error:

        return {

            "success": False,

            "status_code": 500,

            "data": {},

            "request_id": None,

            "message": str(error)
        }


# =========================================================
# VERIFY AADHAAR OTP
# =========================================================
def verify_aadhaar_otp(
    request_id,
    otp
):
    try:

        url = (
            f"{BASE_URL}"
            f"/api/kyc/aadhaar/submit-otp"
        )

        payload = {
            "request_id": request_id,
            "otp": otp
        }

        response = requests.post(
            url,
            json=payload,
            auth=AUTH,
            timeout=TIMEOUT
        )

        try:
            data = response.json()

        except Exception:
            data = {
                "message": response.text
            }

        api_success = (
            data.get("success") is True
        )

        return {
            "success": (
                response.status_code in [200, 201]
                and api_success
            ),

            "status_code":
                response.status_code,

            "data":
                data,

            "message":
                data.get(
                    "message",
                    "Aadhaar verification completed."
                )
        }

    except requests.RequestException as error:

        return {
            "success": False,

            "status_code": 500,

            "data": {},

            "message": str(error)
        }
# =========================================================
# VERIFY PAN
# =========================================================

def verify_pan(
    pan_number
):

    try:

        url = (
            f"{BASE_URL}"
            f"/api/kyc/pan/validate"
        )

        payload = {
            "pan_number":
                pan_number
        }

        response = requests.post(
            url,
            json=payload,
            auth=AUTH,
            timeout=TIMEOUT
        )

        try:

            data = response.json()

        except Exception:

            data = {
                "message": response.text
            }

        return {

            "success":
                response.status_code in [200, 201],

            "status_code":
                response.status_code,

            "data":
                data,

            "message":
                data.get(
                    "message",
                    "PAN verification completed."
                )
        }

    except requests.RequestException as error:

        return {

            "success": False,

            "status_code": 500,

            "data": {},

            "message": str(error)
        }