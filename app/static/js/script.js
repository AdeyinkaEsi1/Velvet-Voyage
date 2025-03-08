
const home = () => {
    document.addEventListener("DOMContentLoaded", function () {
        let userLoggedIn = false; // Replace with actual session check
    
        if (!userLoggedIn) {
            setTimeout(() => {
                let modal = document.getElementById("loginModal");
                if (modal) {
                    modal.classList.add("show");
                }
            }, 5000);
        }
    
        let closeButton = document.querySelector(".modal-close-btn");
        if (closeButton) {
            closeButton.addEventListener("click", function () {
                document.getElementById("loginModal").classList.remove("show");
            });
        }
    
        window.addEventListener("click", function (event) {
            let modal = document.getElementById("loginModal");
            if (modal && event.target === modal) {
                modal.classList.remove("show");
            }
        });
    
    
        document.getElementById("flightForm").addEventListener("submit", function (event) {
            event.preventDefault();
        
            let departure = document.getElementById("departure").value;
            let destination = document.getElementById("destination").value;
        
            if (!departure || !destination) {
                alert("Please select both departure and destination!");
                return;
            }
            window.location.href = `/flight_price/?departure=${encodeURIComponent(departure)}&destination=${encodeURIComponent(destination)}`;
        });
    
    });

};
home()



    // document.addEventListener("DOMContentLoaded", function () {
    //     const searchForm = document.getElementById("flight-search-form");
    
    //     searchForm.addEventListener("submit", function (event) {
    //         event.preventDefault();
    
    //         // Get form values
    //         const departure = searchForm.departure.value;
    //         const arrival = searchForm.arrival.value;
    //         const date = searchForm.date.value;
    
    //         if (!departure || !arrival || !date) {
    //             alert("Please fill in all fields.");
    //             return;
    //         }
    
    //         // Redirect to flights page with query params
    //         const searchParams = new URLSearchParams({ departure, arrival, date });
    //         window.location.href = `/flights?${searchParams.toString()}`;
    //     });
    
    
    
    
    // });
