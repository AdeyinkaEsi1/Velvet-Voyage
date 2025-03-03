document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("flight-search-form");

    searchForm.addEventListener("submit", function (event) {
        event.preventDefault();

        // Get form values
        const departure = searchForm.departure.value;
        const arrival = searchForm.arrival.value;
        const date = searchForm.date.value;

        if (!departure || !arrival || !date) {
            alert("Please fill in all fields.");
            return;
        }

        // Redirect to flights page with query params
        const searchParams = new URLSearchParams({ departure, arrival, date });
        window.location.href = `/flights?${searchParams.toString()}`;
    });
});

document.addEventListener("DOMContentLoaded", function () {
    let userLoggedIn = false; // Replace with actual session check

    if (!userLoggedIn) {
        setTimeout(() => {
            let modal = document.getElementById("loginModal");
            if (modal) {
                modal.classList.add("show");
            }
        }, 5000); // Show modal after 5 seconds
    }

    // Close modal when clicking the close button
    let closeButton = document.querySelector(".modal-close-btn");
    if (closeButton) {
        closeButton.addEventListener("click", function () {
            document.getElementById("loginModal").classList.remove("show");
        });
    }

    // Close modal if user clicks outside the content
    window.addEventListener("click", function (event) {
        let modal = document.getElementById("loginModal");
        if (modal && event.target === modal) {
            modal.classList.remove("show");
        }
    });
});
