// ============================================================
// PRISM AI — GLOBAL SCRIPT
// ============================================================

// ------------------------------------------------------------
// THEME
// ------------------------------------------------------------

function applyTheme() {
    const savedTheme = localStorage.getItem("prismTheme");
    const body = document.body;
    const button = document.getElementById("themeToggle");

    if (!body) return;

    if (savedTheme === "light") {
        body.classList.add("light-theme");

        if (button) {
            button.textContent = "🌙 Dark";
        }
    } else {
        body.classList.remove("light-theme");

        if (button) {
            button.textContent = "☀️ Light";
        }
    }
}


function toggleTheme() {
    const body = document.body;
    const button = document.getElementById("themeToggle");

    if (!body) return;

    body.classList.toggle("light-theme");

    if (body.classList.contains("light-theme")) {
        localStorage.setItem("prismTheme", "light");

        if (button) {
            button.textContent = "🌙 Dark";
        }
    } else {
        localStorage.setItem("prismTheme", "dark");

        if (button) {
            button.textContent = "☀️ Light";
        }
    }
}


// ------------------------------------------------------------
// LOGIN STATUS
// ------------------------------------------------------------

function updateLoginStatus() {
    const loggedIn =
        localStorage.getItem("prismLoggedIn") === "true";

    const userName =
        localStorage.getItem("prismUserName") || "Prism User";

    const loginButtons =
        document.querySelectorAll(".login-btn, .login");

    loginButtons.forEach(function (button) {

        if (loggedIn) {

            button.textContent = "👤 " + userName;

            button.href = "#";

            button.onclick = function (event) {
                event.preventDefault();
                showAccountMenu();
            };

        } else {

            button.textContent = "Sign In / Log In";

            button.href = "login.html";

            button.onclick = null;
        }
    });
}


// ------------------------------------------------------------
// ACCOUNT PANEL
// ------------------------------------------------------------

