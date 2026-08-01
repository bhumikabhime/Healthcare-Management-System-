document.addEventListener("DOMContentLoaded", function () {

    function setupPasswordToggle(inputId, toggleId) {

        const input = document.getElementById(inputId);
        const toggle = document.getElementById(toggleId);

        if (!input || !toggle) return;

        toggle.addEventListener("click", function () {

            if (input.type === "password") {

                input.type = "text";

                toggle.classList.replace("fa-eye", "fa-eye-slash");

            } else {

                input.type = "password";

                toggle.classList.replace("fa-eye-slash", "fa-eye");

            }

        });

    }

    setupPasswordToggle("password", "togglePassword");
    setupPasswordToggle("confirmPassword", "toggleConfirmPassword");

    document.body.style.opacity = "0";

    setTimeout(() => {

        document.body.style.transition = "opacity .6s ease";

        document.body.style.opacity = "1";

    }, 100);

});
const input = document.getElementById("profileImage");

const preview = document.getElementById("profilePreview");

if(input){

    input.addEventListener("change",function(){

        const file=this.files[0];

        if(file){

            preview.src=URL.createObjectURL(file);

        }

    });

}