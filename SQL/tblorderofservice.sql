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
-- Table structure for table `tblorderofservice`
--

DROP TABLE IF EXISTS `tblorderofservice`;
CREATE TABLE IF NOT EXISTS `tblorderofservice` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OrderofService` varchar(255) NOT NULL,
  `Line` float NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Content` varchar(255) NOT NULL,
  `Page` int(11) DEFAULT NULL,
  `File` varchar(255) DEFAULT NULL,
  `Note` longtext CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `OrderofService` (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=194 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblorderofservice`
--

INSERT INTO `tblorderofservice` (`ID`, `OrderofService`, `Line`, `Title`, `Content`, `Page`, `File`, `Note`) VALUES
(1, 'DS1', 100, 'Divine Service One', 'Divine Service One ( p.151)', 151, NULL, NULL),
(2, 'DS1', 110, 'Opening Hymn', 'Opening Hymn{tab}{Entrance}', 0, NULL, NULL),
(3, 'DS1', 120, 'Confession/Absolution', 'Confession/Absolution', 151, NULL, NULL),
(4, 'DS1', 130, 'Confession', 'Confession{tab}p.151', 151, NULL, NULL),
(5, 'DS1', 140, 'Service of the Word', 'Service of the Word', 151, NULL, NULL),
(6, 'DS1', 150, 'Psalm', 'Psalm{tab}{Psalm}', 0, NULL, NULL),
(7, 'DS1', 160, 'Kyrie', 'Kyrie{tab}p.152', 152, '03DS1Kyrie1.mp3', NULL),
(8, 'DS1', 170.1, 'Gloira in Excelsis', 'Gloria in Excelsis{tab}p.154', 154, '07DS1GloriainExcelsis.mp3', NULL),
(9, 'DS1', 171.2, 'This is the Feast', 'This is The Feast{tab}p.155', 155, '08DS1ThisIstheFeast.mp3', NULL),
(10, 'DS1', 180, 'Salutation/Collect', 'Salutation / Collect{tab}p.156', 156, NULL, NULL),
(11, 'DS1', 190, 'First Reading', '{tab}Old Test{tab}{First}', 0, NULL, NULL),
(12, 'DS1', 200, 'Epistle', '{tab}Epistle{tab}{Epistle}', 0, NULL, NULL),
(13, 'DS1', 210, 'Gospel', '{tab}Gospel{tab}{Gospel}', 0, NULL, NULL),
(14, 'DS1', 220, 'Creed', 'Nicene or Apostles\' Creed', 0, NULL, NULL),
(15, 'DS1', 230, 'Hymn of the Day', 'Hymn of the Day{tab}{Of the Day}', 0, NULL, NULL),
(16, 'DS1', 290, 'Communion Hymn', 'Communion Hymn{tab}{Communion}', 0, NULL, NULL),
(17, 'DS1', 300, 'Preface', 'Preface{tab}p.160', 160, '17DS1Preface1.mp3', NULL),
(18, 'DS1', 330, 'Post Communion Collect', 'Post-Comm Collect{tab}p.166', 166, NULL, NULL),
(19, 'DS1', 340, 'Benediction', 'Benediction{tab}p.166', 166, NULL, NULL),
(20, 'DS1', 350, 'Closing Hymn', 'Closing Hymn{tab}{Closing}', 151, NULL, NULL),
(21, 'DS1', 151, 'Introit', 'Introit{tab}Bulletin', 0, NULL, NULL),
(24, 'DS1', 280, 'Service of the Sacrament', 'Service of the Sacrament', 0, NULL, NULL),
(26, 'DS1', 240, 'Sermon', 'Sermon', 0, NULL, NULL),
(27, 'DS1', 260, 'Offering', 'Offering', 0, NULL, NULL),
(28, 'DS1', 270, 'Offeratory', 'Offeratory{tab}p.159', 159, '15DS1Offertory.mp3', NULL),
(29, 'DS1', 310, 'Distribution', 'Distribution', 0, NULL, NULL),
(30, 'DS1', 320.2, 'Thank the Lord', 'Thank the Lord{tab}p.164', 164, '24DS1ThanktheLord.mp3', NULL),
(31, 'DS1', 320.1, 'Nunc Dimittus', 'Nunc Dimittis{tab}p.165', 165, '25DS1NuncDimittis.mp3', NULL),
(32, 'DS1', 250, 'Prayer of the Church', 'Prayer of the Church', 0, NULL, NULL),
(34, 'DS4', 100, 'Divine Service Four', 'Divine Service Four (p. 203)', 203, NULL, NULL),
(36, 'DS4', 110, 'Confession / Absolution', 'Confession / Absolution', 203, NULL, NULL),
(37, 'DS4', 131, 'Introit', 'Introit{tab}Bulletin', 0, NULL, NULL),
(38, 'DS4', 132, 'Psalm', 'Psalm{tab}{Psalm}', 0, NULL, NULL),
(39, 'DS4', 140, 'Kyrie', 'Kyrie{tab}p.204', 204, '83DS4KyrieOneTime.mp3', NULL),
(40, 'DS4', 150, 'Gloria in Excelsis', 'Gloria in Excelsis{tab}p.204', 204, '86DS4GloriainExcelsis.mp3', NULL),
(41, 'DS4', 160, 'Salutation and Collect', 'Salutation and Collect{tab}p.205', 205, NULL, NULL),
(42, 'DS4', 170, 'OT', '{tab}Old Test{tab}{First}', 0, NULL, NULL),
(43, 'DS4', 180, 'Epistle', '{tab}Epistle{tab}{Epistle}', 0, NULL, NULL),
(44, 'DS4', 190, 'Gospel', '{tab}Gospel{tab}{Gospel}', 0, NULL, NULL),
(45, 'DS4', 200, 'Nicene or Apostles\' Creed', 'Nicene or Apostles\' Creed', 206, NULL, NULL),
(46, 'DS4', 210, 'Hymn of the Day', 'Hymn of the Day{tab}{Of the Day}', 0, NULL, NULL),
(47, 'DS4', 220, 'Sermon', 'Sermon', 203, NULL, NULL),
(48, 'DS4', 230, 'Prayer of the Church', 'Prayer of the Church', 203, NULL, NULL),
(49, 'DS4', 240, 'Offering', 'Offering', 203, NULL, NULL),
(50, 'DS4', 250, 'Service of the Sacrament', 'Service of the Sacrament', 208, NULL, NULL),
(52, 'DS4', 260, 'Communion Hymn', 'Communion Hymn{tab}{Communion}', 0, NULL, NULL),
(53, 'DS4', 270, 'Preface-Agnus Dei', 'Preface-Agnus Dei{tab}p.208-10', 208, '89DS4AgnusDei.mp3', NULL),
(54, 'DS4', 280, 'Distribution', 'Distribution', 0, NULL, NULL),
(55, 'DS4', 290, 'Nunc Dimittus', 'Nunc Dimittis{tab}p.211', 211, '90DS4NuncDimittis.mp3', NULL),
(56, 'DS4', 300, 'Post Communion Collect', 'Post Comm Collect{tab}p.212', 212, NULL, NULL),
(57, 'DS4', 310, 'Benedictamus & Benediction', 'Benedicamus and Benediction{tab}p.212', 212, NULL, NULL),
(58, 'DS4', 320, 'Closing Hymn', 'Closing Hymn{tab}{Closing}', 0, NULL, NULL),
(60, 'DS1', 173.1, 'Gloria Omitted-Advent', 'Gloria omitted during Advent', 0, NULL, NULL),
(61, 'DS1', 173.2, 'Gloria Omitted-Lent', 'Gloria omitted during Lent', 151, NULL, NULL),
(62, 'DS4', 150.2, 'Gloria Omitted Advent', 'Gloria omitted during Advent', 203, NULL, NULL),
(63, 'DS4', 150.3, 'Gloria Omitted Lent', 'Gloria omitted during Lent', 203, NULL, NULL),
(64, 'Evening Prayer', 100, '', 'Evening Prayer (243)', 243, NULL, NULL),
(65, 'Evening Prayer', 120, '', 'Service of Light{tab}p.243', 243, NULL, NULL),
(66, 'Evening Prayer', 130, '', 'Phos Hilaron{tab}p.244', 243, NULL, NULL),
(67, 'Evening Prayer', 140, '', 'Thanksgiving for Light{tab}p.245', 243, NULL, NULL),
(68, 'Evening Prayer', 150, '', 'Psalmody', 243, NULL, NULL),
(69, 'Evening Prayer', 160, '', 'Psalm 141{tab}p.245', 243, NULL, NULL),
(70, 'Evening Prayer', 170, '', 'Psalm{tab}{Psalm}', 243, NULL, NULL),
(71, 'Evening Prayer', 180, '', 'Office Hymn{tab}{Office Hymn}', 243, NULL, NULL),
(72, 'Evening Prayer', 190, '', 'First Reading{tab}{First Reading}', 243, NULL, NULL),
(73, 'Evening Prayer', 200, '', 'Second Reading{tab}{Epistle}', 243, NULL, NULL),
(74, 'Evening Prayer', 210, '', 'Third Reading{tab}{Gospel}', 243, NULL, NULL),
(75, 'Evening Prayer', 221, '', 'Magnificat{tab}p.248', 243, NULL, NULL),
(76, 'Evening Prayer', 222, '', 'My Soul Rejoices{tab}LSB933', 243, NULL, NULL),
(77, 'Evening Prayer', 223, '', 'Hymn (Magnificat){tab}{Hymn}', 243, NULL, NULL),
(78, 'Evening Prayer', 250, '', 'Prayer', 243, NULL, NULL),
(79, 'Evening Prayer', 260, '', 'Litany{tab}p.249', 243, NULL, NULL),
(80, 'Evening Prayer', 270, '', 'Collect for Peace{tab}p.251', 243, NULL, NULL),
(81, 'Evening Prayer', 280, '', 'Lord\'s Prayer{tab}p.251', 243, NULL, NULL),
(82, 'Evening Prayer', 290, '', 'Benedicamus{tab}p.252', 243, NULL, NULL),
(83, 'Evening Prayer', 300, '', 'Benediction{tab}p.252', 243, NULL, NULL),
(84, 'Evening Prayer', 310, '', 'Closing Hymn{tab}{Closing}', 243, NULL, NULL),
(85, 'Evening Prayer', 110, '', 'Opening Hymn{tab}{Entrance}', 243, NULL, NULL),
(86, 'Evening Prayer', 230, '', 'Sermon', 243, NULL, NULL),
(87, 'Evening Prayer', 240, '', 'Offering', 243, NULL, NULL),
(89, 'DS3', 100, '', 'Divine Service Three  (184)', 184, NULL, NULL),
(90, 'DS3', 200, '', 'Confession and Absolution', 184, NULL, NULL),
(91, 'DS3', 301, '', 'Introit{tab}Bulletin', 184, NULL, 'Use Gloria p.186 instead of \"Glory be to the Father..\" in the Introit.'),
(92, 'DS3', 400, '', 'Kyrie{tab}p.186', 184, NULL, NULL),
(93, 'DS3', 500, '', 'Gloria in Excelsis{tab}p.187', 184, NULL, 'Omitted during Advent and Lent'),
(94, 'DS3', 600, '', 'Salutation/Collect{tab}p.189', 184, NULL, NULL),
(95, 'DS3', 700, '', '{tab}Old Test{tab}{First}', 184, NULL, NULL),
(96, 'DS3', 800, '', '{tab}Epistle{tab}{Epistle}', 184, NULL, NULL),
(97, 'DS3', 900, '', '{tab}Gospel{tab}{Gospel}', 184, NULL, NULL),
(98, 'DS3', 1000, '', 'Apostles\' or Nicene Creed', 184, NULL, NULL),
(99, 'DS3', 1100, '', 'Hymn of the Day{tab}{Of the Day}', 184, NULL, NULL),
(100, 'DS3', 1200, '', 'Sermon', 184, NULL, NULL),
(101, 'DS3', 1300, '', 'Offeratory{tab}p.192', 184, NULL, NULL),
(102, 'DS3', 1400, '', 'Offering', 184, NULL, NULL),
(103, 'DS3', 1500, '', 'Prayer of the Church', 184, NULL, NULL),
(104, 'DS3', 1600, '', 'Service of the Sacrament', 184, NULL, NULL),
(105, 'DS3', 1700, '', 'Preface-Agnus Dei{tab}p.194-8', 184, NULL, NULL),
(111, 'DS3', 1650, '', 'Communion Hymn{tab}{Communion}', 184, NULL, NULL),
(112, 'DS3', 1800, '', 'Distribution', 184, NULL, NULL),
(113, 'DS3', 1900, '', 'Nunc Dimittis{tab}p.199', 184, NULL, NULL),
(114, 'DS3', 2000, '', 'Thanksgiving{tab}p.200', 184, NULL, NULL),
(115, 'DS3', 2100, '', 'Salutation and Benedictamus{tab}p.201', 184, NULL, NULL),
(116, 'DS3', 2200, '', 'Benediction{tab}p.201', 184, NULL, NULL),
(118, 'DS3', 150, '', 'Opening Hymn	{Entrance}', 184, NULL, NULL),
(119, 'DS3', 2300, '', 'Closing Hymn{tab}{Closing}', 184, NULL, NULL),
(121, 'DS3', 302, '', 'Psalm{tab}{Psalm}', 184, NULL, NULL),
(122, 'PP', 190, '', 'Opening Hymn{tab}{Entrance}', 260, NULL, NULL),
(123, 'PP', 290, '', 'Opening Versicles{tab}p.260', 260, NULL, NULL),
(124, 'PP', 390, '', 'Old Testament Canticle{tab}p.261', 260, NULL, NULL),
(125, 'PP', 490, '', 'Psalm{tab}{Psalm}', 260, NULL, NULL),
(126, 'PP', 590, '', 'First Reading{tab}{First Reading}', 260, NULL, NULL),
(127, 'PP', 690, '', '{tab}Second Reading {Epistle}', 260, NULL, NULL),
(128, 'PP', 790, '', '{tab}Third Reading{tab}{Gospel}', 260, NULL, NULL),
(129, 'PP', 890, '', 'Responsory{tab}p.263', 260, NULL, NULL),
(130, 'PP', 990, '', 'Ten Commandments{tab}p.264', 260, NULL, NULL),
(131, 'PP', 1090, '', 'Apostles\' Creed{tab}p.264', 260, NULL, NULL),
(132, 'PP', 1190, '', 'Lord\'s Prayer{tab}p.264', 260, NULL, NULL),
(133, 'PP', 1290, '', 'Sermon', 260, NULL, NULL),
(134, 'PP', 1340, '', 'Sermon Hymn{tab}{Sermon Hymn}', 260, NULL, NULL),
(135, 'PP', 1490, '', 'Prayer{tab}p.265', 260, NULL, NULL),
(136, 'PP', 1590, '', 'New Testament Canticle{tab}p.266', 260, NULL, NULL),
(137, 'PP', 1690, '', 'Blessing{tab}p.267', 260, NULL, NULL),
(138, 'PP', 1790, '', 'Closing Hymn{tab}{Closing}', 260, NULL, NULL),
(139, 'PP', 1390, '', 'Offering', 260, NULL, NULL),
(140, 'PP', 140, '', 'Office of Prayerand Preaching ( p.260)', 260, NULL, NULL),
(141, 'Vespers', 1090, '', 'Vespers (p.229)', 229, NULL, NULL),
(142, 'Vespers', 1190, '', 'Opening Versicles{tab}p.229', 229, NULL, NULL),
(143, 'Vespers', 1290, '', 'Psalmody', 229, NULL, NULL),
(144, 'Vespers', 1390, '', 'Psalm{tab}{Psalm}', 229, NULL, NULL),
(145, 'Vespers', 1490, '', 'Readings', 229, NULL, NULL),
(146, 'Vespers', 1590, '', '{tab}First{tab}{First}', 229, NULL, NULL),
(147, 'Vespers', 1690, '', '{tab}Second{tab}{Second}', 229, NULL, NULL),
(148, 'Vespers', 1790, '', '{tab}Third{tab}{Third}', 229, NULL, NULL),
(149, 'Vespers', 1890, '', 'Responsory{tab}p.230', 229, NULL, NULL),
(150, 'Vespers', 1990, '', 'Sermon', 229, NULL, NULL),
(151, 'Vespers', 2090, '', 'Canticle', 229, NULL, NULL),
(152, 'Vespers', 2091, '', 'Magnificat{tab}p.231', 229, NULL, NULL),
(153, 'Vespers', 2290, '', 'Prayers', 229, NULL, NULL),
(154, 'Vespers', 2390, '', 'Kyrie{tab}p.233', 229, NULL, NULL),
(155, 'Vespers', 2490, '', 'Lord\'s Prayer{tab}p.233', 229, NULL, NULL),
(156, 'Vespers', 2590, '', 'Collect for Peace{tab}p.233', 229, NULL, NULL),
(157, 'Vespers', 2690, '', 'Benedicamus{tab}p.234', 229, NULL, NULL),
(158, 'Vespers', 2790, '', 'Benediction{tab}p.234', 229, NULL, NULL),
(159, 'Vespers', 1440, '', 'Office Hymn{tab}{Office Hymn}', 229, NULL, NULL),
(160, 'Vespers', 1140, '', 'Entrance Hymn{tab}{Entrance}', 229, NULL, NULL),
(161, 'Vespers', 2990, '', 'Closing Hymn{tab}{Closing}', 229, NULL, NULL),
(162, 'Vespers', 2540, '', 'Prayer of the Church', 229, NULL, NULL),
(163, 'Vespers', 2092, '', 'My Soul Rejoices{tab}LSB933', 229, NULL, NULL),
(164, 'Compline', 100, '', 'Prosessional Hymn{tab}{Entrance}', 253, NULL, NULL),
(165, 'Compline', 200, '', 'Versicals{tab}p.253', 253, NULL, NULL),
(166, 'Compline', 300, '', 'Confession{tab}p.254', 253, NULL, NULL),
(167, 'Compline', 400, '', 'PSALMODY', 253, NULL, NULL),
(168, 'Compline', 500, '', 'Psalm{tab}{Psalm}', 253, NULL, NULL),
(169, 'Compline', 600, '', 'Office Hymn{tab}{Office Hymn}', 253, NULL, NULL),
(170, 'Compline', 700, '', 'READINGS', 253, NULL, NULL),
(171, 'Compline', 800, '', '{tab}First Reading{tab}{First}', 253, NULL, NULL),
(172, 'Compline', 900, '', '{tab}Second Reading{tab}{Second}', 253, NULL, NULL),
(173, 'Compline', 1000, '', '{tab}Third Reading{tab}{Third}', 253, NULL, NULL),
(174, 'Compline', 1100, '', 'Responsory{tab}p.255', 253, NULL, NULL),
(175, 'Compline', 1200, '', 'Hymn{tab}{Sermon}', 253, NULL, NULL),
(176, 'Compline', 1300, '', 'Prayer{tab}p.256', 253, NULL, NULL),
(177, 'Compline', 1400, '', 'Lord\'s Prayer', 253, NULL, NULL),
(178, 'Compline', 1501, '', 'Nunc Dimittis{tab}p.258', 253, NULL, NULL),
(179, 'Compline', 1502, '', 'Hymn{tab}{Nunc Dimittis}', 253, NULL, NULL),
(180, 'Compline', 1600, '', 'Benediction{tab}p.259', 253, NULL, NULL),
(181, 'Compline', 1700, '', 'Closing Hymn{tab}{Closing}', 253, NULL, NULL),
(182, 'Compline', 50, '', 'Compline (253)', 253, NULL, NULL),
(183, 'Compline', 1250, '', 'Sermon', 253, NULL, NULL),
(184, 'Other', 0, '', 'Order of Service - Other', 0, NULL, NULL),
(185, 'DS4', 275, 'Sanctus', 'Sanctus ', 208, '88DS4Sanctus.mp3', NULL),
(187, 'DS4', 120, 'Entrance Hymn', 'Entrance{tab}{Entrance}', 0, NULL, NULL),
(188, 'DS1', 302, 'Sanctus', 'Sanctus{tab}p.161', 161, '20DS1Sanctus.mp3', NULL),
(189, 'DS1', 305, 'Agnus Dei', 'Agnus Dei{tab}p. 163', 163, '23DS1AgnusDei.mp3', NULL),
(191, 'Vespers', 2541, '', 'Litany{tab}p.288', 288, NULL, NULL),
(192, 'DS4', 122, 'Confession', 'Confession{tab}p.203', 203, NULL, NULL),
(193, 'Compline', 1260, '', 'Offering', NULL, NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
