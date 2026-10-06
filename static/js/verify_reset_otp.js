document.addEventListener("DOMContentLoaded", function () {

    const inputs = document.querySelectorAll(".otp-input");
    const otpValue = document.getElementById("otpValue");
    const form = document.getElementById("otpForm");
    const verifyBtn = document.getElementById("verifyBtn");



    // ==========================================
    // UPDATE HIDDEN OTP
    // ==========================================

    function updateOTP() {

        let otp = "";

        inputs.forEach(function (input) {

            otp += input.value;

        });

        otpValue.value = otp;

    }



    // ==========================================
    // OTP INPUT
    // ==========================================

    inputs.forEach(function (input, index) {


        input.addEventListener("input", function () {

            // Only numbers

            this.value = this.value.replace(/\D/g, "");


            updateOTP();


            // Automatically move to next box

            if (this.value !== "" && index < inputs.length - 1) {

                inputs[index + 1].focus();

            }

        });



        // ======================================
        // BACKSPACE
        // ======================================

        input.addEventListener("keydown", function (event) {

            if (
                event.key === "Backspace" &&
                this.value === "" &&
                index > 0
            ) {

                inputs[index - 1].focus();

            }

        });


    });



    // ==========================================
    // PASTE FULL OTP
    // ==========================================

    inputs[0].addEventListener("paste", function (event) {

        event.preventDefault();


        const pastedOTP =
            event.clipboardData
                .getData("text")
                .replace(/\D/g, "")
                .slice(0, 6);


        pastedOTP.split("").forEach(function (digit, index) {

            if (inputs[index]) {

                inputs[index].value = digit;

            }

        });


        updateOTP();


        if (pastedOTP.length === 6) {

            inputs[5].focus();

        }

    });



    // ==========================================
    // VERIFY FORM
    // ==========================================

    form.addEventListener("submit", function (event) {

        updateOTP();


        /*
         * If Verify button clicked
         */

        if (
            event.submitter &&
            event.submitter.value === "verify"
        ) {

            if (otpValue.value.length !== 6) {

                event.preventDefault();

                alert("Please enter all 6 digits.");

                const emptyInput =
                    [...inputs].find(input => input.value === "");

                if (emptyInput) {

                    emptyInput.focus();

                }

                return;

            }

            verifyBtn.disabled = true;

            verifyBtn.innerHTML = `
                <span>Verifying...</span>
                <i class="fa-solid fa-spinner fa-spin"></i>
            `;

        }

    });


});