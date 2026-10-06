document.addEventListener("DOMContentLoaded", function () {

"use strict";


/* =========================================================
   ELEMENTS
========================================================= */

const aadhaarFront =
    document.getElementById("aadhaarFront");

const aadhaarBack =
    document.getElementById("aadhaarBack");

const panCardInput =
    document.getElementById("panCardInput");


/* =========================================================
   FILE NAMES
========================================================= */

const aadhaarFrontName =
    document.getElementById("aadhaarFrontName");

const aadhaarBackName =
    document.getElementById("aadhaarBackName");

const panFileName =
    document.getElementById("panFileName");


/* =========================================================
   AADHAAR DETAILS
   Details are intentionally not displayed.
========================================================= */

const aadhaarDetails =
    document.getElementById("aadhaarDetails");

const aadhaarAddressDetails =
    document.getElementById("aadhaarAddressDetails");

const aadhaarDetailName =
    document.getElementById("aadhaarDetailName");

const aadhaarDetailDob =
    document.getElementById("aadhaarDetailDob");

const aadhaarDetailGender =
    document.getElementById("aadhaarDetailGender");

const aadhaarDetailNumber =
    document.getElementById("aadhaarDetailNumber");

const aadhaarDetailAddress =
    document.getElementById("aadhaarDetailAddress");


/* =========================================================
   PAN DETAILS
   Details are intentionally not displayed.
========================================================= */

const panDetails =
    document.getElementById("panDetails");

const panDetailName =
    document.getElementById("panDetailName");

const panDetailNumber =
    document.getElementById("panDetailNumber");


/* =========================================================
   STATUS
========================================================= */

const overallStatus =
    document.getElementById("overallStatus");

const aadhaarStatus =
    document.getElementById("aadhaarStatus");

const panStatus =
    document.getElementById("panStatus");

const selfieStatus =
    document.getElementById("selfieStatus");


/* =========================================================
   PROGRESS
========================================================= */

const progressPercentage =
    document.getElementById("progressPercentage");

const progressFill =
    document.getElementById("progressFill");


/* =========================================================
   FINAL RESULT
========================================================= */

const verificationScore =
    document.getElementById("verificationScore");

const finalMessage =
    document.getElementById("finalMessage");

const finalIcon =
    document.getElementById("finalIcon");


/* =========================================================
   TOAST
========================================================= */

const toast =
    document.getElementById("toast");


/* =========================================================
   BUTTONS
========================================================= */

const processAadhaarBtn =
    document.getElementById("processAadhaarBtn");

const saveManualAadhaarBtn =
    document.getElementById("saveManualAadhaarBtn");

const verifyAadhaarOtpBtn =
    document.getElementById("verifyAadhaarOtpBtn");

const processPanBtn =
    document.getElementById("processPanBtn");

const verifyManualPanBtn =
    document.getElementById("verifyManualPanBtn");

const startCameraBtn =
    document.getElementById("startCameraBtn");

const captureSelfieBtn =
    document.getElementById("captureSelfieBtn");

const retakeSelfieBtn =
    document.getElementById("retakeSelfieBtn");

const verifySelfieBtn =
    document.getElementById("verifySelfieBtn");


/* =========================================================
   SECTIONS
========================================================= */

const aadhaarUploadSection =
    document.getElementById("aadhaarUploadSection");

const aadhaarProcessing =
    document.getElementById("aadhaarProcessing");

const aadhaarFallback =
    document.getElementById("aadhaarFallback");

const aadhaarOtpSection =
    document.getElementById("aadhaarOtpSection");

const aadhaarSuccess =
    document.getElementById("aadhaarSuccess");


const panUploadSection =
    document.getElementById("panUploadSection");

const panProcessing =
    document.getElementById("panProcessing");

const panFallback =
    document.getElementById("panFallback");

const panSuccess =
    document.getElementById("panSuccess");


/* =========================================================
   SELFIE SECTIONS
========================================================= */

const selfieCameraSection =
    document.getElementById("selfieCameraSection");

const selfiePreviewWrapper =
    document.getElementById("selfiePreviewWrapper");

const selfieProcessing =
    document.getElementById("selfieProcessing");

const selfieSuccess =
    document.getElementById("selfieSuccess");

const selfieResult =
    document.getElementById("selfieResult");

const selfieResultMessage =
    document.getElementById("selfieResultMessage");


/* =========================================================
   SELFIE ELEMENTS
========================================================= */

const selfieVideo =
    document.getElementById("selfieVideo");

const selfieCanvas =
    document.getElementById("selfieCanvas");

const selfiePreview =
    document.getElementById("selfiePreview");

const selfieCameraMessage =
    document.getElementById("selfieCameraMessage");


let cameraStream = null;
let selfieBlob = null;
let selfiePreviewUrl = null;


/* =========================================================
   DOCUMENT PREVIEW CSS
========================================================= */

function addDocumentPreviewStyles() {

    if (
        document.getElementById(
            "dynamicDocumentPreviewStyles"
        )
    ) {
        return;
    }

    const style =
        document.createElement("style");

    style.id =
        "dynamicDocumentPreviewStyles";

    style.textContent = `

        /* =================================================
           ALL DOCUMENT UPLOAD BOX TYPES
        ================================================= */

        .upload-box,
        .document-upload-box,
        .pan-upload-box {

            position: relative !important;

            overflow: hidden !important;

            box-sizing: border-box !important;

            isolation: isolate !important;
        }


        /* =================================================
           DOCUMENT IMAGE
        ================================================= */

        .box-document-preview {

            position: absolute !important;

            top: 10px !important;

            right: 10px !important;

            width: 48% !important;

            height: calc(100% - 20px) !important;

            object-fit: contain !important;

            border-radius: 10px !important;

            background: #f7f9fc !important;

            border: 1px solid rgba(120,160,255,0.20) !important;

            z-index: 50 !important;

            display: block !important;

            padding: 3px !important;

            box-sizing: border-box !important;
        }


        /* =================================================
           HIDDEN IMAGE
        ================================================= */

        .box-document-preview.hidden {

            display: none !important;
        }


        /* =================================================
           SELECTED DOCUMENT BOX
        ================================================= */

        .upload-box.document-selected,
        .document-upload-box.document-selected,
        .pan-upload-box.document-selected {

            padding-right: 51% !important;

            box-sizing: border-box !important;
        }


        /* =================================================
           HIDE PLACEHOLDER CONTENT
           ONLY WHEN IMAGE EXISTS
        ================================================= */

        .upload-box.document-selected .upload-icon,
        .upload-box.document-selected .upload-title,
        .upload-box.document-selected .file-name,

        .document-upload-box.document-selected .upload-icon,
        .document-upload-box.document-selected .upload-title,
        .document-upload-box.document-selected .file-name,

        .pan-upload-box.document-selected .upload-icon,
        .pan-upload-box.document-selected .upload-title,
        .pan-upload-box.document-selected .file-name {

            display: none !important;
        }


        /* =================================================
           HIDE SMALL UPLOAD DESCRIPTION
        ================================================= */

        .upload-box.document-selected small,
        .document-upload-box.document-selected small,
        .pan-upload-box.document-selected small {

            display: none !important;
        }


        /* =================================================
           IMAGE ALWAYS ABOVE PLACEHOLDER
        ================================================= */

        .upload-box .box-document-preview:not(.hidden),
        .document-upload-box .box-document-preview:not(.hidden),
        .pan-upload-box .box-document-preview:not(.hidden) {

            display: block !important;

            visibility: visible !important;

            opacity: 1 !important;
        }


        /* =================================================
           DETAILS ARE NOT DISPLAYED
        ================================================= */

        #aadhaarDetails,
        #aadhaarAddressDetails,
        #panDetails {

            display: none !important;
        }


        /* =================================================
           MOBILE
        ================================================= */

        @media (max-width: 768px) {

            .upload-box.document-selected,
            .document-upload-box.document-selected,
            .pan-upload-box.document-selected {

                padding-right: 0 !important;

                padding-bottom: 45% !important;
            }


            .box-document-preview {

                top: auto !important;

                right: 10px !important;

                bottom: 10px !important;

                width: calc(100% - 20px) !important;

                height: 40% !important;
            }
        }

    `;

    document.head.appendChild(style);
}


addDocumentPreviewStyles();


/* =========================================================
   CSRF
========================================================= */

function getCSRFToken() {

    const cookieValue =
        document.cookie
            .split("; ")
            .find(row =>
                row.startsWith("csrftoken=")
            );

    if (!cookieValue) {
        return "";
    }

    return decodeURIComponent(
        cookieValue.split("=")[1]
    );
}


/* =========================================================
   TOAST
========================================================= */

function showToast(
    message,
    type = "info"
) {

    if (!toast) {
        return;
    }

    toast.textContent =
        message;

    toast.className =
        "toast";

    toast.classList.add(type);

    toast.classList.add("show");

    setTimeout(function () {

        toast.classList.remove("show");

    }, 3500);
}


/* =========================================================
   HIDE
========================================================= */

function hideElement(element) {

    if (element) {
        element.classList.add("hidden");
    }
}


/* =========================================================
   SHOW
========================================================= */

function showElement(element) {

    if (element) {
        element.classList.remove("hidden");
    }
}


/* =========================================================
   GET DOCUMENT UPLOAD BOX
   IMPORTANT:
   Supports all three classes.
========================================================= */

function getDocumentUploadBox(inputElement) {

    if (!inputElement) {
        return null;
    }

    return inputElement.closest(
        ".upload-box, .document-upload-box, .pan-upload-box"
    );
}


/* =========================================================
   GET DOCUMENT PREVIEW IMAGE
========================================================= */

function getBoxPreviewImage(inputElement) {

    if (!inputElement) {
        return null;
    }


    const uploadBox =
        getDocumentUploadBox(
            inputElement
        );


    if (!uploadBox) {

        console.error(
            "Document upload box not found for:",
            inputElement.id
        );

        return null;
    }


    let preview =
        uploadBox.querySelector(
            ".box-document-preview"
        );


    if (!preview) {

        preview =
            document.createElement("img");

        preview.className =
            "box-document-preview hidden";

        preview.alt =
            "Document preview";

        uploadBox.appendChild(
            preview
        );
    }


    uploadBox.classList.add(
        "document-selected"
    );


    return preview;
}


/* =========================================================
   SHOW UPLOADED IMAGE
========================================================= */

function showImagePreview(
    file,
    inputElement,
    fileNameElement
) {

    if (
        !file ||
        !inputElement
    ) {
        return;
    }


    if (
        !file.type ||
        !file.type.startsWith("image/")
    ) {

        showToast(
            "Please select a valid image file.",
            "error"
        );

        return;
    }


    if (fileNameElement) {

        fileNameElement.textContent =
            file.name;
    }


    const imageElement =
        getBoxPreviewImage(
            inputElement
        );


    if (!imageElement) {

        showToast(
            "Unable to display document preview.",
            "error"
        );

        return;
    }


    /* Revoke old temporary URL */

    if (
        imageElement.dataset.previewUrl
    ) {

        URL.revokeObjectURL(
            imageElement.dataset.previewUrl
        );
    }


    const previewUrl =
        URL.createObjectURL(file);


    imageElement.src =
        previewUrl;


    imageElement.dataset.previewUrl =
        previewUrl;


    /* IMPORTANT:
       Remove hidden after setting src */

    imageElement.classList.remove(
        "hidden"
    );


    imageElement.style.display =
        "block";


    const uploadBox =
        getDocumentUploadBox(
            inputElement
        );


    if (uploadBox) {

        uploadBox.classList.add(
            "document-selected"
        );
    }
}


/* =========================================================
   AADHAAR FRONT UPLOAD
========================================================= */

if (aadhaarFront) {

    aadhaarFront.addEventListener(
        "change",
        function () {

            const file =
                this.files &&
                this.files[0];

            if (!file) {
                return;
            }

            showImagePreview(
                file,
                aadhaarFront,
                aadhaarFrontName
            );
        }
    );
}


/* =========================================================
   AADHAAR BACK UPLOAD
========================================================= */

if (aadhaarBack) {

    aadhaarBack.addEventListener(
        "change",
        function () {

            const file =
                this.files &&
                this.files[0];

            if (!file) {
                return;
            }

            showImagePreview(
                file,
                aadhaarBack,
                aadhaarBackName
            );
        }
    );
}


/* =========================================================
   PAN UPLOAD
========================================================= */

if (panCardInput) {

    panCardInput.addEventListener(
        "change",
        function () {

            const file =
                this.files &&
                this.files[0];

            if (!file) {
                return;
            }

            showImagePreview(
                file,
                panCardInput,
                panFileName
            );
        }
    );
}


/* =========================================================
   AADHAAR DETAILS
   Disabled intentionally.
========================================================= */

function renderAadhaarDetails(data) {

    /*
        OCR/API details are intentionally NOT
        displayed on the verification page.
    */

    return;
}


/* =========================================================
   PAN DETAILS
   Disabled intentionally.
========================================================= */

function renderPanDetails(data) {

    /*
        PAN OCR/API details are intentionally NOT
        displayed on the verification page.
    */

    return;
}


/* =========================================================
   LOAD SAVED DOCUMENT IMAGE
========================================================= */

function loadSavedImage(
    imageUrl,
    inputElement
) {

    if (
        !imageUrl ||
        !inputElement
    ) {
        return;
    }


    const imageElement =
        getBoxPreviewImage(
            inputElement
        );


    if (!imageElement) {
        return;
    }


    /* Saved Django MEDIA image */

    imageElement.src =
        imageUrl;


    imageElement.removeAttribute(
        "data-preview-url"
    );


    imageElement.classList.remove(
        "hidden"
    );


    imageElement.style.display =
        "block";


    const uploadBox =
        getDocumentUploadBox(
            inputElement
        );


    if (uploadBox) {

        uploadBox.classList.add(
            "document-selected"
        );
    }


    imageElement.onload =
        function () {

            imageElement.classList.remove(
                "hidden"
            );

            imageElement.style.display =
                "block";

            if (uploadBox) {

                uploadBox.classList.add(
                    "document-selected"
                );
            }
        };


    imageElement.onerror =
        function () {

            console.error(
                "Unable to load saved document image."
            );
        };
}


/* =========================================================
   LOAD SAVED SELFIE
========================================================= */

function loadSavedSelfie(
    imageUrl
) {

    if (
        !imageUrl ||
        !selfiePreview
    ) {
        return;
    }


    selfiePreview.src =
        imageUrl;


    selfiePreview.style.display =
        "block";


    showElement(
        selfiePreviewWrapper
    );
}


/* =========================================================
   AADHAAR UI
========================================================= */

function updateAadhaarUI(status) {

    const normalized =
        normalizeStatus(status);


    hideElement(
        aadhaarProcessing
    );

    hideElement(
        aadhaarFallback
    );

    hideElement(
        aadhaarOtpSection
    );

    hideElement(
        aadhaarSuccess
    );


    /* =====================================================
       VERIFIED
       IMPORTANT:
       Upload section remains visible.
       Images remain visible.
    ===================================================== */

    if (
        normalized === "VERIFIED"
    ) {

        showElement(
            aadhaarUploadSection
        );


        showElement(
            aadhaarSuccess
        );


        return;
    }


    /* =====================================================
       OTP SENT
    ===================================================== */

    if (
        normalized === "OTP_SENT"
    ) {

        hideElement(
            aadhaarUploadSection
        );


        showElement(
            aadhaarOtpSection
        );


        return;
    }


    /* =====================================================
       PROCESSING
    ===================================================== */

    if (
        normalized === "PROCESSING"
    ) {

        hideElement(
            aadhaarUploadSection
        );


        showElement(
            aadhaarProcessing
        );


        return;
    }


    /* =====================================================
       NEEDS REVIEW
    ===================================================== */

    if (
        normalized === "NEEDS_REVIEW"
    ) {

        showElement(
            aadhaarUploadSection
        );


        return;
    }


    /* =====================================================
       FAILED
    ===================================================== */

    if (
        normalized === "FAILED"
    ) {

        showElement(
            aadhaarUploadSection
        );


        showElement(
            aadhaarFallback
        );


        return;
    }


    /* =====================================================
       PENDING
    ===================================================== */

    showElement(
        aadhaarUploadSection
    );
}


/* =========================================================
   INITIAL STATE
========================================================= */

hideElement(
    aadhaarProcessing
);

hideElement(
    aadhaarFallback
);

hideElement(
    aadhaarOtpSection
);

hideElement(
    aadhaarSuccess
);


hideElement(
    panProcessing
);

hideElement(
    panFallback
);

hideElement(
    panSuccess
);


hideElement(
    selfieProcessing
);

hideElement(
    selfieSuccess
);

hideElement(
    selfieResult
);


/* =========================================================
   LOAD SAVED STATUS
========================================================= */

async function loadSavedStatus() {

    try {

        const response =
            await fetch(
                window.identityUrls
                    .verificationStatus,
                {
                    method: "GET",

                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest"
                    },

                    credentials:
                        "same-origin"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Status request failed"
            );
        }


        const result =
            await response.json();


        if (!result.success) {
            return;
        }


        /* =================================================
           STATUS BADGES
        ================================================= */

        updateStatusBadge(
            aadhaarStatus,
            result.aadhaar_status
        );


        updateStatusBadge(
            panStatus,
            result.pan_status
        );


        updateStatusBadge(
            selfieStatus,
            result.selfie_status
        );


        /* =================================================
           AADHAAR FRONT IMAGE
        ================================================= */

        if (
            result.aadhaar_front_url
        ) {

            loadSavedImage(
                result.aadhaar_front_url,
                aadhaarFront
            );
        }


        /* =================================================
           AADHAAR BACK IMAGE
        ================================================= */

        if (
            result.aadhaar_back_url
        ) {

            loadSavedImage(
                result.aadhaar_back_url,
                aadhaarBack
            );
        }


        /* =================================================
           PAN IMAGE
        ================================================= */

        if (
            result.pan_card_url
        ) {

            loadSavedImage(
                result.pan_card_url,
                panCardInput
            );
        }


        /* =================================================
           SELFIE IMAGE
        ================================================= */

        if (
            result.selfie_image_url
        ) {

            loadSavedSelfie(
                result.selfie_image_url
            );
        }


        /* =================================================
           AADHAAR UI
        ================================================= */

        updateAadhaarUI(
            result.aadhaar_status
        );


        /* =================================================
           PAN UI
        ================================================= */

        const currentPanStatus =
            normalizeStatus(
                result.pan_status
            );


        if (
            currentPanStatus === "VERIFIED"
        ) {

            /* IMPORTANT:
               Keep upload box visible */

            showElement(
                panUploadSection
            );

            hideElement(
                panProcessing
            );

            hideElement(
                panFallback
            );

            showElement(
                panSuccess
            );
        }

        else if (
            currentPanStatus === "PROCESSING"
        ) {

            hideElement(
                panUploadSection
            );

            showElement(
                panProcessing
            );
        }

        else {

            showElement(
                panUploadSection
            );
        }


        /* =================================================
           SELFIE UI
        ================================================= */

        const currentSelfieStatus =
            normalizeStatus(
                result.selfie_status
            );


        if (
            currentSelfieStatus === "VERIFIED"
        ) {

            showElement(
                selfieCameraSection
            );


            hideElement(
                selfieProcessing
            );


            hideElement(
                selfieResult
            );


            showElement(
                selfieSuccess
            );


            if (
                result.selfie_image_url
            ) {

                loadSavedSelfie(
                    result.selfie_image_url
                );
            }
        }


        else if (
            currentSelfieStatus === "PROCESSING"
        ) {

            showElement(
                selfieCameraSection
            );

            hideElement(
                selfieSuccess
            );
        }


        else {

            showElement(
                selfieCameraSection
            );
        }


        /* =================================================
           PROGRESS
        ================================================= */

        updateProgress(
            result
        );


        /* =================================================
           FINAL RESULT
        ================================================= */

        updateFinalResult(
            result
        );

    }

    catch (error) {

        console.error(
            "Unable to load verification status.",
            error
        );
    }
}


/* =========================================================
   PROGRESS
========================================================= */

function updateProgress(result) {

    const aadhaarVerified =
        result.aadhaar_verified === true ||
        normalizeStatus(
            result.aadhaar_status
        ) === "VERIFIED";


    const panVerified =
        result.pan_verified === true ||
        normalizeStatus(
            result.pan_status
        ) === "VERIFIED";


    const selfieVerified =
        result.selfie_verified === true ||
        normalizeStatus(
            result.selfie_status
        ) === "VERIFIED";


    let completed = 0;


    if (aadhaarVerified) {
        completed++;
    }


    if (panVerified) {
        completed++;
    }


    if (selfieVerified) {
        completed++;
    }


    const percentage =
        Math.round(
            (completed / 3) * 100
        );


    if (progressPercentage) {

        progressPercentage.textContent =
            percentage + "%";
    }


    if (progressFill) {

        progressFill.style.width =
            percentage + "%";
    }


    if (overallStatus) {

        if (
            completed === 3
        ) {

            overallStatus.textContent =
                "Verified";
        }

        else if (
            normalizeStatus(
                result.verification_status
            ) === "FAILED"
        ) {

            overallStatus.textContent =
                "Failed";
        }

        else if (
            normalizeStatus(
                result.verification_status
            ) === "NEEDS_REVIEW"
        ) {

            overallStatus.textContent =
                "Needs Review";
        }

        else {

            overallStatus.textContent =
                "In Progress";
        }
    }
}


/* =========================================================
   FINAL RESULT
========================================================= */

function updateFinalResult(result) {

    const score =
        Number(
            result.verification_score || 0
        );


    if (verificationScore) {

        verificationScore.textContent =
            score.toFixed(2) + "%";
    }


    const finalStatus =
        normalizeStatus(
            result.verification_status
        );


    if (
        finalStatus === "VERIFIED"
    ) {

        if (finalMessage) {

            finalMessage.textContent =
                "Identity verification completed successfully. All verification checks have been completed.";
        }


        if (finalIcon) {

            finalIcon.textContent =
                "✓";
        }
    }


    else if (
        finalStatus === "FAILED"
    ) {

        if (finalMessage) {

            finalMessage.textContent =
                "Identity verification failed. Please review the verification details.";
        }


        if (finalIcon) {

            finalIcon.textContent =
                "×";
        }
    }


    else if (
        finalStatus === "NEEDS_REVIEW"
    ) {

        if (finalMessage) {

            finalMessage.textContent =
                "Identity verification requires manual review.";
        }


        if (finalIcon) {

            finalIcon.textContent =
                "!";
        }
    }


    else {

        if (finalMessage) {

            finalMessage.textContent =
                "Complete Aadhaar, PAN and Live Selfie verification to finish identity verification.";
        }


        if (finalIcon) {

            finalIcon.textContent =
                "✓";
        }
    }
}


/* =========================================================
   NORMALIZE STATUS
========================================================= */

function normalizeStatus(status) {

    if (!status) {
        return "PENDING";
    }

    return String(status)
        .toUpperCase()
        .replace(/\s+/g, "_");
}


/* =========================================================
   DISPLAY STATUS
========================================================= */

function displayStatus(status) {

    const normalized =
        normalizeStatus(status);


    const statusMap = {

        VERIFIED: "Verified",

        PROCESSING: "Processing",

        OTP_SENT: "OTP Sent",

        NEEDS_REVIEW: "Needs Review",

        FAILED: "Failed",

        PENDING: "Pending"
    };


    return (
        statusMap[normalized] ||
        normalized
    );
}


/* =========================================================
   STATUS BADGE
========================================================= */

function updateStatusBadge(
    element,
    status
) {

    if (!element) {
        return;
    }


    const normalized =
        normalizeStatus(status);


    element.textContent =
        displayStatus(normalized);


    element.classList.remove(
        "verified",
        "processing",
        "failed",
        "pending",
        "review"
    );


    if (
        normalized === "VERIFIED"
    ) {

        element.classList.add(
            "verified"
        );
    }

    else if (
        normalized === "PROCESSING" ||
        normalized === "OTP_SENT"
    ) {

        element.classList.add(
            "processing"
        );
    }

    else if (
        normalized === "FAILED"
    ) {

        element.classList.add(
            "failed"
        );
    }

    else if (
        normalized === "NEEDS_REVIEW"
    ) {

        element.classList.add(
            "review"
        );
    }

    else {

        element.classList.add(
            "pending"
        );
    }
}


/* =========================================================
   GENERATE AADHAAR OTP
========================================================= */

async function generateAadhaarOtp() {

    if (
        !window.identityUrls ||
        !window.identityUrls.generateAadhaarOtp
    ) {

        showToast(
            "Aadhaar OTP URL is not configured.",
            "error"
        );

        return false;
    }


    try {

        updateStatusBadge(
            aadhaarStatus,
            "PROCESSING"
        );


        const response =
            await fetch(
                window.identityUrls
                    .generateAadhaarOtp,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken":
                            getCSRFToken(),

                        "X-Requested-With":
                            "XMLHttpRequest"
                    },

                    credentials:
                        "same-origin"
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message ||
                "OTP request failed."
            );
        }


        if (result.success) {

            updateStatusBadge(
                aadhaarStatus,
                "OTP_SENT"
            );


            showElement(
                aadhaarOtpSection
            );


            hideElement(
                aadhaarProcessing
            );


            hideElement(
                aadhaarSuccess
            );


            showToast(
                result.message ||
                "Aadhaar OTP sent successfully.",
                "success"
            );


            await loadSavedStatus();


            return true;
        }


        updateStatusBadge(
            aadhaarStatus,
            "FAILED"
        );


        showToast(
            result.message ||
            "Unable to send Aadhaar OTP.",
            "error"
        );


        return false;

    }

    catch (error) {

        console.error(
            "Aadhaar OTP generation error:",
            error
        );


        updateStatusBadge(
            aadhaarStatus,
            "FAILED"
        );


        showToast(
            error.message ||
            "Unable to send Aadhaar OTP.",
            "error"
        );


        return false;
    }
}


