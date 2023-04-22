-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:43 PM
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
-- Database: `jsform`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbloptions`
--

DROP TABLE IF EXISTS `tbloptions`;
CREATE TABLE IF NOT EXISTS `tbloptions` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OptionFor` varchar(255) NOT NULL,
  `OptionType` varchar(255) NOT NULL,
  `OptionValue` longtext NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `For Type` (`OptionFor`,`OptionType`) USING HASH
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tbloptions`
--

INSERT INTO `tbloptions` (`ID`, `OptionFor`, `OptionType`, `OptionValue`, `Note`) VALUES
(2, 'Permissions', 'Liturgy', 'Liturgy Used by Permission Concordia Publishing House #000014722', '[Liturgy Used by Permission Concordia Publishing House #000014722]'),
(3, 'Permissions', 'OneLicense', '#A-741154', '[Expires 31-Dec-23]'),
(5, 'Lectionary', 'Current', 'LCMS-A', NULL),
(6, 'JSONSchema', 'CheckForms', 'Yes', '[Use JsonSchema to check for valid forms. Valid Values are \"Yes\" and \"No\"]');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
