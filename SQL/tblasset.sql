-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:09 PM
-- Server version: 10.6.7-MariaDB
-- PHP Version: 7.3.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `churchdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `tblasset`
--

DROP TABLE IF EXISTS `tblasset`;
CREATE TABLE IF NOT EXISTS `tblasset` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT 0,
  `AssetID` varchar(255) NOT NULL,
  `Description` varchar(255) NOT NULL,
  `Reserve` tinyint(1) NOT NULL DEFAULT 0,
  `PurchaseDate` date DEFAULT NULL,
  `Depreciate` tinyint(1) NOT NULL DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblasset`
--

INSERT INTO `tblasset` (`ID`, `ChurchID`, `AssetID`, `Description`, `Reserve`, `PurchaseDate`, `Depreciate`, `Note`) VALUES
(1, 0, 'LiCPrinter1', 'Brother HL-L3230CDW Compact Digital Color Printer', 0, '2022-06-20', 0, NULL),
(2, 0, 'LiCMonitor1', 'ONN Monitor for Announcement Kiosk', 0, NULL, 0, NULL),
(3, 0, 'LiCProjector1', 'Projector', 1, NULL, 0, NULL),
(4, 0, 'LiCComputer1', 'Beelink Mini Computer for Announcement Kisok', 0, NULL, 0, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
