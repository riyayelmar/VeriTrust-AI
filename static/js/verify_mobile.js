document.addEventListener("DOMContentLoaded", function () {

    const otpInputs =
        document.querySelectorAll(".otp-input");

    const otpValue =
        document.getElementById("otpValue");

    const otpForm =
        document.getElementById("otpForm");


    // =====================================================
    // OTP INPUT HANDLING
    // =====================================================

    otpInputs.forEach(function (input, index) {

        input.addEventListener("input", function () {

            this.value =
                this.value.replace(/\D/g, "");

            if (
                this.value &&
                index < otpInputs.length - 1
            ) {

                otpInputs[index + 1].focus();

            }

            updateOTP();

        });


        // =================================================
        // BACKSPACE
        // =================================================

        input.addEventListener("keydown", function (event) {

            if (
                event.key === "Backspace" &&
                !this.value &&
                index > 0
            ) {

                otpInputs[index - 1].focus();

            }

        });


        // =================================================
        // PASTE OTP
        // =================================================

        input.addEventListener("paste", function (event) {

            event.preventDefault();

            const pasted =
                event.clipboardData
                    .getData("text")
                    .replace(/\D/g, "")
                    .slice(0, 6);


            pasted.split("").forEach(
                function (digit, i) {

                    if (otpInputs[i]) {
                        otpInputs[i].value = digit;
                    }

                }
            );


            updateOTP();

            if (otpInputs[pasted.length - 1]) {

                otpInputs[
                    Math.min(
                        pasted.length,
                        otpInputs.length - 1
                    )
                ].focus();

            }

        });

    });


    // =====================================================
    // UPDATE HIDDEN OTP
    // =====================================================

    function updateOTP() {

        let otp = "";

        otpInputs.forEach(function (input) {

            otp += input.value;

        });

        otpValue.value = otp;

    }


    // =====================================================
    // FORM VALIDATION
    // =====================================================

    if (otpForm) {

        otpForm.addEventListener(
            "submit",
            function (event) {

                const clickedButton =
                    document.activeElement;


                // Resend button
                if (
                    clickedButton &&
                    clickedButton.value === "resend"
                ) {

                    return;

                }


                updateOTP();


                if (otpValue.value.length !== 6) {

                    event.preventDefault();

                    alert(
                        "Please enter the complete 6-digit OTP."
                    );

                    return;

                }

            }
        );

    }

});