/* =========================================================
   AADHAAR PROCESS
========================================================= */

if (processAadhaarBtn) {

    processAadhaarBtn.addEventListener(
        "click",
        async function () {

            if (
                !aadhaarFront ||
                !aadhaarBack ||
                !aadhaarFront.files.length ||
                !aadhaarBack.files.length
            ) {

                showToast(
                    "Please upload both Aadhaar front and back images.",
                    "error"
                );

                return;
            }


            const formData =
                new FormData();


            formData.append(
                "aadhaar_front",
                aadhaarFront.files[0]
            );


            formData.append(
                "aadhaar_back",
                aadhaarBack.files[0]
            );


            hideElement(
                aadhaarUploadSection
            );


            showElement(
                aadhaarProcessing
            );


            try {

                const response =
                    await fetch(
                        window.identityUrls
                            .processAadhaar,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCSRFToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            body: formData,

                            credentials:
                                "same-origin"
                        }
                    );


                const result =
                    await response.json();


                hideElement(
                    aadhaarProcessing
                );


                if (result.success) {

                    const status =
                        normalizeStatus(
                            result.aadhaar_status ||
                            result.status
                        );


                    if (
                        status === "VERIFIED"
                    ) {

                        updateStatusBadge(
                            aadhaarStatus,
                            "VERIFIED"
                        );


                        updateAadhaarUI(
                            "VERIFIED"
                        );


                        showToast(
                            "Aadhaar verified successfully.",
                            "success"
                        );
                    }

                    else {

                        updateStatusBadge(
                            aadhaarStatus,
                            "PROCESSING"
                        );


                        showToast(
                            "Aadhaar OCR completed. Sending OTP...",
                            "info"
                        );


                        const otpSent =
                            await generateAadhaarOtp();


                        if (!otpSent) {

                            showElement(
                                aadhaarUploadSection
                            );

                            showElement(
                                aadhaarFallback
                            );
                        }
                    }


                    await loadSavedStatus();

                }

                else {

                    showElement(
                        aadhaarFallback
                    );


                    hideElement(
                        aadhaarSuccess
                    );


                    showElement(
                        aadhaarUploadSection
                    );


                    updateStatusBadge(
                        aadhaarStatus,
                        "FAILED"
                    );


                    showToast(
                        result.message ||
                        "Aadhaar processing failed.",
                        "error"
                    );
                }

            }

            catch (error) {

                console.error(
                    "Aadhaar processing error:",
                    error
                );


                hideElement(
                    aadhaarProcessing
                );


                showElement(
                    aadhaarUploadSection
                );


                hideElement(
                    aadhaarSuccess
                );


                showToast(
                    "Unable to process Aadhaar.",
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   MANUAL AADHAAR
========================================================= */

if (saveManualAadhaarBtn) {

    saveManualAadhaarBtn.addEventListener(
        "click",
        async function () {

            const input =
                document.getElementById(
                    "manualAadhaar"
                );


            const aadhaar =
                input
                    ? input.value.trim()
                    : "";


            if (
                !/^\d{12}$/.test(aadhaar)
            ) {

                showToast(
                    "Enter a valid 12-digit Aadhaar number.",
                    "error"
                );

                return;
            }


            const formData =
                new FormData();


            formData.append(
                "aadhaar_number",
                aadhaar
            );


            try {

                const response =
                    await fetch(
                        window.identityUrls
                            .saveManualAadhaar,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCSRFToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            body: formData,

                            credentials:
                                "same-origin"
                        }
                    );


                const result =
                    await response.json();


                if (result.success) {

                    showToast(
                        result.message ||
                        "Aadhaar information saved.",
                        "success"
                    );


                    await loadSavedStatus();

                }

                else {

                    showToast(
                        result.message ||
                        "Unable to save Aadhaar.",
                        "error"
                    );
                }

            }

            catch (error) {

                console.error(
                    "Manual Aadhaar error:",
                    error
                );


                showToast(
                    "Unable to save Aadhaar.",
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   AADHAAR OTP VERIFY
========================================================= */

if (verifyAadhaarOtpBtn) {

    verifyAadhaarOtpBtn.addEventListener(
        "click",
        async function () {

            const otpInput =
                document.getElementById(
                    "aadhaarOtp"
                );


            const otp =
                otpInput
                    ? otpInput.value.trim()
                    : "";


            if (
                !/^\d{6}$/.test(otp)
            ) {

                showToast(
                    "Enter a valid 6-digit OTP.",
                    "error"
                );

                return;
            }


            const formData =
                new FormData();


            formData.append(
                "otp",
                otp
            );


            try {

                updateStatusBadge(
                    aadhaarStatus,
                    "PROCESSING"
                );


                const response =
                    await fetch(
                        window.identityUrls
                            .verifyAadhaarOtp,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCSRFToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            body: formData,

                            credentials:
                                "same-origin"
                        }
                    );


                const result =
                    await response.json();


                if (result.success) {

                    const status =
                        normalizeStatus(
                            result.aadhaar_status ||
                            result.status
                        );


                    updateStatusBadge(
                        aadhaarStatus,
                        status
                    );


                    if (
                        status === "VERIFIED"
                    ) {

                        updateAadhaarUI(
                            "VERIFIED"
                        );


                        showToast(
                            "Aadhaar verified successfully.",
                            "success"
                        );
                    }


                    else if (
                        status === "NEEDS_REVIEW"
                    ) {

                        updateAadhaarUI(
                            "NEEDS_REVIEW"
                        );


                        showToast(
                            "Aadhaar details require manual review.",
                            "info"
                        );
                    }


                    else {

                        updateAadhaarUI(
                            status
                        );


                        showToast(
                            result.message ||
                            "Aadhaar verification could not be completed.",
                            "error"
                        );
                    }


                    await loadSavedStatus();

                }

                else {

                    updateStatusBadge(
                        aadhaarStatus,
                        "FAILED"
                    );


                    updateAadhaarUI(
                        "FAILED"
                    );


                    showToast(
                        result.message ||
                        "Aadhaar OTP verification failed.",
                        "error"
                    );
                }

            }

            catch (error) {

                console.error(
                    "Aadhaar OTP verification error:",
                    error
                );


                updateStatusBadge(
                    aadhaarStatus,
                    "FAILED"
                );


                updateAadhaarUI(
                    "FAILED"
                );


                showToast(
                    "Unable to verify Aadhaar OTP.",
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   PAN PROCESS
========================================================= */

if (processPanBtn) {

    processPanBtn.addEventListener(
        "click",
        async function () {

            if (
                !panCardInput ||
                !panCardInput.files.length
            ) {

                showToast(
                    "Please upload your PAN card image.",
                    "error"
                );

                return;
            }


            const formData =
                new FormData();


            formData.append(
                "pan_card",
                panCardInput.files[0]
            );


            hideElement(
                panUploadSection
            );


            showElement(
                panProcessing
            );


            try {

                const response =
                    await fetch(
                        window.identityUrls
                            .processPan,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCSRFToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            body: formData,

                            credentials:
                                "same-origin"
                        }
                    );


                const result =
                    await response.json();


                hideElement(
                    panProcessing
                );


                if (result.success) {

                    const status =
                        normalizeStatus(
                            result.pan_status ||
                            result.status
                        );


                    updateStatusBadge(
                        panStatus,
                        status
                    );


                    if (
                        status === "VERIFIED"
                    ) {

                        /* IMPORTANT:
                           Keep PAN image box visible */

                        showElement(
                            panUploadSection
                        );


                        hideElement(
                            panFallback
                        );


                        showElement(
                            panSuccess
                        );


                        showToast(
                            "PAN verified successfully.",
                            "success"
                        );
                    }

                    else {

                        showElement(
                            panUploadSection
                        );


                        hideElement(
                            panSuccess
                        );


                        showElement(
                            panFallback
                        );
                    }


                    await loadSavedStatus();

                }

                else {

                    showElement(
                        panUploadSection
                    );


                    showElement(
                        panFallback
                    );


                    hideElement(
                        panSuccess
                    );


                    updateStatusBadge(
                        panStatus,
                        "FAILED"
                    );


                    showToast(
                        result.message ||
                        "PAN verification failed.",
                        "error"
                    );
                }

            }

            catch (error) {

                console.error(
                    "PAN processing error:",
                    error
                );


                hideElement(
                    panProcessing
                );


                showElement(
                    panUploadSection
                );


                showToast(
                    "Unable to process PAN.",
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   MANUAL PAN
========================================================= */

if (verifyManualPanBtn) {

    verifyManualPanBtn.addEventListener(
        "click",
        async function () {

            const panInput =
                document.getElementById(
                    "manualPan"
                );


            const nameInput =
                document.getElementById(
                    "manualPanName"
                );


            const pan =
                panInput
                    ? panInput.value
                        .trim()
                        .toUpperCase()
                    : "";


            const name =
                nameInput
                    ? nameInput.value.trim()
                    : "";


            if (
                !/^[A-Z]{5}[0-9]{4}[A-Z]$/
                    .test(pan)
            ) {

                showToast(
                    "Enter a valid PAN number.",
                    "error"
                );

                return;
            }


            if (!name) {

                showToast(
                    "Enter applicant name.",
                    "error"
                );

                return;
            }


            const formData =
                new FormData();


            formData.append(
                "pan_number",
                pan
            );


            formData.append(
                "applicant_name",
                name
            );


            try {

                const response =
                    await fetch(
                        window.identityUrls
                            .verifyManualPan,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCSRFToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            body: formData,

                            credentials:
                                "same-origin"
                        }
                    );


                const result =
                    await response.json();


                if (result.success) {

                    updateStatusBadge(
                        panStatus,
                        "VERIFIED"
                    );


                    showElement(
                        panUploadSection
                    );


                    showElement(
                        panSuccess
                    );


                    hideElement(
                        panFallback
                    );


                    showToast(
                        "PAN verified successfully.",
                        "success"
                    );


                    await loadSavedStatus();

                }

                else {

                    showToast(
                        result.message ||
                        "PAN verification failed.",
                        "error"
                    );
                }

            }

            catch (error) {

                console.error(
                    "Manual PAN error:",
                    error
                );


                showToast(
                    "Unable to verify PAN.",
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   START CAMERA
========================================================= */

if (startCameraBtn) {

    startCameraBtn.addEventListener(
        "click",
        async function () {

            try {

                if (cameraStream) {

                    cameraStream
                        .getTracks()
                        .forEach(
                            track =>
                                track.stop()
                        );
                }


                cameraStream =
                    await navigator.mediaDevices
                        .getUserMedia({

                            video: {
                                facingMode:
                                    "user"
                            },

                            audio: false
                        });


                selfieVideo.srcObject =
                    cameraStream;


                selfieCameraMessage.textContent =
                    "Camera is active";


                showToast(
                    "Camera started.",
                    "success"
                );

            }

            catch (error) {

                console.error(
                    "Camera error:",
                    error
                );


                selfieCameraMessage.textContent =
                    "Camera access denied";


                showToast(
                    "Please allow camera permission.",
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   CAPTURE SELFIE
========================================================= */

if (captureSelfieBtn) {

    captureSelfieBtn.addEventListener(
        "click",
        function () {

            if (
                !cameraStream ||
                !selfieVideo.srcObject
            ) {

                showToast(
                    "Please start the camera first.",
                    "error"
                );

                return;
            }


            if (
                selfieVideo.readyState < 2
            ) {

                showToast(
                    "Camera is not ready yet.",
                    "error"
                );

                return;
            }


            const width =
                selfieVideo.videoWidth;

            const height =
                selfieVideo.videoHeight;


            if (
                !width ||
                !height
            ) {

                showToast(
                    "Unable to capture camera frame.",
                    "error"
                );

                return;
            }


            selfieCanvas.width =
                width;

            selfieCanvas.height =
                height;


            const context =
                selfieCanvas.getContext(
                    "2d"
                );


            context.drawImage(
                selfieVideo,
                0,
                0,
                width,
                height
            );


            selfieCanvas.toBlob(
                function (blob) {

                    if (!blob) {

                        showToast(
                            "Unable to capture selfie.",
                            "error"
                        );

                        return;
                    }


                    selfieBlob =
                        blob;


                    if (
                        selfiePreviewUrl
                    ) {

                        URL.revokeObjectURL(
                            selfiePreviewUrl
                        );
                    }


                    selfiePreviewUrl =
                        URL.createObjectURL(
                            selfieBlob
                        );


                    selfiePreview.src =
                        selfiePreviewUrl;


                    selfiePreview.style.display =
                        "block";


                    showElement(
                        selfiePreviewWrapper
                    );


                    selfieCameraMessage.textContent =
                        "Selfie captured";


                    showToast(
                        "Selfie captured successfully.",
                        "success"
                    );

                },
                "image/jpeg",
                0.92
            );
        }
    );
}


/* =========================================================
   RETAKE SELFIE
========================================================= */

if (retakeSelfieBtn) {

    retakeSelfieBtn.addEventListener(
        "click",
        function () {

            selfieBlob = null;


            if (selfiePreviewUrl) {

                URL.revokeObjectURL(
                    selfiePreviewUrl
                );

                selfiePreviewUrl =
                    null;
            }


            selfiePreview.src =
                "";


            hideElement(
                selfiePreviewWrapper
            );


            hideElement(
                selfieSuccess
            );


            hideElement(
                selfieResult
            );


            showElement(
                selfieCameraSection
            );


            selfieCameraMessage.textContent =
                cameraStream
                    ? "Camera is active"
                    : "Camera is not started";


            showToast(
                "You can capture a new selfie.",
                "info"
            );
        }
    );
}


/* =========================================================
   VERIFY SELFIE
========================================================= */

if (verifySelfieBtn) {

    verifySelfieBtn.addEventListener(
        "click",
        async function () {

            if (!selfieBlob) {

                showToast(
                    "Please capture a selfie first.",
                    "error"
                );

                return;
            }


            const formData =
                new FormData();


            formData.append(
                "selfie",
                selfieBlob,
                "live_selfie.jpg"
            );


            hideElement(
                selfieCameraSection
            );


            showElement(
                selfieProcessing
            );


            try {

                const response =
                    await fetch(
                        window.identityUrls
                            .processLiveSelfie,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCSRFToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            body: formData,

                            credentials:
                                "same-origin"
                        }
                    );


                const result =
                    await response.json();


                hideElement(
                    selfieProcessing
                );


                if (result.success) {

                    const status =
                        normalizeStatus(
                            result.selfie_status ||
                            result.status
                        );


                    updateStatusBadge(
                        selfieStatus,
                        status
                    );


                    if (
                        status === "VERIFIED"
                    ) {

                        showElement(
                            selfieCameraSection
                        );


                        showElement(
                            selfieSuccess
                        );


                        hideElement(
                            selfieResult
                        );


                        if (
                            selfiePreviewUrl
                        ) {

                            selfiePreview.src =
                                selfiePreviewUrl;

                            showElement(
                                selfiePreviewWrapper
                            );
                        }


                        showToast(
                            "Selfie verified successfully.",
                            "success"
                        );

                    }

                    else {

                        showElement(
                            selfieCameraSection
                        );


                        hideElement(
                            selfieSuccess
                        );


                        showElement(
                            selfieResult
                        );


                        if (
                            selfieResultMessage
                        ) {

                            selfieResultMessage.textContent =
                                result.message ||
                                result.selfie_verification_message ||
                                "Selfie verification could not be completed.";
                        }
                    }


                    await loadSavedStatus();

                }

                else {

                    showElement(
                        selfieCameraSection
                    );


                    showElement(
                        selfieResult
                    );


                    if (
                        selfieResultMessage
                    ) {

                        selfieResultMessage.textContent =
                            result.message ||
                            "Selfie verification failed.";
                    }


                    showToast(
                        result.message ||
                        "Selfie verification failed.",
                        "error"
                    );
                }

            }

            catch (error) {

                console.error(
                    "Selfie verification error:",
                    error
                );


                hideElement(
                    selfieProcessing
                );


                showElement(
                    selfieCameraSection
                );


                showToast(
                    "Unable to verify selfie.",
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   STOP CAMERA + CLEANUP
========================================================= */

window.addEventListener(
    "beforeunload",
    function () {

        if (cameraStream) {

            cameraStream
                .getTracks()
                .forEach(
                    track =>
                        track.stop()
                );
        }


        document
            .querySelectorAll(
                ".box-document-preview[data-preview-url]"
            )
            .forEach(function (image) {

                URL.revokeObjectURL(
                    image.dataset.previewUrl
                );
            });


        if (selfiePreviewUrl) {

            URL.revokeObjectURL(
                selfiePreviewUrl
            );
        }
    }
);


/* =========================================================
   INITIAL LOAD
========================================================= */

loadSavedStatus();

});