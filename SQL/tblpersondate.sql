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
-- Table structure for table `tblpersondate`
--

DROP TABLE IF EXISTS `tblpersondate`;
CREATE TABLE IF NOT EXISTS `tblpersondate` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) NOT NULL,
  `DateType` varchar(255) NOT NULL,
  `Date` date NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblpersondate`
--

INSERT INTO `tblpersondate` (`ID`, `PersonID`, `DateType`, `Date`, `Note`) VALUES
(36, 30, 'BirthDate', '1961-12-28', NULL),
(37, 166, 'BirthDate', '1950-08-28', NULL),
(38, 166, 'BaptismDate', '1950-11-18', NULL),
(39, 166, 'Confirmation', '1965-06-06', NULL),
(41, 164, 'BirthDate', '1958-03-04', NULL),
(42, 1, 'BirthDate', '1958-06-03', NULL),
(43, 2, 'BirthDate', '1963-08-10', NULL),
(44, 2, 'Baptism', '1963-08-25', NULL),
(45, 2, 'Confirmation', '1977-05-01', NULL),
(46, 3, 'BirthDate', '2005-07-21', NULL),
(47, 3, 'Baptism', '2005-07-21', NULL),
(48, 3, 'Confirmation', '2018-10-21', NULL),
(49, 4, 'BirthDate', '2007-06-20', NULL),
(50, 4, 'Baptism', '2007-07-01', NULL),
(51, 7, 'Confirmation', '2018-10-21', NULL),
(52, 8, 'BirthDate', '2007-09-19', NULL),
(53, 21, 'Confirmation', '1954-07-15', NULL),
(54, 21, 'Baptism', '1940-11-17', NULL),
(55, 20, 'Baptism', '1936-08-23', NULL),
(56, 20, 'Confirmation', '1950-04-02', NULL),
(57, 166, 'BirthDate', '1950-08-25', NULL),
(58, 167, 'BirthDate', '1945-05-26', NULL),
(59, 42, 'BirthDate', '1989-05-04', NULL),
(60, 42, 'Baptism', '1989-05-14', NULL),
(61, 42, 'Confirmation', '2004-05-02', NULL),
(62, 41, 'BirthDate', '1987-02-01', NULL),
(63, 41, 'Baptism', '1987-02-15', NULL),
(64, 41, 'Confirmation', '2000-05-21', NULL),
(65, 164, 'BirthDate', '1958-03-04', NULL),
(66, 31, 'BirthDate', '1998-06-10', ''),
(72, 31, 'Transfer Out', '2023-04-12', '[Transferred to \r\nMessiah Lutheran Church\r\nLincoln, NE]'),
(69, 162, 'Baptism', '2021-10-24', NULL),
(70, 170, 'BirthDate', '2021-04-27', NULL),
(71, 170, 'Baptism', '2021-05-01', NULL),
(74, 30, 'Installation', '2018-09-01', NULL),
(75, 30, 'Ordination', '2001-06-01', NULL),
(76, 41, 'Transfer In', '2019-06-25', NULL),
(77, 42, 'Transfer In', '2019-06-25', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
