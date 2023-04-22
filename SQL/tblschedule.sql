-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:16 PM
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
-- Table structure for table `tblschedule`
--

DROP TABLE IF EXISTS `tblschedule`;
CREATE TABLE IF NOT EXISTS `tblschedule` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Description` varchar(255) DEFAULT NULL,
  `Time` time DEFAULT NULL,
  `DaysofWeek` varchar(255) DEFAULT NULL,
  `Months` varchar(255) DEFAULT NULL,
  `Seasons` varchar(255) DEFAULT NULL,
  `Increment` int(11) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblschedule`
--

INSERT INTO `tblschedule` (`ID`, `Description`, `Time`, `DaysofWeek`, `Months`, `Seasons`, `Increment`, `Note`) VALUES
(2, 'Every Sunday, 9am', '09:00:00', '[Sunday]', NULL, NULL, 1, NULL),
(3, 'Every Sunday in July & August, 11:30am', '11:30:00', '[Sunday]', '[July\r\nAugust]', NULL, NULL, NULL),
(1, 'Advent, 6:30pm', '18:30:00', '[Wednesday]', '[December]', '[ADVENT]', NULL, NULL),
(4, 'Lent, Wednesday 6:30pm', '18:30:00', '[Wednesday]', NULL, '[LENT]', NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
