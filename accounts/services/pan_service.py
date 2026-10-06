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


def verify_pan_number(
    pan_number
):

    url = (
        f"{API_BASE_URL}"
        "/api/kyc/pan/validate"
    )

    payload = {

        "pan_number":
            pan_number

    }

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

        "success":
            response.ok,

        "status_code":
            response.status_code,

        "data":
            data,

    }