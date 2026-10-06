from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('register/', views.register, name='register'),

    path('login/', views.login, name='login'),

    path("verify-mobile/", views.verify_mobile, name="verify_mobile"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("features/", views.features, name="features"),

    path("solutions/", views.solutions, name="solutions"),

    path("about/", views.about, name="about"),

    path("contact/", views.contact, name="contact"),

    path("forgot-password/", views.forgot_password, name="forgot_password"),

    path("forgot-password/verify/", views.verify_reset_otp, name="verify_reset_otp"),

    path("forgot-password/reset/", views.reset_password,name="reset_password"),
    path("logout/", views.logout_view, name="logout"),

    path("my-profile/", views.my_profile, name="my_profile"),
    path("identity-verification/", views.identity_verification, name="identity_verification"),
    path("identity-result/", views.identity_result, name="identity_result"),

path(
    "identity-verification/status/",
    views.identity_verification_status,
    name="identity_verification_status"
),
    path("verification-history/", views.verification_history, name="verification_history"),
    path("address-verification/", views.address_verification, name="address_verification"),
    path(
    "email-verification/",
    views.email_verification,
    name="email_verification"
),

path(
    "verify-email-otp/",
    views.verify_email_otp,
    name="verify_email_otp"
),

    

path(
    "verify-email-otp/",
    views.verify_email_otp,
    name="verify_email_otp"
),

    

    path(
        "identity-verification/process-aadhaar/",
        views.process_aadhaar_document,
        name="process_aadhaar_document"
    ),

    path(
        "identity-verification/generate-aadhaar-otp/",
        views.generate_aadhaar_otp_view,
        name="generate_aadhaar_otp"
    ),

    path(
        "identity-verification/verify-aadhaar-otp/",
        views.verify_aadhaar_otp_view,
        name="verify_aadhaar_otp"
    ),

    path(
        "identity-verification/process-pan/",
        views.process_pan_document,
        name="process_pan_document"
    ),

    path(
        "identity-verification/save-manual-aadhaar/",
        views.save_manual_aadhaar_number,
        name="save_manual_aadhaar_number"
    ),

    path(
        "identity-verification/verify-manual-pan/",
        views.verify_manual_pan,
        name="verify_manual_pan"
    ),

    path(
       "identity-verification/selfie/",
       views.process_live_selfie,
       name="process_live_selfie"
    ),

    path("employment/", views.employment, name="employment"),

    path(
        "education-verification/",
        views.education_verification,
        name="education_verification"
    ),

    path(
        "education-verification/delete/<int:education_id>/",
        views.delete_education,
        name="delete_education"
    ),


]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   