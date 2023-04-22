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
-- Table structure for table `tblpersoncontact`
--

DROP TABLE IF EXISTS `tblpersoncontact`;
CREATE TABLE IF NOT EXISTS `tblpersoncontact` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) DEFAULT NULL,
  `ContactLabel` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `Contact` varchar(255) DEFAULT NULL,
  `Unlisted` tinyint(1) DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblpersoncontact`
--

INSERT INTO `tblpersoncontact` (`ID`, `PersonID`, `ContactLabel`, `Type`, `Contact`, `Unlisted`, `Note`) VALUES
(17, 2, 'Main', 'eMail', 'heidiwberglund@icloud.com', 0, NULL),
(18, 5, 'Main', 'eMail', 'mizpahrtou@yahoo.com', 1, NULL),
(19, 19, 'Main', 'Phone', '(218) 475-2458', 0, NULL),
(20, 20, 'Main', 'Phone', '(218) 387-9282', 0, NULL),
(21, 21, 'Main', 'Phone', '(218) 387-9282', 0, NULL),
(22, 29, 'Main', 'Phone', '(913) 488-8702', 0, NULL),
(23, 31, 'Main', 'Phone', '(641) 247-1207', 0, NULL),
(24, 41, 'Main', 'Phone', '(414) 248-8040', 0, NULL),
(25, 42, 'Main', 'Phone', '(260) 437-4704', 0, NULL),
(26, 19, 'Main', 'eMail', 'lisam@boreal.org', 0, NULL),
(27, 20, 'Main', 'eMail', 'bobganam@boreal.org', 0, NULL),
(28, 21, 'Main', 'eMail', 'glmbtm60@gmail.com', 0, NULL),
(29, 29, 'Main', 'eMail', 'mbulmer1947@gmail.com', 0, NULL),
(30, 31, 'Secondary', 'eMail', 'Hannah@WattsWhat.net', 0, NULL),
(31, 41, 'Main', 'eMail', 'e.saunders.piano@gmail.com', 0, NULL),
(32, 42, 'Main', 'eMail', 'mhsklo@gmail.com', 0, NULL),
(33, 5, 'Main', 'Phone', '(218) 387-4373', 0, NULL),
(42, 166, 'Main', 'Phone', '(218) 387-2234', 0, NULL),
(43, 167, 'Main', 'eMail', 'jim@times2design.com', 0, NULL),
(44, 167, 'Main', 'Phone', '(218) 370-2456', 0, NULL),
(45, 166, 'Main', 'eMail', 'janet@times2design.com', 0, NULL),
(46, 164, 'Main', 'Phone', '(612) 483-0148', 0, NULL),
(47, 164, 'Main', 'eMail', 'loristangler@gmail.com', 0, NULL),
(48, 66, 'Main', 'Phone', '(314) 809-8450', 0, NULL),
(50, 165, 'Main', 'eMail', 'stagler77@gmail.com', 0, NULL),
(51, 31, 'Main', 'eMail', 'Hannah.watt610@gmail.com', 0, NULL),
(52, 165, 'Mobil', 'Phone', '(612) 859-1372', 0, NULL),
(53, 30, 'Home', 'Phone', '(515) 462-0566', 0, NULL),
(54, 30, 'Primary', 'eMail', 'pwbjwatt@gmail.com', 0, NULL),
(55, 30, 'Church', 'eMail', 'pastor@licgm.org', 0, NULL),
(56, 171, 'Mobile', 'Phone', '(218) 940-1602', 0, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
