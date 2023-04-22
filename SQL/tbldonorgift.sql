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
-- Table structure for table `tbldonorgift`
--

DROP TABLE IF EXISTS `tbldonorgift`;
CREATE TABLE IF NOT EXISTS `tbldonorgift` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DonorID` int(11) NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `Date` date NOT NULL,
  `Amount` float NOT NULL DEFAULT 0,
  `Acknowledged` tinyint(1) NOT NULL DEFAULT 0,
  `Note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tbldonorgift`
--

INSERT INTO `tbldonorgift` (`ID`, `DonorID`, `Description`, `Date`, `Amount`, `Acknowledged`, `Note`) VALUES
(1, 1, 'Year End Gift', '2022-12-01', 10000, 1, NULL),
(2, 2, 'Mission Offering', '2023-03-01', 1800, 1, NULL),
(3, 9, NULL, '2022-02-02', 1000, 1, NULL),
(4, 7, 'Gift for Seminarian Support', '2020-10-16', 500, 1, NULL),
(5, 6, 'Mission Support', '2020-08-09', 297, 1, NULL),
(6, 3, 'Where it is needed most', '2020-10-09', 2000, 1, NULL),
(7, 14, 'Seminarian Support', '2019-12-16', 500, 1, NULL),
(8, 2, 'Through Mission Centeral', '2020-02-18', 1561.85, 1, NULL),
(9, 15, 'Mission Support', '2019-10-01', 1400, 1, NULL),
(10, 4, 'General Fund', '2020-07-01', 200, 1, NULL),
(11, 4, 'Seminarian Support', '2020-10-16', 500, 1, NULL),
(12, 6, 'Mission Support', '2020-04-30', 84, 1, NULL),
(13, 5, 'Mission Support', '2020-06-17', 100, 1, NULL),
(14, 5, 'Mission Support', '2020-10-20', 100, 1, NULL),
(15, 4, 'General Fund', '2020-08-05', 200, 1, NULL),
(16, 5, 'Mission Support', '2020-07-21', 100, 1, NULL),
(17, 6, 'Mission Support', '2020-06-30', 312.6, 1, NULL),
(18, 5, 'Mission Support', '2020-09-15', 100, 1, NULL),
(19, 6, '3rd Qtr Missions', '2020-09-30', 256, 1, NULL),
(20, 6, 'Mission Support', '2020-08-14', 41, 1, NULL),
(21, 5, 'Mission Support', '2019-09-13', 100, 1, NULL),
(22, 5, 'Mission Support', '2019-10-15', 100, 1, NULL),
(23, 5, 'Mission Support', '2019-12-19', 100, 1, NULL),
(24, 5, 'Mission Support', '2020-01-21', 100, 1, NULL),
(25, 5, 'Mission Support', '2020-02-18', 100, 1, NULL),
(26, 5, 'Mission Support', '2020-03-17', 100, 1, NULL),
(27, 5, 'Mission Support', '2020-07-21', 100, 1, NULL),
(28, 5, 'Mission Support', '2020-06-17', 100, 1, NULL),
(29, 5, 'Mission Support', '2020-10-20', 100, 1, NULL),
(30, 5, 'Mission Support', '2020-09-15', 100, 1, NULL),
(31, 4, 'General Fund', '2019-09-10', 100, 1, NULL),
(32, 4, 'General Fund', '2019-12-30', 100, 1, NULL),
(33, 4, 'General Fund', '2020-08-05', 200, 1, NULL),
(34, 6, '4th Qtr Mission Support', '2020-12-31', 2396.8, 1, NULL),
(35, 5, 'Mission Support', '2020-12-22', 100, 1, NULL),
(36, 5, 'Mission Support', '2020-02-17', 100, 1, NULL),
(37, 6, '1st Qtr Mission Support', '2021-03-21', 556.59, 1, NULL),
(38, 5, 'Mission Support', '2021-04-20', 100, 1, NULL),
(39, 6, '2nd Qtr Mission Support', '2021-06-30', 541.63, 1, NULL),
(40, 5, 'Mission Support', '2021-06-30', 100, 1, NULL),
(41, 5, 'Mission Support', '2021-08-17', 100, 1, NULL),
(42, 5, 'Mission Support', '2021-07-21', 100, 1, NULL),
(43, 5, 'Mission Support', '2021-10-18', 100, 1, NULL),
(44, 5, 'Mission Support', '2021-09-21', 100, 1, NULL),
(45, 6, '3rd Qtr Mission Support', '2021-09-30', 375, 1, NULL),
(46, 16, 'General Fund', '2022-02-02', 1000, 1, NULL),
(47, 10, 'Mission ', '2020-04-30', 84, 1, NULL),
(48, 7, 'General Fund', '2020-08-05', 200, 1, NULL),
(49, 5, 'Mission Support', '2019-08-22', 100, 1, NULL),
(50, 4, 'General Fund', '2019-11-27', 100, 1, NULL),
(51, 6, 'Mission Support', '2021-09-30', 375, 1, NULL),
(52, 6, 'Mission Support', '2020-12-31', 1296.8, 1, NULL),
(53, 5, 'Mission Support', '2021-02-17', 100, 1, NULL),
(54, 6, 'Mission Support', '2021-12-31', 1205.55, 1, NULL),
(55, 5, 'Mission Support', '2022-01-18', 100, 1, NULL),
(56, 4, 'Seminarian Support', '2021-10-05', 200, 1, NULL),
(57, 14, 'Unrestricted', '2021-10-05', 1000, 1, NULL),
(58, 5, 'Mission Support', '2021-05-18', 100, 1, NULL),
(59, 4, 'Seminarian Support', '2021-02-02', 200, 1, NULL),
(60, 2, 'Mission Support', '2021-01-13', 1881.25, 1, NULL),
(61, 8, 'Unrestricted', '2020-12-21', 1000, 1, NULL),
(62, 4, 'Seminarian Support', '2021-01-04', 200, 1, NULL),
(63, 6, 'Mission Support', '2019-09-30', 354.5, 1, NULL),
(64, 6, 'Mission Support', '2019-12-31', 866.49, 1, NULL),
(65, 6, 'Mission Support', '2019-08-19', 145.81, 1, NULL),
(66, 6, 'Mission Support', '2019-09-30', 354.5, 1, NULL),
(67, 10, 'Mission Support', '2019-12-30', 253.8, 1, NULL),
(68, 2, 'Mission Support', '2019-02-16', 1952.5, 1, NULL),
(69, 11, 'Mission Support', '2018-12-27', 100, 1, NULL),
(70, 11, 'Mission Support', '2018-12-26', 250, 1, NULL),
(71, 15, 'Mission Support', '2019-01-20', 700, 1, NULL),
(72, 6, 'Mission Support', '2018-12-31', 1317.37, 1, NULL),
(73, 5, 'Mission Support', '2019-01-15', 100, 1, NULL),
(74, 5, 'Mission Support', '2019-02-15', 100, 1, NULL),
(75, 5, 'Mission Support', '2020-04-14', 100, 1, NULL),
(76, 7, 'Mission Support', '2020-04-19', 200, 1, NULL),
(77, 7, 'Unrestricted', '2019-06-27', 1000, 1, NULL),
(78, 15, 'Mission Support', '2019-04-01', 700, 1, NULL),
(79, 5, 'Mission Support', '2019-03-18', 100, 1, NULL),
(80, 5, 'Mission Support', '2019-04-15', 100, 1, NULL),
(81, 5, 'Mission Support', '2019-03-16', 100, 1, NULL),
(82, 5, 'Mission Support', '2019-06-17', 100, 1, NULL),
(83, 5, 'Mission Support', '2019-07-31', 100, 1, NULL),
(84, 6, 'Mission Support', '2022-12-31', 949.7, 0, NULL),
(85, 6, 'Mission Support', '2022-03-31', 525.68, 0, NULL),
(86, 4, 'General Fund', '2022-03-14', 200, 0, NULL),
(87, 5, 'Mission Support', '2022-03-11', 100, 0, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
