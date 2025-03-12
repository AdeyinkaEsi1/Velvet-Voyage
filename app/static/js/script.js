async function isLoggedIn() {
    try {
        const response = await fetch("/auth/is_authenticated", {
            method: "GET",
            credentials: "include",
            headers: {
                "Accept": "application/json"
            }
        });

        console.log("Authentication check response:", response);

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
    console.log("User is logged in:", loggedIn);

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

