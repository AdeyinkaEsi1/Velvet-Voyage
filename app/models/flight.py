from app import db

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), nullable=False)
    departure = db.Column(db.String(50), nullable=False)
    arrival = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    
    
    #     # if flight_result:
    #     print("Flight found:", flight_result)
    #     return render_template(
    #         "flight_price.html",-
    #         departure_time=str(flight_result["departure_time"]),
    #         arrival_time=str(flight_result["arrival_time"]),
    #         price=price_result["price"] if price_result else default_price_result["price"]
    #     )
    # else:
    #     print("No flight found, redirecting to index.")
    #     return redirect(url_for("inde"))
        # return render_template("flight_price.html", error="No flight found for this route")
        
        
    # if flight_result:
    #     return jsonify({
    #         "departure_time": str(flight_result["departure_time"]),
    #         "arrival_time": str(flight_result["arrival_time"]),
    #         "price": price_result["price"] if price_result else default_price_result["price"]
    #     })
    