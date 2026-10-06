import json
import re
import hashlib
from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.conf import settings
from django.utils import timezone
from .models import IdentityVerification
from .models import User, VerificationProfile
from django.db.models import Count
from django.db import transaction
from datetime import timedelta
import base64
import uuid
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from .ai.face_verification import compare_faces
from .models import EmployeeProfile
import requests
import random
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import EmailVerification
from django.http import JsonResponse
from datetime import datetime,date

from .models import (
    EmployeeProfile,
    EducationVerification,
    EmployeeEmployment,
    EmploymentDocument,
    IdentityVerification,
    VerificationRequest,
    VerificationResult,
    ActivityLog,
)

from .forms import EducationVerificationForm


from .models import (
    AddressVerification,
    AddressEvidence,
)


from .services.ocr_service import (
    process_aadhaar_ocr,
    process_pan_ocr,
    process_aadhaar_images

)

from .services.aadhaar_service import (
    generate_aadhaar_otp,
    submit_aadhaar_otp,
)

from .services.pan_service import (
    verify_pan_number,
)

from .services.comparison_service import (
    extract_aadhaar_api_data,
    calculate_aadhaar_match_score,
    calculate_pan_match_score,
)

from .services.identity_score_service import (
    update_final_identity_status,
)


from .services.kyc_service import (
    send_mobile_otp,
    verify_mobile_otp,
    generate_aadhaar_otp,
    verify_aadhaar_otp,
    verify_pan
)

from accounts.services.face_verification import verify_face



# =========================
# Home
# =========================

def home(request):

    return render(
        request,
        'home.html'
    )

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")


        print("USERNAME:", username)
        print("EMAIL:", email)
        print("MOBILE:", mobile)
        print("ROLE:", role)


        # =====================================================
        # PASSWORD CHECK
        # =====================================================

        if password != confirm_password:

            print("ERROR: PASSWORD NOT MATCH")

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")


        # =====================================================
        # EMAIL CHECK
        # =====================================================

        if User.objects.filter(email=email).exists():

            print("ERROR: EMAIL ALREADY EXISTS")

            messages.error(
                request,
                "Email already registered."
            )

            return redirect("register")


        # =====================================================
        # USERNAME CHECK
        # =====================================================

        if User.objects.filter(username=username).exists():

            print("ERROR: USERNAME ALREADY EXISTS")

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")


        # =====================================================
        # CREATE USER
        # =====================================================

        print("CREATING USER...")


        user = User.objects.create_user(

            username=username,

            email=email,

            password=password

        )


        user.mobile = mobile

        user.role = role

        user.save()


        print("USER CREATED:", user.id)


        # =====================================================
        # SAVE REGISTRATION DETAILS IN SESSION
        # =====================================================

        request.session["registration_email"] = email

        request.session["registration_mobile"] = mobile

        request.session["mobile_verified"] = False

        request.session["email_verified"] = False

        request.session["otp_sent"] = False

        request.session.modified = True


        print("REGISTRATION EMAIL:", email)

        print("REGISTRATION MOBILE:", mobile)

        print("REDIRECTING TO VERIFY MOBILE")


        return redirect("verify_mobile")


    return render(
        request,
        "register.html"
    )

# =========================
# Login
# =========================

def login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")


        # Check Email Exists

        if not User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email is not registered."
            )

            return redirect("login")



        user = authenticate(
            request,
            email=email,
            password=password
        )



        if user is not None:


            auth_login(
                request,
                user
            )


            messages.success(
                request,
                "Login Successfully"
            )


            return redirect(
                "dashboard"
            )


        else:


            messages.error(
                request,
                "Incorrect password. Please try again."
            )



    return render(
        request,
        "login.html"
    )

@login_required
def dashboard(request):

    user = request.user

    # ==========================
    # Employee Profile
    # ==========================

    profile = EmployeeProfile.objects.filter(
        user=user
    ).first()


    # ==========================
    # Address Verification
    # ==========================

    address = AddressVerification.objects.filter(
        user=user
    ).first()


    # ==========================
    # Identity Verification
    # ==========================

    identity = IdentityVerification.objects.filter(
        user=user
    ).first()


    # ==========================
    # Verification Request
    # ==========================

    verification = VerificationRequest.objects.filter(
        user=user
    ).first()


    result = None

    if verification:

        result = VerificationResult.objects.filter(
            verification_request=verification
        ).first()


    # ==========================
    # Education
    # ==========================

    education_records = EducationVerification.objects.filter(
        user=user
    )

    education_count = education_records.count()


    # ==========================
    # Education Documents
    # ==========================

    total_documents = education_records.exclude(
        education_proof=""
    ).count()


    verified_documents = education_records.filter(
        status="VERIFIED"
    ).count()


    pending_documents = education_records.filter(
        status__in=[
            "PENDING",
            "UPLOADED",
            "UNDER_REVIEW",
        ]
    ).count()


    rejected_documents = education_records.filter(
        status="REJECTED"
    ).count()


    # ==========================
    # Employment
    # ==========================

    employment_count = EmployeeEmployment.objects.filter(
        user=user
    ).count()


    # ==========================
    # Recent Activities
    # ==========================

    activities = ActivityLog.objects.filter(
        user=user
    ).order_by(
        "-created_at"
    )[:5]


    # ==========================
    # Profile Completion
    # ==========================

    completed = 0


    if profile:
        completed += 1


    if address:
        completed += 1


    if education_count > 0:
        completed += 1


    if employment_count > 0:
        completed += 1


    if total_documents > 0:
        completed += 1


    # Identity verification
    if identity and identity.verification_status == "VERIFIED":
        completed += 1


    profile_completion = int(
        (completed / 6) * 100
    )


    # ==========================
    # AI Trust Score
    # ==========================

    ai_trust_score = 0

    if result:
        ai_trust_score = result.ai_trust_score


    # ==========================
    # Verification Status
    # ==========================

    verification_status = "Not Started"

    if verification:
        verification_status = verification.status


    # ==========================
    # Risk Level
    # ==========================

    risk_level = "-"

    if result:
        risk_level = result.risk_level


    # ==========================
    # Context
    # ==========================

    context = {

        "profile": profile,

        "address": address,

        "identity": identity,

        "verification": verification,

        "result": result,

        "profile_completion": profile_completion,

        "ai_trust_score": ai_trust_score,

        "verification_status": verification_status,

        "risk_level": risk_level,

        "total_documents": total_documents,

        "verified_documents": verified_documents,

        "pending_documents": pending_documents,

        "rejected_documents": rejected_documents,

        "education_count": education_count,

        "employment_count": employment_count,

        "activities": activities,

    }


    return render(
        request,
        "dashboard.html",
        context
    )



# =========================
# Features
# =========================

def features(request):

    return render(
        request,
        "features.html"
    )





# =========================
# Solutions
# =========================

def solutions(request):

    return render(
        request,
        "solutions.html"
    )



# =========================
# About
# =========================

def about(request):

    return render(
        request,
        "about.html"
    )





# =========================
# Contact
# =========================

def contact(request):

    return render(
        request,
        "contact.html"
    )

# =========================================================
# FORGOT PASSWORD
# =========================================================

# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password(request):

    if request.method == "POST":

        # =====================================================
        # GET RECOVERY METHOD
        # =====================================================

        method = request.POST.get(
            "method",
            ""
        ).strip()


        # =====================================================
        # GET EMAIL OR MOBILE VALUE
        # =====================================================

        if method == "email":

            value = request.POST.get(
                "email",
                ""
            ).strip()


        elif method == "mobile":

            value = request.POST.get(
                "mobile",
                ""
            ).strip()


        else:

            value = ""


        # =====================================================
        # EMPTY VALUE CHECK
        # =====================================================

        if not value:

            messages.error(
                request,
                "Please enter your email or mobile number."
            )

            return redirect(
                "forgot_password"
            )


        # =====================================================
        # EMAIL
        # =====================================================

        if method == "email":

            users = User.objects.filter(
                email__iexact=value
            )


            # EMAIL NOT FOUND

            if not users.exists():

                messages.error(
                    request,
                    "No account found with this email address."
                )

                return redirect(
                    "forgot_password"
                )


            # MULTIPLE ACCOUNTS

            if users.count() > 1:

                messages.error(
                    request,
                    "Multiple accounts are associated with this email. Please contact support."
                )

                return redirect(
                    "forgot_password"
                )


            user = users.first()


        # =====================================================
        # MOBILE
        # =====================================================

        elif method == "mobile":

            mobile = (
                value
                .replace(" ", "")
                .replace("-", "")
            )


            # REMOVE +91

            if mobile.startswith("+91"):

                mobile = mobile[3:]


            # REMOVE 91

            if (
                mobile.startswith("91")
                and len(mobile) == 12
            ):

                mobile = mobile[2:]


            users = User.objects.filter(
                mobile=mobile
            )


            # MOBILE NOT FOUND

            if not users.exists():

                messages.error(
                    request,
                    "No account found with this mobile number."
                )

                return redirect(
                    "forgot_password"
                )


            # MULTIPLE ACCOUNTS

            if users.count() > 1:

                messages.error(
                    request,
                    "Multiple accounts are associated with this mobile number. Please contact support."
                )

                return redirect(
                    "forgot_password"
                )


            user = users.first()


        # =====================================================
        # INVALID METHOD
        # =====================================================

        else:

            messages.error(
                request,
                "Please select a recovery method."
            )

            return redirect(
                "forgot_password"
            )


        # =====================================================
        # CLEAR OLD RESET SESSION
        # =====================================================

        request.session.pop(
            "reset_user_id",
            None
        )

        request.session.pop(
            "reset_method",
            None
        )

        request.session.pop(
            "reset_otp",
            None
        )

        request.session.pop(
            "reset_otp_created",
            None
        )

        request.session.pop(
            "reset_verified",
            None
        )


        # =====================================================
        # SAVE USER + METHOD
        # =====================================================

        request.session[
            "reset_user_id"
        ] = user.id


        request.session[
            "reset_method"
        ] = method


        # =====================================================
        # EMAIL OTP
        # =====================================================

        if method == "email":

            otp = str(
                random.randint(
                    100000,
                    999999
                )
            )


            request.session[
                "reset_otp"
            ] = otp


            request.session[
                "reset_otp_created"
            ] = timezone.now().isoformat()


            request.session.modified = True


            try:

                send_mail(

                    subject=(
                        "VeriTrust AI - Password Reset OTP"
                    ),

                    message=(

                        f"Hello,\n\n"

                        f"Your password reset verification code is: {otp}\n\n"

                        "This code is valid for 10 minutes.\n"

                        "Do not share this code with anyone.\n\n"

                        "Regards,\n"

                        "VeriTrust AI Security Team"
                    ),

                    from_email=(
                        settings.DEFAULT_FROM_EMAIL
                    ),

                    recipient_list=[
                        user.email
                    ],

                    fail_silently=False,
                )


            except Exception as e:

                print(
                    "EMAIL RESET OTP ERROR:",
                    e
                )


                messages.error(
                    request,
                    "Unable to send verification code. Please try again."
                )


                return redirect(
                    "forgot_password"
                )


        # =====================================================
        # MOBILE OTP
        # =====================================================

        elif method == "mobile":

            try:

                mobile_number = str(
                    user.mobile
                )


                response = requests.post(

                    "https://bargiee.microdynamicsoftware.uk/api/otp/send",

                    json={

                        "mobile":
                            mobile_number,

                        "source":
                            "web"
                    },

                    timeout=15
                )


                print(
                    "OTP SEND STATUS:",
                    response.status_code
                )


                print(
                    "OTP SEND RESPONSE:",
                    response.text
                )


                if response.status_code >= 400:

                    messages.error(
                        request,
                        "Unable to send OTP to your mobile number."
                    )


                    return redirect(
                        "forgot_password"
                    )


            except Exception as e:

                print(
                    "MOBILE OTP SEND ERROR:",
                    e
                )


                messages.error(
                    request,
                    "Unable to send verification code. Please try again."
                )


                return redirect(
                    "forgot_password"
                )


        # =====================================================
        # GO TO OTP PAGE
        # =====================================================

        return redirect(
            "verify_reset_otp"
        )


    # =====================================================
    # GET REQUEST
    # =====================================================

    return render(
        request,
        "forgot_password.html"
    )
