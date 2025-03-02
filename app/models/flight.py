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
    