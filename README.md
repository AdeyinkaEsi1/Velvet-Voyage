# travel-booking

i have exported the db with command - mysqldump -u root -p ht_booking > backup.sql; from terminal


1:  Import the Database;

        Login to MySQL (Using the credentials set during installation):
        mysql login command ---->   mysql -u <your_username> -p 
        
        --- Enter your password when prompted.

2: CREATE DATABASE ht_booking;


3: Exit MySQL with command --> exit;

4: Import the Database Dump with command ---> mysql -u <your_username> -p ht_booking < database/backup.sql
       ---Run from cmd or powershell

        ---  Enter the MySQL password when prompted.
        --- It will restore all tables and data.



5: to verify setup
        -- mysql -u root -p
        -- USE ht_booking;
        -- SHOW TABLES;




