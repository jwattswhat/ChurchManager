-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:09 PM
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
-- Table structure for table `tblchecklist`
--

DROP TABLE IF EXISTS `tblchecklist`;
CREATE TABLE IF NOT EXISTS `tblchecklist` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `CheckList` longtext NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblchecklist`
--

INSERT INTO `tblchecklist` (`ID`, `Name`, `CheckList`) VALUES
(0, 'Default', '{\"Hymns, Selected\": \"False\", \"Worship Planning, Complete\": \"False\", \"Worship Planning, Printed\": \"False\", \"Participants Scheduled\": \"False\", \"Participants Notified\": \"False\", \"Bulletin, Prepared\": \"False\", \"Bulletin, Printed\": \"False\", \"Sermon, Prepared\": \"False\", \"Sermon, Printed\": \"False\", \"Sermon, Posted to Blog\": \"False\", \"Prayers, Printed\": \"False\"}'),
(2, 'Add: No Organist', '{\"Concordia Organist, Prepared\": \"False\"}'),
(6, 'No Sermon', '{\"Hymns, Selected\": \"False\", \"Worship Planning, Complete\": \"False\", \"Worship Planning, Printed\": \"False\", \"Participants Scheduled\": \"False\", \"Participants Notified\": \"False\", \"Bulletin, Prepared\": \"False\", \"Bulletin, Printed\": \"False\", \"Prayers, Printed\": \"False\"}'),
(3, 'WeekDay', '{\"Hymns, Selected\": \"False\", \"Worship Planning, Complete\": \"False\", \"Worship Planning, Printed\": \"False\", \"Participants Scheduled\": \"False\", \"Particpiants Notified\": \"False\", \"Readings, Selected\":\"False\",\"Readings, Printed\":\"False\",\"Bulletin, Prepared\": \"False\", \"Bulletin, Printed\": \"False\", \"Sermon, Prepared\": \"False\", \"Sermon, Printed\": \"False\", \"Prayers, Printed\": \"False\"}'),
(4, 'MSLNorthland', '{\"Hymns, Selected\": \"False\", \"Worship Planning, Complete\": \"False\", \"Sermon, Prepared\": \"False\", \"Sermon, Printed\": \"False\", \"Documents, Printed\": \"False\"}'),
(5, 'Hestons', '{\"Hymns, Selected\": \"False\", \"Worship Planning, Complete\": \"False\", \"Worship Planning, Printed\": \"False\", \"Participants Scheduled\": \"False\", \"Particpiants Notified\": \"False\", \"Bulletin, Prepared\": \"False\", \"Bulletin, Printed\": \"False\", \"Bulletin, Posted to Website\": \"False\", \"Sermon, Prepared\": \"False\", \"Sermon, Printed\": \"False\", \"Sermon, Posted to Blog\": \"False\", \"Prayers, Printed\": \"False\", \"Concordia Organist, Prepared\": \"False\"}');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
