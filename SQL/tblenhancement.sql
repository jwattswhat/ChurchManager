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
-- Table structure for table `tblenhancement`
--

DROP TABLE IF EXISTS `tblenhancement`;
CREATE TABLE IF NOT EXISTS `tblenhancement` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Description` varchar(255) DEFAULT NULL,
  `Priority` char(1) NOT NULL DEFAULT '1',
  `Module` varchar(255) DEFAULT NULL,
  `Screen` varchar(255) DEFAULT NULL,
  `DateEntered` date DEFAULT NULL,
  `DateDue` date DEFAULT NULL,
  `EnteredBy` char(255) DEFAULT NULL,
  `Complete` tinyint(1) DEFAULT 0,
  `CompleteDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblenhancement`
--

INSERT INTO `tblenhancement` (`ID`, `Description`, `Priority`, `Module`, `Screen`, `DateEntered`, `DateDue`, `EnteredBy`, `Complete`, `CompleteDate`, `Note`) VALUES
(1, 'fix clsNoDataDBRecord to skip saverecord()', '1', 'clsDB', NULL, '2022-08-10', '2022-08-10', 'JW', 1, '2023-04-05', NULL),
(2, 'update forms (.json) to use \"table\" instad of \"sql\"', '1', 'forms', NULL, '2022-08-10', '2022-08-10', 'JW', 1, '2022-08-10', NULL),
(3, 'labels turn to white background on first,prev,next,last', '3', 'class clsForms,clsFields', 'frmMain.json', '2022-08-10', '2022-08-10', 'JW', 1, '2022-08-10', NULL),
(4, 'When closing any linked form in frmService the subform frmPropers doesnt refil', '1', 'clsForms', 'frmService', '2022-08-20', '2022-08-20', 'JW', 1, '2022-08-20', NULL),
(6, 'filepickter - show the filename only, store the directory internally.', '1', 'class clsFilePickerCtrl in clsFields', 'frmSermons.json', '2022-09-10', '2022-09-10', 'JW', 1, '2022-09-10', NULL),
(7, 'The Same Family Names appear on every Family Directory Listing', '1', 'rptMemberDirectory.py', NULL, '2022-09-29', '2022-09-29', 'JW', 1, '2022-09-29', NULL),
(8, 'OS List - Order of Service Listing not working', '1', 'frmOS.json & clsForms', NULL, '2022-09-29', '2022-09-29', 'JW', 1, '2022-09-29', NULL),
(10, 'Form for updating Checklists.', '3', 'New', 'New', '2022-09-29', '2022-08-10', 'JW', 1, '2023-01-06', NULL),
(11, 'Fix Char spacing by font', '1', 'clsForm', NULL, '2022-11-06', '2022-11-06', 'JW', 1, '2022-11-06', NULL),
(12, 'Backup DB', '1', 'System', NULL, '2022-11-06', '2022-11-06', NULL, 1, '2022-11-06', NULL),
(13, 'Convert Point to Char in Screens', '1', '*.json', NULL, '2022-11-06', '2022-11-06', 'JW', 1, '2022-11-06', NULL),
(15, 'Refresh Form on Change of Propers', '1', 'clsForms', 'Worship Service', '2022-12-10', '2022-12-10', 'JW', 1, '2022-12-10', NULL),
(16, 'Add Priority and Category to Projects', '1', 'DataBase & Form', 'frmPriority.json ', '2022-12-12', '2022-12-12', 'JW', 1, '2022-12-12', NULL),
(17, 'After Notify Particpants is finished close the Form', '2', 'cm.py', 'NotifyviaeMail.json', '2022-12-15', '2022-12-15', 'JW', 1, '2022-12-15', NULL),
(18, 'forms clear on update ', '1', 'clsForm ', NULL, '2022-12-15', '2022-12-15', 'JW', 1, '2022-12-15', NULL),
(19, 'Add ID to Sermon File Names when Adding them to the Sermon Screen', '1', 'Local clsForm', 'frmSermon.json', '2022-12-15', '2022-12-15', 'JW', 1, '2022-12-15', NULL),
(20, 'Add Priority to Enhancement report', '2', 'report generator', NULL, '2022-12-15', '2022-12-15', 'JW', 1, '2022-12-15', NULL),
(21, 'remove path from Sermon name on select file', '1', 'clsFields - File Picker', 'frmSermon.json', '2022-12-15', '2022-12-15', 'JW', 1, '2022-12-15', NULL),
(22, 'Firgue out what json forms belong with JSForm. Update forms to look in JSForms first.', '5', 'JSForm vs ChurchManager', NULL, '2022-12-17', NULL, 'JW', 0, NULL, NULL),
(23, 'Refresh on forms with no Base Record', '2', 'clsForms', 'All with no base record', '2022-12-18', '2022-12-15', 'JW', 1, '2023-01-05', NULL),
(24, 'ComboBox Default values', '3', 'clsFields', NULL, '2022-12-18', '2022-08-10', 'JW', 1, '2022-12-23', NULL),
(25, 'Clear Warning Color on when moving to a new screen after Field changes', '1', 'clsForms', NULL, '2022-12-19', '2022-12-15', 'JW', 1, '2022-12-19', NULL),
(26, 'Refresh screen after delete record to remove deleted record', '1', 'clsForms', NULL, '2022-12-18', '2022-12-15', 'JW', 1, '2022-12-18', NULL),
(27, 'Print phone numbers with seperators.', '2', 'LimeReports - CMPH01', NULL, '2022-12-18', '2022-12-15', 'JW', 1, '2022-12-22', NULL),
(28, 'Switch Announcements from Remember the Milk to ChurchDB', '5', 'New', NULL, '2022-12-19', '2023-04-05', 'JW', 1, '2023-04-05', NULL),
(29, 'Find a way for Dates not entered to be NULL', '1', 'clsFields', NULL, '2022-12-19', '2022-12-15', 'JW', 1, '2022-12-19', NULL),
(30, 'Required Field Values', '2', 'clsForms, clsFields', 'All', '2022-12-19', '2022-12-15', 'JW', 1, '2022-12-22', '[Default to Required = True or False?]'),
(31, 'update TimePicker and DateTimePicker to allow for no entry', '1', 'clsFields, TimePicker, DateTimePicker', NULL, '2022-12-19', '2023-04-05', 'JW', 1, '2023-04-05', NULL),
(33, 'Add Pictures to CMMD01 - Member Directory', '1', 'CMMD01', NULL, '2022-08-10', '2022-08-10', 'JW', 1, '2022-08-10', NULL),
(34, 'Add Tasks to Projects', '2', NULL, NULL, '2022-12-19', '2022-12-15', 'JW', 1, '2022-12-19', NULL),
(35, 'More for Sermon Tracking. ', '4', 'frmSermon.json, tblSermon', NULL, '2022-12-22', NULL, 'JW', 0, NULL, NULL),
(36, 'Automaticly format Phone Numbers with () -', '3', 'clsFields', NULL, '2022-12-22', '2023-04-05', 'JW', 1, '2022-12-23', NULL),
(38, 'Add ChurchID to tblHymnUsage', '1', 'SQL DB', NULL, '2023-01-03', '2022-08-10', 'JW', 1, '2023-01-04', '[Other Required Changes to update ChurchID in tblHymnUsage Record]'),
(39, 'Finish Checklists, On Merge Lists, Keep Checked Value', '1', 'clsFields', NULL, '2023-04-05', NULL, 'JW', 0, NULL, NULL),
(40, 'Show pictures on People and Family screens', '2', 'clsFields', 'frmPeople, frmFamily', '2023-01-06', NULL, 'JW', 0, NULL, NULL),
(41, 'Why does Date Entered on frmBugs not default to today, like Date Due:', '1', 'clsForms, clsFields', 'frmBugs', '2023-01-06', '2023-04-05', NULL, 1, '2023-01-04', NULL),
(42, 'Hymn History on frmSearchHymns', '1', 'clsForms', 'frmSearchHymns', '2023-04-05', NULL, 'JW', 0, NULL, NULL),
(43, 'close problems when clicking [X]', '1', 'clsForms', NULL, '2023-01-06', NULL, 'JW', 0, NULL, NULL),
(44, 'Page headers on Bug Report', '2', 'LimeReports CMEN01', NULL, '2023-01-06', '2022-12-15', NULL, 1, '2022-08-10', NULL),
(45, 'spacing on Alt Reading form', '2', 'frmAltReading', NULL, '2023-01-06', '2023-04-05', NULL, 1, '2022-08-10', NULL),
(46, 'Update DB with Hymn History', '1', NULL, NULL, '2023-01-06', '2023-04-05', NULL, 1, '2023-01-04', NULL),
(47, 'Update db for Home Landlines, and Mobile phones. ', '1', 'db', NULL, '2022-12-19', '2023-04-05', 'JW', 1, '2023-01-04', NULL),
(48, 'Add Play Hymn to Hymn Selections', '1', NULL, NULL, '2023-03-14', NULL, 'JW', 0, NULL, NULL),
(49, 'Update Box on Report Screen', '2', 'frmReports.json', 'frmReports', '2022-12-19', NULL, 'JW', 0, NULL, NULL),
(50, 'Highlight fields with vaild parameters on Reports screen', '2', 'clsForm', 'frmReports.json', '2022-12-19', NULL, 'JW', 1, '2023-04-13', NULL),
(51, 'Place RecordAttendance in membership box on frmMain', '1', 'frmMain, frmMain.json', 'frmMain.json', '2022-12-19', NULL, 'JW', 1, '2023-04-13', NULL),
(53, 'implement Autoselect for frequent members in attendance entry', '2', NULL, NULL, '2023-04-05', NULL, 'JW', 0, NULL, '[Make a table with a list of frequent attendance to apply at attendance entry time.]'),
(52, 'Implement JSONSchema', '1', 'json files', NULL, '2023-04-05', NULL, 'JW', 1, '2023-04-01', '[see Jsonschema.org]'),
(54, 'Add Float to DB and Fields', '1', 'clsFields', NULL, '2023-04-05', NULL, 'JW', 1, '2023-04-13', NULL),
(55, 'add Pastors Report to Main Menu', '1', 'CM.py', 'frmMain.json', '2023-04-12', NULL, 'JW', 1, '2023-04-13', '[Print Journal Transfers Attendance etc.]'),
(57, 'Update the Main form. ', '1', 'frmMain.json', 'frmMain.json', '2023-04-05', NULL, 'JW', 0, NULL, NULL),
(58, 'Fix Hymnsearch screen (Width to WidthCH)', '1', 'frmHymnSearch.json', NULL, '2023-04-05', NULL, 'JW', 0, NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
