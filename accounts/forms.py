from django import forms

from .models import AddressVerification

from .models import EducationVerification



class AddressVerificationForm(forms.ModelForm):

    class Meta:
        model = AddressVerification

        fields = [
            "house_no",
            "street",
            "area",
            "city",
            "district",
            "state",
            "pincode",
            "latitude",
            "longitude",
            "location_accuracy",
        ]

        widgets = {
            "house_no": forms.TextInput(
                attrs={
                    "placeholder": "Enter flat / house no."
                }
            ),

            "street": forms.TextInput(
                attrs={
                    "placeholder": "Detected automatically"
                }
            ),

            "area": forms.TextInput(
                attrs={
                    "placeholder": "Detected automatically"
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "placeholder": "Detected automatically"
                }
            ),

            "district": forms.TextInput(
                attrs={
                    "placeholder": "Detected automatically"
                }
            ),

            "state": forms.TextInput(
                attrs={
                    "placeholder": "Detected automatically"
                }
            ),

            "pincode": forms.TextInput(
                attrs={
                    "placeholder": "Detected automatically",
                    "maxlength": "6",
                    "inputmode": "numeric"
                }
            ),

            "latitude": forms.HiddenInput(),

            "longitude": forms.HiddenInput(),

            "location_accuracy": forms.HiddenInput(),
        }

from django import forms

from .models import IdentityVerification


class AadhaarUploadForm(forms.ModelForm):

    class Meta:

        model = IdentityVerification

        fields = [
            "aadhaar_front",
            "aadhaar_back",
        ]


class PanUploadForm(forms.ModelForm):

    class Meta:

        model = IdentityVerification

        fields = [
            "pan_card",
        ]


class EducationVerificationForm(forms.ModelForm):

    class Meta:
        model = EducationVerification

        fields = [
            "education_level",
            "institute_name",
            "university_name",
            "board_name",
            "passing_year",
            "percentage",
            "certificate_number",
            "document_type",
            "education_proof",
        ]

        widgets = {

            "education_level": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "institute_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter institute / college name",
                }
            ),

            "university_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter university name",
                }
            ),

            "board_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter board name",
                }
            ),

            "passing_year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter passing year",
                    "min": "1950",
                    "max": "2100",
                }
            ),

            "percentage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter percentage / CGPA",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),

            "certificate_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter certificate / enrollment number",
                }
            ),

            "document_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "education_proof": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.jpg,.jpeg,.png",
                }
            ),
        }

    # =====================================================
    # FILE VALIDATION
    # =====================================================

    def clean_education_proof(self):

        file = self.cleaned_data.get("education_proof")

        if not file:
            raise forms.ValidationError(
                "Please upload your education document."
            )

        # Maximum file size = 10 MB
        max_size = 10 * 1024 * 1024

        if file.size > max_size:
            raise forms.ValidationError(
                "File size must not exceed 10 MB."
            )

        # Allowed file types
        allowed_extensions = [
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
        ]

        file_name = file.name.lower()

        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            raise forms.ValidationError(
                "Only PDF, JPG, JPEG and PNG files are allowed."
            )

        return file

    # =====================================================
    # PASSING YEAR VALIDATION
    # =====================================================

    def clean_passing_year(self):

        year = self.cleaned_data.get("passing_year")

        if year and (year < 1950 or year > 2100):
            raise forms.ValidationError(
                "Please enter a valid passing year."
            )

        return year

    # =====================================================
    # PERCENTAGE VALIDATION
    # =====================================================

    def clean_percentage(self):

        percentage = self.cleaned_data.get("percentage")

        if percentage is not None:

            if percentage < 0 or percentage > 100:
                raise forms.ValidationError(
                    "Percentage must be between 0 and 100."
                )

        return percentage