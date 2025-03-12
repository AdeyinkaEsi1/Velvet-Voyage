async function isLoggedIn() {
    try {
        const response = await fetch("/auth/is_authenticated", {
            method: "GET",
            credentials: "include" // Include cookies in the request
        });

        if (response.ok) {
            return true; // User is logged in
        } else {
            return false; // User is not logged in
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

    const loggedIn = await isLoggedIn()

    if (loggedIn) {
        signInLink.style.display = "none";
        registerLink.style.display = "none";
        dashboardLink.style.display = "inline-block";
        signOutLink.style.display = "inline-block";
    } else {
        signInLink.style.display = "inline-block";
        registerLink.style.display = "inline-block";
        dashboardLink.style.display = "none";
        signOutLink.style.display = "none";
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