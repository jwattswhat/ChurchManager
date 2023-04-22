-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:14 PM
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
-- Table structure for table `tblpersonaddress`
--

DROP TABLE IF EXISTS `tblpersonaddress`;
CREATE TABLE IF NOT EXISTS `tblpersonaddress` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) NOT NULL,
  `AddressLabel` varchar(255) NOT NULL DEFAULT 'Home',
  `Address` varchar(255) DEFAULT NULL,
  `Address2` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT 'Grand Marais',
  `State` varchar(255) DEFAULT 'MN',
  `Zip` varchar(255) DEFAULT '55604',
  `Unlisted` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblpersonaddress`
--

INSERT INTO `tblpersonaddress` (`ID`, `PersonID`, `AddressLabel`, `Address`, `Address2`, `City`, `State`, `Zip`, `Unlisted`, `StartDate`, `EndDate`, `Note`) VALUES
(1, 31, 'Home', '6035 Meridian Dr', NULL, 'Lincoln', 'NE', '68504', 0, NULL, NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