function createAccountPanel() {

    if (document.getElementById("prismAccountPanel")) {
        return;
    }

    const overlay = document.createElement("div");

    overlay.id = "prismAccountPanel";

    overlay.innerHTML = `
        <div class="prism-account-overlay">
            <div class="prism-account-card">

                <button
                    class="prism-account-close"
                    onclick="closeAccountMenu()"
                    aria-label="Close"
                >
                    ×
                </button>

                <div class="prism-account-avatar">
                    👤
                </div>

                <div class="prism-account-title">
                    Welcome back
                </div>

                <div
                    class="prism-account-name"
                    id="prismAccountName"
                >
                </div>

                <div class="prism-account-status">
                    ✦ Prism AI account active
                </div>

                <button
                    class="prism-account-explore"
                    onclick="goToFeatures()"
                >
                    Explore Prism AI →
                </button>

                <button
                    class="prism-account-logout"
                    onclick="logoutPrism()"
                >
                    Log Out
                </button>

            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    addAccountStyles();
}


// ------------------------------------------------------------
// SHOW ACCOUNT
// ------------------------------------------------------------

function showAccountMenu() {

    const menu =
        document.getElementById("accountMenu");

    const name =
        localStorage.getItem(
            "prismUserName"
        ) || "Prism User";

    const email =
        localStorage.getItem(
            "prismUserEmail"
        ) || "No email";

    const nameElement =
        document.getElementById("accountName");

    const emailElement =
        document.getElementById("accountEmail");

    if (nameElement) {
        nameElement.textContent = name;
    }

    if (emailElement) {
        emailElement.textContent = email;
    }

    if (menu) {
        menu.classList.toggle("show");
    }
}


/* =========================================
   SEE PROFILE
========================================= */

function seeProfile() {

    const name =
        localStorage.getItem(
            "prismUserName"
        ) || "Prism User";

    const email =
        localStorage.getItem(
            "prismUserEmail"
        ) || "No email";

    alert(
        "👤 Your Prism AI Profile\n\n" +
        "Name: " + name + "\n" +
        "Email: " + email
    );
}


/* =========================================
   EDIT PROFILE
========================================= */

function editProfile() {

    const name =
        localStorage.getItem(
            "prismUserName"
        ) || "Prism User";

    const newName =
        prompt(
            "Enter your new name:",
            name
        );

    if (
        newName &&
        newName.trim()
    ) {

        localStorage.setItem(
            "prismUserName",
            newName.trim()
        );

        updateLoginStatus();

        const menu =
            document.getElementById(
                "accountMenu"
            );

        if (menu) {
            menu.classList.remove("show");
        }
    }
}


/* =========================================
   LOG OUT
========================================= */

function logoutUser() {

    const confirmed =
        confirm(
            "Are you sure you want to log out?"
        );

    if (!confirmed) {
        return;
    }

    localStorage.removeItem(
        "prismLoggedIn"
    );

    localStorage.removeItem(
        "prismUserName"
    );

    localStorage.removeItem(
        "prismUserEmail"
    );

    localStorage.removeItem(
        "prismUserId"
    );

    window.location.href =
        "index.html";
}


/* =========================================
   CLOSE ACCOUNT MENU
   WHEN CLICKING OUTSIDE
========================================= */

document.addEventListener(
    "click",
    function(event) {

        const wrapper =
            document.querySelector(
                ".account-wrapper"
            );

        const menu =
            document.getElementById(
                "accountMenu"
            );

        if (
            wrapper &&
            menu &&
            !wrapper.contains(event.target)
        ) {

            menu.classList.remove("show");
        }

    }
);


// ------------------------------------------------------------
// CLOSE ACCOUNT
// ------------------------------------------------------------

function closeAccountMenu() {

    const panel =
        document.getElementById("prismAccountPanel");

    if (panel) {
        panel.classList.remove("active");
    }
}


// ------------------------------------------------------------
// LOGOUT
// ------------------------------------------------------------

function logoutPrism() {

    localStorage.removeItem("prismLoggedIn");
    localStorage.removeItem("prismUserName");

    closeAccountMenu();

    updateLoginStatus();

    setTimeout(function () {
        alert("You have been logged out of Prism AI.");
        window.location.href = "index.html";
    }, 150);
}


// ------------------------------------------------------------
// GO TO FEATURES
// ------------------------------------------------------------

function goToFeatures() {

    window.location.href = "features.html";
}


// ------------------------------------------------------------
// GET INITIAL
// ------------------------------------------------------------

function getInitial(name) {

    if (!name) {
        return "P";
    }

    return name
        .trim()
        .charAt(0)
        .toUpperCase();
}


// ------------------------------------------------------------
// ESCAPE HTML
// ------------------------------------------------------------

function escapeHTML(text) {

    if (!text) {
        return "";
    }

    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ------------------------------------------------------------
// ACCOUNT PANEL STYLES
// ------------------------------------------------------------

function addAccountStyles() {

    if (document.getElementById("prismAccountStyles")) {
        return;
    }

    const style = document.createElement("style");

    style.id = "prismAccountStyles";

    style.textContent = `
        .prism-account-overlay {
            position: fixed;
            inset: 0;
            z-index: 99999;

            display: flex;
            align-items: center;
            justify-content: center;

            padding: 20px;

            background: rgba(0, 0, 0, 0.72);

            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }

        .prism-account-card {
            position: relative;

            width: min(420px, 100%);

            padding: 42px 30px 30px;

            text-align: center;

            border-radius: 28px;

            border: 1px solid rgba(255, 255, 255, 0.14);

            background:
                linear-gradient(
                    145deg,
                    rgba(25, 25, 50, 0.98),
                    rgba(10, 10, 25, 0.98)
                );

            box-shadow:
                0 30px 90px rgba(0, 0, 0, 0.55),
                0 0 45px rgba(120, 80, 255, 0.18);

            color: white;

            animation: prismAccountIn 0.28s ease;
        }

        .light-theme .prism-account-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.98),
                    rgba(242, 242, 255, 0.98)
                );

            color: #17172a;

            border-color: rgba(50, 50, 100, 0.12);
        }

        .prism-account-close {
            position: absolute;

            top: 14px;
            right: 16px;

            width: 36px;
            height: 36px;

            border: 0;
            border-radius: 50%;

            background: rgba(255, 255, 255, 0.08);

            color: inherit;

            font-size: 25px;

            cursor: pointer;

            transition: 0.2s ease;
        }

        .prism-account-close:hover {
            transform: rotate(90deg);

            background: rgba(255, 255, 255, 0.16);
        }

        .prism-account-avatar {
            width: 82px;
            height: 82px;

            margin: 0 auto 18px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            font-size: 34px;

            background:
                linear-gradient(
                    135deg,
                    #7c3aed,
                    #06b6d4
                );

            box-shadow:
                0 0 35px rgba(124, 58, 237, 0.35);
        }

        .prism-account-title {
            font-size: 27px;
            font-weight: 800;

            margin-bottom: 8px;
        }

        .prism-account-name {
            font-size: 18px;
            font-weight: 600;

            opacity: 0.82;

            margin-bottom: 15px;
        }

        .prism-account-status {
            display: inline-block;

            padding: 8px 14px;

            margin-bottom: 25px;

            border-radius: 999px;

            font-size: 13px;

            background: rgba(124, 58, 237, 0.12);

            color: #a78bfa;
        }

        .prism-account-explore,
        .prism-account-logout {
            width: 100%;

            padding: 14px 18px;

            border-radius: 14px;

            font-size: 15px;
            font-weight: 700;

            cursor: pointer;

            transition: 0.2s ease;
        }

        .prism-account-explore {
            border: 0;

            color: white;

            background:
                linear-gradient(
                    135deg,
                    #7c3aed,
                    #06b6d4
                );

            margin-bottom: 11px;
        }

        .prism-account-explore:hover {
            transform: translateY(-2px);

            box-shadow:
                0 12px 30px rgba(124, 58, 237, 0.25);
        }

        .prism-account-logout {
            border: 1px solid rgba(255, 255, 255, 0.12);

            color: inherit;

            background: rgba(255, 255, 255, 0.05);
        }

        .prism-account-logout:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        @keyframes prismAccountIn {

            from {
                opacity: 0;
                transform: translateY(18px) scale(0.96);
            }

            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }

        }

        @media (max-width: 500px) {

            .prism-account-card {
                padding: 38px 20px 22px;
            }

            .prism-account-title {
                font-size: 23px;
            }

        }
    `;

    document.head.appendChild(style);
}


// ------------------------------------------------------------
// STARTUP
// ------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {

    applyTheme();

    updateLoginStatus();

});