-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:13 PM
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
-- Table structure for table `tblparticipant`
--

DROP TABLE IF EXISTS `tblparticipant`;
CREATE TABLE IF NOT EXISTS `tblparticipant` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) DEFAULT NULL,
  `Name` varchar(255) NOT NULL,
  `Roles` varchar(255) DEFAULT NULL,
  `Schedule` varchar(255) DEFAULT NULL,
  `Phone` varchar(255) DEFAULT NULL,
  `eMail` varchar(255) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblparticipant`
--

INSERT INTO `tblparticipant` (`ID`, `PersonID`, `Name`, `Roles`, `Schedule`, `Phone`, `eMail`, `Note`) VALUES
(1, NULL, 'Rev. Jonathan C. Watt', '[Liturgist\rPreacher]', '[1\r3\r2\r4]', NULL, 'jonathan@wattswhat.net', NULL),
(2, NULL, 'Lisa Mesenbring', '[Organist]', '[1\r2\r4]', NULL, 'lisam@boreal.org', NULL),
(3, NULL, 'Jay Mesenbring', '[Elder]', '[1\r2\r4]', NULL, NULL, NULL),
(4, NULL, 'Greg Gecas', '[Elder]', '[1\r3\r2\r4]', NULL, 'info@hestons.com', NULL),
(6, NULL, 'Erik Saunders', '[Organist]', NULL, '(218) 388-0120', 'erik.saunders@ctsfw.edu', NULL),
(7, NULL, 'Rev. Daniel Preus', '[Liturgist\r\nPreacher]', NULL, '(314) 809-8418', 'dospreus@gmail.com', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
