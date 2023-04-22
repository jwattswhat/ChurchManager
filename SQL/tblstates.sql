-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:17 PM
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
-- Table structure for table `tblstates`
--

DROP TABLE IF EXISTS `tblstates`;
CREATE TABLE IF NOT EXISTS `tblstates` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `StateCode` varchar(2) DEFAULT NULL,
  `State` varchar(255) DEFAULT 'MN',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblstates`
--

INSERT INTO `tblstates` (`ID`, `StateCode`, `State`) VALUES
(1, 'AK', 'Alaska'),
(2, 'AZ', 'Arizona'),
(3, 'AL', 'Alabama'),
(4, 'AR', 'Arkansas'),
(5, 'CA', 'California'),
(6, 'CO', 'Colorado'),
(7, 'CT', 'Connecticut'),
(8, 'DE', 'Delaware'),
(9, 'FL', 'Florida'),
(10, 'GA', 'Georgia'),
(11, 'HI', 'Hawaii'),
(12, 'IL', 'Illinois'),
(13, 'IN', 'Indiana'),
(14, 'IA', 'Iowa'),
(15, 'ID', 'Idaho'),
(16, 'KS', 'Kansas'),
(17, 'KY', 'Kentucky'),
(18, 'LA', 'Louisiana'),
(19, 'MN', 'Minnesota'),
(20, 'ME', 'Maine'),
(21, 'MA', 'Massachusetts'),
(22, 'MI', 'Michigan'),
(23, 'MO', 'Missouri'),
(24, 'MS', 'Mississippi'),
(25, 'MT', 'Montana'),
(26, 'NY', 'New York'),
(27, 'NJ', 'New Jersey'),
(28, 'NM', 'New Mexico'),
(29, 'NH', 'New Hampshire'),
(30, 'NC', 'North Carolina'),
(31, 'ND', 'North Dakota'),
(32, 'NE', 'Nebraska'),
(33, 'NV', 'Nevada'),
(34, 'OH', 'Ohio'),
(35, 'OR', 'Oregon'),
(36, 'OK', 'Oklahoma'),
(37, 'PA', 'Pennsylvania'),
(38, 'RI', 'Rhode Island'),
(39, 'SC', 'South Carolina'),
(40, 'SD', 'South Dakota'),
(41, 'UT', 'Utah'),
(42, 'VT', 'Vermont'),
(43, 'VA', 'Virginia'),
(44, 'WA', 'Washington'),
(45, 'WI', 'Wisconsin'),
(46, 'WY', 'Wyoming'),
(47, 'WV', 'West Virginia'),
(48, 'TX', 'Texas'),
(49, 'TN', 'Tennessee'),
(50, 'DC', 'District of Col'),
(51, 'MD', 'Maryland'),
(52, 'PR', 'Puerto Rico'),
(53, 'VI', 'US Virgin Islan'),
(54, 'AB', 'Alberta'),
(55, 'BC', 'British Columbia'),
(56, 'MB', 'Manitoba'),
(57, 'NB', 'New Brunswick'),
(58, 'NL', 'Newfoundland and Labrador'),
(59, 'NT', 'Northwest Territories'),
(60, 'NS', 'Nova Scotia'),
(61, 'NU', 'Nunavut'),
(62, 'ON', 'Ontario'),
(63, 'PE', 'Prince Edward Island'),
(64, 'QC', 'Quebec'),
(65, 'SK', 'Saskatchewan'),
(66, 'YT', 'Yukon');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
