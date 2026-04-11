-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: civitrack_db
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `complaints`
--

DROP TABLE IF EXISTS `complaints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaints` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text,
  `incident_date` datetime DEFAULT NULL,
  `incident_location` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `video` varchar(255) DEFAULT NULL,
  `resolved_image` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Pending',
  `tracking_id` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `complaints_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaints`
--

LOCK TABLES `complaints` WRITE;
/*!40000 ALTER TABLE `complaints` DISABLE KEYS */;
INSERT INTO `complaints` VALUES (1,2,'Road / PWD','pothhole','road','2026-02-03 14:36:00','? Lat: 8.560310, Lon: 76.876272','bg.jpg',NULL,'bg.jpg','Resolved','PWD-001','2026-02-03 09:07:10'),(2,2,'Road / PWD','road pothole','road not cleared','2026-02-03 14:46:00','? Lat: 8.560356, Lon: 76.876275','Gemini_Generated_Image_55z9zx55z9zx55z9.png',NULL,'Image_preview.png','Resolved','PWD-002','2026-02-03 09:16:48'),(5,2,'Road / PWD','ifdfdf','fdfd','2026-02-03 15:27:00','? Lat: 8.560261, Lon: 76.876286','bg.jpg',NULL,'bg.jpg','Resolved','PWD-005','2026-02-03 09:57:42'),(6,2,'Water Authority','sdsd','dsds','2026-02-03 15:43:00','dsdsd','bg.jpg',NULL,'stranger-things-s5-joe-keery-steve-harrington-4k-wallpaper-uhdpaper.com-8405j.jpg','Resolved','WTR-006','2026-02-03 10:13:20'),(11,2,'Municipality','garbage clceaning','it is not cleaned','2026-02-04 11:19:00','techno park','Gemini_Generated_Image_55z9zx55z9zx55z9.png',NULL,'1725682222084.jpeg','Resolved','MUN-011','2026-02-04 05:49:27'),(12,2,'Green Services','fd','fdfd','2026-02-04 11:34:00','dfd','Gemini_Generated_Image_undrb9undrb9undr.png',NULL,'bg.jpg','Resolved','GRN-012','2026-02-04 06:04:17'),(13,17,'Road / PWD','road brokage','road brokage cleared already','2026-02-04 15:17:00','? Lat: 8.560310, Lon: 76.876291','Gemini_Generated_Image_kaw2rrkaw2rrkaw2.png',NULL,'download.png','Resolved','PWD-013','2026-02-04 09:47:34'),(14,18,'Water Authority','water broakage','brokage','2026-02-05 12:00:00','? Lat: 8.560288, Lon: 76.876296','WhatsApp_Image_2025-10-05_at_19.23.59_2.jpeg',NULL,'WhatsApp_Image_2025-11-26_at_21.11.06.jpeg','Resolved','WTR-014','2026-02-05 06:31:02'),(15,18,'Municipality','ffd','df','2026-02-05 12:03:00','fdf','bg.jpg',NULL,NULL,'Assigned','MUN-015','2026-02-05 06:33:18'),(16,2,'Road / PWD','road damage','roaf damage','2026-02-07 20:58:00','? Lat: 8.513204, Lon: 77.556643','ChatGPT_Image_Feb_7_2026_08_26_53_PM.png',NULL,'medi_point.png','Resolved','PWD-016','2026-02-07 15:28:20'),(17,2,'Road / PWD','broken road','heritage','2026-02-13 18:09:00','? Lat: 8.559624, Lon: 76.877854','aadhar_bk.jpg',NULL,'aadhar_bk.jpg','Resolved','PWD-017','2026-02-11 12:42:35'),(18,20,'Road / PWD','road damage','damge causes accidents and block','2026-02-03 10:44:00','? Lat: 8.559632, Lon: 76.877738','IMG_20251017_110734.jpg',NULL,'IMG_20251017_110734.jpg','Resolved','PWD-018','2026-02-16 05:14:43'),(19,2,'Road / PWD','damage','damage','2026-02-26 16:10:00','? Lat: 8.560310, Lon: 76.876272','Screenshot_2025-09-17_141608.png',NULL,NULL,'Assigned','PWD-019','2026-02-26 10:41:19'),(20,2,'Road / PWD','ad','dvs','2026-03-11 15:33:00','kslskf','ER.png',NULL,NULL,'Pending','PWD-020','2026-03-11 10:04:18');
/*!40000 ALTER TABLE `complaints` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-01 13:47:47
