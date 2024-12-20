document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.needs-validation');
    const formAlert = document.getElementById('formAlert');
    const reCAPTCHAAlert = document.getElementById('reCAPTCHAAlert');

    form.addEventListener('submit', function (event) {
        const isFormValid = form.checkValidity();
        const recaptchaValue = grecaptcha.getResponse();

        if (!isFormValid || recaptchaValue === "") {
            event.preventDefault();
            event.stopPropagation();

            if (!isFormValid) {
                form.classList.add('was-validated');
                formAlert.style.display = 'block';
            } else {
                formAlert.style.display = 'none';
            }

            if (recaptchaValue === "") {
                reCAPTCHAAlert.style.display = 'block';
            } else {
                reCAPTCHAAlert.style.display = 'none';
            }
            grecaptcha.reset();

        } else {
            formAlert.style.display = 'none';
            reCAPTCHAAlert.style.display = 'none';
            // Form submission occurs now
        }
    });
});
