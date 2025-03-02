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
