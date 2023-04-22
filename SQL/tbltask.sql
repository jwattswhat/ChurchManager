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
-- Table structure for table `tbltask`
--

DROP TABLE IF EXISTS `tbltask`;
CREATE TABLE IF NOT EXISTS `tbltask` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Task` varchar(255) NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `Complete` tinyint(4) NOT NULL DEFAULT 0,
  `CompletionDate` date DEFAULT NULL,
  `Priority` int(11) NOT NULL DEFAULT 1,
  `ProjectID` int(11) NOT NULL,
  `DependencyID` varchar(255) DEFAULT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tbltask`
--

INSERT INTO `tbltask` (`ID`, `Task`, `Description`, `Complete`, `CompletionDate`, `Priority`, `ProjectID`, `DependencyID`, `StartDate`, `EndDate`, `Note`) VALUES
(3, 'Remove Floor ', 'Remove Floor from the old cafeteria', 0, NULL, 1, 5, NULL, NULL, NULL, NULL),
(4, 'Remove Foundations', 'Remove the foundation from the old cafeteria', 0, NULL, 1, 5, 'Remove Floor', NULL, NULL, NULL),
(5, 'Shape Bank', 'Shape the Bank Along the Highway', 0, NULL, 1, 15, NULL, NULL, NULL, NULL),
(6, 'Cut Down Weeds', 'Cut Down Weeds on the Whole Property', 0, NULL, 1, 15, NULL, NULL, NULL, NULL),
(7, 'Plan Grass Cutting', 'Make a plan for cutting the grass', 0, NULL, 1, 15, 'Old Foundations', NULL, NULL, 'Monthly Signup?'),
(8, 'Remove Debris', 'Remove Debris from Property', 0, NULL, 1, 15, NULL, NULL, NULL, NULL),
(9, 'Parsonage Flowerbed', 'Plant Flowers in the Parsonage Flowerbeds', 0, NULL, 1, 15, NULL, NULL, NULL, NULL),
(10, 'Clear Trees', 'Cut out unwanted trees', 0, NULL, 1, 15, NULL, NULL, NULL, ''),
(11, 'Manage Creeks', 'Clear Dead Brush & Growth in Creeks', 0, NULL, 1, 15, NULL, NULL, NULL, ''),
(12, 'Church Sign', 'Level & Clear area around the sign', 0, NULL, 1, 15, NULL, NULL, NULL, 'Add Flowers?'),
(13, 'Determine Usage', 'Determine which mound is in use', 0, NULL, 1, 17, NULL, NULL, NULL, ''),
(14, 'Septic Lids', 'Clear around the septic lids to make accessable', 0, NULL, 1, 17, NULL, NULL, NULL, ''),
(15, 'Sacristy Chair', 'Fasten down sanctuary chair', 0, NULL, 1, 21, NULL, NULL, NULL, NULL),
(16, 'Sacristy Lighting', 'Fix the Lighting in the Sacristy', 0, NULL, 1, 21, NULL, NULL, NULL, NULL),
(17, 'Water Heater', 'Enclose the water heater in the bathroom', 0, NULL, 1, 21, NULL, NULL, NULL, NULL),
(18, 'Gutters', 'Repair, Replace or Remove Gutters', 0, NULL, 1, 21, NULL, NULL, NULL, NULL),
(19, 'Finish Construction', 'Finish Upstairs Parsonage', 0, NULL, 1, 22, NULL, NULL, NULL, NULL),
(20, 'Front Porch', 'Water Seal the Outdoor Parsonage Front Porch', 0, NULL, 1, 22, NULL, NULL, NULL, NULL),
(21, 'Sump Pump Drain Pipe', 'Replace Parsonage Sump Pump Drain Pipe', 0, NULL, 1, 22, NULL, NULL, NULL, NULL),
(22, 'Front Porch Leak', 'Fix the leak on the parsonage front porch', 0, NULL, 1, 22, NULL, NULL, NULL, NULL),
(23, 'Crosses', 'Add Crosses to the Outdoor Worship Center', 0, NULL, 1, 23, NULL, NULL, NULL, NULL),
(24, 'Seating', 'Add Seating for the Outdoor Worship Center', 0, NULL, 1, 23, NULL, NULL, NULL, NULL),
(25, 'Add Beds', 'Add Beds to the Upper Garage', 0, NULL, 1, 13, NULL, NULL, NULL, NULL),
(26, 'Replace Door ', 'Replace Door on Upper Garage', 0, NULL, 1, 13, NULL, NULL, NULL, NULL),
(27, 'Remove Foundations', 'Remove foundations from removed buildings', 0, NULL, 1, 15, NULL, NULL, NULL, NULL),
(28, 'May', 'Lawn Mowing May', 0, NULL, 1, 25, NULL, '2023-05-01', '2023-05-31', NULL),
(29, 'June', 'Lawn Mowing June', 0, NULL, 1, 25, NULL, '2023-06-01', '2023-06-30', NULL),
(30, 'July', 'Lawn Mowing July', 0, NULL, 1, 25, NULL, '2023-07-01', '2023-07-31', NULL),
(31, 'August', 'Lawn Mowing August', 0, NULL, 1, 25, NULL, '2023-08-01', '2023-08-31', NULL),
(32, 'September', 'Lawn Mowing September', 0, NULL, 1, 25, NULL, '2023-09-01', '2023-09-30', NULL),
(33, 'January 2023', 'Cradle Role January 2023', 0, NULL, 1, 27, NULL, '2023-01-01', '2023-03-31', NULL),
(34, 'April 2023', 'Cradle Role April 2023', 0, NULL, 1, 27, NULL, '2023-04-01', '2023-06-30', NULL),
(35, 'July 2023', 'Cradle Role July 2023', 0, NULL, 1, 27, NULL, '2023-07-01', '2023-09-30', NULL),
(36, 'October 2023', 'Cradle Role October 2023', 0, NULL, 1, 27, NULL, '2023-10-01', '2023-12-31', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
