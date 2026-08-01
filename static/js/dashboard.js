// =========================================
// PROFILE IMAGE PREVIEW
// =========================================

const profileInput = document.getElementById("profileImage");
const profilePreview = document.getElementById("profileImagePreview");

if (profileInput && profilePreview) {

    profileInput.addEventListener("change", function () {

        const file = this.files[0];

        if (file) {

            profilePreview.src = URL.createObjectURL(file);

        }

    });

}

// =========================================
// ANIMATED COUNTERS
// =========================================

const counters = document.querySelectorAll(".stat-card h2");

counters.forEach(counter => {

    const text = counter.innerText;

    if (text.includes("%")) {

        const target = parseInt(text);

        animate(counter, target, "%");

    } else {

        const target = parseInt(text);

        animate(counter, target, "");

    }

});

function animate(element, target, suffix) {

    let count = 0;

    const speed = Math.max(1, Math.ceil(target / 60));

    const interval = setInterval(() => {

        count += speed;

        if (count >= target) {

            count = target;

            clearInterval(interval);

        }

        element.innerText = count + suffix;

    }, 25);

}

// =========================================
// ACTIVE SIDEBAR ITEM
// =========================================

const menuItems = document.querySelectorAll(".menu li");

menuItems.forEach(item => {

    item.addEventListener("click", () => {

        menuItems.forEach(i => i.classList.remove("active"));

        item.classList.add("active");

    });

});

// =========================================
// MODEL CARD HOVER EFFECT
// =========================================

const modelCards = document.querySelectorAll(".model-card");

modelCards.forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-10px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0px)";

    });

});