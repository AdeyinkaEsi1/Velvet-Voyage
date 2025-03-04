INSERT INTO flight_prices (departure, destination, price) VALUES
('Dundee', 'Portsmouth', 120.00),
('Portsmouth', 'Dundee', 120.00),  -- Reverse route

('Bristol', 'Manchester', 80.00),
('Manchester', 'Bristol', 80.00),  -- Reverse route

('Bristol', 'Newcastle', 90.00),
('Newcastle', 'Bristol', 90.00),  -- Reverse route

('Bristol', 'Glasgow', 110.00),
('Glasgow', 'Bristol', 110.00),  -- Reverse route

('Bristol', 'London', 80.00),
('London', 'Bristol', 80.00),  -- Reverse route

('Manchester', 'Southampton', 90.00),
('Southampton', 'Manchester', 90.00),  -- Reverse route

('Cardiff', 'Edinburgh', 90.00),
('Edinburgh', 'Cardiff', 90.00),  -- Reverse route

-- Default price for all other routes
('DEFAULT', 'DEFAULT', 100.00);
