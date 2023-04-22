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
-- Table structure for table `tbldonor`
--

DROP TABLE IF EXISTS `tbldonor`;
CREATE TABLE IF NOT EXISTS `tbldonor` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT 0,
  `Name` varchar(255) NOT NULL,
  `Phone` varchar(255) DEFAULT NULL,
  `eMail` varchar(255) DEFAULT NULL,
  `Address` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `Address2` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `City` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `State` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `Zip` varchar(255) DEFAULT NULL,
  `Note` longtext CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tbldonor`
--

INSERT INTO `tbldonor` (`ID`, `ChurchID`, `Name`, `Phone`, `eMail`, `Address`, `Address2`, `City`, `State`, `Zip`, `Note`) VALUES
(1, 0, 'Christian & Cindy Preus', NULL, 'capreus@outlook.com', '11 N Loon Lake Rd', NULL, 'Grand Marais', 'MN', '55604', NULL),
(2, 0, 'Fergus Falls Circuit Minnesota North District, LCMS', '(651)231-5934', 'pastortj@live.com', '2801 32nd St. S', NULL, 'Moorhead', 'MN', '56560', NULL),
(3, 0, 'Rolland and Mary Adkins', NULL, NULL, '200 North Loon Lake Rd ', NULL, 'Grand Maris', 'MN', '55604', NULL),
(4, 0, 'Ruth and Stephen Saunders', NULL, NULL, '900 E Elm Rd', NULL, 'Oak Creek', 'WI', '53154-6472', NULL),
(5, 0, 'Redeemer Lutheran Church Ladies Guild', NULL, NULL, '500 Centeral Ave.', NULL, 'Aurora', 'MN', '55705', NULL),
(6, 0, 'St. Johns Lutheran Church (Hutchinson)', NULL, NULL, '60929 110th Street', NULL, 'Hutchinson', 'MN', '55350', NULL),
(7, 0, 'Erik & Jody Preus', NULL, NULL, '15231 Elm Road North', NULL, 'Maple Grove', 'MN', '55311', NULL),
(8, 0, 'Christian Preus', NULL, NULL, '4770 Underwood Lne N, Unit G', NULL, 'Plymouth', 'MN', '55442-2373', NULL),
(9, 0, 'Rober & Marth Ulmer', NULL, NULL, '21300 W 106th St', NULL, 'Olathe', 'KS', '66061-9775', NULL),
(10, 0, 'St. Johns Lutheran Church (Hinckly)', NULL, NULL, '2158 Velvet ST', NULL, 'Hinckly', 'MN', '55037', NULL),
(11, 0, 'Yvonne Hogie Streich', NULL, NULL, '451 County Rd 8 SW', NULL, 'Buffalo', 'MN', '50003', NULL),
(12, 0, 'Rev. Richard & Barbara Resch', NULL, NULL, '2221 Youngman Ave Apt 403', NULL, 'St. Paul ', 'MN', '55163078', '[Unsure apt #]'),
(14, 0, 'Erik Robert Preus', NULL, NULL, '15231 Elm Road', NULL, 'Maple Grove', 'MN', '55611', NULL),
(15, 0, 'Gloria Dei Lutheran Church', '(218)741-1977', NULL, '6959 Highway 169', NULL, 'Virginia', 'MN', '55792', NULL),
(16, 0, 'Bob & Martha Ulmer', NULL, NULL, NULL, NULL, 'Kansas City', 'KS', NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
