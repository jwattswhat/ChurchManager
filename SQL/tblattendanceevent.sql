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
-- Table structure for table `tblattendanceevent`
--

DROP TABLE IF EXISTS `tblattendanceevent`;
CREATE TABLE IF NOT EXISTS `tblattendanceevent` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `ServiceID` int(11) DEFAULT NULL,
  `DateTime` datetime DEFAULT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `AttendanceType` varchar(255) DEFAULT 'Worship Service w/ Communion',
  `CommunionOffered` tinyint(1) NOT NULL DEFAULT 0,
  `HandCount` int(11) NOT NULL DEFAULT 0,
  `HandCountCommunion` int(11) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblattendanceevent`
--

INSERT INTO `tblattendanceevent` (`ID`, `ChurchID`, `ServiceID`, `DateTime`, `Description`, `AttendanceType`, `CommunionOffered`, `HandCount`, `HandCountCommunion`, `Note`) VALUES
(1, 0, NULL, '2023-03-14 18:30:00', 'Home Visit', 'Visit', 1, 2, 2, '[Home visit with Randy and Lori Stangler before Randys knee replacement surgery.]'),
(2, 0, 30, NULL, 'First Sunday afte r Christmas', 'Worship Service', 1, 15, 12, NULL),
(16, 0, 40, '2023-03-14 18:30:00', 'Ash Wednesday', 'Worship Service', 0, 18, NULL, NULL),
(3, 0, 31, '2023-03-14 18:30:00', 'Epiphany', 'Worship Service', 1, 13, 12, NULL),
(4, 0, 32, NULL, 'Baptism of Our Lord', 'Worship Service', 1, 16, 15, NULL),
(5, 0, 33, '2023-03-14 18:30:00', 'Third Sunday after the Epiphany', 'Worship Service', 1, 15, 13, NULL),
(6, 0, 35, NULL, 'Fourth Sunday after the Epiphany', 'Worship Service', 1, 14, 13, NULL),
(7, 0, 37, NULL, 'Fifth Sunday after The Epiphany', 'Worship Service', 1, 19, 17, NULL),
(8, 0, 38, NULL, 'Sixth Sunday after the Epiphany', 'Worship Service', 1, 12, 12, NULL),
(9, 0, 39, NULL, 'Transfiguration', 'Worship Service', 1, 25, 21, NULL),
(10, 0, 41, NULL, 'First Sunday in Lent', 'Worship Service', 1, 15, 15, NULL),
(11, 0, 42, NULL, 'Weekday Lent 1', 'Worship Service', 0, 16, NULL, NULL),
(12, 0, 43, NULL, 'Second Sunday in Lent', 'Worship Service', 1, 16, 15, NULL),
(13, 0, 44, NULL, 'Weekday Lent 2', 'Worship Service', 0, 11, NULL, NULL),
(14, 0, 45, NULL, 'Third Sunday in Lent', 'Worship Service', 1, 10, 9, NULL),
(15, 0, 46, NULL, 'Weekday Lent 3', 'Worship Service', 0, 15, NULL, NULL),
(17, 0, 47, NULL, 'The Fourth Sunday in Lent', 'Worship Service', 1, 23, 23, NULL),
(18, 0, NULL, '2023-03-19 10:00:00', 'Office Visit member of the Community', 'Visit', 0, 1, NULL, '[requested a visit due to depression.]'),
(19, 0, 48, NULL, 'Weekday Lent Service 4', 'Worship Service', 0, 0, NULL, NULL),
(20, 0, 49, NULL, 'The Fifth Sunday in Lent', 'Worship Service', 1, 23, 23, NULL),
(21, 0, 50, NULL, 'Weekday Lent Service 5', 'Worship Service', 0, 11, NULL, NULL),
(22, 0, 51, NULL, 'Palm Passion Sunday', 'Worship Service', 1, 16, 16, NULL),
(23, 0, 53, '2023-03-14 18:30:00', 'Holy (Maunday) Thursday', 'Worship Service', 1, 30, 27, NULL),
(24, 0, 54, '2023-03-14 18:30:00', 'Good Friday', 'Worship Service', 0, 19, 0, NULL),
(25, 0, 55, '2023-03-14 18:30:00', 'Easter Sunday', 'Worship Service', 1, 16, 16, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
