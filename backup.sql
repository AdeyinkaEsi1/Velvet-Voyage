-- MySQL dump 10.13  Distrib 9.2.0, for Win64 (x86_64)
--
-- Host: localhost    Database: ht_booking
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `flight_id` int DEFAULT NULL,
  `booking_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `seats` int NOT NULL,
  `flight_class` enum('economy','business') NOT NULL,
  `round_trip` tinyint(1) DEFAULT '0',
  `booking_id` varchar(20) NOT NULL,
  `status` enum('pending','confirmed','checked-in','cancelled','completed','no-show') DEFAULT 'pending',
  `payment_status` enum('pending','paid','failed') DEFAULT 'pending',
  `payment_reference` varchar(50) DEFAULT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `discount_applied` decimal(10,2) DEFAULT '0.00',
  `cancellation_fee` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `booking_id` (`booking_id`),
  UNIQUE KEY `booking_id_2` (`booking_id`),
  UNIQUE KEY `payment_reference` (`payment_reference`),
  KEY `bookings_ibfk_1` (`user_id`),
  KEY `fk_flight_id` (`flight_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_flight_id` FOREIGN KEY (`flight_id`) REFERENCES `flights` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_seats` CHECK ((`seats` between 1 and 130))
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (58,3,17,'2025-03-11 14:09:02',33,'business',0,'C5712E574FB','pending','pending',NULL,3300.00,0.00,0.00),(59,3,17,'2025-03-11 14:20:39',33,'economy',0,'40189042418','pending','pending',NULL,3300.00,0.00,0.00),(60,3,17,'2025-03-11 14:34:06',33,'economy',0,'8C90765C6A2','pending','pending',NULL,3300.00,0.00,0.00),(61,3,14,'2025-03-11 14:35:22',2,'business',0,'F0C87E47495','pending','pending',NULL,360.00,120.00,0.00),(64,7,14,'2025-03-12 00:40:37',1,'economy',0,'E633069ECA1','pending','pending',NULL,120.00,0.00,0.00),(69,11,14,'2025-03-12 05:53:02',1,'business',1,'454B370F655','confirmed','paid','5QTKOZVMYM0A',240.00,0.00,0.00),(70,3,19,'2025-03-13 13:01:15',1,'business',0,'B43574C8DA0','pending','pending',NULL,200.00,0.00,0.00);
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight_prices`
--

DROP TABLE IF EXISTS `flight_prices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight_prices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `departure` varchar(50) NOT NULL,
  `destination` varchar(50) NOT NULL,
  `price` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight_prices`
--

LOCK TABLES `flight_prices` WRITE;
/*!40000 ALTER TABLE `flight_prices` DISABLE KEYS */;
INSERT INTO `flight_prices` VALUES (1,'Newcastle','Bristol',90),(2,'Bristol','Newcastle',90),(3,'Cardiff','Edinburgh',90),(4,'Bristol','Manchester',80),(5,'Manchester','Bristol',80),(6,'Bristol','London',80),(7,'London','Manchester',100),(8,'Manchester','Glasgow',100),(9,'Bristol','Glasgow',110),(10,'Glasgow','Newcastle',100),(11,'Newcastle','Manchester',100),(12,'Portsmouth','Dundee',120),(13,'Dundee','Portsmouth',120),(14,'Edinburgh','Cardiff',100),(15,'Southampton','Manchester',100),(16,'Manchester','Southampton',90),(17,'Birmingham','Newcastle',100),(18,'Newcastle','Birmingham',100),(19,'Aberdeen','Portsmouth',100);
/*!40000 ALTER TABLE `flight_prices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flights`
--

DROP TABLE IF EXISTS `flights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flights` (
  `id` int NOT NULL AUTO_INCREMENT,
  `departure` varchar(255) NOT NULL,
  `destination` varchar(255) NOT NULL,
  `departure_time` time NOT NULL,
  `arrival_time` time NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flights`
--

LOCK TABLES `flights` WRITE;
/*!40000 ALTER TABLE `flights` DISABLE KEYS */;
INSERT INTO `flights` VALUES (5,'Manchester','Bristol','13:20:00','16:20:00'),(6,'Bristol','London','07:40:00','08:20:00'),(7,'London','Manchester','13:00:00','14:00:00'),(9,'Bristol','Glasgow','08:40:00','09:45:00'),(10,'Glasgow','Newcastle','14:30:00','15:45:00'),(12,'Manchester','Bristol','18:25:00','19:30:00'),(13,'Bristol','Manchester','06:20:00','07:20:00'),(14,'Portsmouth','Dundee','12:00:00','14:00:00'),(15,'Dundee','Portsmouth','10:00:00','12:00:00'),(16,'Edinburgh','Cardiff','18:30:00','20:00:00'),(17,'Southampton','Manchester','12:00:00','13:30:00'),(18,'Manchester','Southampton','19:00:00','20:30:00'),(19,'Birmingham','Newcastle','17:00:00','17:45:00'),(20,'Newcastle','Birmingham','07:00:00','07:45:00'),(21,'Aberdeen','Portsmouth','08:00:00','09:30:00'),(26,'Paris','Tokyo','12:35:00','14:33:00');
/*!40000 ALTER TABLE `flights` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `mobile_number` varchar(20) NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` enum('Male','Female','Other') NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `reset_otp` varchar(6) DEFAULT NULL,
  `otp_expires` timestamp NULL DEFAULT NULL,
  `role` enum('user','admin') DEFAULT 'user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (3,'Admin','01','admin@example.com','123 Street','Instabul','08059472483','1990-01-07','Male','$2b$12$Y5TDJurpZ8/u/8QXZYx2FuM7deJJPq7qw1KuBwNejOd5dNJJ0qIQa',NULL,NULL,'admin'),(7,'Lanre','Agbaje','olanrewajuyus02@gmail.com','2A, FREEMAN STREET','Ebutte-Metta','08059472483','2012-10-04','Male','$2b$12$RvQToeMAtGq5Sv29SNEz1e19MOOtiKUEFq4N2MEgBCyi0WR2WqzK6',NULL,NULL,'user'),(9,'Admin','02','admin2@example.com','456 Street','Lagos','08059472483','2001-01-07','Male','$2b$12$65M.qdUUZqk336ImwFHvDOR8kiXD/LrwBPxSuu0SKc3srPlosDX72',NULL,NULL,'admin'),(11,'Idayat','Asiwaju','adeyinkah.28@gmail.com','456 Street','Lagos','08059472483','2001-01-07','Female','$2b$12$H1hYkMgJMJF8Ki8t0GINm.XGkTm8tB5DkMrlzBFtKbXObgN2Twsqy',NULL,NULL,'user');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-13 16:36:17
