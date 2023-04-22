-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:43 PM
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
-- Database: `jsform`
--

-- --------------------------------------------------------

--
-- Table structure for table `tblchoices`
--

DROP TABLE IF EXISTS `tblchoices`;
CREATE TABLE IF NOT EXISTS `tblchoices` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Field` varchar(255) NOT NULL,
  `Choices` longtext NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblchoices`
--

INSERT INTO `tblchoices` (`ID`, `Field`, `Choices`, `Note`) VALUES
(29, 'Priority', '[1\r\n2\r\n3\r\n4\r\n5]', NULL),
(30, 'EnteredBy', '[JW]', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
