-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 15, 2023 at 03:08 PM
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
-- Table structure for table `tblannouncement`
--

DROP TABLE IF EXISTS `tblannouncement`;
CREATE TABLE IF NOT EXISTS `tblannouncement` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Label` varchar(255) NOT NULL,
  `Announcement` longtext DEFAULT NULL,
  `RequestBy` varchar(255) DEFAULT NULL,
  `Continuous` tinyint(1) NOT NULL DEFAULT 1,
  `First` tinyint(1) NOT NULL DEFAULT 0,
  `Second` tinyint(1) NOT NULL DEFAULT 0,
  `Third` tinyint(1) NOT NULL DEFAULT 0,
  `Fourth` tinyint(1) NOT NULL DEFAULT 0,
  `Fifth` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `eDisplayOnly` tinyint(1) NOT NULL DEFAULT 0,
  `Note` longtext NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `tblannouncement`
--

INSERT INTO `tblannouncement` (`ID`, `ChurchID`, `Label`, `Announcement`, `RequestBy`, `Continuous`, `First`, `Second`, `Third`, `Fourth`, `Fifth`, `StartDate`, `EndDate`, `eDisplayOnly`, `Note`) VALUES
(1, 0, 'My Savior Lives Norhland', 'My Savior Lives Northland weekly televised ministry, produced of the in Duluth, Minnesota by the Minnesota North District, LCMS. https://www.mslnorthland.com/home/', NULL, 1, 1, 1, 1, 1, 1, NULL, NULL, 0, ''),
(2, 0, 'Swaddling Clothes', 'Consider a gift to \"Swaddling Clothes\" an outreach of Faith Lutheran Church, Silver Bay. It is a place for moms and moms-to-be to find help gathering items that are needed for a new baby. The store is opening February 18.\r\n', NULL, 1, 0, 0, 0, 1, 0, NULL, NULL, 0, ''),
(3, 0, 'LiC Building Fund', 'Consider a gift to Life in Christ building fund. Help us build our new church! Please indicate “Building Fund” on your check Note.', NULL, 1, 0, 0, 0, 1, 0, NULL, NULL, 0, ''),
(4, 0, 'Project Signup', 'Please find the Project Sign Up List on the Bulletin Board. Sign up and help keep up the church property.', NULL, 1, 1, 0, 1, 0, 0, NULL, NULL, 0, ''),
(5, 0, 'LiC Membership Information', 'Update your membership information for Life in Christ. Visit LiCgm.org/forms', NULL, 1, 0, 0, 0, 1, 0, NULL, NULL, 0, ''),
(6, 0, 'Bulletin Announcements', 'Announcements for the bulletin and the announcement display are due by Thursday evening.', NULL, 1, 1, 0, 0, 0, 0, NULL, NULL, 0, ''),
(7, 0, 'LiC Notifications', 'Please sign up for Life in Christ Notifications on Remind.com you will receive important messages about classes, worship services, etc. Set the browser on your phone to remind.com/join/licgm', NULL, 1, 1, 0, 0, 0, 0, NULL, NULL, 0, ''),
(8, 0, 'Private Communion', 'If you need Private Communion for any reason, a pending hospitalization, having a bad week, or you need the gifts that God gives in His Holy Supper. Please know I am available any time. It is part of my Divine Call to this congregation to administer the Sacrament. Call or text to make an appointment or drop in during office hours. I would be glad to help.', NULL, 1, 1, 0, 0, 0, 0, NULL, NULL, 0, ''),
(9, 0, 'Prayer Requests', 'Please fill out the Prayer request form to request prayers for Sunday Morning.', NULL, 1, 1, 0, 0, 0, 0, NULL, NULL, 0, ''),
(10, 0, 'Lawn Mowing', 'The lawn needs mowing. Please find the Mowing Sign Up List on the bulletin board.', NULL, 1, 0, 1, 0, 1, 0, NULL, NULL, 0, ''),
(11, 0, 'Associate Membership', 'Associate Membership to Life in Christ is available! This provides spiritual care while you are away from your home congregation. See Pastor Watt for details.', NULL, 1, 0, 1, 0, 0, 0, NULL, NULL, 0, ''),
(12, 0, 'Sermon Text Available', 'The Manuscripts for Pastor Watt\'s Sermons are available online.  Go to the Life in Christ web page http://licgm.org and click on \"Sermons\".', NULL, 1, 0, 1, 0, 0, 0, NULL, NULL, 0, ''),
(13, 0, 'LiC App', 'We have an App for that! LiC has an App for Smartphones. Goto LiCgm.org scan the QR-Code.', NULL, 1, 0, 0, 1, 0, 0, NULL, NULL, 0, ''),
(14, 0, 'White Wine in Use', 'White wine will be used for the Sacrament during Festival Services (i.e. Christmas, Easter, etc.).  Both red and white were used in ancient times (based on availability) for the celebration of Holy Communion. Theologian A. Jungmann says, \"when . . . the use of the purificator became general, that is since the sixteenth century, white wine has become commonly preferred because it leaves fewer traces in the linen.\" Jesus did not specify the color of the wine used for the sacrament.', NULL, 1, 0, 0, 1, 0, 0, NULL, NULL, 0, ''),
(15, 0, 'Listen to Lutheran Witness', 'You can Listen to the Lutheran Witness! Check out their PodCast on KFUO Radio\'s Web Page: https://www.kfuo.org/category/lutheran-witness/', NULL, 1, 0, 0, 1, 0, 0, NULL, NULL, 0, ''),
(16, 0, 'LiC Cradle Role', 'There is a Cradle Role Signup Sheet on the Narthex Table. Please sign up to keep in touch with our infant members, by providing faith resources for them. See Pastor Watt for Questions.', NULL, 1, 0, 1, 0, 0, 0, NULL, NULL, 0, ''),
(17, 0, 'Student Support', 'Life in Christ Church Work Student Support: Gifts are currently being accepted for our Church Work Student Support fund. These funds go directly to College Students who are members in our congregation and in Church Work Programs. We are currently supporting Eric Saunders. Please specify \"Student Fund\" on your check.', NULL, 1, 0, 0, 1, 0, 0, NULL, NULL, 0, ''),
(18, 0, 'Lorem ipsum dolor sit amet', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Est lorem ipsum dolor sit amet. Tempus egestas sed sed risus pretium quam vulputate dignissim suspendisse. Quam id leo in vitae turpis massa sed elementum. Varius morbi enim nunc faucibus a pellentesque sit amet. Urna cursus eget nunc scelerisque viverra mauris in. Etiam dignissim diam quis enim lobortis. Scelerisque viverra mauris in aliquam sem fringilla ut morbi. Non diam phasellus vestibulum lorem sed risus ultricies tristique. Sapien pellentesque habitant morbi tristique senectus et netus et. Varius morbi enim nunc faucibus a pellentesque sit. Quis vel eros donec ac odio tempor orci dapibus. Libero nunc consequat interdum varius sit amet mattis vulputate. Blandit aliquam etiam erat velit scelerisque in. Sociis natoque penatibus et magnis dis parturient montes. Semper feugiat nibh sed pulvinar proin gravida hendrerit lectus a.', NULL, 0, 0, 0, 0, 0, 0, NULL, NULL, 0, ''),
(19, 0, 'Greeting Cards Available', 'Greeting Cards for Confirmation, Graduation, etc. are available on the table at the Church entrance. Proceeds go to LiC LWML.\r\n', 'Jan', 1, 1, 1, 1, 1, 1, NULL, NULL, 0, ''),
(20, 0, 'Issues Etc.', 'EXPERT GUESTS, EXPANSIVE TOPICS, EXTOLLING CHRIST… Issues, Etc. is a radio show and podcast produced by Lutheran Public Radio, hosted by Rev. Todd Wilken.  This week\'s teachings include: \r\nPutting Children at the Center of Family Policy; \r\nResponding to Unanswered Bible Questions; \r\nThe Doctrine of the Trinity & the Bible; \r\nLies about Human Nature; \r\nThe Sacrifice of the Mass and more.  \r\nYou can listen on-demand at issuesetc.org, the LPR mobile app and your favorite podcast provider.', NULL, 1, 1, 1, 1, 1, 1, NULL, NULL, 0, ''),
(21, 0, 'Pastor Installation', 'Rev. Marty Mably will be installed at St. Matthews Church, Esco, MN on May 6 at 4pm. There will be a catered dinner following. RSVP by April 30 (218) 348-6033 or joesuew@yahoo.com', 'St. Matthews, Esco', 0, 1, 1, 1, 1, 1, '2023-04-05', '2023-04-30', 0, ''),
(22, 0, 'LCMS National Offering', 'The LCMS National Offering has its goal making carefully selected materials available in other languages so that all may hear the Good News of Christ crucified for all people. Translation work is especially important as the communities around our congregations increasingly include people for whom Engilish is not their first language. For more information please visit https://www.lcms.org/convention/noffering. ', 'President Harrison', 0, 1, 0, 1, 0, 1, '2023-04-05', '2023-07-31', 0, ''),
(23, 0, 'LFL National Conference', '2023 Lutherans For Life National Conference • October 11-13\r\nHoliday Inn Cincinnati Airport | Erlanger, Kentucky, with visits to the Ark Encounter and Creation Museum\r\nNational Conference Early Bird Registration Is Now Open!\r\nEarly Bird Registration – $100 through May 31, 2023. Early Bird discounts for adults only.\r\nRegister online beginning May 31 https://lutheransforlife.org/conference/', 'Pastor Watt', 1, 0, 1, 0, 1, 0, '2023-04-09', '2023-08-31', 0, ''),
(26, 0, 'This Week at Life in Christ\r\n', 'Wed 0am-1pm Pastor’s Office Hours\r\nThurs 10am-11am Pastor’s Reading Group\r\nFri 10am-1pm Pastor’s Office Hours\r\nSun 9am	Divine Service—Grand Marais\r\n10:30am	Bible Class\r\n', 'Pastor', 1, 1, 1, 1, 1, 1, NULL, NULL, 1, ''),
(27, 0, 'Upcoming Events:\r\n', 'May 8-10 Minnesota Pastor’s Conference\r\n', 'Pasor', 1, 1, 1, 1, 1, 1, NULL, NULL, 1, ''),
(28, 0, 'Frist & Second Thrift Store', 'Please save your gently-used household items for the new store (in the Birchbark building downtown). We hope to start donations in May.\r\nIf you\'d like to volunteer in the store, you\'ll earn credit toward a donation to your favorite local nonprofits. (Last year $20+/hour)\r\nContact us at 1stand2nd@boreal.org', 'The First and Second Thrift Store', 0, 1, 1, 1, 1, 0, '2023-04-12', '2023-05-31', 0, ''),
(29, 0, 'LCMS Founded 1847', 'The Lutheran Church was founded on April 26, 1847.\r\nHappy Birthday LCMS!', NULL, 0, 1, 1, 1, 1, 1, '2023-04-22', '2023-05-01', 0, '');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
