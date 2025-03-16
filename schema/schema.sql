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
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user'
);


CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    flight_id INT NULL,  -- Allow NULL values
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE SET NULL,
    seats INT NOT NULL CHECK (seats BETWEEN 1 AND 130),
    flight_class ENUM('economy', 'business', 'premium') NOT NULL,
    round_trip BOOLEAN DEFAULT FALSE,
    status ENUM('pending', 'confirmed', 'checked-in', 'cancelled', 'completed', 'no-show') DEFAULT 'pending'
);



INSERT INTO flight_prices (departure, destination, price) VALUES
('Newcastle', 'Bristol', 90),
('Bristol', 'Newcastle', 90),
('Cardiff', 'Edinburgh', 90),
('Bristol', 'Manchester', 80),
('Manchester', 'Bristol', 80),


('Bristol', 'London', 80),
('London', 'Manchester', 100),
('Manchester', 'Glasgow', 100),
('Bristol', 'Glasgow', 110),
('Glasgow', 'Newcastle', 100),

('Newcastle', 'Manchester', 100),
('Portsmouth', 'Dundee', 120),
('Dundee', 'Portsmouth', 120),
('Edinburgh', 'Cardiff', 100),
('Southampton', 'Manchester', 100),

('Manchester', 'Southampton', 90),
('Birmingham', 'Newcastle', 100),
('Newcastle', 'Birmingham', 100),
('Aberdeen', 'Portsmouth', 100);

