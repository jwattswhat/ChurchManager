-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 08, 2022 at 07:45 PM
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
-- Table structure for table `tblchoices`
--

DROP TABLE IF EXISTS `tblchoices`;
CREATE TABLE IF NOT EXISTS `tblchoices` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Field` varchar(255) NOT NULL,
  `Choices` longtext NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblchoices`
--

INSERT INTO `tblchoices` (`ID`, `Field`, `Choices`, `Note`) VALUES
(19, 'Status', 'Active', NULL),
(20, 'AddressLabel', 'Home', NULL),
(21, 'ContactLabel', 'Main', NULL),
(22, 'ContactType', 'Phone', NULL),
(23, 'ConfigType', 'FormLocation', NULL),
(24, 'AddressLabel', 'Main', NULL),
(25, 'DateType', 'BirthDate', NULL),
(26, 'DateType', 'MarriageDate', NULL),
(27, 'MarriageStatus', 'Single', NULL),
(28, 'MarriageStatus', 'Married', NULL),
(29, 'MarriageStatus', 'Divorced', NULL),
(30, 'MarriageStatus', 'Unknown', NULL),
(31, 'MarriageStatus', 'Widowed', NULL),
(32, 'Status', 'Accociate', NULL),
(33, 'Status', 'At School', NULL),
(34, 'Status', 'Deceased', NULL),
(35, 'Status', 'Non Member', NULL),
(36, 'Status', 'Prospect', NULL),
(37, 'Status', 'Visitor', NULL),
(38, 'Status', 'Prospect', NULL),
(39, 'Status', 'Inactive', NULL),
(40, 'ContactLabel', 'Mobile', NULL),
(41, 'ContactLabel', 'Home', NULL),
(42, 'ContactLabel', 'Work', NULL),
(43, 'ContactType', 'eMail', NULL),
(44, 'ContactType', 'Text', NULL),
(45, 'DateType', 'Baptism', NULL),
(46, 'DateType', 'Confirmation', NULL),
(47, 'DateType', 'Membership', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tblchurch`
--

DROP TABLE IF EXISTS `tblchurch`;
CREATE TABLE IF NOT EXISTS `tblchurch` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Church` varchar(255) NOT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `Address2` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT 'Grand Marais',
  `State` varchar(255) DEFAULT 'MN',
  `Zip` varchar(255) DEFAULT NULL,
  `Pastor` varchar(255) DEFAULT NULL,
  `Phone` varchar(255) DEFAULT NULL,
  `eMail` varchar(255) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblchurch`
--

INSERT INTO `tblchurch` (`ID`, `Church`, `Address`, `Address2`, `City`, `State`, `Zip`, `Pastor`, `Phone`, `eMail`, `Note`) VALUES
(0, 'Life in Christ Lutheran Church', '2017 West Hwy 61', 'PO Box 765', 'Grand Marais', 'MN', '55604', NULL, NULL, NULL, NULL),
(2, 'Augsburg Lutheran Church', '13902 W 67th St', NULL, 'Shawnee', 'KS', '66216-2306', 'Rev. Jay watson', '9134036194', 'paterjww@sbcglobal.net', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tblchurchinfo`
--

DROP TABLE IF EXISTS `tblchurchinfo`;
CREATE TABLE IF NOT EXISTS `tblchurchinfo` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT NULL,
  `InfoType` varchar(255) DEFAULT NULL,
  `InfoValue` varchar(255) NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `ChurchID` (`ChurchID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

-- --------------------------------------------------------

--
-- Table structure for table `tblconfig`
--

DROP TABLE IF EXISTS `tblconfig`;
CREATE TABLE IF NOT EXISTS `tblconfig` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ConfigType` varchar(100) NOT NULL,
  `ConfigValue` varchar(255) NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ConfigType` (`ConfigType`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblconfig`
--

INSERT INTO `tblconfig` (`ID`, `ConfigType`, `ConfigValue`, `Note`) VALUES
(4, 'FormLocation', '.\\Forms\\', NULL),
(5, 'PictureLocation', '.\\Pictures\\', NULL),
(6, 'ReportLocation', '.\\Reports\\', NULL),
(7, 'FontPointSize', '10', NULL),
(8, 'FontFamily', '74', NULL),
(9, 'FontStyle', '90', NULL),
(10, 'FontWeight', '400', NULL),
(11, 'FontFace', 'Calibri', NULL),
(12, 'FontUnderlined', 'False', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tblfamily`
--

DROP TABLE IF EXISTS `tblfamily`;
CREATE TABLE IF NOT EXISTS `tblfamily` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyName` varchar(255) NOT NULL,
  `ChurchID` int(11) DEFAULT NULL,
  `MarriageStatus` varchar(255) DEFAULT NULL,
  `Directory` tinyint(1) DEFAULT 0,
  `Picture` varchar(255) DEFAULT NULL,
  `Magazine` tinyint(1) NOT NULL DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=122 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblfamily`
--

INSERT INTO `tblfamily` (`ID`, `FamilyName`, `ChurchID`, `MarriageStatus`, `Directory`, `Picture`, `Magazine`, `Note`) VALUES
(1, 'Berglund, David & Heidi', 0, 'Married', 1, NULL, 1, ''),
(2, 'Berglund, Danny & Rachel', 0, 'Married', 1, 'Berglund.Danny & Rachael.jpg', 1, ''),
(3, 'Bockovich,', 0, 'Married', 0, NULL, 0, NULL),
(4, 'Gecas, Greg & Barb', 0, 'Married', 1, 'Gecas.Greg & Bab.jpg', 1, ''),
(5, 'Mesenbring, Jay & Lisa', 0, 'Married', 1, 'Mesenbring.Jay & Lisa.jpg', 0, ''),
(6, 'Mesenbring, Bob & Gen', 0, 'Married', 1, 'Mesenbring.Bob & Jan.jpg', 1, ''),
(7, 'Lashinski, Jason & Sherrie', 0, 'Married', 0, NULL, 0, ''),
(8, 'Higgins, Paul & Caroline', 0, 'Married', 1, NULL, 1, NULL),
(9, 'Raymond, Mike', 0, 'Single', 1, NULL, 1, ''),
(10, 'Ulmer, Bob & Martha', 1, 'Married', 0, NULL, 0, ''),
(11, 'Watt, Jonathan', 0, 'Divorced', 1, NULL, 0, ''),
(14, 'Damschen, Daniel & Janice', 0, 'Widowed', 0, NULL, 0, ''),
(18, 'Saunders, Erik & Katherine', 0, 'Married', 1, 'Saunders.Erik & Katie.jpg', 1, ''),
(19, 'Gecas, Paul', 0, 'Single', 1, 'Gecas.Paul.jpg', 1, ''),
(69, 'Gesch, Dave', 0, 'Unknown', 0, NULL, 0, ''),
(70, 'Lisuth, Ed', 0, 'Unknown', 0, NULL, 0, ''),
(71, 'Saunders, Steve', 0, 'Unknown', 0, NULL, 0, ''),
(72, 'Preus, Rolf', 0, 'Unknown', 0, NULL, 0, ''),
(73, 'Preus, Daniel & Linda', 0, 'Unknown', 1, NULL, 0, NULL),
(75, 'Benolkin, Dan', 0, 'Unknown', 0, NULL, 0, ''),
(76, 'Nemiz, Randy', 0, 'Unknown', 0, NULL, 0, ''),
(77, 'Kolhoff', 0, 'Unknown', 0, NULL, 0, ''),
(78, 'Higgins', 0, 'Unknown', 0, NULL, 0, NULL),
(79, 'Anderson, Jerry', 0, 'Unknown', 0, NULL, 0, 'Jay\'s Friend\r\nFrequent Visitor\r\nNon-LCMS'),
(80, 'Flack, Mike & Carol', 0, 'Unknown', 0, NULL, 0, 'Carole is Wisconsin Synod\r\nMike is Baptist'),
(81, 'Heston, Geri', 0, 'Unknown', 0, NULL, 0, 'Sister to Greg Gecas\r\nNot connected to any church'),
(82, 'LeTourneu, Jim & Sharlene', 0, 'Unknown', 0, NULL, 0, 'Mother of Greg Gecas\r\nJim has alzheimers\r\nAttending at Hestons Lodge'),
(83, 'Lushinski, Jason & Sherri', 0, 'Unknown', 0, NULL, 0, 'LCMS Background\r\nAttend occasionally \r\nLive at Devil Track Lake'),
(84, 'Penning, Mark & Cathy', 0, 'Unknown', 0, NULL, 0, 'Right now, because of work schedules, Cathy and I worship in Lutsen.  Should we have a free Sunday from work we will certainly stop in for worship. Mark and Cathy Penning'),
(85, 'Wizykoski, Linda', 0, 'Unknown', 0, NULL, 0, ''),
(86, 'Preus, Luke & Rachel', 0, 'Unknown', 0, NULL, 0, ''),
(87, 'Preus, Christian & Cindy', 0, 'Unknown', 0, NULL, 0, ''),
(88, 'Preus, Janet', 0, 'Unknown', 0, NULL, 0, ''),
(89, 'Schmidt, Bill & Kim', 0, 'Unknown', 0, NULL, 0, ''),
(90, 'Staley, Rochelle', 0, 'Unknown', 0, NULL, 0, ''),
(91, 'Perkins', 0, 'Unknown', 0, NULL, 0, ''),
(92, 'Preus, Seth', 0, 'Unknown', 0, NULL, 0, ''),
(93, 'Sabol, Rev. William', 0, 'Unknown', 0, NULL, 0, ''),
(94, 'Carter, Fritz', 0, 'Unknown', 0, NULL, 0, ''),
(95, 'Nemanic, Brian', 0, 'Unknown', 0, NULL, 0, ''),
(96, 'Watt, Zachariah', 0, 'Unknown', 0, NULL, 0, ''),
(97, 'Watt, Nathaniel', 0, 'Unknown', 0, NULL, 0, ''),
(98, 'Preus, Pete', 0, 'Unknown', 0, NULL, 0, ''),
(99, 'Preus, Cindy', 0, 'Unknown', 0, NULL, 0, ''),
(100, 'Prues, Kristiiana', 0, 'Unknown', 0, NULL, 0, ''),
(101, 'Preus, Erik & Jody', 0, 'Unknown', 0, NULL, 0, ''),
(104, 'Hofius, Pete', 0, 'Unknown', 0, NULL, 0, ''),
(105, 'Kerber, Pat', 0, 'Unknown', 0, NULL, 0, ''),
(106, 'Unknown, Roger', 0, 'Unknown', 0, NULL, 0, ''),
(107, 'Larsen, Steve', 0, 'Unknown', 0, NULL, 0, ''),
(108, 'Bottorff, Lawrence', 0, 'Unknown', 0, NULL, 0, NULL),
(109, 'Micen, Roger', 0, 'Unknown', 0, NULL, 0, ''),
(110, 'Staley, Rochelle', 0, 'Unknown', 0, NULL, 0, ''),
(111, 'Johnson, Rev. Matthew', 0, 'Unknown', 0, NULL, 0, ''),
(113, 'Bergland, Elizabeth', 0, 'Unknown', 0, NULL, 0, ''),
(114, 'Unknown, Daniel', 0, 'Unknown', 0, NULL, 0, ''),
(115, 'None Specified', 0, 'Unknown', 0, NULL, 0, ''),
(116, 'Zimmer, Axel', 0, 'Single', 1, NULL, 1, ''),
(118, 'Stangler, Randy & Lori', 0, 'Married', 1, NULL, 1, NULL),
(119, 'Ringquist, James & Janet', 0, 'Married', 1, 'Ringquist.Jim&Janet.jpg', 1, NULL),
(120, 'Muus, Paul & Bonnie', 0, 'Married', 1, NULL, 0, NULL),
(121, 'Gecas, Addie', 0, NULL, 0, NULL, 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tblfamilyaddress`
--

DROP TABLE IF EXISTS `tblfamilyaddress`;
CREATE TABLE IF NOT EXISTS `tblfamilyaddress` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) DEFAULT NULL,
  `AddressLabel` varchar(255) DEFAULT 'Main',
  `Address` varchar(255) DEFAULT NULL,
  `Address2` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT 'Grand Marais',
  `State` varchar(255) DEFAULT 'MN',
  `Zip` varchar(255) DEFAULT '55604',
  `Unlisted` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblfamilyaddress`
--

INSERT INTO `tblfamilyaddress` (`ID`, `FamilyID`, `AddressLabel`, `Address`, `Address2`, `City`, `State`, `Zip`, `Unlisted`, `StartDate`, `EndDate`, `Note`) VALUES
(1, 1, 'Main', '140 Co Rd 56', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(2, 2, 'Main', '1410 Wahlstrom Rd', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(3, 3, 'Main', '6019 North Rd', '', 'Hoveland', 'MN', '55606-', 0, '0000-00-00', '0000-00-00', NULL),
(4, 4, 'Main', '579 S. Gunflint Lake', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(5, 5, 'Main', '4305 E. Hwy 61', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(6, 6, 'Main', '2347 Co Rd 7', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(7, 7, 'Main', '', 'PO Box 862', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(8, 8, 'Main', '1605 E. Hwy 61', '', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(9, 9, 'Main', '', 'PO Box 871', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(10, 10, 'Main', '', '', 'Kansas City', 'MO', '', 0, '0000-00-00', '0000-00-00', NULL),
(11, 11, 'Main', '2017 W Highway 61', 'PO Box 765', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(12, 14, 'Main', '4913 Winterset Drive', '', 'Minnetonka', 'MN', '55343-8725', 0, '0000-00-00', '0000-00-00', NULL),
(13, 18, 'Main', '1322 Berwick Lane', '', 'New Haven', 'IN', '46774', 0, '0000-00-00', '0000-00-00', NULL),
(14, 19, 'Main', '', 'PO Box 715', 'Grand Marais', 'MN', '55604-', 0, '0000-00-00', '0000-00-00', NULL),
(15, 71, 'Secondary', '175 Mile O Pine', '', 'Grand Maras', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(16, 72, 'Secondary', '171 Mile  O Pine', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(17, 75, 'Main', '14565 268th Ave NW', '', 'Zimmerman', 'MN', '55398', 0, '0000-00-00', '0000-00-00', NULL),
(18, 76, 'Main', '11549 284th Ave NW', '', 'Zimmerman', 'MN', '55398', 0, '0000-00-00', '0000-00-00', NULL),
(19, 77, 'Main', '31065 Co Rd 5 NW', '', 'Princeton', 'MN', '55371', 0, '0000-00-00', '0000-00-00', NULL),
(20, 78, 'Main', 'Linnel Rd', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(21, 79, 'Main', 'PO Box 121', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(22, 80, 'Main', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(23, 81, 'Main', '1322 Berwick Lane', '', '1322 Berwick Lane\r\n\r\nNew Haven', 'IN', '46774', 0, '0000-00-00', '0000-00-00', NULL),
(24, 82, 'Main', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(25, 83, 'Main', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(26, 84, 'Main', '', '', 'Lutsen', 'MN', '', 0, '0000-00-00', '0000-00-00', NULL),
(27, 85, 'Main', '54 Stonegate Rd', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(28, 31, 'School', '198 E Roberts St.', '', 'Seward', 'NE', '96434', 0, '0000-00-00', '0000-00-00', NULL),
(29, 92, 'Main', '2151 E Raw Hide St', '', 'Gilbert', 'AZ', '85296-2739', 0, '0000-00-00', '0000-00-00', NULL),
(31, 93, 'Main', '11346 Wren St. NW', '', 'Coon Rapids', 'MN', '55433', 0, '0000-00-00', '0000-00-00', NULL),
(32, 94, 'Main', '715 E Lincoln Ln', 'Apt O', 'Gardner', 'KS', '66030', 0, '0000-00-00', '0000-00-00', NULL),
(33, 95, 'Main', '7611 Knox Ave', '', 'Richfield', 'MN', '55423', 0, '0000-00-00', '0000-00-00', NULL),
(34, 96, 'Main', '1833 210th Ave', '', 'Fairmont', 'MN', '56031', 0, '0000-00-00', '0000-00-00', NULL),
(35, 97, 'Main', '1833 210th Ave', '', 'Fairmont', 'MN', '56031', 0, '0000-00-00', '0000-00-00', NULL),
(36, 101, 'Main', '171 Mile O\' Pine', '', 'Grand Marais', '', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(38, 103, 'Main', '241 Mile O\' Pine', '', 'Grand Marais', '', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(39, 104, 'Main', '', '', 'Excelser', 'MN', '', 0, '0000-00-00', '0000-00-00', NULL),
(40, 105, 'Main', '', '', 'Mtka', '', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(41, 105, 'Main', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(42, 106, 'Main', '', '', 'Mtka', 'MN', '', 0, '0000-00-00', '0000-00-00', NULL),
(43, 107, 'Main', '', '', 'Burnsville', 'MN', '', 0, '0000-00-00', '0000-00-00', NULL),
(44, 108, 'Main', '', '', 'Grand Marais', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(45, 109, 'Main', '', '', 'Mtka', 'MN', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(46, 119, 'Main', '969 Devil Track Rd', '', 'Grand Marais', '', '55604', 0, '0000-00-00', '0000-00-00', NULL),
(47, 118, 'Main', '4 Beargrease Crossing', '', 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL),
(48, 120, 'Home', NULL, 'PO Box 652', 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL),
(49, 73, 'Home', NULL, NULL, 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL),
(50, 116, 'Home', '2017 West Hwy 61', NULL, 'Grand Marais', 'MN', '55604', 0, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tblfamilycontact`
--

DROP TABLE IF EXISTS `tblfamilycontact`;
CREATE TABLE IF NOT EXISTS `tblfamilycontact` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) DEFAULT NULL,
  `ContactLabel` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `Contact` varchar(255) DEFAULT NULL,
  `Unlisted` tinyint(1) DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblfamilycontact`
--

INSERT INTO `tblfamilycontact` (`ID`, `FamilyID`, `ContactLabel`, `Type`, `Contact`, `Unlisted`, `Note`) VALUES
(1, 1, 'Main', 'Phone', '2183872591', 0, NULL),
(2, 3, 'Main', 'Phone', '2184752499', 0, NULL),
(3, 4, 'Main', 'Phone', '2183882243', 0, NULL),
(4, 5, 'Main', 'Phone', '2184752458', 0, NULL),
(5, 6, 'Main', 'Phone', '2183879282', 0, NULL),
(6, 7, 'Main', 'Phone', '2183872653', 0, NULL),
(7, 8, 'Main', 'Phone', '2183872396', 0, NULL),
(8, 10, 'Main', 'Phone', '9134888702', 0, NULL),
(9, 11, 'Main', 'Phone', '5154620566', 0, NULL),
(10, 11, 'Main', 'eMail', 'Jonathan@WattsWhat.net', 0, NULL),
(13, 82, 'Main', 'Phone', '2183889449', 0, NULL),
(14, 83, 'Main', 'Phone', '2182700384', 0, NULL),
(15, 84, 'Main', 'eMail', 'mmstevepenning@gmail.com', 0, NULL),
(16, 85, 'Main', 'Phone', '2184752482', 0, NULL),
(37, 93, 'Main', 'Phone', '5075256677', 0, NULL),
(38, 94, 'Main', 'Phone', '9139679715', 0, NULL),
(39, 95, 'Main', 'Phone', '9206605476', 0, NULL),
(40, 96, 'Main', 'Phone', '9206605520', 0, NULL),
(41, 97, 'Main', 'Phone', '', 0, NULL),
(42, 120, 'Home', 'Phone', '2183872772', 0, NULL),
(43, 120, 'Mobile', 'Phone', '2183700288', 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tblfamilydate`
--

DROP TABLE IF EXISTS `tblfamilydate`;
CREATE TABLE IF NOT EXISTS `tblfamilydate` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) DEFAULT NULL,
  `DateType` varchar(255) NOT NULL,
  `Date` date NOT NULL,
  `Note` longtext DEFAULT NULL,
  `Picture` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

