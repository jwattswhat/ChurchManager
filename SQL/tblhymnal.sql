-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:12 PM
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
-- Table structure for table `tblhymnal`
--

DROP TABLE IF EXISTS `tblhymnal`;
CREATE TABLE IF NOT EXISTS `tblhymnal` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Hymnal` varchar(255) NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Publisher` varchar(255) NOT NULL,
  `Note` longtext DEFAULT NULL,
  UNIQUE KEY `ID` (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblhymnal`
--

INSERT INTO `tblhymnal` (`ID`, `Hymnal`, `Title`, `Publisher`, `Note`) VALUES
(1, 'LSB', 'Lutheran Service Book', 'Concordia Publishing House, St. Louis', NULL),
(2, 'TLH', 'The Lutheran Hymnal', 'Concordia Publishing House, St. Louis', NULL),
(3, 'kingsway', 'Kingsway Thankyou Music', '', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
