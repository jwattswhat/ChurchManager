-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:16 PM
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
-- Table structure for table `tblsermon`
--

DROP TABLE IF EXISTS `tblsermon`;
CREATE TABLE IF NOT EXISTS `tblsermon` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Reference` varchar(255) NOT NULL,
  `Title` varchar(255) DEFAULT NULL,
  `Preacher` varchar(255) DEFAULT NULL,
  `Author` varchar(255) DEFAULT NULL,
  `Series` varchar(255) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `Sermon` varchar(255) DEFAULT NULL,
  `Outline` varchar(255) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblsermon`
--

INSERT INTO `tblsermon` (`ID`, `Reference`, `Title`, `Preacher`, `Author`, `Series`, `Date`, `Sermon`, `Outline`, `Note`) VALUES
(9, '1 Timothy 1:12-17', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-08-17', 'Romans.8.31–39.ID(15).doc', NULL, '[#1Timothy]'),
(10, 'Hebrews 12:1-2', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-08-21', 'Hebrews.12.1-2.ID(10).doc', NULL, '[#Hebrews]'),
(12, 'Luke 14:1-14', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-08-24', 'Luke.14.1-14.ID(12).doc', NULL, '[#Luke]'),
(13, 'Philemon', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-08-31', 'Philemon.ID(13).doc', NULL, '[#Philemon]'),
(14, 'John 10:11-18', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-09-10', 'John.10.11-18.ID(14).doc', NULL, '[#John]'),
(15, 'Romans 8:31-39', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-09-11', 'Romans.8.31–39.ID(15).doc', NULL, '[#Romans]'),
(16, '1 Timothy 2:1-15', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-09-13', '1.Timothy.2.1-15ID(16).doc', NULL, '[#1Timothy]'),
(17, 'Luke 16:10-31', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-09-20', 'Luke.6.19-31.ID(17).doc', NULL, '[#Luke]'),
(18, 'Luke 17:1-10', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-09-29', 'Luke.17.1-10.ID(18).doc', NULL, '[#Luke]'),
(19, 'Ruth 1:1-19a', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-08-17', 'Ruth.1.1-19a.ID(19).doc', NULL, '[#Ruth]'),
(20, 'Genesis 32:22-30', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-09-18', 'Gen.32.22-30.ID(20).doc', NULL, '[#Genesis]'),
(21, 'Revelation 14:6-7', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-10-26', 'Revelation.14.6-7.ID(21).doc', NULL, '[#Revelation]'),
(22, 'Psalm 149', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-11-06', 'Psalm.149.ID(22).docx', NULL, '[#Psalm]'),
(23, '2 Thessalonians 3:6:13', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-11-12', '2.Thessalonians.3.6-13.ID(23).doc', NULL, '[#2Thessalonians]'),
(24, 'Psalm 46', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-11-20', 'Psalm.46.1.ID(24).doc', NULL, '[#Psalm]'),
(25, '1 Timothy 2:1-6', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-11-23', '1.Timothy.2.1-6..ID(25).doc', NULL, '[#1Timothy]'),
(26, 'Rev 22:20; Matt 13:1-9; Eph 6:10-20', 'Come, Lord Jesus (1)', 'Rev. Jonathan C. Watt', 'Rev. W. Mart Thompson', 'Come, Lord Jesus', '2022-11-30', 'ComeLordJesus.1.ID(26).docx', NULL, '[#Revelation; #Matthew; #Ephesians]'),
(27, 'Matthew 3:1-11', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-12-04', 'Matthew.3.1-11.ID(27).docx', NULL, '[#Matthew]'),
(28, 'Matthew 13:5-6,20-21; Luke 10:38-42', 'Come Lord Jesus', 'Rev. Jonathan C. Watt', 'Rev. W. Mart Thompson', 'Come, Lord Jesus', '2022-12-07', 'ComeLordJesus.2.ID(28).docx', NULL, '[#Matthew; #Luke]'),
(29, 'James 5:7-11', NULL, 'Rev. Jonathan C. Watt', NULL, NULL, '2022-12-11', 'James.5.7-11.ID(29).docx', NULL, '[#James]'),
(30, 'Matthew 13:7,21; 2 Peter 3:10-13', NULL, 'Rev. Jonathan C. Watt', 'Rev. W. Mart Thompson', 'Come, Lord Jesus', '2022-12-21', 'Matthew.13.7,21.2 Peter.3.10–13.ID(30).docx', NULL, '[#Matthew; #2Peter]'),
(31, 'Matthew 1:18-25', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2022-12-15', 'Matthew.1.18-25.ID(31).docx', NULL, '[From a sermon by Paul Robinson\r#Matthew]'),
(35, 'Matthew 1:18-25', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2022-12-24', 'Matthew.1.18-25.ID(35).docx', NULL, '[#Matthew]'),
(36, 'John 1:1-18', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2022-12-25', 'John.1.1-18.ID(36).docx', NULL, '[#John]'),
(37, 'Matthew 2:13-18', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-01-01', 'Matthew.2.13-18.ID(37).docx', NULL, '[#Matthew]'),
(38, 'Matthew 2:1-12', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, NULL, 'Matthew.2.1-12.ID(38).docx', NULL, '[#Matthew]'),
(39, 'Isaiah 42:1-4', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-01-15', 'Isaiah.42.1-4.ID(39).docx', NULL, '[#Isaiah]'),
(40, 'Psalm 27:14', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, NULL, 'Psalm.27.14.ID(40).doc', NULL, '[#Psalm]'),
(41, 'Miciah 6:1-8', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-01-29', 'Micah.6.1-8.ID(41).docx', NULL, '[#Miciah]'),
(42, '1 Corinthians 1:26-31', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-01-29', '1.Corinthians.1.26-31.ID(42).docx', NULL, '[#1Corinthians]'),
(43, '1 Corinthians 2:1-16', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-02-05', '1.Corinthians.2.1-16.ID(43).docx', NULL, '[#1Corinthians]'),
(44, 'Matthew 5:21-37', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-02-12', 'Matthew.5.21-37.ID(44).docx', NULL, '[#Matthew]'),
(46, 'Matthew 6:9', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-02-22', 'Matthew.6.9.ID(46).docx', NULL, '[#Matthew]'),
(47, 'Matthew 4:1-11', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-02-26', 'Matthew.4.1-11.ID(47).doc', NULL, '[#Matthew]'),
(48, 'Matthew 4:1-11', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-02-26', 'Matthew.4.1-11.ID(47).doc', NULL, '[#Matthew]'),
(49, 'Psalm 51', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-03-01', 'Psalm.51.ID(49).docx', NULL, '[#Psalm]'),
(51, 'Genesis 2:1-3; 15:1-6', NULL, 'Rev. Jonathan C. Watt', 'Rev. Randy Asbury', NULL, '2023-03-05', 'Genesis.1.21-3; 15.1-6.ID(50).doc', NULL, '[#Genesis]'),
(56, 'John 9', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-03-19', 'John.9.ID(56).doc', NULL, NULL),
(52, 'Psalm 13', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', 'Prayer, Lent 23', '2023-03-08', 'Psalm.13.ID(52).docx', NULL, '[#Psalm #Lent23]'),
(53, 'Exodus 17:1-7', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-03-12', 'Exodus.17.1-7.ID(53).docx', NULL, '[#Exodus #Lent #Lent23]'),
(54, 'The Third Petition', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-03-15', 'The Third Petition of the Lords Prayer.ID(54).docx', NULL, NULL),
(55, 'John 9', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, NULL, 'John.9.ID(55).doc', NULL, NULL),
(57, 'Luke 23:26-43', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', 'Prayer', '2023-03-22', 'Luke.23.26-43.ID(57).docx', NULL, NULL),
(58, 'John 11', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-03-26', 'John.11.ID(58).doc', NULL, NULL),
(59, 'Luke 2:22-35', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', 'Prayer', '2023-03-29', 'Luke.2.22-35.ID(59).docx', NULL, NULL),
(60, 'John 12:20-33', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-04-02', 'John.12.20-33.ID(60).doc', NULL, NULL),
(61, 'Luke 23:50-55', 'At The Grave of Jesus', 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-04-02', 'Luke 23.50-55.Good Friday Devotion.At the Grave of Jesus.ID(61).docx', NULL, '[Devoiton for Good Friday]'),
(62, 'Exodus 12:21-23', NULL, 'Rev. Jonathan C. Watt', NULL, 'Christ our Passover', '2023-04-06', 'Exodus.12.21-23.ID(62).docx', NULL, NULL),
(63, '1 Corinthians 15:1-8', NULL, 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-04-09', '1.Corinthians.15.1-8.ID(63).docx', NULL, NULL),
(64, 'John 20:19-31', 'Jesus breaks in...', 'Rev. Jonathan C. Watt', 'Rev. Joanthan C. Watt', NULL, '2023-04-16', 'John.20.19-31.ID(64).docx', NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