# =========================================================
# VERIFY RESET OTP
# =========================================================

def verify_reset_otp(request):

    # =====================================================
    # GET RECOVERY SESSION
    # =====================================================

    user_id = request.session.get(
        "reset_user_id"
    )

    method = request.session.get(
        "reset_method"
    )

    if not user_id or not method:

        messages.error(
            request,
            "Your password recovery session has expired."
        )

        return redirect(
            "forgot_password"
        )


    # =====================================================
    # GET USER
    # =====================================================

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        request.session.flush()

        messages.error(
            request,
            "Account not found."
        )

        return redirect(
            "forgot_password"
        )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get(
            "action",
            "verify"
        )


        # =================================================
        # RESEND OTP
        # =================================================

        if action == "resend":


            # =============================================
            # EMAIL RESEND OTP
            # =============================================-

            if method == "email":

                new_otp = str(
                    random.randint(
                        100000,
                        999999
                    )
                )

                request.session["reset_otp"] = (
                    new_otp
                )

                request.session[
                    "reset_otp_created"
                ] = (
                    timezone.now().isoformat()
                )

                request.session.modified = True


                try:

                    send_mail(

                        subject=(
                            "VeriTrust AI - New Password Reset Code"
                        ),

                        message=(
                            f"Hello,\n\n"
                            f"Your password reset verification "
                            f"code is:\n\n"
                            f"{new_otp}\n\n"
                            "This code is valid for 10 minutes.\n\n"
                            "Do not share this code with anyone.\n\n"
                            "Regards,\n"
                            "VeriTrust AI Security Team"
                        ),

                        from_email=(
                            settings.DEFAULT_FROM_EMAIL
                        ),

                        recipient_list=[
                            user.email
                        ],

                        fail_silently=False,
                    )


                except Exception as error:

                    print(
                        "EMAIL RESEND ERROR:",
                        error
                    )

                    messages.error(
                        request,
                        "Unable to resend verification code. "
                        "Please try again."
                    )

                    return redirect(
                        "verify_reset_otp"
                    )


            # =============================================
            # MOBILE RESEND OTP
            # =============================================

            elif method == "mobile":

                try:

                    response = requests.post(
                        "https://bargiee.microdynamicsoftware.uk/api/otp/send",

                        json={
                            "mobile": str(
                                user.mobile
                            ),

                            "source": "web"
                        },

                        timeout=15
                    )


                    print(
                        "MOBILE RESEND STATUS:",
                        response.status_code
                    )

                    print(
                        "MOBILE RESEND RESPONSE:",
                        response.text
                    )


                    # API RESPONSE
                    try:

                        api_data = response.json()

                    except ValueError:

                        api_data = {}


                    # CHECK SUCCESS
                    if (
                        response.status_code != 200
                        or
                        api_data.get("success") is not True
                    ):

                        messages.error(
                            request,
                            api_data.get(
                                "message",
                                "Unable to resend OTP. "
                                "Please try again."
                            )
                        )

                        return redirect(
                            "verify_reset_otp"
                        )


                except requests.RequestException as error:

                    print(
                        "MOBILE RESEND ERROR:",
                        error
                    )

                    messages.error(
                        request,
                        "OTP service is temporarily unavailable."
                    )

                    return redirect(
                        "verify_reset_otp"
                    )


            # =============================================
            # INVALID METHOD
            # =============================================

            else:

                messages.error(
                    request,
                    "Invalid recovery method."
                )

                return redirect(
                    "forgot_password"
                )


            messages.success(
                request,
                "A new verification code has been sent."
            )

            return redirect(
                "verify_reset_otp"
            )


        # =================================================
        # VERIFY OTP
        # =================================================

        otp = request.POST.get(
            "otp",
            ""
        ).strip()


        # -------------------------------------------------
        # EMPTY OTP
        # -------------------------------------------------

        if not otp:

            messages.error(
                request,
                "Please enter the verification code."
            )

            return redirect(
                "verify_reset_otp"
            )


        # -------------------------------------------------
        # VALIDATE 6 DIGITS
        # -------------------------------------------------

        if (
            not otp.isdigit()
            or
            len(otp) != 6
        ):

            messages.error(
                request,
                "Please enter a valid 6-digit verification code."
            )

            return redirect(
                "verify_reset_otp"
            )


        # =================================================
        # MOBILE OTP VERIFY
        # =================================================

        if method == "mobile":

            try:

                response = requests.post(
                    "https://bargiee.microdynamicsoftware.uk/api/otp/verify",

                    json={
                        "mobile": str(
                            user.mobile
                        ),

                        "otp": otp,

                        "source": "web"
                    },

                    timeout=15
                )


                print(
                    "MOBILE OTP VERIFY STATUS:",
                    response.status_code
                )

                print(
                    "MOBILE OTP VERIFY RESPONSE:",
                    response.text
                )


                try:

                    api_data = response.json()

                except ValueError:

                    api_data = {}


                # =========================================
                # VERIFY API RESPONSE
                # =========================================

                if (
                    response.status_code != 200
                    or
                    api_data.get("success") is not True
                ):

                    messages.error(
                        request,
                        api_data.get(
                            "message",
                            "Invalid or expired verification code."
                        )
                    )

                    return redirect(
                        "verify_reset_otp"
                    )


            except requests.RequestException as error:

                print(
                    "MOBILE OTP VERIFY ERROR:",
                    error
                )

                messages.error(
                    request,
                    "OTP verification service is temporarily unavailable."
                )

                return redirect(
                    "verify_reset_otp"
                )


        # =================================================
        # EMAIL OTP VERIFY
        # =================================================

        elif method == "email":

            saved_otp = request.session.get(
                "reset_otp"
            )

            created_at = request.session.get(
                "reset_otp_created"
            )


            # -------------------------------------------------
            # CHECK SESSION OTP
            # -------------------------------------------------

            if not saved_otp or not created_at:

                messages.error(
                    request,
                    "Your verification code has expired. "
                    "Please request a new one."
                )

                return redirect(
                    "forgot_password"
                )


            # -------------------------------------------------
            # CONVERT OTP CREATED TIME
            # -------------------------------------------------

            try:

                otp_created_time = (
                    timezone.datetime.fromisoformat(
                        created_at
                    )
                )


                if timezone.is_naive(
                    otp_created_time
                ):

                    otp_created_time = (
                        timezone.make_aware(
                            otp_created_time
                        )
                    )


            except Exception:

                messages.error(
                    request,
                    "Invalid password recovery session."
                )

                return redirect(
                    "forgot_password"
                )


            # -------------------------------------------------
            # OTP EXPIRY - 10 MINUTES
            # -------------------------------------------------

            expiry_time = (
                otp_created_time
                +
                timedelta(minutes=10)
            )


            if timezone.now() > expiry_time:

                request.session.pop(
                    "reset_otp",
                    None
                )

                request.session.pop(
                    "reset_otp_created",
                    None
                )

                request.session.modified = True


                messages.error(
                    request,
                    "Your verification code has expired. "
                    "Please start again."
                )

                return redirect(
                    "forgot_password"
                )


            # -------------------------------------------------
            # OTP MATCH
            # -------------------------------------------------

            if otp != saved_otp:

                messages.error(
                    request,
                    "Invalid verification code."
                )

                return redirect(
                    "verify_reset_otp"
                )


        # =================================================
        # INVALID METHOD
        # =================================================

        else:

            messages.error(
                request,
                "Invalid recovery method."
            )

            return redirect(
                "forgot_password"
            )


        # =================================================
        # OTP VERIFIED SUCCESSFULLY
        # =================================================

        request.session["reset_verified"] = True


        # Remove email OTP after verification
        request.session.pop(
            "reset_otp",
            None
        )

        request.session.pop(
            "reset_otp_created",
            None
        )

        request.session.modified = True


        messages.success(
            request,
            "Identity verified successfully. "
            "You can now create a new password."
        )


        return redirect(
            "reset_password"
        )


    # =====================================================
    # PAGE LOAD
    # =====================================================

    return render(
        request,
        "verify_reset_otp.html",
        {
            "method": method,
            "email": user.email,
            "mobile": user.mobile,
        }
    )

# =========================================================
# RESET PASSWORD
# =========================================================

def reset_password(request):

    # =====================================================
    # CHECK OTP VERIFIED
    # =====================================================

    if not request.session.get(
        "reset_verified"
    ):

        messages.error(
            request,
            "Please verify your identity first."
        )

        return redirect(
            "forgot_password"
        )


    # =====================================================
    # GET USER ID
    # =====================================================

    user_id = request.session.get(
        "reset_user_id"
    )


    if not user_id:

        messages.error(
            request,
            "Password recovery session has expired. "
            "Please try again."
        )

        return redirect(
            "forgot_password"
        )


    # =====================================================
    # GET USER
    # =====================================================

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        # Clear recovery session
        request.session.pop(
            "reset_user_id",
            None
        )

        request.session.pop(
            "reset_method",
            None
        )

        request.session.pop(
            "reset_otp",
            None
        )

        request.session.pop(
            "reset_otp_created",
            None
        )

        request.session.pop(
            "reset_verified",
            None
        )

        request.session.modified = True


        messages.error(
            request,
            "Account not found. "
            "Please start password recovery again."
        )

        return redirect(
            "forgot_password"
        )


    # =====================================================
    # POST - CHANGE PASSWORD
    # =====================================================

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        ).strip()


        confirm_password = request.POST.get(
            "confirm_password",
            ""
        ).strip()


        # -------------------------------------------------
        # EMPTY FIELDS
        # -------------------------------------------------

        if not password or not confirm_password:

            messages.error(
                request,
                "Please fill in both password fields."
            )

            return redirect(
                "reset_password"
            )


        # -------------------------------------------------
        # PASSWORD MATCH
        # -------------------------------------------------

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "reset_password"
            )


        # -------------------------------------------------
        # PASSWORD VALIDATION
        # -------------------------------------------------

        try:

            validate_password(
                password,
                user=user
            )


        except ValidationError as error:

            for message in error.messages:

                messages.error(
                    request,
                    message
                )

            return redirect(
                "reset_password"
            )


        # -------------------------------------------------
        # SAVE NEW PASSWORD
        # -------------------------------------------------

        user.set_password(
            password
        )

        user.save(
            update_fields=[
                "password"
            ]
        )


        # =================================================
        # CLEAR COMPLETE RECOVERY SESSION
        # =================================================

        request.session.pop(
            "reset_user_id",
            None
        )

        request.session.pop(
            "reset_method",
            None
        )

        request.session.pop(
            "reset_otp",
            None
        )

        request.session.pop(
            "reset_otp_created",
            None
        )

        request.session.pop(
            "reset_verified",
            None
        )

        request.session.modified = True


        # =================================================
        # SUCCESS
        # =================================================

        messages.success(
            request,
            "Your password has been changed successfully. "
            "Please login with your new password."
        )

        return redirect(
            "login"
        )


    # =====================================================
    # GET - DISPLAY PAGE
    # =====================================================

    return render(
        request,
        "reset_password.html"
    )

