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
-- Table structure for table `tblreports`
--

DROP TABLE IF EXISTS `tblreports`;
CREATE TABLE IF NOT EXISTS `tblreports` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Report` varchar(255) NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Params` longtext DEFAULT NULL,
  `Batch` longtext DEFAULT NULL,
  `Note` longtext NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblreports`
--

INSERT INTO `tblreports` (`ID`, `Report`, `Title`, `Params`, `Batch`, `Note`) VALUES
(1, 'CMPR01', 'Prayer Requests', '[ChurchID]', NULL, ''),
(2, 'CMWP01', 'Worship Planning Worksheet', '[ChurchID\r\nServiceID]\r\n', NULL, ''),
(3, 'CMFD01', 'Congregation Family Directory', '[ChurchID]', NULL, ''),
(5, 'CMPH02', 'Member Contact Listing', '[ChurchID\r\nProjectID]', NULL, ''),
(7, 'CMHU01', 'Hymn Usage by Service', '[ChurchID]', NULL, ''),
(8, 'CMHU02', 'Hymn Usage by Hymn', '[ChurchID]\r\n', NULL, ''),
(9, 'CMPJ01', 'Projects', '[ChurchID\r\nProjectID]', NULL, ''),
(24, 'CMPE01', 'Transfers', '[ChurchID\r\nStartDate\r\nEndDate]', NULL, ''),
(11, 'CMWS01', 'Worship Services - By Date', '[ChurchID]', NULL, ''),
(12, 'CMHU03', 'Hymn Usage', '[ChurchID\r\nHymnID]', NULL, ''),
(19, 'CMML01', 'Member Status List', '[ChurchID]', NULL, ''),
(14, 'CMML02', 'Member Date Listing', '[ChurchID]', NULL, ''),
(15, 'CMCL01', 'Family Listing', '[ChurchID]', NULL, ''),
(21, 'CMPJ03', 'Project Sign Up Sheet', '[ChurchID]', NULL, ''),
(17, 'CMMI01', 'Member (One) Information', '[ChurchID\r\nPersonID]', NULL, ''),
(18, 'CMMI02', 'Member (All) Information Listing', '[ChurchID]', NULL, ''),
(20, 'CMMI03', 'Member Update Forms', '[ChurchID]', NULL, ''),
(22, 'CMHU04', 'Hymn Usage since {Date}', '[ChurchID\r\nStartDate]', NULL, ''),
(23, 'CMAT01', 'Attendance Event Listing', '[ChurchID\r\nAttendanceType\r\nDetail\r\nStartDate]', NULL, ''),
(25, 'CMJR01', 'Journal', '[ChurchID\r\nStartDate\r\nEndDate]', NULL, ''),
(26, 'CMAS01', 'Asset Listing', '[ChurchID]', NULL, ''),
(27, 'CMDN01', 'Donor Listing', '[ChurchID]', NULL, ''),
(28, 'CMDN02', 'Donor Acknowledgement Due Listing', '[ChurchID]', NULL, ''),
(29, 'CMBATCH00', 'Pastor\'s Reports', '[ChurchID\r\nAttendanceType\r\nDetail\r\nStartDate\r\nEndDate]', '[CMML01\r\nCMAT01\r\nCMPE01\r\nCMJR01\r\nCMDN02]', '');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
