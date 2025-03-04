CREATE TABLE
    flight_prices (
        id INT PRIMARY KEY AUTO_INCREMENT,
        departure VARCHAR(255) NOT NULL,
        destination VARCHAR(255) NOT NULL,
        price INT NOT NULL
    );

CREATE TABLE
    flights (
        id INT PRIMARY KEY AUTO_INCREMENT,
        departure VARCHAR(255) NOT NULL,
        destination VARCHAR(255) NOT NULL,
        departure_time TIME NOT NULL,
        arrival_time TIME NOT NULL
    );

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    flight_id INT NOT NULL,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (flight_id) REFERENCES flights(id)
);