def logout_view(request):
    logout(request)
    return redirect("login")    

# =========================================================
# EMAIL VERIFICATION PAGE
# =========================================================

def email_verification(request):

    # =====================================================
    # MOBILE VERIFICATION CHECK
    # =====================================================

    if not request.session.get("mobile_verified"):

        messages.error(
            request,
            "Please verify your mobile number first."
        )

        return redirect(
            "verify_mobile"
        )


    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        email = request.session.get(
            "registration_email",
            ""
        )

        return render(
            request,
            "email_verification.html",
            {
                "email": email
            }
        )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get(
            "action",
            "send"
        )


        # =================================================
        # RESEND OTP
        # =================================================

        if action == "resend":

            email = request.session.get(
                "registration_email"
            )

            if not email:

                messages.error(
                    request,
                    "Email verification session expired."
                )

                return redirect(
                    "email_verification"
                )


        # =================================================
        # NEW EMAIL / SEND OTP
        # =================================================

        else:

            email = request.POST.get(
                "email",
                ""
            ).strip().lower()


            if not email:

                messages.error(
                    request,
                    "Please enter your email address."
                )

                return redirect(
                    "email_verification"
                )


            # Save email

            request.session[
                "registration_email"
            ] = email


        # =================================================
        # GENERATE NEW OTP
        # =================================================

        otp = str(
            random.randint(
                100000,
                999999
            )
        )


        # =================================================
        # SAVE OTP
        # =================================================

        request.session[
            "email_otp"
        ] = otp

        request.session[
            "email_otp_created_at"
        ] = timezone.now().isoformat()

        request.session.modified = True


        # =================================================
        # SEND EMAIL
        # =================================================

        try:

            send_mail(

                subject=(
                    "VeriTrust AI - "
                    "Email Verification OTP"
                ),

                message=(

                    f"Hello,\n\n"

                    f"Your VeriTrust AI "
                    f"email verification OTP is:\n\n"

                    f"{otp}\n\n"

                    f"This OTP is valid for 10 minutes.\n\n"

                    f"Please do not share this OTP "
                    f"with anyone.\n\n"

                    f"Regards,\n"
                    f"VeriTrust AI"
                ),

                from_email=(
                    settings.DEFAULT_FROM_EMAIL
                ),

                recipient_list=[
                    email
                ],

                fail_silently=False,
            )


            # =================================================
            # SUCCESS MESSAGE
            # =================================================

            if action == "resend":

                messages.success(
                    request,
                    "A new OTP has been sent to your email."
                )

            else:

                messages.success(
                    request,
                    "OTP has been sent to your email."
                )


            # =================================================
            # GO TO OTP PAGE
            # =================================================

            return redirect(
                "verify_email_otp"
            )


        except Exception as error:

            print(
                "EMAIL OTP ERROR:",
                error
            )

            messages.error(
                request,
                "Unable to send OTP. Please try again."
            )

            return redirect(
                "email_verification"
            )


    return redirect(
        "email_verification"
    )
# =========================================================
# VERIFY EMAIL OTP
# =========================================================

def verify_email_otp(request):

    # =====================================================
    # MOBILE CHECK
    # =====================================================

    if not request.session.get("mobile_verified"):

        messages.error(
            request,
            "Please verify your mobile number first."
        )

        return redirect("verify_mobile")


    # =====================================================
    # EMAIL CHECK
    # =====================================================

    email = request.session.get(
        "registration_email"
    )

    if not email:

        messages.error(
            request,
            "Email verification session expired."
        )

        return redirect("email_verification")


    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return render(
            request,
            "verify_email_otp.html",
            {
                "email": email
            }
        )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get(
            "action",
            "verify"
        )


        # =================================================
        # RESEND OTP
        # =================================================

        if action == "resend":

            new_otp = str(
                random.randint(
                    100000,
                    999999
                )
            )


            # Save new OTP

            request.session["email_otp"] = new_otp

            request.session["email_otp_created_at"] = (
                timezone.now().isoformat()
            )

            request.session.modified = True


            # Send new OTP

            try:

                send_mail(

                    subject=(
                        "VeriTrust AI - "
                        "Email Verification OTP"
                    ),

                    message=(

                        f"Hello,\n\n"

                        f"Your new VeriTrust AI "
                        f"email verification OTP is:\n\n"

                        f"{new_otp}\n\n"

                        f"This OTP is valid for 10 minutes.\n\n"

                        f"Please do not share this OTP "
                        f"with anyone.\n\n"

                        f"Regards,\n"
                        f"VeriTrust AI"
                    ),

                    from_email=(
                        settings.DEFAULT_FROM_EMAIL
                    ),

                    recipient_list=[
                        email
                    ],

                    fail_silently=False,
                )


                messages.success(
                    request,
                    "A new OTP has been sent to your email."
                )


            except Exception as error:

                print(
                    "RESEND EMAIL OTP ERROR:",
                    error
                )

                messages.error(
                    request,
                    "Unable to resend OTP. Please try again."
                )


            return redirect(
                "verify_email_otp"
            )


        # =================================================
        # VERIFY OTP
        # =================================================

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        saved_otp = request.session.get(
            "email_otp"
        )


        # =================================================
        # EMPTY OTP
        # =================================================

        if not entered_otp:

            messages.error(
                request,
                "Please enter the OTP."
            )

            return redirect(
                "verify_email_otp"
            )


        # =================================================
        # INVALID OTP
        # =================================================

        if entered_otp != saved_otp:

            messages.error(
                request,
                "Invalid OTP. Please try again."
            )

            return redirect(
                "verify_email_otp"
            )


        # =================================================
        # EMAIL VERIFIED
        # =================================================

        request.session["email_verified"] = True

        request.session.modified = True


        # Remove OTP

        request.session.pop(
            "email_otp",
            None
        )

        request.session.pop(
            "email_otp_created_at",
            None
        )

        request.session.modified = True


        messages.success(
            request,
            "Email verified successfully."
        )


        # =================================================
        # NEXT = LOGIN
        # =================================================

        return redirect(
            "login"
        )
@login_required
def my_profile(request):

    profile, created = EmployeeProfile.objects.get_or_create(
        user=request.user
    )
    if not profile.employee_id:
        profile.employee_id = f"VT{request.user.id:05d}"
        profile.save()


    if request.method == "POST":

        profile.first_name = request.POST.get("first_name")
        profile.middle_name = request.POST.get("middle_name")
        profile.last_name = request.POST.get("last_name")

        profile.gender = request.POST.get("gender")
        profile.date_of_birth = request.POST.get("date_of_birth") or None
        profile.blood_group = request.POST.get("blood_group")
        profile.marital_status = request.POST.get("marital_status")
        profile.nationality = request.POST.get("nationality")


        request.user.mobile = request.POST.get("mobile")
        profile.alternate_mobile = request.POST.get("alternate_mobile")
    

        request.user.save()

        if request.FILES.get("profile_photo"):

            profile.profile_image = request.FILES["profile_photo"]

        profile.save()

        messages.success(
            request,
            "Profile Updated Successfully."
        )

        return redirect("my_profile")

    context = {

        "profile": profile

    }

    return render(
        request,
        "my_profile.html",
        context
    )



# =====================================================
# IDENTITY VERIFICATION PAGE
# =====================================================

