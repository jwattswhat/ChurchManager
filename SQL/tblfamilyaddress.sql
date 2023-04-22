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
-- Table structure for table `tblfamilyaddress`
--

DROP TABLE IF EXISTS `tblfamilyaddress`;
CREATE TABLE IF NOT EXISTS `tblfamilyaddress` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) NOT NULL,
  `AddressLabel` varchar(255) NOT NULL DEFAULT 'Main',
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
) ENGINE=MyISAM AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblfamilyaddress`
--

INSERT INTO `tblfamilyaddress` (`ID`, `FamilyID`, `AddressLabel`, `Address`, `Address2`, `City`, `State`, `Zip`, `Unlisted`, `StartDate`, `EndDate`, `Note`) VALUES
(1, 1, 'Home', '11 North Loon Lake Rd', NULL, 'Grand Marais', 'MN', '55604-', 0, NULL, NULL, NULL),
(2, 2, 'Home', '1410 Wahlstrom Rd', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(3, 3, 'Home', '6019 North Rd', '', 'Hoveland', 'MN', '55606-', 0, '0000-00-00', '0000-00-00', NULL),
(4, 4, 'Home', '579 S. Gunflint Lake', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(5, 5, 'Home', '4305 E. Hwy 61', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(6, 6, 'Home', '2347 Co Rd 7', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(7, 7, 'Home', '', 'PO Box 862', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(8, 8, 'Home', '1605 E. Hwy 61', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(9, 9, 'Home', '', 'PO Box 871', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(10, 10, 'Home', '', '', 'Kansas City', 'MO', '', 0, '0000-00-00', '0000-00-00', NULL),
(11, 11, 'Home', '2017 W Highway 61', 'PO Box 765', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(12, 14, 'Home', '4913 Winterset Drive', '', 'Minnetonka', 'MN', '55343-8725', 0, '0000-00-00', '0000-00-00', NULL),
(13, 18, 'Home', '1322 Berwick Lane', '', 'New Haven', 'IN', '46774', 0, '0000-00-00', '0000-00-00', NULL),
(14, 19, 'Home', '', 'PO Box 715', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(15, 71, 'Secondary', '175 Mile O Pine', '', 'Grand Maras', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(16, 72, 'Secondary', '171 Mile  O Pine', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(17, 75, 'Home', '14565 268th Ave NW', '', 'Zimmerman', 'MN', '55398', 0, '0000-00-00', '0000-00-00', NULL),
(18, 76, 'Home', '11549 284th Ave NW', '', 'Zimmerman', 'MN', '55398', 0, '0000-00-00', '0000-00-00', NULL),
(19, 77, 'Home', '31065 Co Rd 5 NW', '', 'Princeton', 'MN', '55371', 0, '0000-00-00', '0000-00-00', NULL),
(20, 78, 'Home', 'Linnel Rd', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(21, 79, 'Home', 'PO Box 121', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(22, 80, 'Home', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(23, 81, 'Home', '1322 Berwick Lane', '', '1322 Berwick Lane\r\n\r\nNew Haven', 'IN', '46774', 0, '0000-00-00', '0000-00-00', NULL),
(24, 82, 'Home', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(25, 83, 'Home', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(26, 84, 'Home', '', '', 'Lutsen', 'MN', '', 0, '0000-00-00', '0000-00-00', NULL),
(27, 85, 'Home', '54 Stonegate Rd', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(28, 31, 'School', '198 E Roberts St.', '', 'Seward', 'NE', '96434', 0, '0000-00-00', '0000-00-00', NULL),
(29, 92, 'Home', '2151 E Raw Hide St', '', 'Gilbert', 'AZ', '85296-2739', 0, '0000-00-00', '0000-00-00', NULL),
(31, 93, 'Home', '11346 Wren St. NW', '', 'Coon Rapids', 'MN', '55433', 0, '0000-00-00', '0000-00-00', NULL),
(32, 94, 'Home', '715 E Lincoln Ln', 'Apt O', 'Gardner', 'KS', '66030', 0, '0000-00-00', '0000-00-00', NULL),
(33, 95, 'Home', '7611 Knox Ave', '', 'Richfield', 'MN', '55423', 0, '0000-00-00', '0000-00-00', NULL),
(34, 96, 'Home', '1833 210th Ave', '', 'Fairmont', 'MN', '56031', 0, '0000-00-00', '0000-00-00', NULL),
(35, 97, 'Home', '1833 210th Ave', '', 'Fairmont', 'MN', '56031', 0, '0000-00-00', '0000-00-00', NULL),
(36, 101, 'Home', '171 Mile O\' Pine', '', 'Grand Marais', '', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(38, 103, 'Home', '241 Mile O\' Pine', '', 'Grand Marais', '', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(39, 104, 'Home', '', '', 'Excelser', 'MN', '', 0, '0000-00-00', '0000-00-00', NULL),
(40, 105, 'Home', '', '', 'Mtka', '', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(41, 105, 'Home', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(42, 106, 'Home', '', '', 'Mtka', 'MN', '', 0, '0000-00-00', '0000-00-00', NULL),
(43, 107, 'Home', '', '', 'Burnsville', 'MN', '', 0, '0000-00-00', '0000-00-00', NULL),
(44, 108, 'Home', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(45, 109, 'Home', '', '', 'Mtka', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(46, 119, 'Home', '969 Devil Track Rd', '', 'Grand Marais', '', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(47, 118, 'Home', '4 Beargrease Crossing', '', 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL),
(48, 120, 'Home', NULL, 'PO Box 652', 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL),
(49, 73, 'Home', NULL, '', 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL),
(50, 116, 'Home', '2027 West Hwy 61', '', 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL),
(51, 87, 'Home', '11 N Loon Lake Rd', NULL, 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
