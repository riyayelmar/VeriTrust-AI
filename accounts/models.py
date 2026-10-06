from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model


# ==========================================
# Custom User
# ==========================================

class User(AbstractUser):

    ROLE_CHOICES = (

        ('EMPLOYEE', 'Employee'),

        ('HR', 'HR'),

        ('ADMIN', 'Admin'),

    )

    email = models.EmailField(
        unique=True
    )

    mobile = models.CharField(
        max_length=15
    )

    role = models.CharField(

        max_length=20,

        choices=ROLE_CHOICES,

        default="EMPLOYEE"

    )

    is_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def __str__(self):

        return self.email


# ==========================================
# Employee Profile
# ==========================================



class EmployeeProfile(models.Model):

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )

    MARITAL_STATUS_CHOICES = (
        ("Single", "Single"),
        ("Married", "Married"),
        ("Divorced", "Divorced"),
        ("Widowed", "Widowed"),
    )

    BLOOD_GROUP_CHOICES = (
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    profile_image = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True
    )

    first_name = models.CharField(
        max_length=100,
        blank=True
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
        blank=True
    )

    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True
    )

    nationality = models.CharField(
        max_length=100,
        default="Indian"
    )
    alternate_mobile = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"
        ordering = ["employee_id"]

    def __str__(self):
        if self.first_name:
            return f"{self.employee_id} - {self.first_name} {self.last_name}"
        return self.employee_id



# ==========================================
# Existing Verification Profile
# (Temporary - Remove Later)
# ==========================================

class VerificationProfile(models.Model):

    user = models.OneToOneField(

        User,

        on_delete=models.CASCADE

    )

    personal_details = models.BooleanField(
        default=False
    )

    identity_verified = models.BooleanField(
        default=False
    )

    address_verified = models.BooleanField(
        default=False
    )

    education_verified = models.BooleanField(
        default=False
    )

    employment_verified = models.BooleanField(
        default=False
    )

    documents_uploaded = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.user.email

# ==========================================
# Employee Education
# ==========================================
class EducationVerification(models.Model):

    EDUCATION_CHOICES = (
        ("SSC", "SSC"),
        ("HSC", "HSC"),
        ("Diploma", "Diploma"),
        ("Graduation", "Graduation"),
        ("Post Graduation", "Post Graduation"),
        ("Other", "Other"),
    )

    DOCUMENT_TYPE_CHOICES = (
        ("MARKSHEET", "Marksheet"),
        ("DEGREE", "Degree Certificate"),
        ("PASSING", "Passing Certificate"),
        ("DIPLOMA", "Diploma Certificate"),
        ("OTHER", "Other"),
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("UPLOADED", "Uploaded"),
        ("UNDER_REVIEW", "Under Review"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="education_verifications"
    )

    education_level = models.CharField(
        max_length=30,
        choices=EDUCATION_CHOICES
    )

    institute_name = models.CharField(
        max_length=255
    )

    university_name = models.CharField(
        max_length=255,
        blank=True
    )

    board_name = models.CharField(
        max_length=255,
        blank=True
    )

    passing_year = models.PositiveIntegerField()

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    certificate_number = models.CharField(
        max_length=100,
        blank=True
    )

    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default="OTHER"
    )

    education_proof = models.FileField(
        upload_to="education_proofs/%Y/%m/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    verification_message = models.TextField(
        blank=True,
        null=True
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.education_level}"
# ==========================================
# Employee Employment
# ==========================================

