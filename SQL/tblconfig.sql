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
-- Table structure for table `tblconfig`
--

DROP TABLE IF EXISTS `tblconfig`;
CREATE TABLE IF NOT EXISTS `tblconfig` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ConfigFamily` varchar(255) NOT NULL,
  `ConfigType` varchar(100) NOT NULL,
  `ConfigValue` varchar(255) NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Family Type` (`ConfigFamily`,`ConfigType`) USING HASH
) ENGINE=MyISAM AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblconfig`
--

INSERT INTO `tblconfig` (`ID`, `ConfigFamily`, `ConfigType`, `ConfigValue`, `Note`) VALUES
(4, 'Location', 'Form', '.\\Forms\\', NULL),
(5, 'Location', 'Picture', '.\\Pictures\\', NULL),
(6, 'Location', 'Report', '.\\Reports\\', NULL),
(7, 'Font', 'PointSize', '10', NULL),
(8, 'Font', 'Family', '74', NULL),
(9, 'Font', 'Style', '90', NULL),
(10, 'Font', 'Weight', '400', NULL),
(11, 'Font', 'Face', 'Calibri', NULL),
(12, 'Font', 'Underlined', 'False', NULL),
(22, 'Location', 'Sermon', '.\\Sermons\\', NULL),
(14, 'Format', 'DateTime', '%m/%d/%Y %I:%M %p', '[%a - abbreviated weekday name\r\n%A - full weekday name\r\n%b - abbreviated month name\r\n%B - full month name\r\n%c - preferred date and time representation\r\n%C - century number (the year divided by 100, range 00 to 99)\r\n%d - day of the month (01 to 31)\r\n%D - same as %m/%d/%y\r\n%e - day of the month (1 to 31)\r\n%g - like %G, but without the century\r\n%G - 4-digit year corresponding to the ISO week number (see %V).\r\n%h - same as %b\r\n%H - hour, using a 24-hour clock (00 to 23)\r\n%I - hour, using a 12-hour clock (01 to 12)\r\n%j - day of the year (001 to 366)\r\n%m - month (01 to 12)\r\n%M - minute\r\n%n - newline character\r\n%p - either am or pm according to the given time value\r\n%r - time in a.m. and p.m. notation\r\n%R - time in 24 hour notation\r\n%S - second\r\n%t - tab character\r\n%T - current time, equal to %H:%M:%S\r\n%u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1\r\n%U - week number of the current year, starting with the first Sunday as the first day of the first week\r\n%V - The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week\r\n%W - week number of the current year, starting with the first Monday as the first day of the first week\r\n%w - day of the week as a decimal, Sunday=0\r\n%x - preferred date representation without the time\r\n%X - preferred time representation without the date\r\n%y - year without a century (range 00 to 99)\r\n%Y - year including the century\r\n%Z or %z - time zone or name or abbreviation\r\n%% - a literal % character]'),
(15, 'Format', 'Date', '%m/%d/%Y', '[%a - abbreviated weekday name\r\n%A - full weekday name\r\n%b - abbreviated month name\r\n%B - full month name\r\n%c - preferred date and time representation\r\n%C - century number (the year divided by 100, range 00 to 99)\r\n%d - day of the month (01 to 31)\r\n%D - same as %m/%d/%y\r\n%e - day of the month (1 to 31)\r\n%g - like %G, but without the century\r\n%G - 4-digit year corresponding to the ISO week number (see %V).\r\n%h - same as %b\r\n%H - hour, using a 24-hour clock (00 to 23)\r\n%I - hour, using a 12-hour clock (01 to 12)\r\n%j - day of the year (001 to 366)\r\n%m - month (01 to 12)\r\n%M - minute\r\n%n - newline character\r\n%p - either am or pm according to the given time value\r\n%r - time in a.m. and p.m. notation\r\n%R - time in 24 hour notation\r\n%S - second\r\n%t - tab character\r\n%T - current time, equal to %H:%M:%S\r\n%u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1\r\n%U - week number of the current year, starting with the first Sunday as the first day of the first week\r\n%V - The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week\r\n%W - week number of the current year, starting with the first Monday as the first day of the first week\r\n%w - day of the week as a decimal, Sunday=0\r\n%x - preferred date representation without the time\r\n%X - preferred time representation without the date\r\n%y - year without a century (range 00 to 99)\r\n%Y - year including the century\r\n%Z or %z - time zone or name or abbreviation\r\n%% - a literal % character]'),
(16, 'Format', 'Time', '%I:%M %p', '[%a - abbreviated weekday name\r\n%A - full weekday name\r\n%b - abbreviated month name\r\n%B - full month name\r\n%c - preferred date and time representation\r\n%C - century number (the year divided by 100, range 00 to 99)\r\n%d - day of the month (01 to 31)\r\n%D - same as %m/%d/%y\r\n%e - day of the month (1 to 31)\r\n%g - like %G, but without the century\r\n%G - 4-digit year corresponding to the ISO week number (see %V).\r\n%h - same as %b\r\n%H - hour, using a 24-hour clock (00 to 23)\r\n%I - hour, using a 12-hour clock (01 to 12)\r\n%j - day of the year (001 to 366)\r\n%m - month (01 to 12)\r\n%M - minute\r\n%n - newline character\r\n%p - either am or pm according to the given time value\r\n%r - time in a.m. and p.m. notation\r\n%R - time in 24 hour notation\r\n%S - second\r\n%t - tab character\r\n%T - current time, equal to %H:%M:%S\r\n%u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1\r\n%U - week number of the current year, starting with the first Sunday as the first day of the first week\r\n%V - The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week\r\n%W - week number of the current year, starting with the first Monday as the first day of the first week\r\n%w - day of the week as a decimal, Sunday=0\r\n%x - preferred date representation without the time\r\n%X - preferred time representation without the date\r\n%y - year without a century (range 00 to 99)\r\n%Y - year including the century\r\n%Z or %z - time zone or name or abbreviation\r\n%% - a literal % character]'),
(17, 'SQLFormat', 'DateTime', '%m/%d/%Y %h:%i %p', '[%a	Short weekday name in current locale (Variable lc_time_names).\r\n%b	Short form month name in current locale. For locale en_US this is one of: Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov or Dec.\r\n%c	Month with 1 or 2 digits.\r\n%D	Day with English suffix \'th\', \'nd\', \'st\' or \'rd\'\'. (1st, 2nd, 3rd...).\r\n%d	Day with 2 digits.\r\n%e	Day with 1 or 2 digits.\r\n%f	Microseconds 6 digits.\r\n%H	Hour with 2 digits between 00-23.\r\n%h	Hour with 2 digits between 01-12.\r\n%I	Hour with 2 digits between 01-12.\r\n%i	Minute with 2 digits.\r\n%j	Day of the year (001-366)\r\n%k	Hour with 1 digits between 0-23.\r\n%l	Hour with 1 digits between 1-12.\r\n%M	Full month name in current locale (Variable lc_time_names).\r\n%m	Month with 2 digits.\r\n%p	AM/PM according to current locale (Variable lc_time_names).\r\n%r	Time in 12 hour format, followed by AM/PM. Short for \'%I:%i:%S %p\'.\r\n%S	Seconds with 2 digits.\r\n%s	Seconds with 2 digits.\r\n%T	Time in 24 hour format. Short for \'%H:%i:%S\'.\r\n%U	Week number (00-53), when first day of the week is Sunday.\r\n%u	Week number (00-53), when first day of the week is Monday.\r\n%V	Week number (01-53), when first day of the week is Sunday. Used with %X.\r\n%v	Week number (01-53), when first day of the week is Monday. Used with %x.\r\n%W	Full weekday name in current locale (Variable lc_time_names).\r\n%w	Day of the week. 0 = Sunday, 6 = Saturday.\r\n%X	Year with 4 digits when first day of the week is Sunday. Used with %V.\r\n%x	Year with 4 digits when first day of the week is Monday. Used with %v.\r\n%Y	Year with 4 digits.\r\n%y	Year with 2 digits.\r\n%#	For str_to_date(), skip all numbers.\r\n%.	For str_to_date(), skip all punctation characters.\r\n%@	For str_to_date(), skip all alpha characters.\r\n%%	A literal % character.]'),
(18, 'SQLFormat', 'Date', '%m/%d/%Y', '[%a	Short weekday name in current locale (Variable lc_time_names).\r\n%b	Short form month name in current locale. For locale en_US this is one of: Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov or Dec.\r\n%c	Month with 1 or 2 digits.\r\n%D	Day with English suffix \'th\', \'nd\', \'st\' or \'rd\'\'. (1st, 2nd, 3rd...).\r\n%d	Day with 2 digits.\r\n%e	Day with 1 or 2 digits.\r\n%f	Microseconds 6 digits.\r\n%H	Hour with 2 digits between 00-23.\r\n%h	Hour with 2 digits between 01-12.\r\n%I	Hour with 2 digits between 01-12.\r\n%i	Minute with 2 digits.\r\n%j	Day of the year (001-366)\r\n%k	Hour with 1 digits between 0-23.\r\n%l	Hour with 1 digits between 1-12.\r\n%M	Full month name in current locale (Variable lc_time_names).\r\n%m	Month with 2 digits.\r\n%p	AM/PM according to current locale (Variable lc_time_names).\r\n%r	Time in 12 hour format, followed by AM/PM. Short for \'%I:%i:%S %p\'.\r\n%S	Seconds with 2 digits.\r\n%s	Seconds with 2 digits.\r\n%T	Time in 24 hour format. Short for \'%H:%i:%S\'.\r\n%U	Week number (00-53), when first day of the week is Sunday.\r\n%u	Week number (00-53), when first day of the week is Monday.\r\n%V	Week number (01-53), when first day of the week is Sunday. Used with %X.\r\n%v	Week number (01-53), when first day of the week is Monday. Used with %x.\r\n%W	Full weekday name in current locale (Variable lc_time_names).\r\n%w	Day of the week. 0 = Sunday, 6 = Saturday.\r\n%X	Year with 4 digits when first day of the week is Sunday. Used with %V.\r\n%x	Year with 4 digits when first day of the week is Monday. Used with %v.\r\n%Y	Year with 4 digits.\r\n%y	Year with 2 digits.\r\n%#	For str_to_date(), skip all numbers.\r\n%.	For str_to_date(), skip all punctation characters.\r\n%@	For str_to_date(), skip all alpha characters.\r\n%%	A literal % character.]'),
(19, 'SQLFormat', 'Time', '%h:%i %p', '[%a	Short weekday name in current locale (Variable lc_time_names).\r\n%b	Short form month name in current locale. For locale en_US this is one of: Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov or Dec.\r\n%c	Month with 1 or 2 digits.\r\n%D	Day with English suffix \'th\', \'nd\', \'st\' or \'rd\'\'. (1st, 2nd, 3rd...).\r\n%d	Day with 2 digits.\r\n%e	Day with 1 or 2 digits.\r\n%f	Microseconds 6 digits.\r\n%H	Hour with 2 digits between 00-23.\r\n%h	Hour with 2 digits between 01-12.\r\n%I	Hour with 2 digits between 01-12.\r\n%i	Minute with 2 digits.\r\n%j	Day of the year (001-366)\r\n%k	Hour with 1 digits between 0-23.\r\n%l	Hour with 1 digits between 1-12.\r\n%M	Full month name in current locale (Variable lc_time_names).\r\n%m	Month with 2 digits.\r\n%p	AM/PM according to current locale (Variable lc_time_names).\r\n%r	Time in 12 hour format, followed by AM/PM. Short for \'%I:%i:%S %p\'.\r\n%S	Seconds with 2 digits.\r\n%s	Seconds with 2 digits.\r\n%T	Time in 24 hour format. Short for \'%H:%i:%S\'.\r\n%U	Week number (00-53), when first day of the week is Sunday.\r\n%u	Week number (00-53), when first day of the week is Monday.\r\n%V	Week number (01-53), when first day of the week is Sunday. Used with %X.\r\n%v	Week number (01-53), when first day of the week is Monday. Used with %x.\r\n%W	Full weekday name in current locale (Variable lc_time_names).\r\n%w	Day of the week. 0 = Sunday, 6 = Saturday.\r\n%X	Year with 4 digits when first day of the week is Sunday. Used with %V.\r\n%x	Year with 4 digits when first day of the week is Monday. Used with %v.\r\n%Y	Year with 4 digits.\r\n%y	Year with 2 digits.\r\n%#	For str_to_date(), skip all numbers.\r\n%.	For str_to_date(), skip all punctation characters.\r\n%@	For str_to_date(), skip all alpha characters.\r\n%%	A literal % character.]'),
(21, 'Report', 'Description', '.\\ReportDescription\\', NULL),
(23, 'Location', 'Outline', '.\\Outlines\\', NULL),
(24, 'Location', 'Bulletin', '.\\Bulletins\\', NULL),
(30, 'SMTP', 'UserName', 'pwbjwatt@gmail.com', NULL),
(29, 'SMTP', 'Server', 'smtp.gmail.com', NULL),
(31, 'SMTP', 'Password', '[REDACTED_SMTP_PASSWORD]', NULL),
(32, 'SMTP', 'Port', '587', NULL),
(33, 'License', 'Liturgy', '000014722', NULL),
(35, 'SMTP', 'Key', '[REDACTED_GOOGLE_API_KEY]', NULL),
(36, 'Location', 'LimeReport', 'C:\\Users\\jonat\\Documents\\PythonProjects\\LimeReports\\', NULL),
(37, 'Location', 'LimeReportPattern', '.\\LimeReportPattern\\', NULL),
(43, 'Location', 'JSONSchema', '.\\schema\\', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
