-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:07 PM
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
-- Table structure for table `tblaltreading`
--

DROP TABLE IF EXISTS `tblaltreading`;
CREATE TABLE IF NOT EXISTS `tblaltreading` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ServiceID` int(11) NOT NULL,
  `Reading` varchar(255) DEFAULT NULL,
  `Reference` varchar(255) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblaltreading`
--

INSERT INTO `tblaltreading` (`ID`, `ServiceID`, `Reading`, `Reference`, `Note`) VALUES
(4, 20, 'First', 'Revelation 22:20', NULL),
(5, 20, 'Second', 'Matthew 13:1-9', NULL),
(6, 20, 'Third', 'Ephesians 6:10-20', NULL),
(7, 22, 'First', 'Matthew 13:5-6; 20-21', NULL),
(8, 22, 'Second', 'Luke 10:38-42', NULL),
(9, 24, 'First', 'Matthew 13:7,22', NULL),
(10, 24, 'Second', '2 Peter 3:10-13', NULL),
(11, 42, 'First', '2 Sammuel 11,12', NULL),
(12, 44, 'First', '2 Samuel 15:1–16, 2 Samuel 18:1–18', '[Need to pick out relevant verses.]'),
(13, 44, 'Second', 'Psalm 13', NULL),
(14, 46, 'Second', 'Mark 26:35-50', NULL),
(15, 46, 'Third', 'Galatians 4:1-7', NULL),
(16, 46, 'First', 'The Third Petition of the Lords Prayer', NULL),
(17, 48, 'First', 'Luke 23:26-41', NULL),
(18, 50, 'First', 'Luke 2:22-35', NULL),
(19, 53, 'Psalm', 'Psalm 122', NULL),
(20, 51, 'First', 'The Passion of Our Lord Jesus Christ', NULL),
(21, 51, 'First', NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
