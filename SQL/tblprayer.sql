-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:15 PM
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
-- Table structure for table `tblprayer`
--

DROP TABLE IF EXISTS `tblprayer`;
CREATE TABLE IF NOT EXISTS `tblprayer` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
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
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblprayer`
--

INSERT INTO `tblprayer` (`ID`, `ChurchID`, `Request`, `PrayerCategory`, `RequestFor`, `RequestBy`, `Continuous`, `First`, `Second`, `Third`, `Fourth`, `Fifth`, `StartDate`, `EndDate`, `Note`) VALUES
(1, 0, 'Cancer', 'Cancer', 'David Weides', NULL, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(3, 0, 'Affected by War', 'World', 'People Everywhere', NULL, 1, 0, 1, 0, 1, 0, NULL, NULL, NULL),
(4, 0, 'Church', 'Church', 'LCMS Presidium: Matthew Harrison, Peter Lang, Scott Murry, Nabil Nour, Chris Esget, Ben Ball', NULL, 1, 0, 1, 0, 0, 0, NULL, NULL, NULL),
(6, 0, 'Help in trouble', 'General', 'Quist Family', 'Lisa', 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(7, 0, 'Help in Trouble', 'General', 'Ruth Johnson', NULL, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(8, 0, 'Medical', 'General', 'Steve', 'Jay', 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(9, 0, 'Cancer', 'Cancer', 'Jason Forland', NULL, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(10, 0, 'Cancer', 'Cancer', 'Pauli Bakstrom', NULL, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(11, 0, 'Cancer', 'Cancer', 'Samantha Walner', NULL, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(15, 0, 'Church like ours', 'Church', 'Redeemer Lutheran Church', 'Jay', 1, 1, 0, 0, 0, 0, NULL, NULL, NULL),
(13, 0, 'Cancer', 'Cancer', 'Vicky Sherman', NULL, 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(14, 0, 'Cancer', 'Cancer', 'Llyod Speck', 'Randy', 1, 1, 1, 1, 1, 1, NULL, NULL, NULL),
(20, 0, 'Recovery', 'Surgery', 'Randy Stangler', 'Pastor Watt', 1, 1, 1, 1, 1, 1, '2023-03-19', '2023-04-16', NULL),
(18, 0, 'Death', 'Death in Christ', 'Family of BJ Muus', 'Pastor Watt', 0, 1, 1, 1, 1, 1, '2023-03-05', '2023-03-19', NULL),
(19, 0, 'LCMS Presidential Vote', 'Church', 'LCMS Presidential Vote', 'LCMS', 0, 1, 1, 1, 1, 1, '2023-06-11', '2023-06-29', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
