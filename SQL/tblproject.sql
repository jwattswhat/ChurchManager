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
-- Table structure for table `tblproject`
--

DROP TABLE IF EXISTS `tblproject`;
CREATE TABLE IF NOT EXISTS `tblproject` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `Project` varchar(255) NOT NULL,
  `Description` varchar(255) NOT NULL,
  `Complete` tinyint(1) NOT NULL DEFAULT 0,
  `CompletionDate` date DEFAULT NULL,
  `ProjectCategory` varchar(255) NOT NULL,
  `Priority` int(11) NOT NULL DEFAULT 1,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `AssignedTo` int(11) DEFAULT NULL,
  `AssignedToText` varchar(255) DEFAULT NULL,
  `Note` longtext CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblproject`
--

INSERT INTO `tblproject` (`ID`, `ChurchID`, `Project`, `Description`, `Complete`, `CompletionDate`, `ProjectCategory`, `Priority`, `StartDate`, `EndDate`, `AssignedTo`, `AssignedToText`, `Note`) VALUES
(5, 0, 'Old Cafeteria', 'Finish Removal of the Old Cafeteria', 0, NULL, 'Property', 1, NULL, NULL, 165, NULL, '[Spring 2023]'),
(23, 0, 'Update OWC', 'Update the Outdoor Worship Center', 0, NULL, 'Outdoor Worship Center', 1, NULL, NULL, NULL, NULL, NULL),
(13, 0, 'Maintain Garage', 'Maintain the Garage', 0, NULL, 'Garage', 1, NULL, NULL, NULL, NULL, NULL),
(15, 0, 'Manage Landscape', 'Manage Landsacpe', 0, NULL, 'Property', 1, NULL, NULL, NULL, NULL, NULL),
(17, 0, 'Ceptic', 'Identify Ceptic Issues', 0, NULL, 'Property', 1, NULL, NULL, NULL, NULL, NULL),
(22, 0, 'Maintain Parsonage', 'Maintain Parsonage', 0, NULL, 'Parsonage', 1, NULL, NULL, NULL, NULL, NULL),
(21, 0, 'Maintain Church', 'Maintain the Church Building', 0, NULL, 'Church', 1, NULL, NULL, NULL, NULL, NULL),
(25, 0, 'Lawn Mowing', 'Monthly Lawn Mowing 2023', 0, NULL, 'Property', 1, '2023-05-01', '2022-09-30', NULL, 'Elders', NULL),
(27, 0, 'Cradle Role', 'Cradle Role', 0, '2023-03-21', 'Ministry', 1, NULL, NULL, NULL, NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
