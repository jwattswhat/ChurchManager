-- MariaDB dump 10.19-11.1.0-MariaDB, for Win64 (AMD64)
--
-- Host: 192.168.3.200    Database: ChurchDB
-- ------------------------------------------------------
-- Server version	10.5.19-MariaDB-0+deb11u2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tblPrayer`
--

DROP TABLE IF EXISTS `tblPrayer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblPrayer` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Request` varchar(255) NOT NULL,
  `PrayerCategory` varchar(255) DEFAULT NULL,
  `RequestFor` varchar(255) DEFAULT NULL,
  `RequestBy` varchar(255) DEFAULT NULL,
  `Continuous` tinyint(1) NOT NULL DEFAULT 1,
  `First` tinyint(1) NOT NULL DEFAULT 0,
  `Second` tinyint(1) NOT NULL DEFAULT 0,
  `Third` tinyint(1) NOT NULL DEFAULT 0,
  `Fourth` tinyint(1) NOT NULL DEFAULT 0,
  `Fifth` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblprayer_tblchurch1_idx` (`ChurchID`)
) ENGINE=MyISAM AUTO_INCREMENT=60 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblPrayer`
--

LOCK TABLES `tblPrayer` WRITE;
/*!40000 ALTER TABLE `tblPrayer` DISABLE KEYS */;
INSERT INTO `tblPrayer` VALUES
(1,0,'Cancer','Cancer','David Weides',NULL,1,1,1,1,1,1,NULL,NULL,NULL),
(30,0,'Health','Health','John Moos','Pastor ',1,1,1,1,1,1,NULL,NULL,NULL),
(4,0,'Church','Church','LCMS Presidium: Matthew Harrison, Peter Lang, Scott Murry, Nabil Nour, Chris Esget, Ben Ball and their families',NULL,1,0,1,0,0,0,NULL,NULL,NULL),
(50,0,'Cancer','Cancer','Kory Kristensen','',1,1,1,1,1,1,'2025-05-19','2025-05-19',''),
(43,0,'Cancer','Cancer','Elsa Sorensen','Kendra',1,1,1,1,1,1,NULL,NULL,NULL),
(9,0,'Cancer','Cancer','Jason Forland',NULL,1,1,1,1,1,1,NULL,NULL,NULL),
(10,0,'Cancer','Cancer','Pauli Bakstrom',NULL,1,1,1,1,1,1,NULL,NULL,NULL),
(15,0,'Church ','Church','Redeemer Lutheran Church','Jay',1,1,0,0,0,0,NULL,NULL,NULL),
(47,0,'Recovery','Recovery','People Recovering from Hurricanes and Fires','Pastor',1,1,1,1,1,1,NULL,NULL,NULL),
(14,0,'Cancer','Cancer','Llyod Speck','Randy',1,1,1,1,1,1,NULL,NULL,NULL),
(28,0,'Church','Church','Work of the Building Committee',NULL,1,1,1,1,1,1,NULL,NULL,NULL),
(54,0,'Church','Church','New Pastors, Teachers and Other Church Workers','Pastor Watt',1,1,0,0,1,0,NULL,NULL,NULL),
(22,0,'Cancer','Cancer','Bob Brandt','Rachael Burglund',1,1,1,1,1,1,NULL,NULL,NULL),
(24,0,'Church','Church','LCMS Minnesota North District President Rev. Brady Finnern and Staff and Families','Pastor Watt',1,0,0,1,0,0,NULL,NULL,NULL),
(53,0,'Ramero Acero','Cancer','Ramero Acero','Pastor Watt',1,1,1,1,1,1,NULL,NULL,'[School Bus Driver]'),
(31,0,'Health','Health','Mary Watt','Pastor Watt',1,1,1,1,1,1,NULL,NULL,NULL),
(56,0,'Church','Church','Thanksgiving for Reaching our Fundraising Goal!','BuildingCommittee',0,1,1,1,1,1,'2025-05-01','2025-05-30',NULL),
(34,0,'World','World','Wars around the World','Pastor',1,1,1,1,1,1,NULL,NULL,NULL),
(46,0,'Health','Health','Joshua James Simon',NULL,1,1,1,1,1,1,NULL,NULL,NULL),
(35,0,'General','General','Guests and Visitors','Randy',1,1,1,1,1,1,NULL,NULL,NULL),
(49,0,'General','Health','Yarrow Korf','',1,1,1,1,1,1,NULL,NULL,NULL),
(58,0,'General','General','Mothers on Mother\'s Day',NULL,0,1,1,1,1,1,'2025-05-09','2025-05-13',NULL),
(59,0,'Closing','Church','Immanual Lutheran Church, Holloway','Building Committee',0,1,1,1,1,1,'2025-05-11','2025-07-31',NULL);
/*!40000 ALTER TABLE `tblPrayer` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-20 14:24:47
