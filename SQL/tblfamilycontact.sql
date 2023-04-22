-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:11 PM
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
-- Table structure for table `tblfamilycontact`
--

DROP TABLE IF EXISTS `tblfamilycontact`;
CREATE TABLE IF NOT EXISTS `tblfamilycontact` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) DEFAULT NULL,
  `ContactLabel` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `Contact` varchar(255) NOT NULL,
  `Unlisted` tinyint(1) NOT NULL DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblfamilycontact`
--

INSERT INTO `tblfamilycontact` (`ID`, `FamilyID`, `ContactLabel`, `Type`, `Contact`, `Unlisted`, `Note`) VALUES
(1, 1, 'Home', 'Phone', '(218) 387-2591', 0, NULL),
(2, 3, 'Home', 'Phone', '(218) 475-2499', 0, NULL),
(3, 4, 'Home', 'Phone', '(218) 388-2243', 0, NULL),
(4, 5, 'Home', 'Phone', '(218) 475-2458', 0, NULL),
(5, 6, 'Home', 'Phone', '(218) 387-9282', 0, NULL),
(6, 7, 'Home', 'Phone', '(218) 387-2653', 0, NULL),
(7, 8, 'Home', 'Phone', '(218) 387-2396', 0, NULL),
(8, 10, 'Home', 'Phone', '(913) 488-8702', 0, NULL),
(13, 82, 'Home', 'Phone', '(218) 388-9449', 0, NULL),
(14, 83, 'Home', 'Phone', '(218) 270-0384', 0, NULL),
(15, 84, 'Home', 'eMail', 'mmstevepenning@gmail.com', 0, NULL),
(16, 85, 'Home', 'Phone', '(218) 475-2482', 0, NULL),
(37, 93, 'Home', 'Phone', '(507) 525-6677', 0, NULL),
(38, 94, 'Home', 'Phone', '(913) 967-9715', 0, NULL),
(39, 95, 'Home', 'Phone', '(920) 660-5476', 0, NULL),
(40, 96, 'Home', 'Phone', '(920) 660-5520', 0, NULL),
(42, 120, 'Home', 'Phone', '(218) 387-2772', 0, NULL),
(43, 120, 'Home', 'Phone', '(218) 370-0288', 0, NULL),
(44, 79, 'Home', 'Phone', '(218) 370-1508', 0, '[Leave a message he will not answer a \r\nnumber he won\'t recognize]');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