@login_required
def identity_verification(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    context = {

        "verification":
            verification

    }

    return render(

        request,

        "identity_verification.html",

        context

    )


# =====================================================
# JSON HELPER
# =====================================================

def get_json_body(request):

    try:

        return json.loads(
            request.body.decode("utf-8")
        )

    except Exception:

        return {}

        

def convert_ocr_date_to_db_date(date_string):
    if not date_string:
        return None

    if isinstance(date_string, datetime):
        return date_string.date()

    if isinstance(date_string, date):
        return date_string

    date_string = str(date_string).strip()

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except (ValueError, TypeError):
            continue

    return None

@login_required
@require_POST
def process_aadhaar_document(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    aadhaar_front = request.FILES.get(
        "aadhaar_front"
    )

    aadhaar_back = request.FILES.get(
        "aadhaar_back"
    )

    if not aadhaar_front:

        return JsonResponse({

            "success": False,

            "message":
                "Please upload Aadhaar front document."

        }, status=400)

    try:

        verification.aadhaar_front = aadhaar_front

        if aadhaar_back:

            verification.aadhaar_back = aadhaar_back

        verification.aadhaar_status = "PROCESSING"

        verification.save()

        # OCR PROCESSING
        result = process_aadhaar_ocr(

            verification.aadhaar_front.path,

            verification.aadhaar_back.path


        )

        print("AADHAAR OCR RESULT:", result)

        aadhaar_number = result.get(
            "aadhaar_number"
        )

        if not aadhaar_number:

            verification.aadhaar_status = (
                "NEEDS_REVIEW"
            )

            verification.aadhaar_verification_message = (
                "Aadhaar number could not be extracted from the document."
            )

            verification.save()

            return JsonResponse({

                "success": False,

                "manual_aadhaar_required": True,

                "message":
                    "We could not read the Aadhaar number. Please enter it to continue."

            }, status=422)

        verification.aadhaar_ocr_text = (
            result.get("raw_text", "")
        )

        verification.aadhaar_ocr_name = (
            result.get("name", "")
        )

        verification.aadhaar_ocr_date_of_birth = convert_ocr_date_to_db_date(
            result.get("date_of_birth")
        )

        verification.aadhaar_ocr_number = (
            aadhaar_number
        )

        verification.aadhaar_ocr_address = (
            result.get("address", "")
        )

        verification.aadhaar_status = "PROCESSING"

        verification.aadhaar_verification_message = (
            "Document processed successfully."
        )

        verification.save()

        return JsonResponse({

            "success": True,

            "message":
                "Aadhaar document processed successfully."

        })

    except Exception as error:

        import traceback

        traceback.print_exc()

        verification.aadhaar_status = "FAILED"

        verification.aadhaar_verification_message = str(error)

        verification.save()

        return JsonResponse({

            "success": False,

            "message": str(error)

        }, status=500)


@login_required
@require_POST
def process_pan_document(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    # -------------------------------------------------
    # GET PAN FILE
    # -------------------------------------------------

    pan_card = request.FILES.get("pan_card")

    print("========== PAN REQUEST DEBUG ==========")
    print("PAN FILE RECEIVED:", bool(pan_card))
    print("=======================================")

    if not pan_card:

        return JsonResponse({
            "success": False,
            "message": "Please upload PAN document."
        }, status=400)

    try:

        # -------------------------------------------------
        # SAVE PAN CARD
        # -------------------------------------------------

        verification.pan_card.save(
            pan_card.name,
            pan_card,
            save=True
        )

        verification.pan_status = "PROCESSING"

        verification.pan_verification_message = (
            "PAN document is being processed."
        )

        verification.save()


        # -------------------------------------------------
        # PAN OCR
        # -------------------------------------------------

        result = process_pan_ocr(
            verification.pan_card.path
        )

        print("========== PAN OCR RESULT ==========")
        print(result)
        print("====================================")


        # -------------------------------------------------
        # EXTRACT PAN NUMBER
        # -------------------------------------------------

        pan_number = (
            result.get("pan_number") or ""
        ).upper().strip()


        # -------------------------------------------------
        # EXTRACT APPLICANT NAME
        # -------------------------------------------------

        pan_name = (
            result.get("name") or ""
        ).strip()

        print("PAN OCR COMPLETED")
        print("PAN NUMBER FOUND:", bool(pan_number))
        print("PAN NAME FOUND:", bool(pan_name))


        # -------------------------------------------------
        # PAN NUMBER CHECK
        # -------------------------------------------------

        if not pan_number:

            verification.pan_status = "NEEDS_REVIEW"

            verification.pan_verification_message = (
                "PAN number could not be extracted. "
                "Please enter the PAN number manually."
            )

            verification.save()

            return JsonResponse({
                "success": False,
                "manual_pan_required": True,
                "message": (
                    "PAN number could not be read. "
                    "Please enter it manually."
                )
            }, status=422)


        # -------------------------------------------------
        # APPLICANT NAME CHECK
        # -------------------------------------------------

        if not pan_name:

            verification.pan_status = "NEEDS_REVIEW"

            verification.pan_verification_message = (
                "Applicant name could not be extracted from PAN."
            )

            verification.save()

            return JsonResponse({
                "success": False,
                "manual_pan_required": True,
                "message": (
                    "Applicant name could not be read from PAN."
                )
            }, status=422)


        # -------------------------------------------------
        # SAVE OCR DATA
        # -------------------------------------------------

        verification.pan_ocr_number = pan_number
        verification.pan_ocr_name = pan_name

        # PAN मध्ये फक्त:
        # 1. PAN Number
        # 2. Applicant Name
        #
        # DOB save करायचा नाही.

        verification.pan_status = "PROCESSING"

        verification.pan_verification_message = (
            "PAN OCR completed. Validating PAN details."
        )

        verification.save()


        # =================================================
        # PAN API VERIFICATION
        # =================================================

        print("========== PAN API VERIFICATION ==========")

        api_response = verify_pan(
            pan_number
        )

        print("========== FULL PAN API RESPONSE ==========")
        print(api_response)
        print("===========================================")

        print("PAN API RESPONSE RECEIVED:", bool(api_response))

        print("===========================================")


        # -------------------------------------------------
        # SAVE API RESPONSE
        # -------------------------------------------------

        verification.pan_api_response = api_response


        # -------------------------------------------------
        # COMPARE OCR WITH API
        #
        # PAN Number  -> exact match
        # Applicant Name -> exact match
        #
        # Both must match for 100%.
        # -------------------------------------------------

        pan_match_score = calculate_pan_match_score(
            pan_number,
            pan_name,
            api_response
        )

        verification.pan_match_score = pan_match_score


        print(
            "PAN MATCH SCORE:",
            float(pan_match_score)
        )


        # =================================================
        # PAN VERIFIED
        # =================================================

        if pan_match_score == Decimal("100.00"):

            verification.pan_status = "VERIFIED"

            verification.pan_verification_message = (
                "PAN verification completed successfully. "
                "PAN number and applicant name matched."
            )

            verification.save()

            # ---------------------------------------------
            # UPDATE FINAL IDENTITY SCORE
            # Aadhaar = 40%
            # PAN = 30%
            # Face = 30%
            # ---------------------------------------------

            update_final_identity_status(
                verification
            )

            verification.save()


            return JsonResponse({

                "success": True,

                "message": (
                    "PAN verified successfully."
                ),

                "pan_status": (
                    verification.pan_status
                ),

                "pan_match_score": float(
                    verification.pan_match_score or 0
                ),

                "verification_status": (
                    verification.verification_status
                ),

                "verification_score": float(
                    verification.verification_score or 0
                )

            })


        # =================================================
        # PAN DETAILS DO NOT MATCH
        # =================================================

        else:

            verification.pan_status = "NEEDS_REVIEW"

            verification.pan_verification_message = (
                "PAN verification completed, but the "
                "PAN number or applicant name did not "
                "match the verification API data."
            )

            verification.save()


            # ---------------------------------------------
            # UPDATE FINAL SCORE
            # ---------------------------------------------

            update_final_identity_status(
                verification
            )

            verification.save()


            return JsonResponse({

                "success": False,

                "message": (
                    "PAN details could not be verified. "
                    "The PAN number or applicant name "
                    "does not match."
                ),

                "pan_status": (
                    verification.pan_status
                ),

                "pan_match_score": float(
                    verification.pan_match_score or 0
                ),

                "verification_status": (
                    verification.verification_status
                ),

                "verification_score": float(
                    verification.verification_score or 0
                )

            }, status=422)


    except Exception as error:

        import traceback

        traceback.print_exc()


        verification.pan_status = "FAILED"

        verification.pan_match_score = 0

        verification.pan_verification_message = str(
            error
        )

        verification.save()


        # ---------------------------------------------
        # UPDATE FINAL STATUS
        # ---------------------------------------------

        update_final_identity_status(
            verification
        )

        verification.save()


        return JsonResponse({

            "success": False,

            "message": (
                "Unable to process PAN verification."
            )

        }, status=500)


@login_required
@require_POST
def generate_aadhaar_otp_view(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    data = get_json_body(request)

    aadhaar_number = verification.aadhaar_ocr_number

    if not aadhaar_number:
        aadhaar_number = (
            data.get("aadhaar_number", "")
            .replace(" ", "")
            .strip()
        )

    if not aadhaar_number:
        return JsonResponse({
            "success": False,
            "message": "Aadhaar number is not available."
        }, status=400)

    if (
        not aadhaar_number.isdigit()
        or len(aadhaar_number) != 12
    ):
        return JsonResponse({
            "success": False,
            "message": "Invalid Aadhaar number."
        }, status=400)

    try:

        verification.aadhaar_status = "PROCESSING"
        verification.aadhaar_verification_message = (
            "Generating Aadhaar OTP..."
        )
        verification.save()

        # ============================================
        # GENERATE OTP THROUGH API
        # ============================================

        response = generate_aadhaar_otp(
            aadhaar_number
        )

        if not response.get("success"):

            verification.aadhaar_status = "FAILED"
            verification.aadhaar_verification_message = (
                "Unable to generate Aadhaar OTP."
            )
            verification.save()

            print()
            print("=" * 60)
            print("          AADHAAR OTP")
            print("=" * 60)
            print("OTP Status : FAILED")
            print("=" * 60)
            print()

            return JsonResponse({
                "success": False,
                "message": "Unable to generate Aadhaar OTP."
            }, status=400)

        # ============================================
        # GET API RESPONSE DATA
        # ============================================

        response_data = response.get(
            "data",
            {}
        )

        # ============================================
        # GET REQUEST ID
        # Supports both:
        # data.request_id
        # data.data.request_id
        # ============================================

        request_id = (
            response_data.get("request_id")
            or response_data.get("requestId")
        )

        if not request_id:

            nested_data = response_data.get(
                "data"
            )

            if isinstance(
                nested_data,
                dict
            ):
                request_id = (
                    nested_data.get("request_id")
                    or nested_data.get("requestId")
                )

        # ============================================
        # REQUEST ID NOT RECEIVED
        # ============================================

        if not request_id:

            verification.aadhaar_status = "FAILED"
            verification.aadhaar_verification_message = (
                "API did not return request_id."
            )
            verification.save()

            print()
            print("=" * 60)
            print("          AADHAAR OTP")
            print("=" * 60)
            print("OTP Status : FAILED")
            print("Reason     : Request ID not received")
            print("=" * 60)
            print()

            return JsonResponse({
                "success": False,
                "message": (
                    "OTP request could not be completed."
                )
            }, status=400)

        # ============================================
        # SAVE REQUEST ID
        # ============================================

        verification.aadhaar_request_id = str(
            request_id
        )

        verification.aadhaar_status = "OTP_SENT"

        verification.aadhaar_verification_message = (
            "OTP sent successfully."
        )

        verification.save()

        # ============================================
        # CLEAN TERMINAL OUTPUT
        # ============================================

        print()
        print("=" * 60)
        print("          AADHAAR OTP")
        print("=" * 60)
        print("OTP Status : SENT")
        print("=" * 60)
        print()

        return JsonResponse({

            "success": True,

            "message": (
                "OTP has been sent to the mobile number "
                "registered with Aadhaar."
            )

        })

    except Exception as error:

        import traceback

        traceback.print_exc()

        verification.aadhaar_status = "FAILED"

        verification.aadhaar_verification_message = (
            "Unable to connect to Aadhaar verification service."
        )

        verification.save()

        return JsonResponse({

            "success": False,

            "message": (
                "Unable to connect to Aadhaar "
                "verification service."
            )

        }, status=500)
        
@login_required
@require_POST
def verify_aadhaar_otp_view(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    data = get_json_body(request)

    otp = request.POST.get("otp", "").strip()

    # ---------------------------------------------
    # CHECK REQUEST ID
    # ---------------------------------------------

    if not verification.aadhaar_request_id:

        return JsonResponse({
            "success": False,
            "message": "Please generate Aadhaar OTP first."
        }, status=400)

    # ---------------------------------------------
    # CHECK OTP
    # ---------------------------------------------

    if not otp:

        return JsonResponse({
            "success": False,
            "message": "Please enter OTP."
        }, status=400)

    try:

        # ---------------------------------------------
        # SUBMIT AADHAAR OTP
        # ---------------------------------------------

        response = submit_aadhaar_otp(
            verification.aadhaar_request_id,
            otp
        )

        # ---------------------------------------------
        # API FAILURE
        # ---------------------------------------------

        if not response.get("success"):

            verification.aadhaar_status = "FAILED"

            verification.aadhaar_verification_message = (
                "Aadhaar OTP verification failed."
            )

            verification.save()

            return JsonResponse({
                "success": False,
                "message": "Invalid or expired OTP."
            }, status=400)

        # ---------------------------------------------
        # GET API RESPONSE DATA
        # ---------------------------------------------

        response_data = response.get(
            "data",
            {}
        )

        verification.aadhaar_api_response = (
            response_data
        )

        # ---------------------------------------------
        # EXTRACT API DATA
        # ---------------------------------------------

        api_data = extract_aadhaar_api_data(
            response_data
        )

        verification.aadhaar_api_name = (
            api_data.get("name")
        )

        verification.aadhaar_api_address = (
            api_data.get("address")
        )

        api_dob = api_data.get(
            "date_of_birth"
        )

        # ---------------------------------------------
        # CONVERT API DOB
        # ---------------------------------------------

        api_dob_date = None

        if api_dob:

            api_dob_date = (
                convert_ocr_date_to_db_date(
                    api_dob
                )
            )

        verification.aadhaar_api_date_of_birth = (
            api_dob_date
        )

        # ---------------------------------------------
        # CALCULATE MATCH SCORE
        # ---------------------------------------------

        score = calculate_aadhaar_match_score(

            verification.aadhaar_ocr_name,

            verification.aadhaar_ocr_date_of_birth,

            verification.aadhaar_ocr_address,

            verification.aadhaar_api_name,

            api_dob,

            verification.aadhaar_api_address

        )

        # ---------------------------------------------
        # CLEAN TERMINAL OUTPUT
        # ---------------------------------------------

        print()
        print("=" * 60)
        print("          AADHAAR OCR vs API")
        print("=" * 60)

        print()
        print("OCR DATA")
        print("Name    :", verification.aadhaar_ocr_name)
        print(
            "DOB     :",
            verification.aadhaar_ocr_date_of_birth
        )
        print(
            "Address :",
            verification.aadhaar_ocr_address
        )

        print()
        print("API DATA")
        print(
            "Name    :",
            verification.aadhaar_api_name
        )
        print(
            "DOB     :",
            api_dob
        )
        print(
            "Address :",
            verification.aadhaar_api_address
        )

        print()
        print(
            "MATCH SCORE :",
            score
        )

        print("=" * 60)
        print()

        # ---------------------------------------------
        # SAVE MATCH SCORE
        # ---------------------------------------------

        verification.aadhaar_match_score = (
            score
        )

        # ---------------------------------------------
        # AADHAAR VERIFIED
        # ---------------------------------------------

        if score == Decimal("100.00"):

            verification.aadhaar_status = (
                "VERIFIED"
            )

            verification.aadhaar_match_score = (
                Decimal("100.00")
            )

            verification.aadhaar_verification_message = (
                "Aadhaar verification completed successfully."
            )

        # ---------------------------------------------
        # AADHAAR NEEDS REVIEW
        # ---------------------------------------------

        else:

            verification.aadhaar_status = (
                "NEEDS_REVIEW"
            )

            verification.aadhaar_verification_message = (
                "Aadhaar details were verified but "
                "the match score requires manual review."
            )

        # ---------------------------------------------
        # SAVE AADHAAR RESULT
        # ---------------------------------------------

        verification.save()

        # ---------------------------------------------
        # UPDATE FINAL IDENTITY STATUS
        # ---------------------------------------------

        update_final_identity_status(
            verification
        )

        verification.save()

        # ---------------------------------------------
        # SUCCESS RESPONSE
        # ---------------------------------------------

        return JsonResponse({

            "success": True,

            "message": (
                "Aadhaar verified successfully."
            ),

            "aadhaar_status": (
                verification.aadhaar_status
            ),

            "aadhaar_match_score": float(
                verification.aadhaar_match_score or 0
            )

        })

    # ---------------------------------------------
    # EXCEPTION
    # ---------------------------------------------

    except Exception as error:

        import traceback

        traceback.print_exc()

        verification.aadhaar_status = (
            "FAILED"
        )

        verification.aadhaar_verification_message = (
            str(error)
        )

        verification.save()

        return JsonResponse({

            "success": False,

            "message": (
                "Unable to verify Aadhaar OTP."
            )

        }, status=500)
# =====================================================
# MANUAL AADHAAR FALLBACK
#
# Only when OCR fails to extract number.
# =====================================================

@login_required
@require_POST
def save_manual_aadhaar_number(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    data = get_json_body(
        request
    )

    aadhaar_number = (
        str(
            data.get(
                "aadhaar_number",
                ""
            )
        )
        .replace(" ", "")
        .strip()
    )

    if (

        not aadhaar_number.isdigit()

        or

        len(aadhaar_number) != 12

    ):

        return JsonResponse({

            "success": False,

            "message":
                "Please enter a valid 12-digit Aadhaar number."

        }, status=400)

    verification.aadhaar_ocr_number = (
        aadhaar_number
    )

    verification.save()

    return JsonResponse({

        "success": True

    })


# =====================================================
# MANUAL PAN FALLBACK
# =====================================================

@login_required
@require_POST
def verify_manual_pan(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    data = get_json_body(request)

    pan_number = str(
        data.get(
            "pan_number",
            ""
        )
    ).upper().strip()

    pan_name = str(
        data.get(
            "name",
            ""
        )
    ).strip()

    if len(pan_number) != 10:

        return JsonResponse({

            "success": False,

            "message":
                "Please enter a valid PAN number."

        }, status=400)

    if not pan_name:

        return JsonResponse({

            "success": False,

            "message":
                "Applicant name is required for PAN verification."

        }, status=400)

    try:

        verification.pan_ocr_number = pan_number

        verification.pan_ocr_name = pan_name

        verification.pan_status = "PROCESSING"

        verification.save()

        response = verify_pan_number(
            pan_number
        )

        verification.pan_api_response = (
            response.get("data")
        )

        if not response.get("success"):

            verification.pan_status = "FAILED"

            verification.pan_verification_message = (
                "PAN verification failed."
            )

            verification.save()

            return JsonResponse({

                "success": False,

                "message":
                    "PAN verification failed."

            }, status=400)

        score = calculate_pan_match_score(

            pan_number,

            pan_name,

            response.get("data")

        )

        verification.pan_match_score = score

        # EXACT MATCH ONLY
        if score == 100:

            verification.pan_status = "VERIFIED"

            verification.pan_verification_message = (
                "PAN verified successfully."
            )

        else:

            verification.pan_status = "NEEDS_REVIEW"

            verification.pan_verification_message = (
                "PAN details were verified but "
                "the match score requires manual review."
            )

        verification.save()

        update_final_identity_status(
            verification
        )

        verification.save()

        return JsonResponse({

            "success": True,

            "message":
                "PAN verification processed successfully."

        })

    except Exception as error:

        import traceback

        traceback.print_exc()

        verification.pan_status = "FAILED"

        verification.pan_verification_message = (
            str(error)
        )

        verification.save()

        return JsonResponse({

            "success": False,

            "message":
                "Unable to verify PAN."

        }, status=500)

# =====================================================
# LIVE SELFIE VERIFICATION
# =====================================================
@login_required
@require_POST
def process_live_selfie(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    selfie = request.FILES.get("selfie")

    print("========== SELFIE DEBUG ==========")
    print("FILES:", request.FILES)
    print("SELFIE:", request.FILES.get("selfie"))
    print("==================================")   

    if not selfie:

        return JsonResponse({
            "success": False,
            "message": "Please capture a live selfie."
        }, status=400)

    try:

        # ---------------------------------------------
        # GET EMPLOYEE PROFILE
        # ---------------------------------------------

        try:
            profile = request.user.profile
        except Exception:

            verification.selfie_status = "FAILED"
            verification.selfie_match_score = 0
            verification.selfie_face_detected = False
            verification.selfie_verification_message = (
                "Employee profile was not found."
            )

            verification.save()

            return JsonResponse({
                "success": False,
                "message": "Employee profile was not found."
            }, status=400)

        # ---------------------------------------------
        # CHECK PROFILE PHOTO
        # ---------------------------------------------

        if not profile.profile_image:

            verification.selfie_status = "FAILED"
            verification.selfie_match_score = 0
            verification.selfie_face_detected = False
            verification.selfie_verification_message = (
                "Profile photo is required for face verification."
            )

            verification.save()

            return JsonResponse({
                "success": False,
                "message": (
                    "Profile photo is required "
                    "for face verification."
                )
            }, status=400)

        # ---------------------------------------------
        # SAVE SELFIE
        # ---------------------------------------------

        verification.selfie_image.save(
            selfie.name,
            selfie,
            save=True
        )

        verification.selfie_status = "PROCESSING"
        verification.selfie_match_score = 0
        verification.selfie_face_detected = False

        verification.selfie_verification_message = (
            "Face verification is processing."
        )

        verification.save()

        # ---------------------------------------------
        # ACTUAL FACE COMPARISON
        # ---------------------------------------------

        result = verify_face(

            reference_image_path=(
                profile.profile_image.path
            ),

            selfie_image_path=(
                verification.selfie_image.path
            )

        )

        print(
            "========== FACE VERIFICATION =========="
        )

        print(
            "FACE SUCCESS:",
            result.get("success")
        )

        print(
            "FACE DETECTED:",
            result.get("face_detected")
        )

        print(
            "FACE VERIFIED:",
            result.get("verified")
        )

        print(
            "FACE SCORE:",
            result.get("score")
        )

        print(
            "FACE MESSAGE:",
            result.get("message")
        )

        print(
            "======================================="
        )

        # ---------------------------------------------
        # SAVE FACE RESULT
        # ---------------------------------------------

        verification.selfie_face_detected = bool(
            result.get(
                "face_detected",
                False
            )
        )

        verification.selfie_match_score = float(
            result.get(
                "score",
                0
            )
        )

        # ---------------------------------------------
        # FACE VERIFIED
        # ---------------------------------------------

        if (
            result.get("success")
            and
            result.get("verified")
        ):

            verification.selfie_status = "VERIFIED"

            verification.selfie_verification_message = (
                "Selfie verified successfully. "
                "Face matched with profile photo."
            )

            verification.selfie_verified_at = (
                timezone.now()
            )

        # ---------------------------------------------
        # FACE NOT MATCHED
        # ---------------------------------------------

        elif result.get("success"):

            verification.selfie_status = "NEEDS_REVIEW"

            verification.selfie_verification_message = (
                result.get(
                    "message",
                    "Face did not match."
                )
            )

            verification.selfie_verified_at = None

        # ---------------------------------------------
        # FACE PROCESSING ERROR
        # ---------------------------------------------

        else:

            verification.selfie_status = "FAILED"

            verification.selfie_verification_message = (
                result.get(
                    "message",
                    "Face verification failed."
                )
            )

            verification.selfie_verified_at = None

        verification.save()

        # ---------------------------------------------
        # FINAL SCORE
        # ---------------------------------------------

        update_final_identity_status(
            verification
        )

        verification.save()

        return JsonResponse({

            "success": True,

            "message": (
                verification.selfie_verification_message
            ),

            "selfie_status": (
                verification.selfie_status
            ),

            "selfie_match_score": float(
                verification.selfie_match_score or 0
            ),

            "selfie_face_detected": (
                verification.selfie_face_detected
            ),

            "verification_status": (
                verification.verification_status
            ),

            "verification_score": float(
                verification.verification_score or 0
            )

        })

    except Exception as error:

        import traceback

        traceback.print_exc()

        verification.selfie_status = "FAILED"
        verification.selfie_match_score = 0
        verification.selfie_face_detected = False
        verification.selfie_verified_at = None

        verification.selfie_verification_message = (
            str(error)
        )

        verification.save()

        return JsonResponse({

            "success": False,

            "message": (
                "Unable to process live selfie."
            ),

            "error": str(error)

        }, status=500)
# =========================================================
# GET VERIFICATION STATUS
# =========================================================
@login_required
def identity_verification_status(request):

    verification, created = (
        IdentityVerification.objects
        .get_or_create(
            user=request.user
        )
    )

    aadhaar_front_url = None
    aadhaar_back_url = None
    pan_card_url = None
    selfie_image_url = None

    if verification.aadhaar_front:
        aadhaar_front_url = verification.aadhaar_front.url

    if verification.aadhaar_back:
        aadhaar_back_url = verification.aadhaar_back.url

    if verification.pan_card:
        pan_card_url = verification.pan_card.url

    if verification.selfie_image:
        selfie_image_url = verification.selfie_image.url


    return JsonResponse({

        "success": True,


        # =================================================
        # AADHAAR
        # =================================================

        "aadhaar_verified":
            verification.aadhaar_status == "VERIFIED",

        "aadhaar_status":
            verification.aadhaar_status,

        "aadhaar_match_score":
            float(
                verification.aadhaar_match_score or 0
            ),

        "aadhaar_front_url":
            aadhaar_front_url,

        "aadhaar_back_url":
            aadhaar_back_url,


        # =================================================
        # AADHAAR DETAILS
        # =================================================

        "aadhaar_ocr_name":
            verification.aadhaar_ocr_name,

        "aadhaar_ocr_date_of_birth":
            (
                verification.aadhaar_ocr_date_of_birth.isoformat()
                if verification.aadhaar_ocr_date_of_birth
                else None
            ),

        "aadhaar_ocr_number":
            verification.aadhaar_ocr_number,

        "aadhaar_ocr_address":
            verification.aadhaar_ocr_address,


        # =================================================
        # PAN
        # =================================================

        "pan_verified":
            verification.pan_status == "VERIFIED",

        "pan_status":
            verification.pan_status,

        "pan_match_score":
            float(
                verification.pan_match_score or 0
            ),

        "pan_card_url":
            pan_card_url,

        "pan_ocr_name":
            verification.pan_ocr_name,

        "pan_ocr_number":
            verification.pan_ocr_number,


        # =================================================
        # SELFIE
        # =================================================

        "selfie_verified":
            verification.selfie_status == "VERIFIED",

        "selfie_status":
            verification.selfie_status,

        "selfie_match_score":
            float(
                verification.selfie_match_score or 0
            ),

        "selfie_image_url":
            selfie_image_url,


        # =================================================
        # FINAL
        # =================================================

        "verification_score":
            float(
                verification.verification_score or 0
            ),

        "verification_status":
            verification.verification_status,

        "verification_message":
            verification.verification_message or "",

    })
    
@login_required
def identity_result(request):

    identity = IdentityVerification.objects.filter(
        user=request.user
    ).first()

    profile = EmployeeProfile.objects.filter(
        user=request.user
    ).first()

    verification_request = VerificationRequest.objects.filter(
        user=request.user
    ).first()

    verification_result = None

    if verification_request:

        verification_result = (
            VerificationResult.objects.filter(
                verification_request=verification_request
            ).first()
        )

    context = {
        "identity": identity,
        "profile": profile,
        "verification_request": verification_request,
        "verification_result": verification_result,
    }

    return render(
        request,
        "identity_result.html",
        context
    )

@login_required
def verification_history(request):
    return render(request, "verification_history.html")

# =========================================================
# MOBILE OTP VERIFICATION
# =========================================================


def verify_mobile(request):

    mobile = request.session.get("registration_mobile")

    # =====================================================
    # DEBUG + CLEAN MOBILE NUMBER
    # =====================================================

    print("SESSION MOBILE:", repr(mobile))

    if mobile:
        mobile = str(mobile).strip()

    print("CLEAN MOBILE:", repr(mobile))


    # =====================================================
    # SESSION CHECK
    # =====================================================

    if not mobile:

        messages.error(
            request,
            "Mobile verification session expired. Please register again."
        )

        return redirect("register")


    # =====================================================
    # AUTOMATICALLY SEND OTP ON FIRST PAGE LOAD
    # =====================================================

    if request.method == "GET":

        otp_already_sent = request.session.get(
            "otp_sent",
            False
        )


        if not otp_already_sent:

            try:

                payload = {
                    "mobile": mobile,
                    "source": "web"
                }

                print("OTP SEND PAYLOAD:", payload)


                response = requests.post(

                    "https://bargiee.microdynamicsoftware.uk/api/otp/send",

                    json=payload,

                    timeout=15
                )


                print(
                    "OTP SEND STATUS:",
                    response.status_code
                )

                print(
                    "OTP SEND RESPONSE:",
                    response.text
                )


                if response.status_code == 200:

                    request.session["otp_sent"] = True

                    request.session.modified = True


                else:

                    messages.error(

                        request,

                        "Unable to send OTP. Please try again."
                    )


            except requests.RequestException as e:

                print(
                    "OTP SEND ERROR:",
                    e
                )


                messages.error(

                    request,

                    "OTP service is temporarily unavailable."
                )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get("action")


        # =================================================
        # RESEND OTP
        # =================================================

        if action == "resend":

            try:

                payload = {
                    "mobile": mobile,
                    "source": "web"
                }

                print("RESEND PAYLOAD:", payload)


                response = requests.post(

                    "https://bargiee.microdynamicsoftware.uk/api/otp/send",

                    json=payload,

                    timeout=15
                )


                print(
                    "RESEND STATUS:",
                    response.status_code
                )

                print(
                    "RESEND RESPONSE:",
                    response.text
                )


                if response.status_code == 200:

                    request.session["otp_sent"] = True

                    request.session.modified = True


                    messages.success(

                        request,

                        "A new verification code has been sent."
                    )


                else:

                    messages.error(

                        request,

                        "Unable to resend OTP. Please try again."
                    )


            except requests.RequestException as e:

                print(
                    "RESEND ERROR:",
                    e
                )


                messages.error(

                    request,

                    "OTP service is temporarily unavailable."
                )


            return redirect("verify_mobile")


        # =================================================
        # VERIFY OTP
        # =================================================

        if action == "verify":

            otp = request.POST.get(
                "otp",
                ""
            ).strip()


            if not otp:

                messages.error(

                    request,

                    "Please enter the verification code."
                )

                return redirect(
                    "verify_mobile"
                )


            if not otp.isdigit() or len(otp) != 6:

                messages.error(

                    request,

                    "Please enter a valid 6-digit OTP."
                )

                return redirect(
                    "verify_mobile"
                )


            try:

                verify_payload = {

                    "mobile": mobile,

                    "otp": otp,

                    "source": "web"
                }


                print(
                    "VERIFY PAYLOAD:",
                    verify_payload
                )


                response = requests.post(

                    "https://bargiee.microdynamicsoftware.uk/api/otp/verify",

                    json=verify_payload,

                    timeout=15
                )


                print(
                    "VERIFY STATUS:",
                    response.status_code
                )

                print(
                    "VERIFY RESPONSE:",
                    response.text
                )


                try:

                    api_data = response.json()


                except ValueError:

                    api_data = {}


                if response.status_code == 200:

                    if api_data.get("success") is True:

                        request.session[
                            "mobile_verified"
                        ] = True


                        request.session[
                            "otp_sent"
                        ] = False


                        request.session.modified = True


                        messages.success(

                            request,

                            "Mobile number verified successfully."
                        )


                        return redirect(
                            "email_verification"
                        )


                    else:

                        messages.error(

                            request,

                            api_data.get(

                                "message",

                                "Invalid OTP. Please try again."
                            )
                        )


                else:

                    messages.error(

                        request,

                        api_data.get(

                            "message",

                            "Invalid or expired OTP."
                        )
                    )


            except requests.RequestException as e:

                print(
                    "VERIFY API ERROR:",
                    e
                )


                messages.error(

                    request,

                    "OTP verification service is temporarily unavailable."
                )


            return redirect(
                "verify_mobile"
            )


    # =====================================================
    # PAGE LOAD
    # =====================================================

    return render(

        request,

        "verify_mobile.html",

        {

            "mobile": mobile

        }
    )


# =========================================================
# DISTANCE CALCULATION
# =========================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    try:

        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

    except (TypeError, ValueError):

        return None

    earth_radius = 6371000

    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = (
        sin(d_lat / 2) ** 2
        +
        cos(radians(lat1))
        *
        cos(radians(lat2))
        *
        sin(d_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


# =========================================================
# ADDRESS VERIFICATION
# =========================================================

@login_required
def address_verification(request):

    # =====================================================
    # GET EXISTING ADDRESSES
    # =====================================================

    correspondence = (
        AddressVerification.objects
        .filter(
            user=request.user,
            address_type="correspondence"
        )
        .first()
    )

    permanent = (
        AddressVerification.objects
        .filter(
            user=request.user,
            address_type="permanent"
        )
        .first()
    )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        same_address = (
            request.POST.get("same_address")
            == "on"
        )

        # =================================================
        # CORRESPONDENCE
        # =================================================

        c = {

            "house_no":
                request.POST.get(
                    "correspondence-house_no",
                    ""
                ).strip(),

            "street":
                request.POST.get(
                    "correspondence-street",
                    ""
                ).strip(),

            "area":
                request.POST.get(
                    "correspondence-area",
                    ""
                ).strip(),

            "city":
                request.POST.get(
                    "correspondence-city",
                    ""
                ).strip(),

            "district":
                request.POST.get(
                    "correspondence-district",
                    ""
                ).strip(),

            "state":
                request.POST.get(
                    "correspondence-state",
                    ""
                ).strip(),

            "pincode":
                request.POST.get(
                    "correspondence-pincode",
                    ""
                ).strip(),

            "latitude":
                request.POST.get(
                    "correspondence-latitude"
                ) or None,

            "longitude":
                request.POST.get(
                    "correspondence-longitude"
                ) or None,

            "accuracy":
                request.POST.get(
                    "correspondence-location_accuracy"
                ) or None,

            "map_latitude":
                request.POST.get(
                    "correspondence-map_latitude"
                ) or None,

            "map_longitude":
                request.POST.get(
                    "correspondence-map_longitude"
                ) or None,

            "map_address":
                request.POST.get(
                    "correspondence-map_address",
                    ""
                ).strip(),
        }

        # =================================================
        # PERMANENT
        # =================================================

        if same_address:

            p = c.copy()

        else:

            p = {

                "house_no":
                    request.POST.get(
                        "permanent-house_no",
                        ""
                    ).strip(),

                "street":
                    request.POST.get(
                        "permanent-street",
                        ""
                    ).strip(),

                "area":
                    request.POST.get(
                        "permanent-area",
                        ""
                    ).strip(),

                "city":
                    request.POST.get(
                        "permanent-city",
                        ""
                    ).strip(),

                "district":
                    request.POST.get(
                        "permanent-district",
                        ""
                    ).strip(),

                "state":
                    request.POST.get(
                        "permanent-state",
                        ""
                    ).strip(),

                "pincode":
                    request.POST.get(
                        "permanent-pincode",
                        ""
                    ).strip(),

                "latitude":
                    request.POST.get(
                        "permanent-latitude"
                    ) or None,

                "longitude":
                    request.POST.get(
                        "permanent-longitude"
                    ) or None,

                "accuracy":
                    request.POST.get(
                        "permanent-location_accuracy"
                    ) or None,

                "map_latitude":
                    request.POST.get(
                        "permanent-map_latitude"
                    ) or None,

                "map_longitude":
                    request.POST.get(
                        "permanent-map_longitude"
                    ) or None,

                "map_address":
                    request.POST.get(
                        "permanent-map_address",
                        ""
                    ).strip(),
            }

        # =================================================
        # EVIDENCE FILES
        # =================================================

        c_selfie = request.FILES.get(
            "correspondence-selfie"
        )

        c_home_photo = request.FILES.get(
            "correspondence-home_photo"
        )

        c_video = request.FILES.get(
            "correspondence-video"
        )

        p_selfie = request.FILES.get(
            "permanent-selfie"
        )

        p_home_photo = request.FILES.get(
            "permanent-home_photo"
        )

        p_video = request.FILES.get(
            "permanent-video"
        )

        # =================================================
        # VALIDATION
        # =================================================

        errors = []

        required_fields = [
            "house_no",
            "street",
            "area",
            "city",
            "district",
            "state",
            "pincode",
        ]

        for field in required_fields:

            if not c[field]:

                errors.append(
                    f"Correspondence "
                    f"{field.replace('_', ' ')} "
                    f"is required."
                )

        if not same_address:

            for field in required_fields:

                if not p[field]:

                    errors.append(
                        f"Permanent "
                        f"{field.replace('_', ' ')} "
                        f"is required."
                    )

        # =================================================
        # CORRESPONDENCE EVIDENCE
        # =================================================

        if not c_selfie:

            errors.append(
                "Please capture Correspondence Selfie."
            )

        if not c_home_photo:

            errors.append(
                "Please capture Correspondence Home Photo."
            )

        if not c_video:

            errors.append(
                "Please record Correspondence Verification Video."
            )

        # =================================================
        # PERMANENT EVIDENCE
        # =================================================

        if not same_address:

            if not p_selfie:

                errors.append(
                    "Please capture Permanent Selfie."
                )

            if not p_home_photo:

                errors.append(
                    "Please capture Permanent Home Photo."
                )

            if not p_video:

                errors.append(
                    "Please record Permanent Verification Video."
                )

        # =================================================
        # ERROR
        # =================================================

        if errors:

            for error in errors:

                messages.error(
                    request,
                    error
                )

            return render(
                request,
                "address_verification.html",
                {
                    "correspondence": c,
                    "permanent": p,
                    "same_address": same_address,
                    "correspondence_verification": correspondence,
                    "permanent_verification": permanent,
                }
            )

        # =================================================
        # SAVE ADDRESS
        # =================================================

        def save_address(
            existing,
            address_type,
            values
        ):

            verification = (
                existing
                or
                AddressVerification(
                    user=request.user,
                    address_type=address_type
                )
            )

            verification.house_no = values["house_no"]
            verification.street = values["street"]
            verification.area = values["area"]
            verification.city = values["city"]
            verification.district = values["district"]
            verification.state = values["state"]
            verification.pincode = values["pincode"]

            verification.latitude = (
                values["latitude"]
            )

            verification.longitude = (
                values["longitude"]
            )

            verification.location_accuracy = (
                values["accuracy"]
            )

            verification.map_latitude = (
                values["map_latitude"]
            )

            verification.map_longitude = (
                values["map_longitude"]
            )

            verification.map_address = (
                values["map_address"]
            )

            verification.map_verified = (
                bool(
                    values["map_latitude"]
                    and
                    values["map_longitude"]
                )
            )

            verification.status = "pending"

            verification.location_verified = False

            # =================================================
            # DISTANCE BETWEEN LIVE GPS AND MAP LOCATION
            # =================================================

            if (
                verification.latitude
                and verification.longitude
                and verification.map_latitude
                and verification.map_longitude
            ):

                distance = calculate_distance(

                    verification.latitude,
                    verification.longitude,

                    verification.map_latitude,
                    verification.map_longitude
                )

                verification.gps_distance = distance

                # 100 meter threshold
                if distance is not None:

                    verification.location_verified = (
                        distance <= 100
                    )

                    if verification.location_verified:

                        verification.status = "verified"

                    else:

                        verification.status = "needs_review"

            verification.save()

            return verification

        # =================================================
        # SAVE ALL
        # =================================================

        with transaction.atomic():

            correspondence_verification = save_address(

                correspondence,
                "correspondence",
                c
            )

            permanent_verification = save_address(

                permanent,
                "permanent",
                p
            )

            # =================================================
            # EVIDENCE SAVE FUNCTION
            # =================================================

            def save_evidence(
                verification,
                evidence_file,
                evidence_type
            ):

                if not evidence_file:

                    return

                AddressEvidence.objects.create(

                    address_verification=verification,

                    file=evidence_file,

                    evidence_type=evidence_type,

                    capture_latitude=(
                        verification.latitude
                    ),

                    capture_longitude=(
                        verification.longitude
                    ),

                    capture_accuracy=(
                        verification.location_accuracy
                    ),

                    captured_address=(
                        verification.map_address
                        or
                        f"{verification.house_no}, "
                        f"{verification.street}, "
                        f"{verification.area}, "
                        f"{verification.city}, "
                        f"{verification.district}, "
                        f"{verification.state} - "
                        f"{verification.pincode}"
                    ),

                    captured_at=timezone.now(),

                    location_match=(
                        verification.location_verified
                    ),

                    distance_from_address=(
                        verification.gps_distance
                    )
                )

            # =================================================
            # CORRESPONDENCE EVIDENCE
            # =================================================

            save_evidence(
                correspondence_verification,
                c_selfie,
                "selfie"
            )

            save_evidence(
                correspondence_verification,
                c_home_photo,
                "home_photo"
            )

            save_evidence(
                correspondence_verification,
                c_video,
                "verification_video"
            )

            # =================================================
            # SAME ADDRESS
            # =================================================

            if same_address:

                # Copy evidence references logically
                for evidence in (
                    correspondence_verification
                    .evidence
                    .all()
                ):

                    AddressEvidence.objects.create(

                        address_verification=
                            permanent_verification,

                        file=evidence.file.name,

                        evidence_type=
                            evidence.evidence_type,

                        capture_latitude=
                            evidence.capture_latitude,

                        capture_longitude=
                            evidence.capture_longitude,

                        capture_accuracy=
                            evidence.capture_accuracy,

                        captured_address=
                            evidence.captured_address,

                        captured_at=
                            evidence.captured_at,

                        location_match=
                            evidence.location_match,

                        distance_from_address=
                            evidence.distance_from_address
                    )

            else:

                save_evidence(
                    permanent_verification,
                    p_selfie,
                    "selfie"
                )

                save_evidence(
                    permanent_verification,
                    p_home_photo,
                    "home_photo"
                )

                save_evidence(
                    permanent_verification,
                    p_video,
                    "verification_video"
                )

        # =================================================
        # SUCCESS
        # =================================================

        messages.success(
            request,
            "Address verification evidence submitted successfully."
        )

        return redirect(
            request.path
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "address_verification.html",
        {
            "correspondence_verification":
                correspondence,

            "permanent_verification":
                permanent,

            "same_address":
                False,
        }
    )
    
@login_required
def employment(request):

    # =========================================================
    # POST
    # =========================================================

    if request.method == "POST":

        # =====================================================
        # CHECK ACTION
        # =====================================================

        action = request.POST.get("action")

        # =====================================================
        # DELETE ONE SPECIFIC COMPANY
        # =====================================================

        if action == "delete":

            employment_id = request.POST.get("employment_id")

            if employment_id:

                employment_record = (
                    EmployeeEmployment.objects.filter(
                        id=employment_id,
                        user=request.user
                    ).first()
                )

                if employment_record:

                    employment_record.delete()

                    messages.success(
                        request,
                        "Employment company deleted successfully."
                    )

                else:

                    messages.error(
                        request,
                        "Employment record not found."
                    )

            else:

                messages.error(
                    request,
                    "Invalid employment record."
                )

            return redirect("employment")

                # =====================================================
        # EDIT COMPANY DOCUMENT
        # =====================================================

        if action == "edit_document":

            document_id = request.POST.get("document_id")

            document_name = request.POST.get(
                "document_name",
                ""
            ).strip()

            new_document_file = request.FILES.get(
                "document_file"
            )

            # -------------------------------------------------
            # VALIDATE DOCUMENT ID
            # -------------------------------------------------

            if not document_id:

                messages.error(
                    request,
                    "Invalid document."
                )

                return redirect("employment")

            # -------------------------------------------------
            # GET DOCUMENT
            # -------------------------------------------------

            document = (
                EmploymentDocument.objects
                .filter(
                    id=document_id,
                    employment__user=request.user
                )
                .select_related("employment")
                .first()
            )

            # -------------------------------------------------
            # DOCUMENT NOT FOUND
            # -------------------------------------------------

            if not document:

                messages.error(
                    request,
                    "Document not found."
                )

                return redirect("employment")

            # -------------------------------------------------
            # DOCUMENT NAME
            # -------------------------------------------------

            if document_name:

                document.document_name = document_name

            # -------------------------------------------------
            # REPLACE FILE
            # -------------------------------------------------

            if new_document_file:

                document.document_file = new_document_file

            # -------------------------------------------------
            # SAVE
            # -------------------------------------------------

            document.save()

            messages.success(
                request,
                "Document updated successfully."
            )

            return redirect("employment")    

        # =====================================================
        # GET COMPANY DETAILS
        # =====================================================

        company_names = request.POST.getlist(
            "company_name[]"
        )

        designations = request.POST.getlist(
            "designation[]"
        )

        employee_codes = request.POST.getlist(
            "employee_code[]"
        )

        # =====================================================
        # HR DETAILS
        # =====================================================

        hr_names = request.POST.getlist(
            "hr_name[]"
        )

        hr_contacts = request.POST.getlist(
            "hr_contact[]"
        )

        # =====================================================
        # REFERENCE 1
        # =====================================================

        reference1_names = request.POST.getlist(
            "reference1_name[]"
        )

        reference1_positions = request.POST.getlist(
            "reference1_position[]"
        )

        reference1_contacts = request.POST.getlist(
            "reference1_contact[]"
        )

        # =====================================================
        # REFERENCE 2
        # =====================================================

        reference2_names = request.POST.getlist(
            "reference2_name[]"
        )

        reference2_positions = request.POST.getlist(
            "reference2_position[]"
        )

        reference2_contacts = request.POST.getlist(
            "reference2_contact[]"
        )

        # =====================================================
        # DATES
        # =====================================================

        joining_dates = request.POST.getlist(
            "joining_date[]"
        )

        relieving_dates = request.POST.getlist(
            "relieving_date[]"
        )

        employment_statuses = request.POST.getlist(
            "employment_status[]"
        )

        # =====================================================
        # DOCUMENTS
        # =====================================================

        document_names = request.POST.getlist(
            "document_name[]"
        )

        document_files = request.FILES.getlist(
            "document_file[]"
        )

        # =====================================================
        # SAVE EVERY COMPANY
        # =====================================================

        for i in range(len(company_names)):

            # -------------------------------------------------
            # COMPANY NAME
            # -------------------------------------------------

            company_name = (
                company_names[i].strip()
                if i < len(company_names)
                else ""
            )

            if not company_name:
                continue

            # -------------------------------------------------
            # DESIGNATION
            # -------------------------------------------------

            designation = (
                designations[i].strip()
                if i < len(designations)
                else ""
            )

            # -------------------------------------------------
            # EMPLOYEE CODE
            # -------------------------------------------------

            employee_code = (
                employee_codes[i].strip()
                if i < len(employee_codes)
                else ""
            )

            # =================================================
            # HR DETAILS
            # =================================================

            # -------------------------------------------------
            # HR NAME
            # -------------------------------------------------

            hr_name = (
                hr_names[i].strip()
                if i < len(hr_names)
                else ""
            )

            # -------------------------------------------------
            # HR CONTACT
            # -------------------------------------------------

            hr_contact = (
                hr_contacts[i].strip()
                if i < len(hr_contacts)
                else ""
            )

            # =================================================
            # REFERENCE 1
            # =================================================

            reference1_name = (
                reference1_names[i].strip()
                if i < len(reference1_names)
                else ""
            )

            reference1_position = (
                reference1_positions[i].strip()
                if i < len(reference1_positions)
                else ""
            )

            reference1_contact = (
                reference1_contacts[i].strip()
                if i < len(reference1_contacts)
                else ""
            )

            # =================================================
            # REFERENCE 2
            # =================================================

            reference2_name = (
                reference2_names[i].strip()
                if i < len(reference2_names)
                else ""
            )

            reference2_position = (
                reference2_positions[i].strip()
                if i < len(reference2_positions)
                else ""
            )

            reference2_contact = (
                reference2_contacts[i].strip()
                if i < len(reference2_contacts)
                else ""
            )

            # =================================================
            # JOINING DATE
            # =================================================

            joining_date = (
                joining_dates[i]
                if i < len(joining_dates)
                else ""
            )

            # =================================================
            # RELIEVING DATE
            # =================================================

            relieving_date = (
                relieving_dates[i]
                if i < len(relieving_dates)
                else ""
            )

            # =================================================
            # EMPLOYMENT STATUS
            # =================================================

            employment_status = (
                employment_statuses[i]
                if i < len(employment_statuses)
                else "Previous"
            )

            # =================================================
            # JOINING DATE VALIDATION
            # =================================================

            if not joining_date:
                continue

            try:

                joining_date_obj = date.fromisoformat(
                    joining_date
                )

            except (
                ValueError,
                TypeError
            ):

                continue

            # =================================================
            # RELIEVING DATE
            # =================================================

            relieving_date_obj = None

            # Current company ला relieving date save करू नये

            if (
                relieving_date
                and employment_status != "Current"
            ):

                try:

                    relieving_date_obj = date.fromisoformat(
                        relieving_date
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    relieving_date_obj = None

            # =================================================
            # CREATE EMPLOYMENT RECORD
            # =================================================

            employment_record = EmployeeEmployment.objects.create(

                # USER
                user=request.user,

                # COMPANY
                company_name=company_name,

                designation=designation,

                employee_code=employee_code,

                # HR
                hr_name=hr_name,

                hr_contact=hr_contact,

                # REFERENCE 1
                reference1_name=reference1_name,

                reference1_position=reference1_position,

                reference1_contact=reference1_contact,

                # REFERENCE 2
                reference2_name=reference2_name,

                reference2_position=reference2_position,

                reference2_contact=reference2_contact,

                # DATES
                joining_date=joining_date_obj,

                relieving_date=relieving_date_obj,

                # STATUS
                employment_status=employment_status,
            )

            # =================================================
            # SAVE COMPANY DOCUMENTS
            # =================================================

            for document_index in range(
                min(
                    len(document_names),
                    len(document_files)
                )
            ):

                document_name = (
                    document_names[document_index].strip()
                )

                document_file = (
                    document_files[document_index]
                )

                if document_name and document_file:

                    EmploymentDocument.objects.create(

                        employment=employment_record,

                        document_name=document_name,

                        document_file=document_file,
                    )

        # =====================================================
        # SUCCESS MESSAGE
        # =====================================================

        messages.success(
            request,
            "Employment details saved successfully."
        )

        # =====================================================
        # REDIRECT
        # =====================================================

        return redirect("employment")

    # =========================================================
    # GET - FETCH ALL EMPLOYMENTS
    # =========================================================

    employments = (
        EmployeeEmployment.objects
        .filter(
            user=request.user
        )
        .prefetch_related(
            "documents"
        )
        .order_by(
            "-joining_date"
        )
    )

    # =========================================================
    # ADD MODE
    # =========================================================

    add_mode = (
        request.GET.get("add") == "1"
    )

    # =========================================================
    # EXPERIENCE CALCULATION
    # =========================================================

    total_months = 0

    today = timezone.localdate()

    # =========================================================
    # CALCULATE EACH COMPANY EXPERIENCE
    # =========================================================

    for employment_item in employments:

        # -----------------------------------------------------
        # START DATE
        # -----------------------------------------------------

        start_date = (
            employment_item.joining_date
        )

        # -----------------------------------------------------
        # SAFETY CHECK
        # -----------------------------------------------------

        if not start_date:

            employment_item.experience_years = 0

            employment_item.experience_months = 0

            employment_item.experience_text = (
                "0 Years 0 Months"
            )

            continue

        # -----------------------------------------------------
        # END DATE
        # -----------------------------------------------------

        if (
            employment_item.employment_status
            == "Current"
        ):

            # Current company → today's date

            end_date = today

        else:

            # Previous company → relieving date

            end_date = (
                employment_item.relieving_date
            )

        # -----------------------------------------------------
        # NO END DATE
        # -----------------------------------------------------

        if not end_date:

            employment_item.experience_years = 0

            employment_item.experience_months = 0

            employment_item.experience_text = (
                "0 Years 0 Months"
            )

            continue

        # -----------------------------------------------------
        # INVALID DATE
        # -----------------------------------------------------

        if end_date < start_date:

            employment_item.experience_years = 0

            employment_item.experience_months = 0

            employment_item.experience_text = (
                "Invalid dates"
            )

            continue

        # =====================================================
        # CALCULATE COMPLETED MONTHS
        # =====================================================

        months = (
            (
                end_date.year
                - start_date.year
            ) * 12
            +
            (
                end_date.month
                - start_date.month
            )
        )

        # If end day is before joining day,
        # current month is not completed.

        if end_date.day < start_date.day:

            months -= 1

        # =====================================================
        # SAFETY
        # =====================================================

        if months < 0:

            months = 0

        # =====================================================
        # COMPANY EXPERIENCE
        # =====================================================

        years = (
            months // 12
        )

        remaining_months = (
            months % 12
        )

        employment_item.experience_years = (
            years
        )

        employment_item.experience_months = (
            remaining_months
        )

        employment_item.experience_text = (
            f"{years} Years "
            f"{remaining_months} Months"
        )

        # =====================================================
        # ADD TO TOTAL
        # =====================================================

        total_months += months

    # =========================================================
    # TOTAL EXPERIENCE
    # =========================================================

    total_years = (
        total_months // 12
    )

    total_remaining_months = (
        total_months % 12
    )

    total_experience_text = (
        f"{total_years} Years "
        f"{total_remaining_months} Months"
    )

    # =========================================================
    # RENDER
    # =========================================================

    return render(
        request,
        "employment.html",
        {
            "employments": employments,

            "add_mode": add_mode,

            "total_years": total_years,

            "total_months": total_remaining_months,

            "total_experience_text":
                total_experience_text,
        }
    )



@login_required
def education_verification(request):

    # =====================================================
    # ADD EDUCATION
    # =====================================================

    if request.method == "POST":

        form = EducationVerificationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            education = form.save(commit=False)

            # Attach record to logged-in employee
            education.user = request.user

            # New document starts as Uploaded
            education.status = "UPLOADED"

            education.save()

            messages.success(
                request,
                "Education record and document uploaded successfully."
            )

            return redirect("education_verification")

        else:

            messages.error(
                request,
                "Please correct the errors below and try again."
            )

    else:

        form = EducationVerificationForm()

    # =====================================================
    # GET USER EDUCATION RECORDS
    # =====================================================

    education_records = (
        EducationVerification.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    # =====================================================
    # DASHBOARD COUNTS
    # =====================================================

    total_records = education_records.count()

    uploaded_documents = education_records.exclude(
        education_proof=""
    ).count()

    verified_records = education_records.filter(
        status="VERIFIED"
    ).count()

    pending_records = education_records.filter(
        status__in=[
            "PENDING",
            "UPLOADED",
            "UNDER_REVIEW",
        ]
    ).count()

    # =====================================================
    # PAGE
    # =====================================================

    context = {
        "form": form,
        "education_records": education_records,

        "total_records": total_records,
        "uploaded_documents": uploaded_documents,
        "verified_records": verified_records,
        "pending_records": pending_records,
    }

    return render(
        request,
        "education_verification.html",
        context
    )


# =========================================================
# DELETE EDUCATION RECORD
# =========================================================

@login_required
def delete_education(request, education_id):

    education = get_object_or_404(
        EducationVerification,
        id=education_id,
        user=request.user
    )

    if request.method == "POST":

        # Delete database record + uploaded file
        education.delete()

        messages.success(
            request,
            "Education record deleted successfully."
        )

    return redirect("education_verification")    