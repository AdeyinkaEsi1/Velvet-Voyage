

async function isLoggedIn() {
    try {
        const response = await fetch("/auth/is_authenticated", {
            method: "GET",
            credentials: "include",
            headers: {
                "Accept": "application/json"
            }
        });


        if (response.status === 401) {
            console.log("Token expired or user is not authenticated.");
            window.location.href = "/auth/login?message=Session expired. Please log in again.";
            return false;
        }
        if (response.ok) {
            const data = await response.json();
            console.log("User authenticated:", data);
            return true;
        } else {
            return false;
        }
    } catch (error) {
        console.error("Error checking auth status:", error);
        return false;
    }
}


document.addEventListener("DOMContentLoaded", async function () {
    const signInLink = document.getElementById("sign-in-link");
    const registerLink = document.getElementById("register-link");
    const dashboardLink = document.getElementById("dashboard-link");
    const signOutLink = document.getElementById("sign-out-link");

    const loggedIn = await isLoggedIn();

    if (loggedIn) {
        signInLink.classList.add('hidden')
        registerLink.classList.add('hidden')
        dashboardLink.classList.remove('hidden')
        signOutLink.classList.remove('hidden')
    } else {
        dashboardLink.classList.add('hidden')
        signOutLink.classList.add('hidden')
        signInLink.classList.remove('hidden')
        registerLink.classList.remove('hidden')
    }

    signOutLink.addEventListener("click", async function (e) {
        e.preventDefault();

        try {
            const response = await fetch("/logout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include"
            });

            if (!response.ok) {
                throw new Error("Logout failed. Please try again.");
            }

            window.location.reload();
        } catch (error) {
            console.error("Logout error:", error);
            alert(error.message);
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const loginModal = document.getElementById("loginModal");
    const closeModalBtn = document.querySelector(".modal-close-btn");

    if (!localStorage.getItem("modalShown")) {
        setTimeout(() => {
            loginModal.classList.add("show");
            localStorage.setItem("modalShown", "true");
        }, 3000);
    }

    closeModalBtn.addEventListener("click", function () {
        loginModal.classList.remove("show");
    });

    window.addEventListener("click", function (event) {
        if (event.target === loginModal) {
            loginModal.classList.remove("show");
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            loginModal.classList.remove("show");
        }
    });
});

// document.addEventListener('DOMContentLoaded', () => {
//     const bars = document.querySelector('.fa-bars')
//     const nav = document.querySelector('.nav')

//     if (nav && bars) {
//         console.log('bars and nav are present')
//         bars.addEventListener('click', () => {
//             console.log('clicked')
//             nav.classList.toggle('translate-x-full')
//             document.addEventListener('click', event => {
//                 if (
//                     !bars.contains(event.target) &&
//                     !nav.classList.contains('translate-x-full')
//                 ) {
//                     nav.classList.add('translate-x-full')
//                 }
//             })
//         })
//     } else {
//         console.log('bars or nav not found on this page')
//     }
// })


// function menuBar() {
//     alert('hi')
//     const bars = document.querySelector('.fa-bars');
//     const nav = document.querySelector('.nav');

//     if (nav && bars) {
//         console.log('bars and nav are present')
//         bars.addEventListener('click', () => {
//             console.log('clicked')
//             nav.classList.toggle('translate-x-full')
//             document.addEventListener('click', event => {
//                 if (
//                     !bars.contains(event.target) &&
//                     !nav.classList.contains('translate-x-full')
//                 ) {
//                     nav.classList.add('translate-x-full')
//                 }
//             })
//         })
//     } else {
//         console.log('bars or nav not found on this page')
//     }
// };
// menuBar();
