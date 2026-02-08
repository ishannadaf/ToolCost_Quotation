CREATE DATABASE  IF NOT EXISTS `tool_management` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `tool_management`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: tool_management
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Table structure for table `account_master`
--

DROP TABLE IF EXISTS `account_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_master` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `party_name` varchar(70) DEFAULT NULL,
  `provider_names` varchar(150) DEFAULT NULL,
  `contact` varchar(12) DEFAULT NULL,
  `address` varchar(70) DEFAULT NULL,
  `pdf_path` varchar(80) DEFAULT NULL,
  `login_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_master`
--

LOCK TABLES `account_master` WRITE;
/*!40000 ALTER TABLE `account_master` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_manage_master`
--

DROP TABLE IF EXISTS `delivery_manage_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_manage_master` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `quot_no` varchar(45) DEFAULT NULL,
  `part_no` varchar(45) DEFAULT NULL,
  `delivery_qty` int DEFAULT NULL,
  `delivery_dt` date DEFAULT NULL,
  `login_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_manage_master`
--

LOCK TABLES `delivery_manage_master` WRITE;
/*!40000 ALTER TABLE `delivery_manage_master` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_manage_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firm_master`
--

DROP TABLE IF EXISTS `firm_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `firm_master` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `firm_name` varchar(150) DEFAULT NULL,
  `firm_address` varchar(150) DEFAULT NULL,
  `firm_contact` varchar(12) DEFAULT NULL,
  `login_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firm_master`
--

LOCK TABLES `firm_master` WRITE;
/*!40000 ALTER TABLE `firm_master` DISABLE KEYS */;
/*!40000 ALTER TABLE `firm_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gst_percentage_table`
--

DROP TABLE IF EXISTS `gst_percentage_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gst_percentage_table` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `gst_per` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gst_percentage_table`
--

LOCK TABLES `gst_percentage_table` WRITE;
/*!40000 ALTER TABLE `gst_percentage_table` DISABLE KEYS */;
INSERT INTO `gst_percentage_table` VALUES (1,18);
/*!40000 ALTER TABLE `gst_percentage_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice_master`
--

DROP TABLE IF EXISTS `invoice_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_master` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `invoice_id` varchar(45) DEFAULT NULL,
  `po_no` varchar(45) DEFAULT NULL,
  `quot_id` varchar(45) DEFAULT NULL,
  `part_no` varchar(45) DEFAULT NULL,
  `date_tr` datetime DEFAULT NULL,
  `login_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_master`
--

LOCK TABLES `invoice_master` WRITE;
/*!40000 ALTER TABLE `invoice_master` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_master`
--

DROP TABLE IF EXISTS `login_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_master` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `firm_id` int DEFAULT NULL,
  `user_name` varchar(45) DEFAULT NULL,
  `user_pass` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_master`
--

LOCK TABLES `login_master` WRITE;
/*!40000 ALTER TABLE `login_master` DISABLE KEYS */;
INSERT INTO `login_master` VALUES (1,1,'admin','admin');
/*!40000 ALTER TABLE `login_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `machining_master`
--

DROP TABLE IF EXISTS `machining_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `machining_master` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `price` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machining_master`
--

LOCK TABLES `machining_master` WRITE;
/*!40000 ALTER TABLE `machining_master` DISABLE KEYS */;
/*!40000 ALTER TABLE `machining_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_table`
--

DROP TABLE IF EXISTS `master_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_table` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(100) DEFAULT NULL,
  `customer_contact` varchar(45) DEFAULT NULL,
  `date_of_activation` datetime DEFAULT NULL,
  `client_hard_key` varchar(45) DEFAULT NULL,
  `client_secret_key` varchar(45) DEFAULT NULL,
  `valid_till` datetime DEFAULT NULL,
  `active` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_table`
--

LOCK TABLES `master_table` WRITE;
/*!40000 ALTER TABLE `master_table` DISABLE KEYS */;
INSERT INTO `master_table` VALUES (1,'Ishan','8530013777','2025-12-19 00:00:00','23247204','2324720426121978','2026-12-19 00:00:00',1);
/*!40000 ALTER TABLE `master_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `material_master`
--

DROP TABLE IF EXISTS `material_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_master` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `density` double DEFAULT NULL,
  `rate` double DEFAULT NULL,
  `login_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material_master`
--

LOCK TABLES `material_master` WRITE;
/*!40000 ALTER TABLE `material_master` DISABLE KEYS */;
INSERT INTO `material_master` VALUES (1,'M.S',7860,130,1),(2,'S.S',8000,400,1),(3,'Al',2700,650,1),(4,'20MnCr5',8000,140,1),(5,'EN8',8000,85,1),(6,'8620',8000,100,1),(7,'Copper',8960,853,1),(8,'Gun metal',8719,875,1),(9,'Nylon',1160,1000,1),(10,'UHMW',970,950,1),(11,'PU',961,1250,1),(12,'Delrin',1420,500,1),(13,'Kelvler',1440,1800,1);
/*!40000 ALTER TABLE `material_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quotation_master`
--

DROP TABLE IF EXISTS `quotation_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quotation_master` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `quotation_id` varchar(15) DEFAULT NULL,
  `invoice_id` varchar(45) DEFAULT NULL,
  `cust_id` int DEFAULT NULL,
  `cust_name` varchar(50) DEFAULT NULL,
  `provider_name` varchar(50) DEFAULT NULL,
  `date_tr_quot` datetime DEFAULT NULL,
  `invoice_generated` varchar(2) DEFAULT NULL,
  `invoice_tr_date` datetime DEFAULT NULL,
  `login_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quotation_master`
--

LOCK TABLES `quotation_master` WRITE;
/*!40000 ALTER TABLE `quotation_master` DISABLE KEYS */;
/*!40000 ALTER TABLE `quotation_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quotation_master_details`
--

DROP TABLE IF EXISTS `quotation_master_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quotation_master_details` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `Quotation_Id` varchar(15) DEFAULT NULL,
  `part_no` varchar(45) DEFAULT NULL,
  `part_desc` varchar(60) DEFAULT NULL,
  `part_qty` int DEFAULT NULL,
  `material` varchar(45) DEFAULT NULL,
  `unit_measurement` varchar(45) DEFAULT NULL,
  `shape` varchar(45) DEFAULT NULL,
  `width` double DEFAULT NULL,
  `length_part` double DEFAULT NULL,
  `thickness` double DEFAULT NULL,
  `unit_weight` double DEFAULT NULL,
  `rmc` double DEFAULT NULL,
  `profit_per` double DEFAULT NULL,
  `unit_price` varchar(45) DEFAULT NULL,
  `total_price` double DEFAULT NULL,
  `date_tr` datetime DEFAULT NULL,
  `delivery_flag` varchar(2) DEFAULT NULL,
  `login_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quotation_master_details`
--

LOCK TABLES `quotation_master_details` WRITE;
/*!40000 ALTER TABLE `quotation_master_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `quotation_master_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quotation_master_details_machining_details`
--

DROP TABLE IF EXISTS `quotation_master_details_machining_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quotation_master_details_machining_details` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `Quotation_Id` varchar(45) DEFAULT NULL,
  `part_no_id` varchar(20) DEFAULT NULL,
  `machining_name` varchar(45) DEFAULT NULL,
  `lbl_rate` double DEFAULT NULL,
  `cust_rate` double DEFAULT NULL,
  `total_hr` double DEFAULT NULL,
  `date_tr` datetime DEFAULT NULL,
  `login_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quotation_master_details_machining_details`
--

LOCK TABLES `quotation_master_details_machining_details` WRITE;
/*!40000 ALTER TABLE `quotation_master_details_machining_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `quotation_master_details_machining_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `raw_cost`
--

DROP TABLE IF EXISTS `raw_cost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_cost` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `price` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_cost`
--

LOCK TABLES `raw_cost` WRITE;
/*!40000 ALTER TABLE `raw_cost` DISABLE KEYS */;
/*!40000 ALTER TABLE `raw_cost` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `secret_key`
--

DROP TABLE IF EXISTS `secret_key`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `secret_key` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `secret_key_hard` varchar(100) DEFAULT NULL,
  `secret_key_1` varchar(100) DEFAULT NULL,
  `secret_keycol` varchar(45) DEFAULT NULL,
  `valid_from` date DEFAULT NULL,
  `valid_till` date DEFAULT NULL,
  `active_` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `secret_key`
--

LOCK TABLES `secret_key` WRITE;
/*!40000 ALTER TABLE `secret_key` DISABLE KEYS */;
/*!40000 ALTER TABLE `secret_key` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-14  0:00:31
