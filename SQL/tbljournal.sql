-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:13 PM
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
-- Table structure for table `tbljournal`
--

DROP TABLE IF EXISTS `tbljournal`;
CREATE TABLE IF NOT EXISTS `tbljournal` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Event` varchar(255) NOT NULL,
  `Complete` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` datetime DEFAULT NULL,
  `EndDate` datetime DEFAULT NULL,
  `Note` longtext CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tbljournal`
--

INSERT INTO `tbljournal` (`ID`, `ChurchID`, `Event`, `Complete`, `StartDate`, `EndDate`, `Note`) VALUES
(1, 0, 'Mission / Vision Process', 1, '2022-05-19 00:00:00', '2022-10-19 00:00:00', 'The Vision Statement was Adopted October 19.\r\n\r\nAlive in Christ bringing Life in Christ\r\n\r\nAlive in Christ\r\n- We are alive! Baptized into Christ’s life, death, and resurrection.\r\n- We are alive to serve our neighbors\r\nBringing\r\n- Bringing is an ongoing activity…\r\n- We bring what we have been given to bring. And it all depends on the work of the Holy Spirit\r\n- We bring it by the Means of Grace - Preaching, Word, Sacraments, and Law and Gospel\r\n- We bring it by a personal witness of Jesus’ Work\r\n- We bring it by showing Christ-like attitudes and serving our neighbor.\r\nLife In Christ\r\n- Life in Christ is our Church. Together, we are God’s people, inviting other to be with us as well.\r\n- Bringing people to Life in Christ'),
(2, 0, 'Election of Officers for 2023', 1, '2022-12-07 16:30:00', '2022-12-07 16:30:00', 'Election for Officers for 2023\r\nPresident Jay Mesenbring\r\nVice-President Greg Gecas\r\nTreasure-Bob Mesenbring\r\nElders-Jay Mesenbring, Greg Gecas\r\nTreasurer-Vacant'),
(3, 0, 'Master Plan Committee', 0, '2022-11-16 18:30:00', NULL, NULL),
(4, 0, '2022 - 4th Quarter Voter\'s Meeting 2023 ', 1, '2023-01-11 00:00:00', '2023-01-11 00:00:00', '2023 - Budget Adopted'),
(5, 0, '2022 - Services at Gunflint Lake', 1, '2022-07-03 00:00:00', '2022-08-28 00:00:00', '9 Services Sunday 11:30am'),
(6, 0, '2023 Strategic Planning Meeting', 1, '2023-02-19 00:00:00', '2023-02-19 00:00:00', NULL),
(7, 0, 'Special Voters Meeting', 1, '2023-01-22 10:22:00', '2023-01-22 10:22:00', 'Logo accepted.'),
(8, 0, '2023 - 1st Quarterly Voters Meeting', 1, '2023-04-12 18:30:00', '2023-04-12 18:30:00', 'Changes to the Bylaws presented\r\nApproved 2023 Gunflint Services. July and August, Possibly 1st Sunday in September.');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