class EmployeeEmployment(models.Model):

    EMPLOYMENT_STATUS = (
        ("Current", "Current"),
        ("Previous", "Previous"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="employments"
    )

    company_name = models.CharField(
        max_length=255
    )

    designation = models.CharField(
        max_length=255
    )

    employee_code = models.CharField(
        max_length=100,
        blank=True
    )

    hr_name = models.CharField(
        max_length=255,
        blank=True
    )

    hr_contact = models.CharField(
        max_length=15,
        blank=True
    )

    reference1_name = models.CharField(
        max_length=255,
        blank=True
    )

    reference1_position = models.CharField(
        max_length=255,
        blank=True
    )

    reference1_contact = models.CharField(
        max_length=20,
        blank=True
    )

    # REFERENCE 2
    reference2_name = models.CharField(
        max_length=255,
        blank=True
    )

    reference2_position = models.CharField(
        max_length=255,
        blank=True
    )

    reference2_contact = models.CharField(
        max_length=20,
        blank=True
    )

    joining_date = models.DateField()

    relieving_date = models.DateField(
        null=True,
        blank=True
    )

    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS,
        default="Previous"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.company_name}"

class EmploymentDocument(models.Model):
    
    employment = models.ForeignKey(
        EmployeeEmployment,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_name = models.CharField(max_length=255)

    document_file = models.FileField(
        upload_to="employment_documents/"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employment.company_name} - {self.document_name}"





User = get_user_model()


# ==========================================
# IDENTITY VERIFICATION
# ==========================================

# ==========================================
# IDENTITY VERIFICATION
# ==========================================

class IdentityVerification(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("OTP_SENT", "OTP Sent"),
        ("VERIFIED", "Verified"),
        ("NEEDS_REVIEW", "Needs Review"),
        ("FAILED", "Failed"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="identity_verification"
    )

    # =====================================================
    # AADHAAR DOCUMENT
    # =====================================================

    aadhaar_front = models.ImageField(
        upload_to="verification/aadhaar/",
        blank=True,
        null=True
    )

    aadhaar_back = models.ImageField(
        upload_to="verification/aadhaar/",
        blank=True,
        null=True
    )

    # =====================================================
    # AADHAAR OCR
    # =====================================================

    aadhaar_ocr_text = models.TextField(
        blank=True,
        null=True
    )

    aadhaar_ocr_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    aadhaar_ocr_date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    aadhaar_ocr_number = models.CharField(
        max_length=12,
        blank=True,
        null=True
    )

    aadhaar_ocr_address = models.TextField(
        blank=True,
        null=True
    )

    # =====================================================
    # AADHAAR API / OTP
    # =====================================================

    aadhaar_request_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    aadhaar_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    aadhaar_verification_message = models.TextField(
        blank=True,
        null=True
    )

    # =====================================================
    # AADHAAR KYC RESPONSE
    #
    # Actual API response full JSON safely stored here.
    # =====================================================

    aadhaar_api_response = models.JSONField(
        blank=True,
        null=True
    )

    aadhaar_api_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    aadhaar_api_date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    aadhaar_api_address = models.TextField(
        blank=True,
        null=True
    )

    aadhaar_match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    # =====================================================
    # PAN DOCUMENT
    # =====================================================

    pan_card = models.ImageField(
        upload_to="verification/pan/",
        blank=True,
        null=True
    )

    # =====================================================
    # PAN OCR
    # =====================================================

    pan_ocr_text = models.TextField(
        blank=True,
        null=True
    )

    pan_ocr_number = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    pan_ocr_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    pan_ocr_date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    # =====================================================
    # PAN API
    # =====================================================

    pan_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    pan_verification_message = models.TextField(
        blank=True,
        null=True
    )

    pan_api_response = models.JSONField(
        blank=True,
        null=True
    )

    pan_match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

        # =====================================================
    # LIVE SELFIE VERIFICATION
    # =====================================================

    selfie_image = models.ImageField(
        upload_to="verification/selfie/",
        blank=True,
        null=True
    )

    selfie_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    selfie_verification_message = models.TextField(
        blank=True,
        null=True
    )

    selfie_match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    selfie_face_detected = models.BooleanField(
        default=False
    )

    selfie_verified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    # =====================================================
    # FINAL IDENTITY RESULT
    # =====================================================

    verification_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    verification_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    verification_message = models.TextField(
        blank=True,
        null=True
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.user.email} - "
            f"{self.verification_status}"
        )

class VerificationRequest(models.Model):

    STATUS_CHOICES = (

        ("Pending", "Pending"),
        ("In Review", "In Review"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
        ("On Hold", "On Hold"),

    )


    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="verification_request"
    )


    requested_at = models.DateTimeField(
        auto_now_add=True
    )


    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )


    def __str__(self):

        return f"{self.user.email} - {self.status}"
        