-- --------------------------------------------------------

--
-- Table structure for table `tblfamilyvisit`
--

DROP TABLE IF EXISTS `tblfamilyvisit`;
CREATE TABLE IF NOT EXISTS `tblfamilyvisit` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) DEFAULT NULL,
  `DateTime` datetime NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Table structure for table `tblgiving`
--

DROP TABLE IF EXISTS `tblgiving`;
CREATE TABLE IF NOT EXISTS `tblgiving` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `GivingID` int(11) NOT NULL,
  `PersonID` int(11) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `GivingID` (`GivingID`),
  UNIQUE KEY `PersonID` (`PersonID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Table structure for table `tbloptions`
--

DROP TABLE IF EXISTS `tbloptions`;
CREATE TABLE IF NOT EXISTS `tbloptions` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OptionFor` varchar(255) DEFAULT NULL,
  `OptionValue` varchar(255) DEFAULT NULL,
  `OptionString` longtext DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Table structure for table `tblperson`
--

DROP TABLE IF EXISTS `tblperson`;
CREATE TABLE IF NOT EXISTS `tblperson` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(255) NOT NULL,
  `MiddleName` varchar(255) DEFAULT NULL,
  `LastName` varchar(255) NOT NULL,
  `FamilyID` int(11) DEFAULT NULL,
  `ChurchID` int(11) DEFAULT NULL,
  `Status` varchar(255) NOT NULL,
  `Baptized` tinyint(1) DEFAULT 0,
  `Confirmed` tinyint(1) DEFAULT 0,
  `Member` tinyint(1) DEFAULT 0,
  `AssociateMember` tinyint(1) DEFAULT 0,
  `Picture` varchar(255) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=170 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblperson`
--

INSERT INTO `tblperson` (`ID`, `FirstName`, `MiddleName`, `LastName`, `FamilyID`, `ChurchID`, `Status`, `Baptized`, `Confirmed`, `Member`, `AssociateMember`, `Picture`, `Note`) VALUES
(1, 'David', '', 'Berglund', 1, NULL, 'Non Member', 1, 1, 0, 0, '', ''),
(2, 'Heidi', '', 'Berglund', 1, 0, 'Active', 1, 1, 1, 0, '', ''),
(3, 'Spencer', '', 'Berglund', 1, 0, 'Active', 1, 1, 1, 0, '', ''),
(4, 'Kendra', 'Lee', 'Berglund', 1, 0, 'Active', 1, 0, 1, 0, '', ''),
(5, 'Rachael', '', 'Berglund', 2, 0, 'Active', 1, 1, 1, 0, 'Berglund.Rachel.jpg', ''),
(6, 'Daniel', '', 'Berglund', 2, 0, 'Active', 1, 1, 1, 0, 'Berglund.Danny.jpg', ''),
(7, 'Julia', '', 'Berglund', 2, 0, 'Active', 1, 1, 1, 0, 'Berglund.Julia.jpg', ''),
(8, 'Russell', 'Wayne', 'Berglund', 2, 0, 'Active', 1, 0, 1, 0, 'Berglund.Russell.jpg', ''),
(9, 'John', '', 'Bockovich', 3, 0, 'Inactive', 0, 0, 1, 0, '', ''),
(10, 'Sandra', '', 'Bockovich', 3, 0, 'Inactive', 0, 0, 1, 0, '', ''),
(11, 'Hallie', '', 'Bockovich', 3, 0, 'Inactive', 0, 0, 1, 0, '', ''),
(12, 'Daniel', '', 'Bockovich', 3, 0, 'Inactive', 0, 0, 1, 0, '', ''),
(13, 'Greg', '', 'Gecas', 4, 0, 'Active', 1, 1, 1, 0, 'Greg Gecas.jpg', ''),
(14, 'Barb', '', 'Gecas', 4, 0, 'Active', 1, 1, 1, 0, 'Barb Gecas.jpg', ''),
(15, 'Robert', '', 'Gecas', 69, 0, 'Inactive', 1, 1, 1, 0, '', ''),
(16, 'Paul', '', 'Gecas', 19, 0, 'Active', 1, 1, 1, 0, '', ''),
(17, 'Addie', '', 'Gecas', 121, 0, 'Inactive', 1, 1, 1, 0, '', ''),
(18, 'Jason', '', 'Mesenbring', 5, 0, 'Active', 1, 1, 1, 0, 'Mesenbring, Jay.jpg', ''),
(19, 'Lisa', '', 'Mesenbring', 5, 0, 'Active', 1, 1, 1, 0, 'Mesenbring, Lisa.jpg', ''),
(20, 'Robert', 'Theodore', 'Mesenbring', 6, 0, 'Active', 1, 1, 1, 0, 'Mesenbring.Bob.jpg', ''),
(21, 'Georgianna', 'Luella', 'Mesenbring', 6, 0, 'Active', 1, 1, 1, 0, 'Mesenbring.Jan.jpg', ''),
(22, 'Jason', '', 'Lashinski', 7, 0, 'Inactive', 0, 0, 0, 0, '', ''),
(23, 'Sherrie', '', 'Pauling', 7, 0, 'Inactive', 0, 0, 0, 0, '', ''),
(24, 'Devan', '', 'Pauling', 7, 0, 'Inactive', 0, 0, 0, 0, '', ''),
(25, 'Paul', '', 'Higgins', 8, 0, 'Active', 1, 1, 1, 0, '', ''),
(26, 'Carolyn', '', 'Higgins', 8, 0, 'Active', 1, 0, 1, 0, '', ''),
(27, 'Mike', '', 'Raymond', 9, 0, 'Active', 1, 1, 1, 0, '', ''),
(28, 'Bob', '', 'Ulmer', 10, 2, 'Associate', 1, 1, 0, 1, '', ''),
(29, 'Martha', '', 'Ulmer', 10, 2, 'Associate', 1, 1, 0, 1, '', ''),
(30, 'Jonathan', 'Charles', 'Watt', 11, 0, 'Active', 1, 1, 1, 0, '', ''),
(31, 'Hannah', 'Kristine Maraie', 'Watt', 11, 0, 'At School', 1, 1, 1, 0, '', ''),
(33, 'Daniel', '', 'Damschen', 14, 0, 'Deceased', 1, 1, 0, 0, '', ''),
(34, 'Janice', '', 'Damschen', 14, NULL, 'Non Member', 1, 1, 0, 0, '', ''),
(41, 'Erik', 'David', 'Saunders', 18, 0, 'Active', 1, 1, 1, 0, 'Saunders, E.jpg', ''),
(42, 'Katherine', 'Lynn', 'Saunders', 18, 0, 'Active', 1, 1, 1, 0, 'Saunders,k.jpg', ''),
(55, 'David', '', 'Gesch', 69, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(56, 'Heidi', '', 'Gesch', 69, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(58, 'Ed', '', 'Lisuth', 70, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(59, 'Mary', '', 'Lisuth', 70, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(61, 'Ruth', '', 'Saunders', 71, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(62, 'Rolf', '', 'Preus', 72, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(63, 'Steve', '', 'Saunders', 71, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(64, 'Thomas', '', 'Saunders', 71, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(65, 'Daniel', '', 'Preus', 73, 0, 'Active', 0, 0, 1, 0, '', ''),
(66, 'Linda', '', 'Prues', 73, 0, 'Active', 0, 0, 1, 0, '', ''),
(69, 'Dan', '', 'Benolkin', 75, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(70, 'Heidi', '', 'Benolkin', 75, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(71, 'Randy', '', 'Nemiz', 76, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(72, 'Dana', '', 'Nimiz', 76, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(73, 'Jodi', '', 'Kolhiff', 77, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(75, 'Merlin', '', 'Higgins', 78, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(76, 'Gerald (Jerry)', '', 'Anderson', 79, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(77, 'Mike', '', 'Flack', 80, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(78, 'Carol', '', 'Flack', 80, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(79, 'Geri', '', 'Heston', 81, 0, 'Prospect', 0, 0, 0, 0, '', '<div>Greg\'s Sister</div>\r\n\r\n\r\n\r\n<div>Not connected to any church</div>'),
(80, 'Jim', '', 'LeTourneau', 82, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(81, 'Sharlene', '', 'LeTourneu', 82, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(82, 'Jason', '', 'Lushinski', 83, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(83, 'Sherri', '', 'Lushinski', 83, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(84, 'Mark', '', 'Penning', 84, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(85, 'Cathy', '', 'Penning', 84, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(86, 'Linda', '', 'Wizykoski', 85, 0, 'Prospect', 0, 0, 0, 0, '', ''),
(107, 'Luke', '', 'Preus', 86, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(108, 'Rachel', '', 'Prues', 86, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(109, 'Christian', '', 'Preus', 87, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(110, 'Cindy', '', 'Preus', 87, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(111, 'Janet', '', 'Preus', 88, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(112, 'Bill', '', 'Schmidt', 89, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(113, 'Kim', '', 'Schmidt', 89, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(114, 'Charlie', '', 'Schmidt', 89, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(115, 'Jack', '', 'Schmidt', 89, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(116, 'Rochelle', '', 'Faley', 90, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(117, 'Karren', '', 'Perkins', 91, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(118, 'Jude', '', 'Perkins', 91, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(120, 'Madiline', '', 'Perkins', 91, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(121, 'Seth', '', 'Prues', 92, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(122, 'William', '', 'Sabol', 93, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(123, 'Natalie', '', 'Sabol', 93, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(124, 'Ryan', '', 'Sabol', 93, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(125, 'Kristof', '', 'Sabol', 93, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(126, 'Miciah', '', 'Carter', 94, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(127, 'Everett', '', 'Carter', 94, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(128, 'Fritz', '', 'Carter', 94, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(129, 'Brian', '', 'Nemanic', 95, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(130, 'Deborah', '', 'Nemanic', 95, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(131, 'Zachariah', '', 'Watt', 96, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(132, 'Nathaniel', '', 'Watt', 97, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(133, 'Teri', '', 'Watt', 97, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(135, 'Julie', '', 'Preus', 98, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(136, 'Pete', '', 'Prues', 98, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(137, 'Cindy', '', 'Prues', 99, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(138, 'Christian', '', 'Prues', 87, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(139, 'Kristiana', '', 'Prues', 100, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(140, 'Jody', '', 'Preus', 101, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(141, 'Erik', '', 'Preus', 101, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(142, 'Michael', '', 'Perkins', 91, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(143, 'Pete', '', 'Hofius', 104, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(145, 'Pat', '', 'Kerber', 105, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(146, 'Steve', '', 'Larson', 107, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(147, 'Lawrence', '', 'Bottorff', 108, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(148, 'Roger', '', 'Micen', 109, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(149, 'Rochelle', '', 'Staley', 110, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(150, 'Matthew', '', 'Johnson', 111, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(151, 'Leah', '', 'Johnson', 111, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(152, 'Josef', '', 'Johnson', 111, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(153, 'Elizabeth', '', 'Bergland', 113, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(154, 'Daniel', '', 'Unknown', 114, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(155, 'Christiana', '', 'Unknown', 114, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(156, 'Elizabeth', '', 'Unknown', 114, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(157, 'William', '', 'Unknown', 114, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(158, 'Brooke', '', 'Unknown', 114, 0, 'Visitor', 0, 0, 0, 0, '', ''),
(159, 'Test', 'Test', 'Test', 115, 0, 'Volunteer', 1, 1, 0, 0, '', ''),
(161, 'test', 'test', 'test', 115, 0, 'Volunteer', 0, 0, 0, 0, '', ''),
(162, 'Axel', '', 'Zimmer', 116, 0, 'Active', 1, 0, 1, 0, '', ''),
(164, 'Lori', '', 'Stangler', 118, 0, 'Active', 0, 0, 1, 0, '', ''),
(165, 'Randy', '', 'Stangler', 118, 0, 'Active', 0, 0, 1, 0, '', ''),
(166, 'Janet', '', 'Ringquist', 119, 0, 'Active', 0, 0, 1, 0, '', ''),
(167, 'James', '', 'Rinqguist', 119, 0, 'Active', 0, 0, 1, 0, '', ''),
(168, 'Paul', '', 'Muus', 120, 0, 'Active', 0, 0, 1, 0, '', ''),
(169, 'Bonnie', '', 'Muus', 120, 0, 'Active', 0, 0, 1, 0, '', '');

-- --------------------------------------------------------

--
-- Table structure for table `tblpersonaddress`
--

DROP TABLE IF EXISTS `tblpersonaddress`;
CREATE TABLE IF NOT EXISTS `tblpersonaddress` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) DEFAULT NULL,
  `AddressLabel` varchar(255) NOT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `Address2` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT 'Grand Marais',
  `State` varchar(255) DEFAULT 'MN',
  `Zip` varchar(255) DEFAULT NULL,
  `Unlisted` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

-- --------------------------------------------------------

--
-- Table structure for table `tblpersoncontact`
--

DROP TABLE IF EXISTS `tblpersoncontact`;
CREATE TABLE IF NOT EXISTS `tblpersoncontact` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) DEFAULT NULL,
  `ContactLabel` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `Contact` varchar(255) DEFAULT NULL,
  `Unlisted` tinyint(1) DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblpersoncontact`
--

INSERT INTO `tblpersoncontact` (`ID`, `PersonID`, `ContactLabel`, `Type`, `Contact`, `Unlisted`, `Note`) VALUES
(17, 2, 'Main', 'eMail', 'heidiwberglund@icloud.com', 0, NULL),
(18, 5, 'Main', 'eMail', 'mizpahrtou@yahoo.com', 1, NULL),
(19, 19, 'Main', 'Phone', '2184752458', 0, NULL),
(20, 20, 'Main', 'Phone', '2183879282', 0, NULL),
(21, 21, 'Main', 'Phone', '2183879282', 0, NULL),
(22, 29, 'Main', 'Phone', '9134888702', 0, NULL),
(23, 31, 'Main', 'Phone', '6412471207', 0, NULL),
(24, 41, 'Main', 'Phone', '4142488040', 0, NULL),
(25, 42, 'Main', 'Phone', '2604374704', 0, NULL),
(26, 19, 'Main', 'eMail', 'lisam@boreal.org', 0, NULL),
(27, 20, 'Main', 'eMail', 'bobganam@boreal.org', 0, NULL),
(28, 21, 'Main', 'eMail', 'glmbtm60@gmail.com', 0, NULL),
(29, 29, 'Main', 'eMail', 'mbulmer1947@gmail.com', 0, NULL),
(30, 31, 'Main', 'eMail', 'Hannah@WattsWhat.net', 0, NULL),
(31, 41, 'Main', 'eMail', 'e.saunders.piano@gmail.com', 0, NULL),
(32, 42, 'Main', 'eMail', 'mhsklo@gmail.com', 0, NULL),
(33, 5, 'Main', 'Phone', '2183874373', 0, NULL),
(34, 30, 'Main', 'Phone', '5154620566', 0, NULL),
(35, 30, 'Main', 'eMail', 'Pastor@WattsWhat.Net', 0, NULL),
(42, 166, 'Main', 'Phone', '2183872234', 0, NULL),
(43, 167, 'Main', 'eMail', 'jim@times2design.com', 0, NULL),
(44, 167, 'Main', 'Phone', '2183702456', 0, NULL),
(45, 166, 'Main', 'eMail', 'janet@times2design.com', 0, NULL),
(46, 164, 'Main', 'Phone', '6124830148', 0, NULL),
(47, 164, 'Main', 'eMail', 'loristangler@gmail.com', 0, NULL),
(48, 66, 'Main', 'Phone', '3148098450', 0, NULL),
(50, 165, 'Main', 'eMail', 'stagler77@gmail.com', 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tblpersondate`
--

DROP TABLE IF EXISTS `tblpersondate`;
CREATE TABLE IF NOT EXISTS `tblpersondate` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) DEFAULT NULL,
  `DateType` varchar(255) DEFAULT NULL,
  `Date` date NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=COMPACT;

--
-- Dumping data for table `tblpersondate`
--

INSERT INTO `tblpersondate` (`ID`, `PersonID`, `DateType`, `Date`, `Note`) VALUES
(36, 30, 'BirthDate', '1961-12-28', NULL),
(37, 166, 'BirthDate', '1950-08-28', NULL),
(38, 166, 'BaptismDate', '1950-11-18', NULL),
(39, 166, 'ConfirmationDate', '1965-06-06', NULL),
(40, 167, 'BirthDate', '1945-05-26', NULL),
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
(66, 31, 'BirthDate', '1998-06-10', NULL),
(67, 30, 'BirthDate', '1961-12-28', NULL),
(68, 162, 'Baptism', '2021-10-24', NULL);

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


--
-- Metadata
--
USE `phpmyadmin`;

--
-- Metadata for table tblchoices
--

--
-- Dumping data for table `pma__table_uiprefs`
--

INSERT INTO `pma__table_uiprefs` (`username`, `db_name`, `table_name`, `prefs`, `last_update`) VALUES
('church', 'churchdb', 'tblchoices', '{\"sorted_col\":\"`tblchoices`.`Field`  ASC\"}', '2022-05-03 23:06:40');

--
-- Metadata for table tblchurch
--

--
-- Metadata for table tblchurchinfo
--

--
-- Metadata for table tblconfig
--

--
-- Metadata for table tblfamily
--

--
-- Dumping data for table `pma__table_uiprefs`
--

INSERT INTO `pma__table_uiprefs` (`username`, `db_name`, `table_name`, `prefs`, `last_update`) VALUES
('church', 'churchdb', 'tblfamily', '{\"sorted_col\":\"`FamilyName` ASC\"}', '2022-05-08 19:12:40');

--
-- Metadata for table tblfamilyaddress
--

--
-- Dumping data for table `pma__table_uiprefs`
--

INSERT INTO `pma__table_uiprefs` (`username`, `db_name`, `table_name`, `prefs`, `last_update`) VALUES
('church', 'churchdb', 'tblfamilyaddress', '{\"sorted_col\":\"`tblfamilyaddress`.`Address` ASC\"}', '2022-05-01 00:44:02');

--
-- Metadata for table tblfamilycontact
--

--
-- Dumping data for table `pma__table_uiprefs`
--

INSERT INTO `pma__table_uiprefs` (`username`, `db_name`, `table_name`, `prefs`, `last_update`) VALUES
('church', 'churchdb', 'tblfamilycontact', '{\"sorted_col\":\"`tblfamilycontact`.`FamilyID` ASC\"}', '2022-05-02 15:53:10');

--
-- Metadata for table tblfamilydate
--

--
-- Metadata for table tblfamilyvisit
--

--
-- Metadata for table tblgiving
--

--
-- Metadata for table tbloptions
--

--
-- Metadata for table tblperson
--

--
-- Dumping data for table `pma__table_uiprefs`
--

INSERT INTO `pma__table_uiprefs` (`username`, `db_name`, `table_name`, `prefs`, `last_update`) VALUES
('church', 'churchdb', 'tblperson', '{\"sorted_col\":\"LastName\"}', '2022-05-07 20:20:55');

--
-- Metadata for table tblpersonaddress
--

--
-- Metadata for table tblpersoncontact
--

--
-- Dumping data for table `pma__table_uiprefs`
--

INSERT INTO `pma__table_uiprefs` (`username`, `db_name`, `table_name`, `prefs`, `last_update`) VALUES
('church', 'churchdb', 'tblpersoncontact', '{\"sorted_col\":\"`PersonID`  ASC\"}', '2022-05-02 16:14:29');

--
-- Metadata for table tblpersondate
--

--
-- Dumping data for table `pma__table_uiprefs`
--

INSERT INTO `pma__table_uiprefs` (`username`, `db_name`, `table_name`, `prefs`, `last_update`) VALUES
('church', 'churchdb', 'tblpersondate', '{\"sorted_col\":\"`tblpersondate`.`PersonID` ASC\"}', '2022-05-08 13:23:23');

--
-- Metadata for table tblstates
--

--
-- Metadata for database churchdb
--

--
-- Dumping data for table `pma__bookmark`
--

INSERT INTO `pma__bookmark` (`dbase`, `user`, `label`, `query`) VALUES
('churchdb', 'church', 'sqlMemberAddressListing', 'SELECT\r\n    tblfamily.FamilyName,\r\n    tblfamilyaddress.Address,\r\n    tblfamilyaddress.Address2,\r\n    tblfamilyaddress.City,\r\n    tblfamilyaddress.State,\r\n    tblfamilyaddress.Zip,\r\n    tblFamily.Directory\r\nFROM\r\n    tblfamily\r\nINNER JOIN tblfamilyAddress ON tblfamilyaddress.FamilyID = tblfamily.ID  \r\nORDER BY `tblfamily`.`FamilyName` ASC\r\nlimit 500'),
('churchdb', 'church', 'sqlMemberCount', 'select count(*) as TotalMembership from tblperson where member = True;'),
('churchdb', 'church', 'sqlMemberList', 'SELECT\r\n    LastName,\r\n    FirstName,\r\nSTATUS\r\n    ,\r\n    Member\r\nFROM\r\n    tblperson\r\nWHERE\r\n    Member = TRUE\r\nLIMIT 500'),
('churchdb', 'church', 'sqlMemberCount', 'SELECT\r\n    COUNT(*) AS TotalMembership\r\nFROM\r\n    tblperson\r\nWHERE\r\n    member = TRUE;'),
('churchdb', 'church', 'sqlLutheranWitness', 'SELECT\r\n    f.FamilyName,\r\n    a.Address,\r\n    a.Address2,\r\n    a.City,\r\n    a.State,\r\n    a.Zip\r\nFROM\r\n    `tblfamily` AS f\r\nJOIN tblfamilyaddress AS a\r\nON\r\n    a.FamilyID = f.ID\r\nWHERE\r\n    f.magazine = TRUE\r\nORDER BY\r\n    FamilyName\r\nLIMIT 500;');

--
-- Dumping data for table `pma__relation`
--

INSERT INTO `pma__relation` (`master_db`, `master_table`, `master_field`, `foreign_db`, `foreign_table`, `foreign_field`) VALUES
('churchdb', 'tblchurchinfo', 'ChurchID', 'churchdb', 'tblchurch', 'ID'),
('churchdb', 'tblfamily', 'ChurchID', 'churchdb', 'tblchurch', 'ID'),
('churchdb', 'tblfamilyaddress', 'FamilyID', 'churchdb', 'tblfamily', 'ID'),
('churchdb', 'tblfamilycontact', 'FamilyID', 'churchdb', 'tblfamily', 'ID'),
('churchdb', 'tblfamilydate', 'FamilyID', 'churchdb', 'tblfamily', 'ID'),
('churchdb', 'tblfamilyvisit', 'FamilyID', 'churchdb', 'tblfamily', 'ID'),
('churchdb', 'tblgiving', 'PersonID', 'churchdb', 'tblperson', 'ID'),
('churchdb', 'tblperson', 'ChurchID', 'churchdb', 'tblchurch', 'ID'),
('churchdb', 'tblperson', 'FamilyID', 'churchdb', 'tblfamily', 'ID'),
('churchdb', 'tblpersonaddress', 'PersonID', 'churchdb', 'tblperson', 'ID'),
('churchdb', 'tblpersoncontact', 'PersonID', 'churchdb', 'tblperson', 'ID'),
('churchdb', 'tblpersondate', 'PersonID', 'churchdb', 'tblperson', 'ID');

--
-- Dumping data for table `pma__pdf_pages`
--

INSERT INTO `pma__pdf_pages` (`db_name`, `page_descr`) VALUES
('churchdb', 'Membership');

SET @LAST_PAGE = LAST_INSERT_ID();

--
-- Dumping data for table `pma__table_coords`
--

INSERT INTO `pma__table_coords` (`db_name`, `table_name`, `pdf_page_number`, `x`, `y`) VALUES
('churchdb', 'tblchoices', @LAST_PAGE, 640, 122),
('churchdb', 'tblchurch', @LAST_PAGE, 53, 13),
('churchdb', 'tblchurchinfo', @LAST_PAGE, 310, 20),
('churchdb', 'tblconfig', @LAST_PAGE, 641, 25),
('churchdb', 'tblfamily', @LAST_PAGE, 100, 230),
('churchdb', 'tblfamilyaddress', @LAST_PAGE, 190, 400),
('churchdb', 'tblfamilycontact', @LAST_PAGE, 190, 640),
('churchdb', 'tblfamilydate', @LAST_PAGE, 190, 790),
('churchdb', 'tblfamilyvisit', @LAST_PAGE, 190, 930),
('churchdb', 'tblgiving', @LAST_PAGE, 824, 296),
('churchdb', 'tbloptions', @LAST_PAGE, 850, 110),
('churchdb', 'tblperson', @LAST_PAGE, 548, 291),
('churchdb', 'tblpersonaddress', @LAST_PAGE, 593, 549),
('churchdb', 'tblpersoncontact', @LAST_PAGE, 593, 794),
('churchdb', 'tblpersondate', @LAST_PAGE, 592, 949),
('churchdb', 'tblstates', @LAST_PAGE, 845, 30);

--
-- Dumping data for table `pma__central_columns`
--

INSERT INTO `pma__central_columns` (`db_name`, `col_name`, `col_type`, `col_length`, `col_collation`, `col_isNull`, `col_extra`, `col_default`) VALUES
('churchdb', 'Address', 'varchar', '255', 'utf8mb4_general_ci', 1, ',', ''),
('churchdb', 'Address2', 'varchar', '255', 'utf8mb4_general_ci', 1, ',', ''),
('churchdb', 'ChurchID', 'INT', '11', '', 1, ',', ''),
('churchdb', 'City', 'VARCHAR', '255', 'utf8mb4_general_ci', 1, ',', 'Grand Marais'),
('churchdb', 'Date', 'date', '', '', 0, ',', ''),
('churchdb', 'DateTime', 'datetime', '', '', 0, ',', ''),
('churchdb', 'FamilyID', 'INT', '11', '', 1, ',', ''),
('churchdb', 'FirstName', 'varchar', '255', 'utf8mb4_general_ci', 0, ',', ''),
('churchdb', 'ID', 'INT', '11', '', 1, 'auto_increment,', ''),
('churchdb', 'LastName', 'varchar', '255', 'utf8mb4_general_ci', 0, ',', ''),
('churchdb', 'MiddleName', 'varchar', '255', 'utf8mb4_general_ci', 1, ',', ''),
('churchdb', 'Note', 'longtext', '', 'utf8mb4_general_ci', 1, ',', ''),
('churchdb', 'PersonID', 'INT', '11', '', 1, ',', ''),
('churchdb', 'Picture', 'varchar', '255', 'utf8mb4_general_ci', 1, ',', ''),
('churchdb', 'State', 'VARCHAR', '255', 'utf8mb4_general_ci', 1, ',', 'MN');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