class VerificationResult(models.Model):

    RISK_LEVEL = (
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    )

    verification_request = models.OneToOneField(
        VerificationRequest,
        on_delete=models.CASCADE,
        related_name="result"
    )

    ai_trust_score = models.PositiveIntegerField(
        default=0
    )

    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL,
        default="Low"
    )

    final_status = models.CharField(
        max_length=20,
        default="Pending"
    )

    remarks = models.TextField(
        blank=True
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_results"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.verification_request.user.email}"      

# ==========================================
# Activity Log
# ==========================================

class ActivityLog(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    activity = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.activity}"


# =========================================================
# ADDRESS VERIFICATION
# =========================================================

class AddressVerification(models.Model):

    ADDRESS_TYPE_CHOICES = (
        ("correspondence", "Correspondence Address"),
        ("permanent", "Permanent Address"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("needs_review", "Needs Review"),
        ("rejected", "Rejected"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="address_verifications"
    )

    # =====================================================
    # ADDRESS TYPE
    # =====================================================

    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES
    )

    # =====================================================
    # ADDRESS
    # =====================================================

    house_no = models.CharField(
        max_length=100
    )

    street = models.CharField(
        max_length=255
    )

    area = models.CharField(
        max_length=255
    )

    city = models.CharField(
        max_length=100
    )

    district = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    # =====================================================
    # SELECTED / LIVE LOCATION
    # =====================================================

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    location_accuracy = models.FloatField(
        null=True,
        blank=True
    )

    # =====================================================
    # SEARCHED MAP LOCATION
    # =====================================================

    map_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    map_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    map_address = models.TextField(
        blank=True,
        null=True
    )

    map_verified = models.BooleanField(
        default=False
    )

    # =====================================================
    # GPS DISTANCE
    # =====================================================

    gps_distance = models.FloatField(
        null=True,
        blank=True,
        help_text="Distance in meters"
    )

    # =====================================================
    # LOCATION CHECK
    # =====================================================

    location_verified = models.BooleanField(
        default=False
    )

    # =====================================================
    # FINAL STATUS
    # =====================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        unique_together = (
            "user",
            "address_type"
        )

    def __str__(self):

        return (
            f"{self.user.email} - "
            f"{self.get_address_type_display()}"
        )


# =========================================================
# ADDRESS VERIFICATION EVIDENCE
# =========================================================

class AddressEvidence(models.Model):

    EVIDENCE_TYPE_CHOICES = (
        ("selfie", "Selfie"),
        ("home_photo", "Home Photo"),
        ("verification_video", "Verification Video"),
    )

    address_verification = models.ForeignKey(
        AddressVerification,
        on_delete=models.CASCADE,
        related_name="evidence"
    )

    evidence_type = models.CharField(
        max_length=30,
        choices=EVIDENCE_TYPE_CHOICES
    )

    file = models.FileField(
        upload_to="address_evidence/"
    )

    # =====================================================
    # CAPTURE LOCATION
    # =====================================================

    capture_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    capture_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    capture_accuracy = models.FloatField(
        null=True,
        blank=True
    )

    # =====================================================
    # CAPTURE INFORMATION
    # =====================================================

    captured_address = models.TextField(
        blank=True,
        null=True
    )

    captured_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================================
    # LOCATION MATCH
    # =====================================================

    location_match = models.BooleanField(
        default=False
    )

    distance_from_address = models.FloatField(
        null=True,
        blank=True,
        help_text="Distance in meters"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.get_evidence_type_display()} - "
            f"{self.address_verification.user.email}"
        )

# =========================================================
# EMAIL VERIFICATION
# =========================================================

class EmailVerification(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification"
    )

    email = models.EmailField()

    otp = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )

    otp_created_at = models.DateTimeField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.user.email} - Email Verification"
        )        