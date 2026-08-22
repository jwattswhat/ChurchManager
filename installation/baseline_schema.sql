/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_asset` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `AssetID`,
  1 AS `Description`,
  1 AS `Reserve`,
  1 AS `PurchaseDate`,
  1 AS `Depreciate`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_attendance` AS SELECT
 1 AS `ID`,
  1 AS `PersonID`,
  1 AS `AttendanceEventID`,
  1 AS `Communion` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_attendance_event` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `ServiceID`,
  1 AS `DateTime`,
  1 AS `Description`,
  1 AS `AttendanceType`,
  1 AS `CommunionOffered`,
  1 AS `HandCount`,
  1 AS `KnownAttendance`,
  1 AS `UnnamedAttendance`,
  1 AS `HandCountCommunion`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_attendance_weekly` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `DateTime`,
  1 AS `AttendanceType`,
  1 AS `EventCount`,
  1 AS `Attendance`,
  1 AS `KnownAttendance`,
  1 AS `UnnamedAttendance`,
  1 AS `Communion` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_church_identity` AS SELECT
 1 AS `ID`,
  1 AS `Church`,
  1 AS `Address`,
  1 AS `Address2`,
  1 AS `City`,
  1 AS `State`,
  1 AS `Zip`,
  1 AS `Pastor`,
  1 AS `Phone`,
  1 AS `eMail`,
  1 AS `Logo` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_directory_family` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `FamilyName`,
  1 AS `MarriageStatus`,
  1 AS `Image`,
  1 AS `Magazine`,
  1 AS `SpecialNotification`,
  1 AS `Directory` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_document` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `Title`,
  1 AS `Document`,
  1 AS `Date`,
  1 AS `DocumentType`,
  1 AS `Description`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_family_address` AS SELECT
 1 AS `ID`,
  1 AS `FamilyID`,
  1 AS `AddressLabel`,
  1 AS `Address`,
  1 AS `Address2`,
  1 AS `City`,
  1 AS `State`,
  1 AS `Zip`,
  1 AS `StartDate`,
  1 AS `EndDate`,
  1 AS `Unlisted` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_family_contact` AS SELECT
 1 AS `ID`,
  1 AS `FamilyID`,
  1 AS `ContactLabel`,
  1 AS `Type`,
  1 AS `Contact`,
  1 AS `Unlisted` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_favorite_hymn` AS SELECT
 1 AS `HymnID`,
  1 AS `HymnalID`,
  1 AS `Hymnal`,
  1 AS `PrintedReference`,
  1 AS `Title`,
  1 AS `Tune`,
  1 AS `Category`,
  1 AS `BibleText` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_hymn` AS SELECT
 1 AS `ID`,
  1 AS `HymnalID`,
  1 AS `EntrySlot`,
  1 AS `PrintedReference`,
  1 AS `Hymn`,
  1 AS `Title`,
  1 AS `Tune`,
  1 AS `BibleText`,
  1 AS `Category`,
  1 AS `PrintedStanzaCount`,
  1 AS `IsActive`,
  1 AS `FirstLine`,
  1 AS `Meter`,
  1 AS `Author`,
  1 AS `Translator`,
  1 AS `Composer`,
  1 AS `SourceNote`,
  1 AS `TextCopyrightStatus`,
  1 AS `TuneCopyrightStatus`,
  1 AS `SettingCopyrightStatus`,
  1 AS `CopyrightOwner`,
  1 AS `CopyrightYear`,
  1 AS `LicenseSource`,
  1 AS `LicenseReference`,
  1 AS `CopyrightNote`,
  1 AS `CopyrightVerifiedDate`,
  1 AS `CopyrightVerifiedBy`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_hymn_usage` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `ServiceID`,
  1 AS `HymnID`,
  1 AS `UsedAs`,
  1 AS `Stanzas`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_individual_attendance` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `PersonID`,
  1 AS `LastName`,
  1 AS `FirstName`,
  1 AS `DateTime`,
  1 AS `Description`,
  1 AS `AttendanceType`,
  1 AS `Communion`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_journal` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `Event`,
  1 AS `Complete`,
  1 AS `StartDate`,
  1 AS `EndDate`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_member_attendance_followup` AS SELECT
 1 AS `PersonID`,
  1 AS `ChurchID`,
  1 AS `LastName`,
  1 AS `FirstName`,
  1 AS `Status`,
  1 AS `LastAttended`,
  1 AS `MissedWeeks` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_membership_person` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `FamilyID`,
  1 AS `FirstName`,
  1 AS `MiddleName`,
  1 AS `LastName`,
  1 AS `Title`,
  1 AS `Status`,
  1 AS `MaritalStatus`,
  1 AS `MarriedTo`,
  1 AS `Baptized`,
  1 AS `Confirmed`,
  1 AS `Member`,
  1 AS `AssociateMember`,
  1 AS `Voter`,
  1 AS `Picture`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_participant` AS SELECT
 1 AS `ID`,
  1 AS `PersonID`,
  1 AS `Name`,
  1 AS `Phone`,
  1 AS `eMail`,
  1 AS `Active`,
  1 AS `ExternalParticipant`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_pastor_report` AS SELECT
 1 AS `ChurchID`,
  1 AS `Date`,
  1 AS `Pastor`,
  1 AS `Reported`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_pastors_attendance_comparison` AS SELECT
 1 AS `ChurchID`,
  1 AS `ReportYear`,
  1 AS `FullYearAttendance`,
  1 AS `ThroughDateAttendance`,
  1 AS `EventsThroughDate`,
  1 AS `AverageThroughDate`,
  1 AS `CommunionThroughDate` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_person_address` AS SELECT
 1 AS `ID`,
  1 AS `PersonID`,
  1 AS `AddressLabel`,
  1 AS `Address`,
  1 AS `Address2`,
  1 AS `City`,
  1 AS `State`,
  1 AS `Zip`,
  1 AS `StartDate`,
  1 AS `EndDate`,
  1 AS `Unlisted` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_person_contact` AS SELECT
 1 AS `ID`,
  1 AS `PersonID`,
  1 AS `ContactLabel`,
  1 AS `Type`,
  1 AS `Contact`,
  1 AS `Unlisted` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_person_date` AS SELECT
 1 AS `ID`,
  1 AS `PersonID`,
  1 AS `DateType`,
  1 AS `Date`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_project` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `Project`,
  1 AS `Description`,
  1 AS `Complete`,
  1 AS `CompletionDate`,
  1 AS `ProjectCategory`,
  1 AS `Priority`,
  1 AS `StartDate`,
  1 AS `EndDate`,
  1 AS `AssignedTo`,
  1 AS `AssignedToText`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_propers` AS SELECT
 1 AS `ID`,
  1 AS `LectionarySystemID`,
  1 AS `Cycle`,
  1 AS `Sort`,
  1 AS `Season`,
  1 AS `LiturgicalDate`,
  1 AS `Color`,
  1 AS `AltColor`,
  1 AS `Theme`,
  1 AS `HymnSug`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_reading` AS SELECT
 1 AS `ID`,
  1 AS `PropersID`,
  1 AS `Reading`,
  1 AS `Reference`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_report_catalog` AS SELECT
 1 AS `ID`,
  1 AS `Report`,
  1 AS `Title`,
  1 AS `Params`,
  1 AS `Batch`,
  1 AS `Note`,
  1 AS `Available`,
  1 AS `RequiredPermissionID` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_sermon` AS SELECT
 1 AS `ID`,
  1 AS `Reference`,
  1 AS `Title`,
  1 AS `Preacher`,
  1 AS `Author`,
  1 AS `Series`,
  1 AS `Date`,
  1 AS `Sermon`,
  1 AS `Outline`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_service` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `DateTime`,
  1 AS `Location`,
  1 AS `PropersID`,
  1 AS `LiturgicalDate`,
  1 AS `HolyCommunion`,
  1 AS `OrderofService`,
  1 AS `BulletinOrderTemplateID`,
  1 AS `OSNote`,
  1 AS `SermonID`,
  1 AS `Bulletin`,
  1 AS `Attendance`,
  1 AS `CommunionAttendance`,
  1 AS `CountforAttendance`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_service_role` AS SELECT
 1 AS `ID`,
  1 AS `ServiceID`,
  1 AS `ParticipantID`,
  1 AS `WorshipRoleID`,
  1 AS `Role`,
  1 AS `AssignmentStatus`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_sunday_announcement` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `AnnouncementCategory`,
  1 AS `Announcement`,
  1 AS `RequestBy`,
  1 AS `ScheduleText`,
  1 AS `ScheduleRule`,
  1 AS `StartDate`,
  1 AS `EndDate`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_sunday_prayer` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `PrayerCategory`,
  1 AS `RequestFor`,
  1 AS `RequestBy`,
  1 AS `ScheduleText`,
  1 AS `ScheduleRule`,
  1 AS `StartDate`,
  1 AS `EndDate`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_task` AS SELECT
 1 AS `ID`,
  1 AS `Task`,
  1 AS `Description`,
  1 AS `Complete`,
  1 AS `CompletionDate`,
  1 AS `Priority`,
  1 AS `ProjectID`,
  1 AS `DependencyID`,
  1 AS `StartDate`,
  1 AS `EndDate`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_task_worker` AS SELECT
 1 AS `ID`,
  1 AS `TaskID`,
  1 AS `PersonID`,
  1 AS `PersonText`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_participant` AS SELECT
 1 AS `ID`,
  1 AS `PersonID`,
  1 AS `DisplayName`,
  1 AS `Phone`,
  1 AS `eMail`,
  1 AS `Active`,
  1 AS `ExternalParticipant`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_planner_checklist` AS SELECT
 1 AS `ServiceID`,
  1 AS `Sequence`,
  1 AS `Task`,
  1 AS `Required`,
  1 AS `Status`,
  1 AS `Note`,
  1 AS `CompletionSource` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_planner_checklist_summary` AS SELECT
 1 AS `ServiceID`,
  1 AS `ManuallyConfirmed` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_planner_hymn` AS SELECT
 1 AS `ID`,
  1 AS `ServiceID`,
  1 AS `Sequence`,
  1 AS `HymnID`,
  1 AS `UsedAs`,
  1 AS `HymnNumber`,
  1 AS `Title`,
  1 AS `Stanzas`,
  1 AS `ReferenceText`,
  1 AS `Hymn` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_planner_order` AS SELECT
 1 AS `ID`,
  1 AS `ServiceID`,
  1 AS `Sequence`,
  1 AS `LineType`,
  1 AS `Label`,
  1 AS `WeeklyValue`,
  1 AS `ReferenceText`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_planner_participant` AS SELECT
 1 AS `ID`,
  1 AS `ServiceID`,
  1 AS `WorshipRoleID`,
  1 AS `Role`,
  1 AS `Name`,
  1 AS `Status` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_planner_reading` AS SELECT
 1 AS `ID`,
  1 AS `ServiceID`,
  1 AS `SortOrder`,
  1 AS `Reading`,
  1 AS `Reference` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_planner_required_position` AS SELECT
 1 AS `ServiceID`,
  1 AS `WorshipRoleID`,
  1 AS `Role`,
  1 AS `RequiredCount` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_planner_service` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `DateTime`,
  1 AS `Location`,
  1 AS `LiturgicalDate`,
  1 AS `HolyCommunion`,
  1 AS `Lectionary`,
  1 AS `Season`,
  1 AS `Color`,
  1 AS `Theme`,
  1 AS `OrderOfService`,
  1 AS `Sermon`,
  1 AS `Bulletin`,
  1 AS `OSNote`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_role` AS SELECT
 1 AS `ID`,
  1 AS `Name`,
  1 AS `Description`,
  1 AS `DisplayOrder`,
  1 AS `Active` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `rpt_worship_service_assignment` AS SELECT
 1 AS `ID`,
  1 AS `ServiceID`,
  1 AS `ParticipantID`,
  1 AS `WorshipRoleID`,
  1 AS `Role`,
  1 AS `Participant`,
  1 AS `AssignmentStatus`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `schema_migrations` (
  `version` varchar(100) NOT NULL,
  `checksum` char(64) NOT NULL,
  `applied_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingaccount` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `Code` varchar(30) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `AccountType` varchar(20) NOT NULL,
  `NormalBalance` varchar(10) NOT NULL,
  `PostingAllowed` tinyint(1) NOT NULL DEFAULT 1,
  `FunctionRequirement` varchar(15) NOT NULL DEFAULT 'OPTIONAL',
  `StatementGroup` varchar(100) DEFAULT NULL,
  `DisplayOrder` int(11) NOT NULL DEFAULT 0,
  `EffectiveFrom` date DEFAULT NULL,
  `EffectiveUntil` date DEFAULT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_account_code` (`OrganizationID`,`Code`),
  KEY `ix_acct_account_type` (`OrganizationID`,`AccountType`,`Active`),
  CONSTRAINT `fk_acct_account_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `ck_acct_account_type` CHECK (`AccountType` in ('ASSET','LIABILITY','NET_ASSET','REVENUE','EXPENSE','TRANSFER','OTHER')),
  CONSTRAINT `ck_acct_normal_balance` CHECK (`NormalBalance` in ('DEBIT','CREDIT')),
  CONSTRAINT `ck_acct_function_rule` CHECK (`FunctionRequirement` in ('REQUIRED','OPTIONAL','PROHIBITED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingattachment` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `TransactionID` bigint(20) NOT NULL,
  `StoredPath` varchar(1000) NOT NULL,
  `OriginalName` varchar(255) NOT NULL,
  `DocumentType` varchar(100) DEFAULT NULL,
  `FileHash` char(64) NOT NULL,
  `AddedByUserID` int(11) NOT NULL,
  `AddedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`ID`),
  KEY `ix_acct_attachment_transaction` (`TransactionID`),
  KEY `fk_acct_attachment_user` (`AddedByUserID`),
  CONSTRAINT `fk_acct_attachment_transaction` FOREIGN KEY (`TransactionID`) REFERENCES `tblaccountingtransaction` (`ID`),
  CONSTRAINT `fk_acct_attachment_user` FOREIGN KEY (`AddedByUserID`) REFERENCES `tbluser` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingauditevent` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `EntityType` varchar(100) NOT NULL,
  `EntityID` varchar(100) NOT NULL,
  `Action` varchar(100) NOT NULL,
  `BeforeJSON` longtext DEFAULT NULL,
  `AfterJSON` longtext DEFAULT NULL,
  `Reason` varchar(1000) DEFAULT NULL,
  `UserID` int(11) NOT NULL,
  `OccurredAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`ID`),
  KEY `ix_acct_audit_entity` (`OrganizationID`,`EntityType`,`EntityID`,`OccurredAt`),
  KEY `ix_acct_audit_user` (`UserID`,`OccurredAt`),
  CONSTRAINT `fk_acct_audit_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `fk_acct_audit_user` FOREIGN KEY (`UserID`) REFERENCES `tbluser` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingbankaccount` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `AccountID` int(11) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `InstitutionName` varchar(255) DEFAULT NULL,
  `AccountLastFour` char(4) DEFAULT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_bank_ledger_account` (`OrganizationID`,`AccountID`),
  KEY `fk_acct_bank_account` (`AccountID`),
  CONSTRAINT `fk_acct_bank_account` FOREIGN KEY (`AccountID`) REFERENCES `tblaccountingaccount` (`ID`),
  CONSTRAINT `fk_acct_bank_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingbankimportbatch` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `BankAccountID` int(11) NOT NULL,
  `OriginalName` varchar(255) NOT NULL,
  `FileHash` char(64) NOT NULL,
  `FileFormat` varchar(20) NOT NULL,
  `MappingJSON` longtext DEFAULT NULL,
  `RowCount` int(11) NOT NULL DEFAULT 0,
  `ImportedByUserID` int(11) NOT NULL,
  `ImportedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_bank_import_hash` (`BankAccountID`,`FileHash`),
  KEY `fk_acct_import_user` (`ImportedByUserID`),
  CONSTRAINT `fk_acct_import_bank` FOREIGN KEY (`BankAccountID`) REFERENCES `tblaccountingbankaccount` (`ID`),
  CONSTRAINT `fk_acct_import_user` FOREIGN KEY (`ImportedByUserID`) REFERENCES `tbluser` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingbankimportrow` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ImportBatchID` bigint(20) NOT NULL,
  `RowNumber` int(11) NOT NULL,
  `ExternalID` varchar(255) DEFAULT NULL,
  `TransactionDate` date NOT NULL,
  `Description` varchar(1000) NOT NULL,
  `Reference` varchar(255) DEFAULT NULL,
  `Amount` decimal(19,4) NOT NULL,
  `Fingerprint` char(64) NOT NULL,
  `MatchStatus` varchar(20) NOT NULL DEFAULT 'UNMATCHED',
  `MatchedTransactionLineID` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_import_row` (`ImportBatchID`,`RowNumber`),
  UNIQUE KEY `uq_acct_import_matched_line` (`MatchedTransactionLineID`),
  KEY `ix_acct_import_fingerprint` (`Fingerprint`),
  KEY `fk_acct_import_row_line` (`MatchedTransactionLineID`),
  CONSTRAINT `fk_acct_import_row_batch` FOREIGN KEY (`ImportBatchID`) REFERENCES `tblaccountingbankimportbatch` (`ID`),
  CONSTRAINT `fk_acct_import_row_line` FOREIGN KEY (`MatchedTransactionLineID`) REFERENCES `tblaccountingtransactionline` (`ID`),
  CONSTRAINT `ck_acct_import_match` CHECK (`MatchStatus` in ('UNMATCHED','MATCHED','IGNORED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingbudget` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `FiscalYearID` int(11) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `DetailMode` varchar(20) NOT NULL DEFAULT 'ACCOUNT_ONLY',
  `VersionNumber` int(11) NOT NULL DEFAULT 1,
  `Status` varchar(20) NOT NULL DEFAULT 'DRAFT',
  `BasedOnBudgetID` bigint(20) DEFAULT NULL,
  `CreatedByUserID` int(11) NOT NULL,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `ProposedByUserID` int(11) DEFAULT NULL,
  `ProposedAt` datetime(6) DEFAULT NULL,
  `AdoptedByUserID` int(11) DEFAULT NULL,
  `AdoptedAt` datetime(6) DEFAULT NULL,
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_budget_version` (`FiscalYearID`,`Name`,`VersionNumber`),
  KEY `ix_acct_budget_status` (`OrganizationID`,`FiscalYearID`,`Status`),
  KEY `fk_acct_budget_based_on` (`BasedOnBudgetID`),
  KEY `fk_acct_budget_creator` (`CreatedByUserID`),
  KEY `fk_acct_budget_proposer` (`ProposedByUserID`),
  KEY `fk_acct_budget_adopter` (`AdoptedByUserID`),
  CONSTRAINT `fk_acct_budget_adopter` FOREIGN KEY (`AdoptedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_acct_budget_based_on` FOREIGN KEY (`BasedOnBudgetID`) REFERENCES `tblaccountingbudget` (`ID`),
  CONSTRAINT `fk_acct_budget_creator` FOREIGN KEY (`CreatedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_acct_budget_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `fk_acct_budget_proposer` FOREIGN KEY (`ProposedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_acct_budget_year` FOREIGN KEY (`FiscalYearID`) REFERENCES `tblaccountingfiscalyear` (`ID`),
  CONSTRAINT `ck_acct_budget_version` CHECK (`VersionNumber` > 0),
  CONSTRAINT `ck_acct_budget_detail_mode` CHECK (`DetailMode` in ('ACCOUNT_ONLY','DETAILED')),
  CONSTRAINT `ck_acct_budget_status` CHECK (`Status` in ('DRAFT','PROPOSED','ADOPTED','SUPERSEDED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingbudgetline` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `BudgetID` bigint(20) NOT NULL,
  `FiscalPeriodID` int(11) NOT NULL,
  `AccountID` int(11) NOT NULL,
  `FundID` int(11) NOT NULL,
  `FunctionID` int(11) DEFAULT NULL,
  `LineItemName` varchar(255) DEFAULT NULL,
  `Amount` decimal(19,2) NOT NULL DEFAULT 0.00,
  `Note` varchar(1000) DEFAULT NULL,
  `DisplayOrder` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`),
  KEY `ix_acct_budget_line_report` (`BudgetID`,`FiscalPeriodID`,`AccountID`,`FundID`,`FunctionID`),
  KEY `ix_acct_budget_line_order` (`BudgetID`,`DisplayOrder`,`ID`),
  KEY `fk_acct_budget_line_period` (`FiscalPeriodID`),
  KEY `fk_acct_budget_line_account` (`AccountID`),
  KEY `fk_acct_budget_line_fund` (`FundID`),
  KEY `fk_acct_budget_line_function` (`FunctionID`),
  CONSTRAINT `fk_acct_budget_line_account` FOREIGN KEY (`AccountID`) REFERENCES `tblaccountingaccount` (`ID`),
  CONSTRAINT `fk_acct_budget_line_budget` FOREIGN KEY (`BudgetID`) REFERENCES `tblaccountingbudget` (`ID`),
  CONSTRAINT `fk_acct_budget_line_function` FOREIGN KEY (`FunctionID`) REFERENCES `tblaccountingfunction` (`ID`),
  CONSTRAINT `fk_acct_budget_line_fund` FOREIGN KEY (`FundID`) REFERENCES `tblaccountingfund` (`ID`),
  CONSTRAINT `fk_acct_budget_line_period` FOREIGN KEY (`FiscalPeriodID`) REFERENCES `tblaccountingfiscalperiod` (`ID`),
  CONSTRAINT `ck_acct_budget_line_amount` CHECK (`Amount` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingfiscalperiod` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FiscalYearID` int(11) NOT NULL,
  `PeriodNumber` smallint(6) NOT NULL,
  `Name` varchar(100) NOT NULL,
  `StartDate` date NOT NULL,
  `EndDate` date NOT NULL,
  `Status` varchar(15) NOT NULL DEFAULT 'OPEN',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_period_number` (`FiscalYearID`,`PeriodNumber`),
  KEY `ix_acct_period_dates` (`StartDate`,`EndDate`,`Status`),
  CONSTRAINT `fk_acct_period_year` FOREIGN KEY (`FiscalYearID`) REFERENCES `tblaccountingfiscalyear` (`ID`),
  CONSTRAINT `ck_acct_period_dates` CHECK (`StartDate` <= `EndDate`),
  CONSTRAINT `ck_acct_period_status` CHECK (`Status` in ('OPEN','CLOSED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 */ /*!50003 TRIGGER trg_acct_period_lock_used_boundaries
BEFORE UPDATE ON tblAccountingFiscalPeriod
FOR EACH ROW
BEGIN
    IF (
        NOT (NEW.FiscalYearID <=> OLD.FiscalYearID)
        OR NOT (NEW.PeriodNumber <=> OLD.PeriodNumber)
        OR NOT (NEW.StartDate <=> OLD.StartDate)
        OR NOT (NEW.EndDate <=> OLD.EndDate)
    ) AND (
        EXISTS (
            SELECT 1 FROM tblAccountingTransaction t
            WHERE t.FiscalPeriodID=OLD.ID AND t.Status IN ('POSTED','REVERSED')
        )
        OR EXISTS (
            SELECT 1 FROM tblAccountingBudgetLine l
            JOIN tblAccountingBudget b ON b.ID=l.BudgetID
            WHERE l.FiscalPeriodID=OLD.ID AND b.Status='ADOPTED'
        )
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT='This fiscal period is locked by posted transactions or an adopted budget.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingfiscalyear` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `Name` varchar(100) NOT NULL,
  `StartDate` date NOT NULL,
  `EndDate` date NOT NULL,
  `Status` varchar(15) NOT NULL DEFAULT 'OPEN',
  `ClosingTransactionID` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_year_name` (`OrganizationID`,`Name`),
  KEY `fk_acct_year_closing_transaction` (`ClosingTransactionID`),
  CONSTRAINT `fk_acct_year_closing_transaction` FOREIGN KEY (`ClosingTransactionID`) REFERENCES `tblaccountingtransaction` (`ID`),
  CONSTRAINT `fk_acct_year_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `ck_acct_year_dates` CHECK (`StartDate` <= `EndDate`),
  CONSTRAINT `ck_acct_year_status` CHECK (`Status` in ('OPEN','CLOSING','CLOSED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingfunction` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `Code` varchar(30) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `FunctionClass` varchar(20) NOT NULL DEFAULT 'PROGRAM',
  `DisplayOrder` int(11) NOT NULL DEFAULT 0,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_function_code` (`OrganizationID`,`Code`),
  CONSTRAINT `fk_acct_function_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `ck_acct_function_class` CHECK (`FunctionClass` in ('PROGRAM','MANAGEMENT_GENERAL','FUNDRAISING'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingfund` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `Code` varchar(30) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `NetAssetClass` varchar(30) NOT NULL,
  `RestrictionType` varchar(30) NOT NULL DEFAULT 'NONE',
  `BoardDesignated` tinyint(1) NOT NULL DEFAULT 0,
  `RestrictionText` varchar(1000) DEFAULT NULL,
  `EffectiveFrom` date DEFAULT NULL,
  `EffectiveUntil` date DEFAULT NULL,
  `NetAssetAccountID` int(11) DEFAULT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `ClosedDate` date DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_fund_code` (`OrganizationID`,`Code`),
  KEY `ix_acct_fund_class` (`OrganizationID`,`NetAssetClass`,`Active`),
  KEY `fk_acct_fund_netasset` (`NetAssetAccountID`),
  CONSTRAINT `fk_acct_fund_netasset` FOREIGN KEY (`NetAssetAccountID`) REFERENCES `tblaccountingaccount` (`ID`),
  CONSTRAINT `fk_acct_fund_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `ck_acct_fund_class` CHECK (`NetAssetClass` in ('WITHOUT_DONOR_RESTRICTIONS','WITH_DONOR_RESTRICTIONS')),
  CONSTRAINT `ck_acct_restriction_type` CHECK (`RestrictionType` in ('NONE','PURPOSE','TIME','PURPOSE_AND_TIME')),
  CONSTRAINT `ck_acct_fund_designation` CHECK (`NetAssetClass` <> 'WITH_DONOR_RESTRICTIONS' or `BoardDesignated` <> 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingorganization` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT NULL,
  `LegalName` varchar(255) NOT NULL,
  `FiscalYearStartMonth` tinyint(4) NOT NULL DEFAULT 1,
  `BaseCurrency` char(3) NOT NULL DEFAULT 'USD',
  `ReportingBasis` varchar(20) NOT NULL DEFAULT 'MODIFIED_CASH',
  `NextTransactionNumber` bigint(20) NOT NULL DEFAULT 1,
  `ApprovalThreshold` decimal(19,2) NOT NULL DEFAULT 500.00,
  `ApprovalPolicy` varchar(30) NOT NULL DEFAULT 'INDEPENDENT_PREFERRED',
  `AttachmentThreshold` decimal(19,2) NOT NULL DEFAULT 250.00,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  KEY `fk_acct_org_church` (`ChurchID`),
  CONSTRAINT `fk_acct_org_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `ck_acct_org_start_month` CHECK (`FiscalYearStartMonth` between 1 and 12),
  CONSTRAINT `ck_acct_org_thresholds` CHECK (`ApprovalThreshold` >= 0 and `AttachmentThreshold` >= 0),
  CONSTRAINT `ck_acct_org_approval_policy` CHECK (`ApprovalPolicy` in ('INDEPENDENT_REQUIRED','INDEPENDENT_PREFERRED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingpayee` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `Reference` varchar(255) DEFAULT NULL,
  `ContactData` longtext DEFAULT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  KEY `ix_acct_payee_name` (`OrganizationID`,`Name`,`Active`),
  CONSTRAINT `fk_acct_payee_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingreconciliation` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `BankAccountID` int(11) NOT NULL,
  `StatementDate` date NOT NULL,
  `BeginningBalance` decimal(19,4) NOT NULL,
  `EndingBalance` decimal(19,4) NOT NULL,
  `Status` varchar(20) NOT NULL DEFAULT 'DRAFT',
  `PreparedByUserID` int(11) NOT NULL,
  `PreparedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `CompletedAt` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_reconciliation_statement` (`BankAccountID`,`StatementDate`),
  KEY `fk_acct_reconciliation_user` (`PreparedByUserID`),
  CONSTRAINT `fk_acct_reconciliation_bank` FOREIGN KEY (`BankAccountID`) REFERENCES `tblaccountingbankaccount` (`ID`),
  CONSTRAINT `fk_acct_reconciliation_user` FOREIGN KEY (`PreparedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `ck_acct_reconciliation_status` CHECK (`Status` in ('DRAFT','COMPLETED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingreconciliationitem` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ReconciliationID` bigint(20) NOT NULL,
  `TransactionLineID` bigint(20) NOT NULL,
  `ImportRowID` bigint(20) DEFAULT NULL,
  `ClearedDate` date NOT NULL,
  `ClearedAmount` decimal(19,4) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_reconciliation_line` (`ReconciliationID`,`TransactionLineID`),
  UNIQUE KEY `uq_acct_recon_transaction_line` (`TransactionLineID`),
  UNIQUE KEY `uq_acct_recon_import_row` (`ImportRowID`),
  KEY `fk_acct_recon_item_line` (`TransactionLineID`),
  KEY `fk_acct_recon_item_import` (`ImportRowID`),
  CONSTRAINT `fk_acct_recon_item_header` FOREIGN KEY (`ReconciliationID`) REFERENCES `tblaccountingreconciliation` (`ID`),
  CONSTRAINT `fk_acct_recon_item_import` FOREIGN KEY (`ImportRowID`) REFERENCES `tblaccountingbankimportrow` (`ID`),
  CONSTRAINT `fk_acct_recon_item_line` FOREIGN KEY (`TransactionLineID`) REFERENCES `tblaccountingtransactionline` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingtransaction` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `OrganizationID` int(11) NOT NULL,
  `TransactionNumber` bigint(20) DEFAULT NULL,
  `TransactionDate` date NOT NULL,
  `FiscalPeriodID` int(11) NOT NULL,
  `TransactionType` varchar(30) NOT NULL DEFAULT 'JOURNAL',
  `Status` varchar(20) NOT NULL DEFAULT 'DRAFT',
  `Description` varchar(1000) NOT NULL,
  `Reference` varchar(255) DEFAULT NULL,
  `OriginalTransactionID` bigint(20) DEFAULT NULL,
  `ReversalTransactionID` bigint(20) DEFAULT NULL,
  `Version` int(11) NOT NULL DEFAULT 1,
  `CreatedByUserID` int(11) NOT NULL,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `ReviewedByUserID` int(11) DEFAULT NULL,
  `ReviewedAt` datetime(6) DEFAULT NULL,
  `PostedByUserID` int(11) DEFAULT NULL,
  `PostedAt` datetime(6) DEFAULT NULL,
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_transaction_number` (`OrganizationID`,`TransactionNumber`),
  KEY `ix_acct_transaction_date` (`OrganizationID`,`TransactionDate`),
  KEY `ix_acct_transaction_status` (`OrganizationID`,`Status`,`TransactionDate`),
  KEY `ix_acct_transaction_period` (`FiscalPeriodID`,`Status`),
  KEY `ix_acct_transaction_reference` (`OrganizationID`,`Reference`),
  KEY `fk_acct_transaction_creator` (`CreatedByUserID`),
  KEY `fk_acct_transaction_reviewer` (`ReviewedByUserID`),
  KEY `fk_acct_transaction_poster` (`PostedByUserID`),
  KEY `fk_acct_transaction_original` (`OriginalTransactionID`),
  KEY `fk_acct_transaction_reversal` (`ReversalTransactionID`),
  CONSTRAINT `fk_acct_transaction_creator` FOREIGN KEY (`CreatedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_acct_transaction_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `fk_acct_transaction_original` FOREIGN KEY (`OriginalTransactionID`) REFERENCES `tblaccountingtransaction` (`ID`),
  CONSTRAINT `fk_acct_transaction_period` FOREIGN KEY (`FiscalPeriodID`) REFERENCES `tblaccountingfiscalperiod` (`ID`),
  CONSTRAINT `fk_acct_transaction_poster` FOREIGN KEY (`PostedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_acct_transaction_reversal` FOREIGN KEY (`ReversalTransactionID`) REFERENCES `tblaccountingtransaction` (`ID`),
  CONSTRAINT `fk_acct_transaction_reviewer` FOREIGN KEY (`ReviewedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `ck_acct_transaction_status` CHECK (`Status` in ('DRAFT','READY','APPROVED','POSTED','REVERSED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblaccountingtransactionline` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `TransactionID` bigint(20) NOT NULL,
  `LineNumber` smallint(6) NOT NULL,
  `AccountID` int(11) NOT NULL,
  `FundID` int(11) NOT NULL,
  `FunctionID` int(11) DEFAULT NULL,
  `PayeeID` int(11) DEFAULT NULL,
  `Description` varchar(1000) DEFAULT NULL,
  `Debit` decimal(19,2) NOT NULL DEFAULT 0.00,
  `Credit` decimal(19,2) NOT NULL DEFAULT 0.00,
  `ClearedState` varchar(15) NOT NULL DEFAULT 'UNCLEARED',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_acct_transaction_line` (`TransactionID`,`LineNumber`),
  KEY `ix_acct_line_account` (`AccountID`,`TransactionID`),
  KEY `ix_acct_line_fund` (`FundID`,`TransactionID`),
  KEY `ix_acct_line_function` (`FunctionID`,`TransactionID`),
  KEY `ix_acct_line_payee` (`PayeeID`,`TransactionID`),
  CONSTRAINT `fk_acct_line_account` FOREIGN KEY (`AccountID`) REFERENCES `tblaccountingaccount` (`ID`),
  CONSTRAINT `fk_acct_line_function` FOREIGN KEY (`FunctionID`) REFERENCES `tblaccountingfunction` (`ID`),
  CONSTRAINT `fk_acct_line_fund` FOREIGN KEY (`FundID`) REFERENCES `tblaccountingfund` (`ID`),
  CONSTRAINT `fk_acct_line_payee` FOREIGN KEY (`PayeeID`) REFERENCES `tblaccountingpayee` (`ID`),
  CONSTRAINT `fk_acct_line_transaction` FOREIGN KEY (`TransactionID`) REFERENCES `tblaccountingtransaction` (`ID`),
  CONSTRAINT `ck_acct_line_amounts` CHECK (`Debit` >= 0 and `Credit` >= 0 and (`Debit` > 0 and `Credit` = 0 or `Credit` > 0 and `Debit` = 0)),
  CONSTRAINT `ck_acct_line_cleared` CHECK (`ClearedState` in ('UNCLEARED','CLEARED','RECONCILED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblannouncement` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Priority` int(11) NOT NULL DEFAULT 4,
  `Announcement` longtext DEFAULT NULL,
  `RequestBy` varchar(255) DEFAULT NULL,
  `ScheduleText` varchar(255) NOT NULL,
  `ScheduleRule` varchar(255) NOT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  `pic` longblob DEFAULT NULL,
  `AnnouncementCategory` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblannouncement_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_announcement_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblasset` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT 0,
  `AssetID` varchar(255) NOT NULL,
  `Description` varchar(255) NOT NULL,
  `Reserve` tinyint(1) NOT NULL DEFAULT 0,
  `PurchaseDate` date DEFAULT NULL,
  `Depreciate` tinyint(1) NOT NULL DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblasset_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_asset_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblattendance` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) NOT NULL,
  `AttendanceEventID` int(11) NOT NULL,
  `Communion` tinyint(1) NOT NULL DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_attendance_person_event` (`PersonID`,`AttendanceEventID`),
  KEY `fk_tblattendance_tblattendanceevent1_idx` (`AttendanceEventID`),
  KEY `fk_tblattendance_tblperson1_idx` (`PersonID`),
  CONSTRAINT `fk_attendance_event` FOREIGN KEY (`AttendanceEventID`) REFERENCES `tblattendanceevent` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_attendance_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblattendanceevent` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `ServiceID` int(11) DEFAULT NULL,
  `DateTime` datetime DEFAULT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `AttendanceType` varchar(255) DEFAULT 'Worship Service w/ Communion',
  `CommunionOffered` tinyint(1) NOT NULL DEFAULT 0,
  `HandCount` int(11) NOT NULL DEFAULT 0,
  `HandCountCommunion` int(11) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblattendanceevent_tblchurch1_idx` (`ChurchID`),
  KEY `fk_tblattendanceevent_tblservice1_idx` (`ServiceID`),
  CONSTRAINT `fk_attendevent_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_attendevent_service` FOREIGN KEY (`ServiceID`) REFERENCES `tblservice` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblbulletinorderline` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `LineKey` varchar(150) NOT NULL,
  `TemplateID` int(11) NOT NULL,
  `Sequence` int(11) NOT NULL,
  `LineType` varchar(40) NOT NULL DEFAULT 'TEXT',
  `Label` varchar(120) NOT NULL DEFAULT '',
  `ValueSource` varchar(40) DEFAULT NULL,
  `ValueKey` varchar(100) DEFAULT NULL,
  `ReferenceText` varchar(80) DEFAULT NULL,
  `StyleName` varchar(60) NOT NULL DEFAULT 'Normal',
  `LabelBold` tinyint(1) NOT NULL DEFAULT 0,
  `ValueBold` tinyint(1) NOT NULL DEFAULT 0,
  `Italic` tinyint(1) NOT NULL DEFAULT 0,
  `IndentLevel` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `TabPosition` decimal(6,2) DEFAULT NULL,
  `TabAlignment` varchar(20) NOT NULL DEFAULT 'LEFT',
  `TabLeader` varchar(20) NOT NULL DEFAULT 'NONE',
  `ConditionType` varchar(40) NOT NULL DEFAULT 'ALWAYS',
  `ConditionValue` varchar(100) DEFAULT NULL,
  `Note` varchar(250) DEFAULT NULL,
  `NeedsReview` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_bulletin_order_line_sequence` (`TemplateID`,`Sequence`),
  UNIQUE KEY `uq_bulletin_order_line_key` (`TemplateID`,`LineKey`),
  KEY `ix_bulletin_order_line_type` (`LineType`),
  CONSTRAINT `fk_bulletin_order_line_template` FOREIGN KEY (`TemplateID`) REFERENCES `tblbulletinordertemplate` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblbulletinordertemplate` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TemplateKey` varchar(150) NOT NULL,
  `PackageID` int(11) DEFAULT NULL,
  `ChurchID` int(11) DEFAULT NULL,
  `HymnalID` int(11) DEFAULT NULL,
  `Name` varchar(255) NOT NULL,
  `Description` varchar(250) DEFAULT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `IsStarter` tinyint(1) NOT NULL DEFAULT 0,
  `Version` int(11) NOT NULL DEFAULT 1,
  `CreatedAt` datetime NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_bulletin_order_template_key` (`TemplateKey`),
  KEY `ix_bulletin_order_church_name` (`ChurchID`,`Name`),
  KEY `ix_bulletin_order_hymnal` (`HymnalID`),
  KEY `ix_bulletin_order_package` (`PackageID`),
  CONSTRAINT `fk_bulletin_order_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_bulletin_order_hymnal` FOREIGN KEY (`HymnalID`) REFERENCES `tblhymnal` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_bulletin_order_package` FOREIGN KEY (`PackageID`) REFERENCES `tblorderofservicepackage` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblchoices` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Field` varchar(255) NOT NULL,
  `Choices` longtext NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_choices_field` (`Field`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblchurch` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Church` varchar(255) NOT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `Address2` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT 'Grand Marais',
  `State` varchar(255) DEFAULT 'MN',
  `Zip` varchar(255) DEFAULT '55604',
  `Pastor` varchar(255) DEFAULT NULL,
  `Phone` varchar(255) DEFAULT NULL,
  `eMail` varchar(255) DEFAULT NULL,
  `Logo` longblob DEFAULT NULL,
  `PrimaryHymnalID` int(11) DEFAULT NULL,
  `PrimaryLectionaryEditionID` int(11) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `ix_church_primary_hymnal` (`PrimaryHymnalID`),
  KEY `ix_church_primary_lectionary_edition` (`PrimaryLectionaryEditionID`),
  CONSTRAINT `fk_church_primary_hymnal` FOREIGN KEY (`PrimaryHymnalID`) REFERENCES `tblhymnal` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_church_primary_lectionary_edition` FOREIGN KEY (`PrimaryLectionaryEditionID`) REFERENCES `tbllectionaryedition` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblchurchinfo` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT NULL,
  `InfoType` varchar(255) NOT NULL,
  `InfoValue` varchar(255) NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `ChurchID` (`ChurchID`),
  CONSTRAINT `fk_churchinfo_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblconfig` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ConfigFamily` varchar(255) NOT NULL,
  `ConfigType` varchar(100) NOT NULL,
  `ConfigValue` varchar(255) NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontribution` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `BatchID` bigint(20) NOT NULL,
  `CorrectionOfContributionID` bigint(20) DEFAULT NULL,
  `ContributorID` bigint(20) DEFAULT NULL,
  `EnteredEnvelopeNumber` varchar(30) DEFAULT NULL,
  `ContributionMethod` varchar(20) NOT NULL DEFAULT 'CASH',
  `ReferenceValue` varchar(255) DEFAULT NULL,
  `ReceivedDate` date NOT NULL,
  `Amount` decimal(19,2) NOT NULL DEFAULT 0.00,
  `NonCashDescription` varchar(1000) DEFAULT NULL,
  `DonorEstimatedValue` decimal(14,2) DEFAULT NULL,
  `StatementEligibility` varchar(20) NOT NULL DEFAULT 'ELIGIBLE',
  `GoodsOrServicesProvided` tinyint(1) NOT NULL DEFAULT 0,
  `GoodsOrServicesDescription` varchar(1000) DEFAULT NULL,
  `GoodsOrServicesValue` decimal(19,2) DEFAULT NULL,
  `IntangibleReligiousBenefitOnly` tinyint(1) NOT NULL DEFAULT 0,
  `EligibilityOverrideReason` varchar(1000) DEFAULT NULL,
  `TributeType` varchar(20) DEFAULT NULL,
  `HonoreeName` varchar(255) DEFAULT NULL,
  `AcknowledgmentContact` varchar(1000) DEFAULT NULL,
  `DonorDisclosureAuthorized` tinyint(1) NOT NULL DEFAULT 0,
  `AmountDisclosureAuthorized` tinyint(1) NOT NULL DEFAULT 0,
  `DonorDirection` varchar(1000) DEFAULT NULL,
  `DirectionStatus` varchar(20) NOT NULL DEFAULT 'NONE',
  `DirectionResolution` varchar(1000) DEFAULT NULL,
  `Note` varchar(2000) DEFAULT NULL,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  KEY `ix_contribution_batch` (`BatchID`,`ID`),
  KEY `ix_contribution_contributor_date` (`ContributorID`,`ReceivedDate`),
  KEY `ix_contribution_correction_source` (`CorrectionOfContributionID`),
  CONSTRAINT `fk_contribution_batch` FOREIGN KEY (`BatchID`) REFERENCES `tblcontributionbatch` (`ID`),
  CONSTRAINT `fk_contribution_contributor` FOREIGN KEY (`ContributorID`) REFERENCES `tblcontributioncontributor` (`ID`),
  CONSTRAINT `fk_contribution_correction_source` FOREIGN KEY (`CorrectionOfContributionID`) REFERENCES `tblcontribution` (`ID`),
  CONSTRAINT `ck_contribution_method` CHECK (`ContributionMethod` in ('CASH','CHECK','ELECTRONIC','NON_CASH','OTHER')),
  CONSTRAINT `ck_contribution_amount` CHECK (`Amount` >= 0),
  CONSTRAINT `ck_contribution_statement` CHECK (`StatementEligibility` in ('ELIGIBLE','INELIGIBLE','REVIEW')),
  CONSTRAINT `ck_contribution_goods_value` CHECK (`GoodsOrServicesValue` is null or `GoodsOrServicesValue` >= 0),
  CONSTRAINT `ck_contribution_benefit` CHECK (`GoodsOrServicesProvided` <> 1 or `IntangibleReligiousBenefitOnly` <> 1),
  CONSTRAINT `ck_contribution_tribute` CHECK (`TributeType` is null and `HonoreeName` is null or `TributeType` in ('IN_MEMORY_OF','IN_HONOR_OF') and `HonoreeName` is not null),
  CONSTRAINT `ck_contribution_direction` CHECK (`DirectionStatus` in ('NONE','REVIEW','CLARIFIED','RETURNED','ACCEPTED')),
  CONSTRAINT `ck_contribution_donor_estimated_value` CHECK (`DonorEstimatedValue` is null or `DonorEstimatedValue` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontributionallocation` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ContributionID` bigint(20) NOT NULL,
  `PurposeID` bigint(20) DEFAULT NULL,
  `OrganizationID` int(11) NOT NULL,
  `FundID` int(11) NOT NULL,
  `RevenueAccountID` int(11) NOT NULL,
  `FunctionID` int(11) DEFAULT NULL,
  `Amount` decimal(19,2) NOT NULL,
  `DonorRestrictionNote` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `ix_contribution_allocation_contribution` (`ContributionID`,`ID`),
  KEY `ix_contribution_allocation_fund` (`OrganizationID`,`FundID`),
  KEY `fk_contribution_allocation_purpose` (`PurposeID`),
  KEY `fk_contribution_allocation_fund` (`FundID`),
  KEY `fk_contribution_allocation_revenue` (`RevenueAccountID`),
  KEY `fk_contribution_allocation_function` (`FunctionID`),
  CONSTRAINT `fk_contribution_allocation_contribution` FOREIGN KEY (`ContributionID`) REFERENCES `tblcontribution` (`ID`),
  CONSTRAINT `fk_contribution_allocation_function` FOREIGN KEY (`FunctionID`) REFERENCES `tblaccountingfunction` (`ID`),
  CONSTRAINT `fk_contribution_allocation_fund` FOREIGN KEY (`FundID`) REFERENCES `tblaccountingfund` (`ID`),
  CONSTRAINT `fk_contribution_allocation_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `fk_contribution_allocation_purpose` FOREIGN KEY (`PurposeID`) REFERENCES `tblcontributionpurpose` (`ID`),
  CONSTRAINT `fk_contribution_allocation_revenue` FOREIGN KEY (`RevenueAccountID`) REFERENCES `tblaccountingaccount` (`ID`),
  CONSTRAINT `ck_contribution_allocation_amount` CHECK (`Amount` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontributionauditevent` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `UserID` int(11) DEFAULT NULL,
  `Action` varchar(100) NOT NULL,
  `EntityType` varchar(100) NOT NULL,
  `EntityID` bigint(20) DEFAULT NULL,
  `SafeReference` varchar(255) DEFAULT NULL,
  `Reason` varchar(1000) DEFAULT NULL,
  `OccurredAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`ID`),
  KEY `ix_contribution_audit_church_time` (`ChurchID`,`OccurredAt`),
  KEY `ix_contribution_audit_entity` (`EntityType`,`EntityID`,`OccurredAt`),
  KEY `fk_contribution_audit_user` (`UserID`),
  CONSTRAINT `fk_contribution_audit_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_contribution_audit_user` FOREIGN KEY (`UserID`) REFERENCES `tbluser` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontributionbatch` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `BatchDate` date NOT NULL,
  `Description` varchar(500) NOT NULL,
  `ServiceID` int(11) DEFAULT NULL,
  `AttendanceEventID` int(11) DEFAULT NULL,
  `DepositDate` date DEFAULT NULL,
  `OrganizationID` int(11) NOT NULL,
  `BankAccountID` int(11) DEFAULT NULL,
  `Status` varchar(12) NOT NULL DEFAULT 'DRAFT',
  `ControlTotal` decimal(19,2) DEFAULT NULL,
  `CalculatedTotal` decimal(19,2) NOT NULL DEFAULT 0.00,
  `AccountingTransactionID` bigint(20) DEFAULT NULL,
  `ReversalAccountingTransactionID` bigint(20) DEFAULT NULL,
  `CorrectsBatchID` bigint(20) DEFAULT NULL,
  `CorrectionBatchID` bigint(20) DEFAULT NULL,
  `CorrectionReason` varchar(1000) DEFAULT NULL,
  `Version` int(11) NOT NULL DEFAULT 1,
  `EnteredByUserID` int(11) NOT NULL,
  `EnteredAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `ReviewedByUserID` int(11) DEFAULT NULL,
  `ReviewedAt` datetime(6) DEFAULT NULL,
  `PostedByUserID` int(11) DEFAULT NULL,
  `PostedAt` datetime(6) DEFAULT NULL,
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_contribution_batch_transaction` (`AccountingTransactionID`),
  UNIQUE KEY `uq_contribution_batch_reversal_transaction` (`ReversalAccountingTransactionID`),
  KEY `ix_contribution_batch_status` (`ChurchID`,`Status`,`BatchDate`),
  KEY `ix_contribution_batch_service` (`ServiceID`),
  KEY `fk_contribution_batch_attendance` (`AttendanceEventID`),
  KEY `fk_contribution_batch_org` (`OrganizationID`),
  KEY `fk_contribution_batch_bank` (`BankAccountID`),
  KEY `fk_contribution_batch_corrects` (`CorrectsBatchID`),
  KEY `fk_contribution_batch_correction` (`CorrectionBatchID`),
  KEY `fk_contribution_batch_entered_by` (`EnteredByUserID`),
  KEY `fk_contribution_batch_reviewed_by` (`ReviewedByUserID`),
  KEY `fk_contribution_batch_posted_by` (`PostedByUserID`),
  CONSTRAINT `fk_contribution_batch_attendance` FOREIGN KEY (`AttendanceEventID`) REFERENCES `tblattendanceevent` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_contribution_batch_bank` FOREIGN KEY (`BankAccountID`) REFERENCES `tblaccountingbankaccount` (`ID`),
  CONSTRAINT `fk_contribution_batch_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_contribution_batch_correction` FOREIGN KEY (`CorrectionBatchID`) REFERENCES `tblcontributionbatch` (`ID`),
  CONSTRAINT `fk_contribution_batch_corrects` FOREIGN KEY (`CorrectsBatchID`) REFERENCES `tblcontributionbatch` (`ID`),
  CONSTRAINT `fk_contribution_batch_entered_by` FOREIGN KEY (`EnteredByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_contribution_batch_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `fk_contribution_batch_posted_by` FOREIGN KEY (`PostedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_contribution_batch_reversal_transaction` FOREIGN KEY (`ReversalAccountingTransactionID`) REFERENCES `tblaccountingtransaction` (`ID`),
  CONSTRAINT `fk_contribution_batch_reviewed_by` FOREIGN KEY (`ReviewedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_contribution_batch_service` FOREIGN KEY (`ServiceID`) REFERENCES `tblservice` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_contribution_batch_transaction` FOREIGN KEY (`AccountingTransactionID`) REFERENCES `tblaccountingtransaction` (`ID`),
  CONSTRAINT `ck_contribution_batch_status` CHECK (`Status` in ('DRAFT','READY','POSTED','VOID')),
  CONSTRAINT `ck_contribution_batch_totals` CHECK (`CalculatedTotal` >= 0 and (`ControlTotal` is null or `ControlTotal` >= 0)),
  CONSTRAINT `ck_contribution_batch_version` CHECK (`Version` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontributioncontributor` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `ContributorType` varchar(12) NOT NULL,
  `PersonID` int(11) DEFAULT NULL,
  `FamilyID` int(11) DEFAULT NULL,
  `DisplayName` varchar(255) NOT NULL,
  `StatementName` varchar(255) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `Address2` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT NULL,
  `State` varchar(100) DEFAULT NULL,
  `PostalCode` varchar(30) DEFAULT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  `StatementEnabled` tinyint(1) NOT NULL DEFAULT 1,
  `Note` varchar(2000) DEFAULT NULL,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_contribution_contributor_person` (`ChurchID`,`PersonID`),
  UNIQUE KEY `uq_contribution_contributor_family` (`ChurchID`,`FamilyID`),
  KEY `ix_contribution_contributor_name` (`ChurchID`,`IsActive`,`DisplayName`),
  KEY `fk_contribution_contributor_person` (`PersonID`),
  KEY `fk_contribution_contributor_family` (`FamilyID`),
  CONSTRAINT `fk_contribution_contributor_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_contribution_contributor_family` FOREIGN KEY (`FamilyID`) REFERENCES `tblfamily` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_contribution_contributor_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `ck_contribution_contributor_type` CHECK (`ContributorType` in ('PERSON','FAMILY','EXTERNAL'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontributionenvelopeassignment` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `ContributorID` bigint(20) NOT NULL,
  `EnvelopeNumber` varchar(30) NOT NULL,
  `EffectiveFrom` date NOT NULL,
  `EffectiveThrough` date DEFAULT NULL,
  `Note` varchar(1000) DEFAULT NULL,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_contribution_envelope_start` (`ChurchID`,`EnvelopeNumber`,`EffectiveFrom`),
  KEY `ix_contribution_envelope_lookup` (`ChurchID`,`EnvelopeNumber`,`EffectiveFrom`,`EffectiveThrough`),
  KEY `ix_contribution_envelope_contributor` (`ContributorID`,`EffectiveFrom`),
  CONSTRAINT `fk_contribution_envelope_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_contribution_envelope_contributor` FOREIGN KEY (`ContributorID`) REFERENCES `tblcontributioncontributor` (`ID`),
  CONSTRAINT `ck_contribution_envelope_number` CHECK (char_length(trim(`EnvelopeNumber`)) > 0),
  CONSTRAINT `ck_contribution_envelope_dates` CHECK (`EffectiveThrough` is null or `EffectiveFrom` <= `EffectiveThrough`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontributionimportevidence` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `BatchID` bigint(20) NOT NULL,
  `StoredPath` varchar(255) NOT NULL,
  `OriginalName` varchar(255) NOT NULL,
  `FileHash` char(64) NOT NULL,
  `FileSize` bigint(20) NOT NULL,
  `MappingJSON` longtext NOT NULL,
  `RowCount` int(11) NOT NULL,
  `ImportedTotal` decimal(19,2) NOT NULL,
  `ImportedByUserID` int(11) NOT NULL,
  `ImportedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_contribution_import_file` (`ChurchID`,`FileHash`),
  UNIQUE KEY `uq_contribution_import_batch` (`BatchID`),
  KEY `fk_contribution_import_user` (`ImportedByUserID`),
  CONSTRAINT `fk_contribution_import_batch` FOREIGN KEY (`BatchID`) REFERENCES `tblcontributionbatch` (`ID`),
  CONSTRAINT `fk_contribution_import_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_contribution_import_user` FOREIGN KEY (`ImportedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `ck_contribution_import_rows` CHECK (`RowCount` > 0),
  CONSTRAINT `ck_contribution_import_total` CHECK (`ImportedTotal` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontributionpurpose` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `Description` varchar(1000) DEFAULT NULL,
  `ApprovalDate` date NOT NULL,
  `ApprovingAuthority` varchar(255) NOT NULL,
  `EffectiveFrom` date NOT NULL,
  `EffectiveThrough` date DEFAULT NULL,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  `OrganizationID` int(11) NOT NULL,
  `FundID` int(11) NOT NULL,
  `RevenueAccountID` int(11) NOT NULL,
  `FunctionID` int(11) DEFAULT NULL,
  `ControlAndDiscretionConfirmed` tinyint(1) NOT NULL DEFAULT 0,
  `StatementTreatment` varchar(20) NOT NULL DEFAULT 'ELIGIBLE',
  `Note` varchar(2000) DEFAULT NULL,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_contribution_purpose_name` (`ChurchID`,`Name`),
  KEY `ix_contribution_purpose_active` (`ChurchID`,`IsActive`,`EffectiveFrom`,`EffectiveThrough`),
  KEY `fk_contribution_purpose_org` (`OrganizationID`),
  KEY `fk_contribution_purpose_fund` (`FundID`),
  KEY `fk_contribution_purpose_revenue` (`RevenueAccountID`),
  KEY `fk_contribution_purpose_function` (`FunctionID`),
  CONSTRAINT `fk_contribution_purpose_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_contribution_purpose_function` FOREIGN KEY (`FunctionID`) REFERENCES `tblaccountingfunction` (`ID`),
  CONSTRAINT `fk_contribution_purpose_fund` FOREIGN KEY (`FundID`) REFERENCES `tblaccountingfund` (`ID`),
  CONSTRAINT `fk_contribution_purpose_org` FOREIGN KEY (`OrganizationID`) REFERENCES `tblaccountingorganization` (`ID`),
  CONSTRAINT `fk_contribution_purpose_revenue` FOREIGN KEY (`RevenueAccountID`) REFERENCES `tblaccountingaccount` (`ID`),
  CONSTRAINT `ck_contribution_purpose_dates` CHECK (`EffectiveFrom` <= `EffectiveThrough` or `EffectiveThrough` is null),
  CONSTRAINT `ck_contribution_purpose_statement` CHECK (`StatementTreatment` in ('ELIGIBLE','INELIGIBLE','REVIEW'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblcontributionstatementissue` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL,
  `ContributorID` bigint(20) NOT NULL,
  `PeriodStart` date NOT NULL,
  `PeriodEnd` date NOT NULL,
  `GeneratedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `GeneratedByUserID` int(11) NOT NULL,
  `TemplateVersion` varchar(50) NOT NULL,
  `DocumentHash` char(64) NOT NULL,
  `OutputFileName` varchar(255) NOT NULL,
  `RevisionOfID` bigint(20) DEFAULT NULL,
  `RevisionNumber` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  KEY `ix_contribution_statement_contributor` (`ContributorID`,`PeriodStart`,`PeriodEnd`,`RevisionNumber`),
  KEY `ix_contribution_statement_church_time` (`ChurchID`,`GeneratedAt`),
  KEY `fk_contribution_statement_user` (`GeneratedByUserID`),
  KEY `fk_contribution_statement_revision` (`RevisionOfID`),
  CONSTRAINT `fk_contribution_statement_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_contribution_statement_contributor` FOREIGN KEY (`ContributorID`) REFERENCES `tblcontributioncontributor` (`ID`),
  CONSTRAINT `fk_contribution_statement_revision` FOREIGN KEY (`RevisionOfID`) REFERENCES `tblcontributionstatementissue` (`ID`),
  CONSTRAINT `fk_contribution_statement_user` FOREIGN KEY (`GeneratedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `ck_contribution_statement_period` CHECK (`PeriodEnd` >= `PeriodStart`),
  CONSTRAINT `ck_contribution_statement_revision` CHECK (`RevisionNumber` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbldocument` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Title` varchar(255) NOT NULL,
  `Document` varchar(255) NOT NULL,
  `Date` date DEFAULT NULL,
  `DocumentType` varchar(255) DEFAULT NULL,
  `Description` longtext DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblDocuments_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_document_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbldocuments` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT NULL,
  `Description` varchar(255) NOT NULL,
  `FileName` varchar(255) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `DocumentType` varchar(255) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblDocuments_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_documents_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblfamily` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT 0,
  `FamilyName` varchar(255) NOT NULL,
  `MarriageStatus` varchar(255) DEFAULT NULL,
  `Directory` tinyint(1) DEFAULT 0,
  `Image` longblob DEFAULT NULL,
  `Magazine` tinyint(1) NOT NULL DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  `SpecialNotification` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`),
  KEY `fk_tblfamily_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_family_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblfamilyaddress` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) NOT NULL,
  `AddressLabel` varchar(255) NOT NULL DEFAULT 'Main',
  `Address` varchar(255) DEFAULT NULL,
  `Address2` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT 'Grand Marais',
  `State` varchar(255) DEFAULT 'MN',
  `Zip` varchar(255) DEFAULT '55604',
  `Unlisted` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblfamilyaddress_tblfamily1_idx` (`FamilyID`),
  CONSTRAINT `fk_familyaddress_family` FOREIGN KEY (`FamilyID`) REFERENCES `tblfamily` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblfamilycontact` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) DEFAULT NULL,
  `ContactLabel` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `Contact` varchar(255) NOT NULL,
  `Unlisted` tinyint(1) NOT NULL DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblfamilycontact_tblfamily1_idx` (`FamilyID`),
  CONSTRAINT `fk_familycontact_family` FOREIGN KEY (`FamilyID`) REFERENCES `tblfamily` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblfamilydate` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FamilyID` int(11) DEFAULT NULL,
  `DateType` varchar(255) NOT NULL,
  `Date` date NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblfamilydate_tblfamily1_idx` (`FamilyID`),
  CONSTRAINT `fk_familydate_family` FOREIGN KEY (`FamilyID`) REFERENCES `tblfamily` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblgroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Description` varchar(255) DEFAULT NULL,
  `Number` int(11) DEFAULT NULL,
  `GroupType` varchar(45) DEFAULT NULL,
  `DateStarted` date DEFAULT NULL,
  `Notes` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_tblgroup_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_group_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblgroupmember` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `GroupID` int(11) NOT NULL,
  `GroupRole` varchar(255) NOT NULL,
  `PersonID` int(11) NOT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Notes` longtext NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblgroupmember_tblgroup1_idx` (`GroupID`),
  KEY `fk_tblgroupmember_tblperson1_idx` (`PersonID`),
  CONSTRAINT `fk_groupmember_group` FOREIGN KEY (`GroupID`) REFERENCES `tblgroup` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_groupmember_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblhymn` (
  `ID` int(11) NOT NULL,
  `HymnalID` int(11) NOT NULL,
  `Hymn` varchar(255) NOT NULL,
  `Title` varchar(255) DEFAULT NULL,
  `Tune` varchar(160) DEFAULT NULL,
  `BibleText` varchar(255) DEFAULT NULL,
  `Category` varchar(255) DEFAULT NULL,
  `File` varchar(255) DEFAULT NULL,
  `Image` longblob DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  `EntrySlot` smallint(5) unsigned DEFAULT NULL,
  `PrintedReference` varchar(50) DEFAULT NULL,
  `PrintedStanzaCount` smallint(5) unsigned NOT NULL DEFAULT 0,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  `PackageOwned` tinyint(1) NOT NULL DEFAULT 0,
  `FirstLine` varchar(500) DEFAULT NULL,
  `Meter` varchar(50) DEFAULT NULL,
  `Author` varchar(255) DEFAULT NULL,
  `Translator` varchar(255) DEFAULT NULL,
  `Composer` varchar(255) DEFAULT NULL,
  `SourceNote` text DEFAULT NULL,
  `TextCopyrightStatus` varchar(20) NOT NULL DEFAULT 'UNKNOWN',
  `TuneCopyrightStatus` varchar(20) NOT NULL DEFAULT 'UNKNOWN',
  `SettingCopyrightStatus` varchar(20) NOT NULL DEFAULT 'UNKNOWN',
  `CopyrightOwner` varchar(255) DEFAULT NULL,
  `CopyrightYear` smallint(5) unsigned DEFAULT NULL,
  `LicenseSource` varchar(100) DEFAULT NULL,
  `LicenseReference` varchar(255) DEFAULT NULL,
  `CopyrightNote` text DEFAULT NULL,
  `CopyrightVerifiedDate` date DEFAULT NULL,
  `CopyrightVerifiedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_hymn_hymnal_entry_slot` (`HymnalID`,`EntrySlot`),
  KEY `fk_tblhymn_tblhymnal1_idx` (`HymnalID`),
  KEY `ix_hymn_active_reference` (`HymnalID`,`IsActive`,`PrintedReference`),
  CONSTRAINT `fk_hymn_hymnal` FOREIGN KEY (`HymnalID`) REFERENCES `tblhymnal` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblhymnal` (
  `ID` int(11) NOT NULL,
  `Hymnal` varchar(255) NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Publisher` varchar(255) NOT NULL,
  `Note` longtext DEFAULT NULL,
  `PackageCode` varchar(100) DEFAULT NULL,
  `PackageVersion` varchar(50) DEFAULT NULL,
  `Edition` varchar(255) DEFAULT NULL,
  `PublicationYear` smallint(5) unsigned DEFAULT NULL,
  `ISBN` varchar(40) DEFAULT NULL,
  `HymnIDStart` int(11) DEFAULT NULL,
  `HymnIDEnd` int(11) DEFAULT NULL,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  UNIQUE KEY `ID` (`ID`),
  UNIQUE KEY `uq_hymnal_package_code` (`PackageCode`),
  UNIQUE KEY `uq_hymnal_id_range_start` (`HymnIDStart`),
  UNIQUE KEY `uq_hymnal_id_range_end` (`HymnIDEnd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblhymnalpackageimport` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `HymnalID` int(11) NOT NULL,
  `PackageCode` varchar(100) NOT NULL,
  `PackageVersion` varchar(50) NOT NULL,
  `Checksum` char(64) NOT NULL,
  `Action` varchar(20) NOT NULL,
  `EntryCount` int(11) NOT NULL,
  `WarningCount` int(11) NOT NULL DEFAULT 0,
  `ImportedAt` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID`),
  KEY `ix_hymnal_package_import` (`HymnalID`,`ImportedAt`),
  CONSTRAINT `fk_hymnal_package_import_hymnal` FOREIGN KEY (`HymnalID`) REFERENCES `tblhymnal` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblhymnidconversionlog` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `MigrationCode` varchar(100) NOT NULL,
  `HymnalID` int(11) NOT NULL,
  `OldHymnID` int(11) NOT NULL,
  `PermanentHymnID` int(11) NOT NULL,
  `EntrySlot` smallint(5) unsigned NOT NULL,
  `PrintedReference` varchar(50) NOT NULL,
  `ConvertedAt` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_hymn_id_conversion` (`MigrationCode`,`OldHymnID`),
  UNIQUE KEY `uq_hymn_permanent_conversion` (`MigrationCode`,`PermanentHymnID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblhymnusage` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `ServiceID` int(11) NOT NULL,
  `ServiceBulletinOrderLineID` int(11) DEFAULT NULL,
  `HymnID` int(11) NOT NULL,
  `UsedAs` varchar(255) NOT NULL,
  `Stanzas` varchar(100) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblhymnusage_tblhymn1_idx` (`HymnID`),
  KEY `fk_tblhymnusage_tblchurch1_idx` (`ChurchID`),
  KEY `fk_tblhymnusage_tblservice1_idx` (`ServiceID`),
  KEY `ix_hymn_usage_weekly_line` (`ServiceBulletinOrderLineID`),
  CONSTRAINT `fk_hymn_usage_weekly_line` FOREIGN KEY (`ServiceBulletinOrderLineID`) REFERENCES `tblservicebulletinorderline` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_hymnusage_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`),
  CONSTRAINT `fk_hymnusage_hymn` FOREIGN KEY (`HymnID`) REFERENCES `tblhymn` (`ID`),
  CONSTRAINT `fk_hymnusage_service` FOREIGN KEY (`ServiceID`) REFERENCES `tblservice` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblimages` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Category` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `ImageData` blob DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbljournal` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Event` varchar(255) NOT NULL,
  `Complete` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` datetime DEFAULT NULL,
  `EndDate` datetime DEFAULT NULL,
  `Note` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tbljournal_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_journal_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbllectionarycycle` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `LectionaryEditionID` int(11) NOT NULL,
  `CycleCode` varchar(100) NOT NULL,
  `DisplayName` varchar(100) NOT NULL,
  `Sequence` int(11) NOT NULL,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_lectionary_cycle_code` (`LectionaryEditionID`,`CycleCode`),
  UNIQUE KEY `uq_lectionary_cycle_sequence` (`LectionaryEditionID`,`Sequence`),
  CONSTRAINT `fk_lectionary_cycle_edition` FOREIGN KEY (`LectionaryEditionID`) REFERENCES `tbllectionaryedition` (`ID`),
  CONSTRAINT `chk_lectionary_cycle_sequence` CHECK (`Sequence` > 0),
  CONSTRAINT `chk_lectionary_cycle_active` CHECK (`IsActive` in (0,1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbllectionaryedition` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `LectionarySystemID` int(11) NOT NULL,
  `EditionCode` varchar(150) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `EditionYear` smallint(6) DEFAULT NULL,
  `Status` varchar(20) NOT NULL DEFAULT 'STABLE',
  `ValidFrom` date DEFAULT NULL,
  `ValidThrough` date DEFAULT NULL,
  `PackageID` int(11) DEFAULT NULL,
  `IsStarter` tinyint(1) NOT NULL DEFAULT 0,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  `SourceNote` text DEFAULT NULL,
  `ResolverVersion` varchar(20) NOT NULL DEFAULT '1',
  `CycleRule` varchar(100) NOT NULL DEFAULT 'none',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_lectionary_edition_code` (`EditionCode`),
  KEY `ix_lectionary_edition_system` (`LectionarySystemID`,`IsActive`),
  KEY `ix_lectionary_edition_package` (`PackageID`),
  CONSTRAINT `fk_lectionary_edition_package` FOREIGN KEY (`PackageID`) REFERENCES `tbllectionarypackage` (`ID`),
  CONSTRAINT `fk_lectionary_edition_system` FOREIGN KEY (`LectionarySystemID`) REFERENCES `tbllectionarysystem` (`ID`),
  CONSTRAINT `chk_lectionary_edition_status` CHECK (`Status` in ('STABLE','TRIAL','RETIRED','LOCAL')),
  CONSTRAINT `chk_lectionary_edition_dates` CHECK (`ValidThrough` is null or `ValidFrom` is null or `ValidThrough` >= `ValidFrom`),
  CONSTRAINT `chk_lectionary_edition_flags` CHECK (`IsStarter` in (0,1) and `IsActive` in (0,1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbllectionarypackage` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PackageCode` varchar(100) NOT NULL,
  `PackageVersion` varchar(50) NOT NULL,
  `Title` varchar(255) NOT NULL,
  `SourceName` varchar(255) NOT NULL,
  `SourceReference` varchar(500) NOT NULL,
  `PackageNotice` varchar(500) NOT NULL,
  `DistributionScope` varchar(20) NOT NULL DEFAULT 'LOCAL_ONLY',
  `Checksum` char(64) NOT NULL,
  `InstalledAt` datetime NOT NULL DEFAULT current_timestamp(),
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_lectionary_package_code` (`PackageCode`),
  CONSTRAINT `chk_lectionary_package_active` CHECK (`IsActive` in (0,1)),
  CONSTRAINT `chk_lectionary_package_distribution_scope` CHECK (`DistributionScope` in ('REDISTRIBUTABLE','LOCAL_ONLY'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbllectionarypackageimport` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `LectionaryPackageID` int(11) NOT NULL,
  `PackageVersion` varchar(50) NOT NULL,
  `Checksum` char(64) NOT NULL,
  `Action` varchar(20) NOT NULL,
  `SystemCount` int(11) NOT NULL,
  `EditionCount` int(11) NOT NULL,
  `CycleCount` int(11) NOT NULL,
  `ProperCount` int(11) NOT NULL,
  `AppointmentCount` int(11) NOT NULL,
  `ImportedAt` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID`),
  KEY `ix_lectionary_package_import` (`LectionaryPackageID`,`ImportedAt`),
  CONSTRAINT `fk_lectionary_package_import_package` FOREIGN KEY (`LectionaryPackageID`) REFERENCES `tbllectionarypackage` (`ID`),
  CONSTRAINT `chk_lectionary_package_import_action` CHECK (`Action` in ('INSTALL','UPGRADE'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbllectionarysystem` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `SystemCode` varchar(150) DEFAULT NULL,
  `PackageID` int(11) DEFAULT NULL,
  `Name` varchar(255) NOT NULL,
  `CycleType` varchar(20) NOT NULL DEFAULT 'None',
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `IsStarter` tinyint(1) NOT NULL DEFAULT 0,
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_lectionary_system_name` (`Name`),
  UNIQUE KEY `uq_lectionary_system_code` (`SystemCode`),
  KEY `ix_lectionary_system_package` (`PackageID`),
  CONSTRAINT `fk_lectionary_system_package` FOREIGN KEY (`PackageID`) REFERENCES `tbllectionarypackage` (`ID`),
  CONSTRAINT `chk_lectionary_system_cycle_type` CHECK (`CycleType` in ('None','ABC','Custom'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbllocalhymnidallocation` (
  `HymnID` int(11) NOT NULL,
  `EntrySlot` smallint(5) unsigned NOT NULL,
  `AllocatedAt` datetime NOT NULL DEFAULT current_timestamp(),
  `RetiredAt` datetime DEFAULT NULL,
  PRIMARY KEY (`HymnID`),
  UNIQUE KEY `uq_local_hymn_entry_slot` (`EntrySlot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblmailsettings` (
  `ID` tinyint(4) NOT NULL DEFAULT 1,
  `Enabled` tinyint(1) NOT NULL DEFAULT 0,
  `Provider` varchar(50) NOT NULL DEFAULT 'SMTP',
  `Server` varchar(255) NOT NULL DEFAULT '',
  `Port` int(11) NOT NULL DEFAULT 587,
  `Security` varchar(20) NOT NULL DEFAULT 'STARTTLS',
  `UserName` varchar(255) NOT NULL DEFAULT '',
  `SenderAddress` varchar(255) NOT NULL DEFAULT '',
  `SenderName` varchar(255) NOT NULL DEFAULT 'ChurchManager',
  `ReplyTo` varchar(255) NOT NULL DEFAULT '',
  `CredentialTarget` varchar(255) NOT NULL DEFAULT 'ChurchManager/SMTP',
  `TimeoutSeconds` int(11) NOT NULL DEFAULT 30,
  `LastTestAt` datetime DEFAULT NULL,
  `LastTestStatus` varchar(255) DEFAULT NULL,
  `UpdatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`ID`),
  CONSTRAINT `ck_mail_settings_singleton` CHECK (`ID` = 1),
  CONSTRAINT `ck_mail_settings_port` CHECK (`Port` between 1 and 65535),
  CONSTRAINT `ck_mail_settings_security` CHECK (`Security` in ('STARTTLS','SSL'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbloptions` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `OptionFor` varchar(255) NOT NULL,
  `OptionType` varchar(255) NOT NULL,
  `OptionValue` longtext NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblorderofservicepackage` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PackageCode` varchar(100) NOT NULL,
  `PackageVersion` varchar(50) NOT NULL,
  `Title` varchar(255) NOT NULL,
  `TemplatePrefix` varchar(20) NOT NULL DEFAULT '',
  `SourceName` varchar(255) NOT NULL DEFAULT '',
  `SourceReference` varchar(500) NOT NULL DEFAULT '',
  `PackageNotice` varchar(500) NOT NULL DEFAULT '',
  `HymnalPackageCode` varchar(100) DEFAULT NULL,
  `MinimumHymnalVersion` varchar(50) DEFAULT NULL,
  `SchemaVersion` int(11) NOT NULL,
  `Checksum` char(64) NOT NULL,
  `InstalledAt` datetime NOT NULL DEFAULT current_timestamp(),
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_order_service_package_code` (`PackageCode`),
  CONSTRAINT `ck_order_service_package_schema` CHECK (`SchemaVersion` > 0),
  CONSTRAINT `ck_order_service_package_checksum` CHECK (`Checksum` regexp '^[0-9a-fA-F]{64}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblorderofservicepackageimport` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `PackageID` int(11) NOT NULL,
  `PackageVersion` varchar(50) NOT NULL,
  `Checksum` char(64) NOT NULL,
  `Action` varchar(20) NOT NULL,
  `TemplateCount` int(11) NOT NULL,
  `LineCount` int(11) NOT NULL,
  `RoleCount` int(11) NOT NULL,
  `ImportedAt` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID`),
  KEY `ix_order_service_import_package` (`PackageID`,`ImportedAt`),
  CONSTRAINT `fk_order_service_import_package` FOREIGN KEY (`PackageID`) REFERENCES `tblorderofservicepackage` (`ID`),
  CONSTRAINT `ck_order_service_import_action` CHECK (`Action` in ('INSTALL','UPGRADE'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblorderofservicepackagerolerequirement` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PackageID` int(11) NOT NULL,
  `TemplateID` int(11) NOT NULL,
  `RoleKey` varchar(100) NOT NULL,
  `RequiredCount` smallint(5) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_order_service_package_role` (`TemplateID`,`RoleKey`),
  KEY `ix_order_service_package_role_owner` (`PackageID`),
  CONSTRAINT `fk_order_service_package_role_package` FOREIGN KEY (`PackageID`) REFERENCES `tblorderofservicepackage` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_order_service_package_role_template` FOREIGN KEY (`TemplateID`) REFERENCES `tblbulletinordertemplate` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `ck_order_service_package_role_count` CHECK (`RequiredCount` between 0 and 99)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblparticipant` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) DEFAULT NULL,
  `DisplayName` varchar(255) DEFAULT NULL,
  `Name` varchar(255) NOT NULL,
  `Phone` varchar(255) DEFAULT NULL,
  `eMail` varchar(255) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `ExternalParticipant` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`),
  KEY `fk_tblparticipant_tblperson1_idx` (`PersonID`),
  CONSTRAINT `fk_participant_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblparticipantavailability` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ParticipantID` int(11) NOT NULL,
  `WorshipRoleID` int(11) NOT NULL,
  `SchedulePatternID` int(11) NOT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `Note` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_participant_role_schedule` (`ParticipantID`,`WorshipRoleID`,`SchedulePatternID`),
  KEY `fk_participantavailability_role` (`WorshipRoleID`),
  KEY `fk_participantavailability_schedule` (`SchedulePatternID`),
  CONSTRAINT `fk_participantavailability_participant` FOREIGN KEY (`ParticipantID`) REFERENCES `tblparticipant` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_participantavailability_role` FOREIGN KEY (`WorshipRoleID`) REFERENCES `tblworshiprole` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_participantavailability_schedule` FOREIGN KEY (`SchedulePatternID`) REFERENCES `tblworshipschedulepattern` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblparticipantrole` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ParticipantID` int(11) NOT NULL,
  `WorshipRoleID` int(11) NOT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `Note` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_participant_worship_role` (`ParticipantID`,`WorshipRoleID`),
  KEY `fk_participantrole_role` (`WorshipRoleID`),
  CONSTRAINT `fk_participantrole_participant` FOREIGN KEY (`ParticipantID`) REFERENCES `tblparticipant` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_participantrole_role` FOREIGN KEY (`WorshipRoleID`) REFERENCES `tblworshiprole` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblpastor` (
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Date` date NOT NULL,
  `Pastor` varchar(255) NOT NULL,
  `Reported` int(1) NOT NULL DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ChurchID`),
  CONSTRAINT `fk_pastor_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblpermission` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(150) NOT NULL,
  `Description` varchar(500) DEFAULT NULL,
  `IsSensitive` tinyint(1) NOT NULL DEFAULT 0,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_permission_name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblperson` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT 0,
  `FamilyID` int(11) DEFAULT NULL,
  `FirstName` varchar(255) NOT NULL,
  `MiddleName` varchar(255) DEFAULT NULL,
  `LastName` varchar(255) NOT NULL,
  `Title` varchar(255) DEFAULT NULL,
  `Status` varchar(255) NOT NULL,
  `MaritalStatus` varchar(255) NOT NULL DEFAULT 'Single',
  `MarriedTo` varchar(255) DEFAULT NULL,
  `Baptized` tinyint(1) NOT NULL DEFAULT 0,
  `Confirmed` tinyint(1) NOT NULL DEFAULT 0,
  `Member` tinyint(1) NOT NULL DEFAULT 0,
  `AssociateMember` tinyint(1) NOT NULL DEFAULT 0,
  `Voter` tinyint(1) NOT NULL DEFAULT 0,
  `Picture` longblob DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblperson_tblchurch1_idx` (`ChurchID`),
  KEY `fk_tblperson_tblfamily1_idx` (`FamilyID`),
  CONSTRAINT `fk_person_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_person_family` FOREIGN KEY (`FamilyID`) REFERENCES `tblfamily` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblpersonaddress` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) NOT NULL,
  `AddressLabel` varchar(255) NOT NULL DEFAULT 'Home',
  `Address` varchar(255) DEFAULT NULL,
  `Address2` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT 'Grand Marais',
  `State` varchar(255) DEFAULT 'MN',
  `Zip` varchar(255) DEFAULT '55604',
  `Unlisted` tinyint(1) NOT NULL DEFAULT 0,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblpersonaddress_tblperson1_idx` (`PersonID`),
  CONSTRAINT `fk_personaddress_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblpersoncontact` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) DEFAULT NULL,
  `ContactLabel` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `Contact` varchar(255) DEFAULT NULL,
  `Unlisted` tinyint(1) DEFAULT 0,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblpersoncontact_tblperson1_idx` (`PersonID`),
  CONSTRAINT `fk_personcontact_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblpersondate` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) NOT NULL,
  `DateType` varchar(255) NOT NULL,
  `Date` date NOT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblpersondate_tblperson1_idx` (`PersonID`),
  CONSTRAINT `fk_persondate_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblprayer` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Request` varchar(255) DEFAULT NULL,
  `PrayerCategory` varchar(255) DEFAULT NULL,
  `RequestFor` varchar(255) DEFAULT NULL,
  `RequestBy` varchar(255) DEFAULT NULL,
  `ScheduleText` varchar(255) NOT NULL,
  `ScheduleRule` varchar(255) NOT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblprayer_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_prayer_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblproject` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) NOT NULL DEFAULT 0,
  `Project` varchar(255) NOT NULL,
  `Description` varchar(255) NOT NULL,
  `Complete` tinyint(1) NOT NULL DEFAULT 0,
  `CompletionDate` date DEFAULT NULL,
  `ProjectCategory` varchar(255) NOT NULL,
  `Priority` int(11) NOT NULL DEFAULT 1,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `AssignedTo` int(11) DEFAULT NULL,
  `AssignedToText` varchar(255) DEFAULT NULL,
  `Note` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblproject_tblchurch1_idx` (`ChurchID`),
  CONSTRAINT `fk_project_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblproperhymnsuggestion` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PropersID` int(11) NOT NULL,
  `HymnID` int(11) NOT NULL,
  `SuggestedAs` varchar(100) NOT NULL DEFAULT '',
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_proper_hymn_suggestion` (`PropersID`,`HymnID`,`SuggestedAs`),
  KEY `ix_proper_hymn_suggestion_hymn` (`HymnID`),
  CONSTRAINT `fk_proper_hymn_suggestion_hymn` FOREIGN KEY (`HymnID`) REFERENCES `tblhymn` (`ID`),
  CONSTRAINT `fk_proper_hymn_suggestion_propers` FOREIGN KEY (`PropersID`) REFERENCES `tblpropers` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblpropers` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `LectionarySystemID` int(11) NOT NULL,
  `LectionaryEditionID` int(11) DEFAULT NULL,
  `LectionaryCycleID` int(11) DEFAULT NULL,
  `ProperKey` varchar(200) DEFAULT NULL,
  `Cycle` varchar(20) DEFAULT NULL,
  `Sort` int(11) DEFAULT NULL,
  `Season` varchar(255) DEFAULT NULL,
  `LiturgicalDate` varchar(255) DEFAULT NULL,
  `Color` varchar(255) DEFAULT NULL,
  `AltColor` varchar(255) DEFAULT NULL,
  `CalendarRule` varchar(255) DEFAULT NULL,
  `PackageID` int(11) DEFAULT NULL,
  `IsStarter` tinyint(1) NOT NULL DEFAULT 0,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  `Theme` longtext DEFAULT NULL,
  `HymnSug` longtext DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  `SourceNote` text DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_propers_stable_key` (`ProperKey`),
  KEY `ix_propers_system_cycle_sort` (`LectionarySystemID`,`Cycle`,`Sort`),
  KEY `ix_propers_edition_cycle_sort` (`LectionaryEditionID`,`LectionaryCycleID`,`Sort`),
  KEY `ix_propers_package` (`PackageID`),
  KEY `fk_propers_lectionary_cycle` (`LectionaryCycleID`),
  CONSTRAINT `fk_propers_lectionary_cycle` FOREIGN KEY (`LectionaryCycleID`) REFERENCES `tbllectionarycycle` (`ID`),
  CONSTRAINT `fk_propers_lectionary_edition` FOREIGN KEY (`LectionaryEditionID`) REFERENCES `tbllectionaryedition` (`ID`),
  CONSTRAINT `fk_propers_lectionary_system` FOREIGN KEY (`LectionarySystemID`) REFERENCES `tbllectionarysystem` (`ID`),
  CONSTRAINT `fk_propers_package` FOREIGN KEY (`PackageID`) REFERENCES `tbllectionarypackage` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblreading` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PropersID` int(11) NOT NULL,
  `AppointmentKey` varchar(220) DEFAULT NULL,
  `Role` varchar(40) DEFAULT NULL,
  `DisplayRole` varchar(100) DEFAULT NULL,
  `Reading` varchar(255) NOT NULL,
  `Reference` varchar(255) DEFAULT NULL,
  `DisplayCitation` varchar(500) DEFAULT NULL,
  `NormalizedCitation` varchar(500) DEFAULT NULL,
  `TrackCode` varchar(100) DEFAULT NULL,
  `OptionGroupCode` varchar(100) DEFAULT NULL,
  `OptionType` varchar(30) DEFAULT NULL,
  `PairedAppointmentID` int(11) DEFAULT NULL,
  `Sequence` int(11) DEFAULT NULL,
  `IsDefault` tinyint(1) NOT NULL DEFAULT 1,
  `PackageID` int(11) DEFAULT NULL,
  `IsStarter` tinyint(1) NOT NULL DEFAULT 0,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_reading_appointment_key` (`AppointmentKey`),
  KEY `fk_tblreading_tblpropers1_idx` (`PropersID`),
  KEY `ix_reading_proper_sequence` (`PropersID`,`Sequence`),
  KEY `ix_reading_pair` (`PairedAppointmentID`),
  KEY `ix_reading_package` (`PackageID`),
  CONSTRAINT `fk_reading_package` FOREIGN KEY (`PackageID`) REFERENCES `tbllectionarypackage` (`ID`),
  CONSTRAINT `fk_reading_pair` FOREIGN KEY (`PairedAppointmentID`) REFERENCES `tblreading` (`ID`),
  CONSTRAINT `fk_reading_propers` FOREIGN KEY (`PropersID`) REFERENCES `tblpropers` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblreports` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Report` varchar(255) NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Params` longtext DEFAULT NULL,
  `Batch` longtext DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  `Available` tinyint(4) NOT NULL DEFAULT 1,
  `RequiredPermissionID` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_reports_report` (`Report`),
  KEY `ix_reports_required_permission` (`RequiredPermissionID`),
  CONSTRAINT `fk_reports_required_permission` FOREIGN KEY (`RequiredPermissionID`) REFERENCES `tblpermission` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblrole` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Description` varchar(500) DEFAULT NULL,
  `SystemRole` tinyint(1) NOT NULL DEFAULT 0,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_role_name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblrolepermission` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `RoleID` int(11) NOT NULL,
  `PermissionID` int(11) NOT NULL,
  `AssignedByUserID` int(11) DEFAULT NULL,
  `AssignedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_rolepermission_assignment` (`RoleID`,`PermissionID`),
  KEY `fk_rolepermission_permission` (`PermissionID`),
  KEY `fk_rolepermission_assigner` (`AssignedByUserID`),
  CONSTRAINT `fk_rolepermission_assigner` FOREIGN KEY (`AssignedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_rolepermission_permission` FOREIGN KEY (`PermissionID`) REFERENCES `tblpermission` (`ID`),
  CONSTRAINT `fk_rolepermission_role` FOREIGN KEY (`RoleID`) REFERENCES `tblrole` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblsecurityauditevent` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) DEFAULT NULL,
  `SessionID` char(36) DEFAULT NULL,
  `Action` varchar(100) NOT NULL,
  `EntityType` varchar(100) DEFAULT NULL,
  `EntityID` varchar(100) DEFAULT NULL,
  `FormName` varchar(150) DEFAULT NULL,
  `BeforeJSON` longtext DEFAULT NULL,
  `AfterJSON` longtext DEFAULT NULL,
  `Reason` varchar(1000) DEFAULT NULL,
  `Workstation` varchar(255) DEFAULT NULL,
  `OccurredAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`ID`),
  KEY `ix_securityaudit_user_time` (`UserID`,`OccurredAt`),
  KEY `ix_securityaudit_action_time` (`Action`,`OccurredAt`),
  CONSTRAINT `fk_securityaudit_user` FOREIGN KEY (`UserID`) REFERENCES `tbluser` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblsermon` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblservice` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT 0,
  `DateTime` datetime NOT NULL,
  `Location` varchar(255) DEFAULT 'Grand Marais',
  `PropersID` int(11) DEFAULT NULL,
  `LiturgicalColorOverride` varchar(32) DEFAULT NULL,
  `LiturgicalDate` varchar(255) DEFAULT NULL,
  `HolyCommunion` tinyint(1) DEFAULT 1,
  `BulletinOrderTemplateID` int(11) DEFAULT NULL,
  `OSNote` varchar(255) DEFAULT NULL,
  `SermonID` int(11) DEFAULT NULL,
  `Bulletin` varchar(255) DEFAULT NULL,
  `Attendance` int(11) DEFAULT NULL,
  `CommunionAttendance` int(11) DEFAULT NULL,
  `CountforAttendance` int(11) DEFAULT NULL,
  `CheckListComplete` tinyint(1) DEFAULT NULL,
  `WorshipChecklistTemplateID` int(11) DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tblservice_tblchurch1_idx` (`ChurchID`),
  KEY `fk_tblservice_tblpropers1_idx` (`PropersID`),
  KEY `fk_tblservice_tblsermon1_idx` (`SermonID`),
  KEY `ix_service_bulletin_order_template` (`BulletinOrderTemplateID`),
  KEY `fk_service_worship_checklist_template` (`WorshipChecklistTemplateID`),
  CONSTRAINT `fk_service_bulletin_order_template_choice` FOREIGN KEY (`BulletinOrderTemplateID`) REFERENCES `tblbulletinordertemplate` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_service_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_service_propers` FOREIGN KEY (`PropersID`) REFERENCES `tblpropers` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_service_sermon` FOREIGN KEY (`SermonID`) REFERENCES `tblsermon` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_service_worship_checklist_template` FOREIGN KEY (`WorshipChecklistTemplateID`) REFERENCES `tblworshipchecklisttemplate` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblservicebulletinorder` (
  `ServiceID` int(11) NOT NULL,
  `TemplateID` int(11) DEFAULT NULL,
  `TemplateName` varchar(255) DEFAULT NULL,
  `GeneratedPlainText` longtext DEFAULT NULL,
  `GeneratedAt` datetime DEFAULT NULL,
  PRIMARY KEY (`ServiceID`),
  KEY `ix_service_bulletin_order_template` (`TemplateID`),
  CONSTRAINT `fk_service_bulletin_order_service` FOREIGN KEY (`ServiceID`) REFERENCES `tblservice` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_service_bulletin_order_template` FOREIGN KEY (`TemplateID`) REFERENCES `tblbulletinordertemplate` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblservicebulletinorderline` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ServiceID` int(11) NOT NULL,
  `TemplateLineID` int(11) DEFAULT NULL,
  `Sequence` int(11) NOT NULL,
  `Included` tinyint(1) NOT NULL DEFAULT 1,
  `LineType` varchar(40) NOT NULL DEFAULT 'TEXT',
  `Label` varchar(500) NOT NULL DEFAULT '',
  `ValueSource` varchar(40) DEFAULT NULL,
  `ValueKey` varchar(100) DEFAULT NULL,
  `WeeklyValue` varchar(500) DEFAULT NULL,
  `ReferenceText` varchar(255) DEFAULT NULL,
  `StyleName` varchar(60) NOT NULL DEFAULT 'Normal',
  `LabelBold` tinyint(1) NOT NULL DEFAULT 0,
  `ValueBold` tinyint(1) NOT NULL DEFAULT 0,
  `Italic` tinyint(1) NOT NULL DEFAULT 0,
  `IndentLevel` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `TabPosition` decimal(6,2) DEFAULT NULL,
  `TabAlignment` varchar(20) NOT NULL DEFAULT 'LEFT',
  `TabLeader` varchar(20) NOT NULL DEFAULT 'NONE',
  `ConditionType` varchar(40) NOT NULL DEFAULT 'ALWAYS',
  `ConditionValue` varchar(100) DEFAULT NULL,
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_service_bulletin_line_sequence` (`ServiceID`,`Sequence`),
  KEY `ix_service_bulletin_template_line` (`TemplateLineID`),
  CONSTRAINT `fk_service_bulletin_line_service` FOREIGN KEY (`ServiceID`) REFERENCES `tblservice` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_service_bulletin_line_template_line` FOREIGN KEY (`TemplateLineID`) REFERENCES `tblbulletinorderline` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblservicechecklistitem` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ServiceID` int(11) NOT NULL,
  `TemplateItemID` int(11) DEFAULT NULL,
  `Sequence` int(11) NOT NULL,
  `Task` varchar(255) NOT NULL,
  `CompletionSource` varchar(30) NOT NULL DEFAULT 'MANUAL',
  `Required` tinyint(1) NOT NULL DEFAULT 1,
  `Status` varchar(20) NOT NULL DEFAULT 'NOT_DONE',
  `Note` text DEFAULT NULL,
  `CompletedAt` datetime DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_service_checklist_item` (`ServiceID`,`Sequence`),
  KEY `fk_service_checklist_template_item` (`TemplateItemID`),
  CONSTRAINT `fk_service_checklist_service` FOREIGN KEY (`ServiceID`) REFERENCES `tblservice` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_service_checklist_template_item` FOREIGN KEY (`TemplateItemID`) REFERENCES `tblworshipchecklisttemplateitem` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblservicereadingsnapshot` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `ServiceID` int(11) NOT NULL,
  `SourceProperID` int(11) DEFAULT NULL,
  `SourceAppointmentID` int(11) DEFAULT NULL,
  `SourceSystemCode` varchar(150) DEFAULT NULL,
  `SourceEditionCode` varchar(150) DEFAULT NULL,
  `SourceProperKey` varchar(200) DEFAULT NULL,
  `SourceAppointmentKey` varchar(220) DEFAULT NULL,
  `SystemName` varchar(255) DEFAULT NULL,
  `EditionName` varchar(255) DEFAULT NULL,
  `CycleName` varchar(100) DEFAULT NULL,
  `ProperName` varchar(255) DEFAULT NULL,
  `Role` varchar(40) DEFAULT NULL,
  `Reading` varchar(100) NOT NULL,
  `Reference` varchar(500) NOT NULL,
  `NormalizedCitation` varchar(500) DEFAULT NULL,
  `TrackCode` varchar(100) DEFAULT NULL,
  `OptionGroupCode` varchar(100) DEFAULT NULL,
  `OptionType` varchar(30) DEFAULT NULL,
  `Sequence` int(11) NOT NULL,
  `CreatedAt` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_service_reading_snapshot_sequence` (`ServiceID`,`Sequence`),
  KEY `ix_service_reading_snapshot_proper` (`SourceProperID`),
  KEY `ix_service_reading_snapshot_appointment` (`SourceAppointmentID`),
  CONSTRAINT `fk_service_reading_snapshot_appointment` FOREIGN KEY (`SourceAppointmentID`) REFERENCES `tblreading` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_service_reading_snapshot_proper` FOREIGN KEY (`SourceProperID`) REFERENCES `tblpropers` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_service_reading_snapshot_service` FOREIGN KEY (`ServiceID`) REFERENCES `tblservice` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `chk_service_reading_snapshot_sequence` CHECK (`Sequence` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblservicerole` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ServiceID` int(11) NOT NULL,
  `ParticipantID` int(11) NOT NULL,
  `WorshipRoleID` int(11) NOT NULL,
  `Note` longtext DEFAULT NULL,
  `AssignmentStatus` varchar(30) NOT NULL DEFAULT 'ASSIGNED',
  PRIMARY KEY (`ID`),
  KEY `fk_tblservicerole_tblservice1_idx` (`ServiceID`),
  KEY `fk_tblservicerole_tblparticipant1_idx` (`ParticipantID`),
  KEY `ix_servicerole_worship_role` (`WorshipRoleID`),
  CONSTRAINT `fk_servicerole_participant` FOREIGN KEY (`ParticipantID`) REFERENCES `tblparticipant` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_servicerole_service` FOREIGN KEY (`ServiceID`) REFERENCES `tblservice` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_servicerole_worship_role` FOREIGN KEY (`WorshipRoleID`) REFERENCES `tblworshiprole` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblstates` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `StateCode` varchar(2) DEFAULT NULL,
  `State` varchar(255) DEFAULT 'MN',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbltask` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Task` varchar(255) NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `Complete` tinyint(4) NOT NULL DEFAULT 0,
  `CompletionDate` date DEFAULT NULL,
  `Priority` int(11) NOT NULL DEFAULT 1,
  `ProjectID` int(11) NOT NULL,
  `DependencyID` varchar(255) DEFAULT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Note` longtext DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tbltask_tblproject1_idx` (`ProjectID`),
  CONSTRAINT `fk_task_project` FOREIGN KEY (`ProjectID`) REFERENCES `tblproject` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbltaskworker` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TaskID` int(11) NOT NULL,
  `PersonID` int(11) DEFAULT NULL,
  `PersonText` varchar(255) DEFAULT NULL,
  `Note` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_tbltaskworker_tbltask1_idx` (`TaskID`),
  KEY `fk_tbltaskworker_tblperson1_idx` (`PersonID`),
  CONSTRAINT `fk_taskworker_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE SET NULL,
  CONSTRAINT `fk_taskworker_task` FOREIGN KEY (`TaskID`) REFERENCES `tbltask` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbluser` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PersonID` int(11) DEFAULT NULL,
  `Username` varchar(100) NOT NULL,
  `DisplayName` varchar(255) NOT NULL,
  `Email` varchar(254) DEFAULT NULL,
  `Phone` varchar(50) DEFAULT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `MasterAdministrator` tinyint(1) NOT NULL DEFAULT 0,
  `MustChangePassword` tinyint(1) NOT NULL DEFAULT 1,
  `FailedLoginCount` int(11) NOT NULL DEFAULT 0,
  `LockedUntil` datetime(6) DEFAULT NULL,
  `LastLoginAt` datetime(6) DEFAULT NULL,
  `CreatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `UpdatedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_user_username` (`Username`),
  UNIQUE KEY `uq_user_person` (`PersonID`),
  CONSTRAINT `fk_user_person` FOREIGN KEY (`PersonID`) REFERENCES `tblperson` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbluserrole` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) NOT NULL,
  `RoleID` int(11) NOT NULL,
  `EffectiveFrom` datetime(6) DEFAULT NULL,
  `EffectiveUntil` datetime(6) DEFAULT NULL,
  `AssignedByUserID` int(11) DEFAULT NULL,
  `AssignedAt` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_userrole_assignment` (`UserID`,`RoleID`),
  KEY `fk_userrole_role` (`RoleID`),
  KEY `fk_userrole_assigner` (`AssignedByUserID`),
  CONSTRAINT `fk_userrole_assigner` FOREIGN KEY (`AssignedByUserID`) REFERENCES `tbluser` (`ID`),
  CONSTRAINT `fk_userrole_role` FOREIGN KEY (`RoleID`) REFERENCES `tblrole` (`ID`),
  CONSTRAINT `fk_userrole_user` FOREIGN KEY (`UserID`) REFERENCES `tbluser` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblworshipchecklisttemplate` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ChurchID` int(11) DEFAULT NULL,
  `Name` varchar(255) NOT NULL,
  `IsStarter` tinyint(1) NOT NULL DEFAULT 0,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_worship_checklist_template` (`ChurchID`,`Name`),
  CONSTRAINT `fk_worship_checklist_template_church` FOREIGN KEY (`ChurchID`) REFERENCES `tblchurch` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblworshipchecklisttemplateitem` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TemplateID` int(11) NOT NULL,
  `Sequence` int(11) NOT NULL,
  `Task` varchar(255) NOT NULL,
  `CompletionSource` varchar(30) NOT NULL DEFAULT 'MANUAL',
  `Required` tinyint(1) NOT NULL DEFAULT 1,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_worship_checklist_template_item` (`TemplateID`,`Sequence`),
  CONSTRAINT `fk_worship_checklist_item_template` FOREIGN KEY (`TemplateID`) REFERENCES `tblworshipchecklisttemplate` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblworshiprole` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Description` varchar(500) DEFAULT NULL,
  `DisplayOrder` int(11) NOT NULL DEFAULT 100,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_worship_role_name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblworshiprolerequirement` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `BulletinOrderTemplateID` int(11) NOT NULL,
  `WorshipRoleID` int(11) NOT NULL,
  `RequiredCount` smallint(5) unsigned NOT NULL DEFAULT 1,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_worship_requirement` (`BulletinOrderTemplateID`,`WorshipRoleID`),
  KEY `fk_worshiprequirement_role` (`WorshipRoleID`),
  CONSTRAINT `fk_worshiprequirement_role` FOREIGN KEY (`WorshipRoleID`) REFERENCES `tblworshiprole` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_worshiprequirement_template` FOREIGN KEY (`BulletinOrderTemplateID`) REFERENCES `tblbulletinordertemplate` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tblworshipschedulepattern` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Description` varchar(255) NOT NULL,
  `ServiceTime` time DEFAULT NULL,
  `DaysOfWeek` varchar(255) DEFAULT NULL,
  `Months` varchar(255) DEFAULT NULL,
  `Seasons` varchar(500) DEFAULT NULL,
  `RotationIncrement` int(11) DEFAULT NULL,
  `Active` tinyint(1) NOT NULL DEFAULT 1,
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_worship_schedule_description` (`Description`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `vmperson` AS SELECT
 1 AS `ID`,
  1 AS `ChurchID`,
  1 AS `FamilyID`,
  1 AS `FirstName`,
  1 AS `MiddleName`,
  1 AS `LastName`,
  1 AS `Title`,
  1 AS `Status`,
  1 AS `MaritalStatus`,
  1 AS `MarriedTo`,
  1 AS `Baptized`,
  1 AS `Confirmed`,
  1 AS `Member`,
  1 AS `AssociateMember`,
  1 AS `Voter`,
  1 AS `Picture`,
  1 AS `Note` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `vwattendance` AS SELECT
 1 AS `ID`,
  1 AS `dt`,
  1 AS `Description`,
  1 AS `AttendanceType` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `vwlectionaryeditionlookup` AS SELECT
 1 AS `ID`,
  1 AS `DisplayName` */;
SET character_set_client = @saved_cs_client;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `vwproperslookup` AS SELECT
 1 AS `ID`,
  1 AS `DisplayName`,
  1 AS `SystemName`,
  1 AS `Cycle`,
  1 AS `Sort` */;
SET character_set_client = @saved_cs_client;
/*!50001 DROP VIEW IF EXISTS `rpt_asset`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_asset` AS select `tblasset`.`ID` AS `ID`,`tblasset`.`ChurchID` AS `ChurchID`,`tblasset`.`AssetID` AS `AssetID`,`tblasset`.`Description` AS `Description`,`tblasset`.`Reserve` AS `Reserve`,`tblasset`.`PurchaseDate` AS `PurchaseDate`,`tblasset`.`Depreciate` AS `Depreciate`,`tblasset`.`Note` AS `Note` from `tblasset` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_attendance`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_attendance` AS select `tblattendance`.`ID` AS `ID`,`tblattendance`.`PersonID` AS `PersonID`,`tblattendance`.`AttendanceEventID` AS `AttendanceEventID`,`tblattendance`.`Communion` AS `Communion` from `tblattendance` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_attendance_event`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_attendance_event` AS select `ae`.`ID` AS `ID`,`ae`.`ChurchID` AS `ChurchID`,`ae`.`ServiceID` AS `ServiceID`,`ae`.`DateTime` AS `DateTime`,`ae`.`Description` AS `Description`,`ae`.`AttendanceType` AS `AttendanceType`,`ae`.`CommunionOffered` AS `CommunionOffered`,`ae`.`HandCount` AS `HandCount`,count(`a`.`ID`) AS `KnownAttendance`,greatest(coalesce(`ae`.`HandCount`,0) - count(`a`.`ID`),0) AS `UnnamedAttendance`,`ae`.`HandCountCommunion` AS `HandCountCommunion`,`ae`.`Note` AS `Note` from (`tblattendanceevent` `ae` left join `tblattendance` `a` on(`a`.`AttendanceEventID` = `ae`.`ID`)) group by `ae`.`ID` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_attendance_weekly`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_attendance_weekly` AS select min(`e`.`ID`) AS `ID`,`e`.`ChurchID` AS `ChurchID`,cast(`e`.`DateTime` as date) - interval dayofweek(`e`.`DateTime`) - 1 day AS `DateTime`,`e`.`AttendanceType` AS `AttendanceType`,count(0) AS `EventCount`,sum(`e`.`HandCount`) AS `Attendance`,sum(`e`.`KnownAttendance`) AS `KnownAttendance`,greatest(sum(`e`.`HandCount`) - sum(`e`.`KnownAttendance`),0) AS `UnnamedAttendance`,sum(`e`.`HandCountCommunion`) AS `Communion` from (select `ae`.`ID` AS `ID`,`ae`.`ChurchID` AS `ChurchID`,`ae`.`DateTime` AS `DateTime`,coalesce(`ae`.`AttendanceType`,'') AS `AttendanceType`,coalesce(`ae`.`HandCount`,0) AS `HandCount`,coalesce(`ae`.`HandCountCommunion`,0) AS `HandCountCommunion`,count(`a`.`ID`) AS `KnownAttendance` from (`tblattendanceevent` `ae` left join `tblattendance` `a` on(`a`.`AttendanceEventID` = `ae`.`ID`)) group by `ae`.`ID`) `e` group by `e`.`ChurchID`,cast(`e`.`DateTime` as date) - interval dayofweek(`e`.`DateTime`) - 1 day,`e`.`AttendanceType` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_church_identity`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_church_identity` AS select `tblchurch`.`ID` AS `ID`,`tblchurch`.`Church` AS `Church`,`tblchurch`.`Address` AS `Address`,`tblchurch`.`Address2` AS `Address2`,`tblchurch`.`City` AS `City`,`tblchurch`.`State` AS `State`,`tblchurch`.`Zip` AS `Zip`,`tblchurch`.`Pastor` AS `Pastor`,`tblchurch`.`Phone` AS `Phone`,`tblchurch`.`eMail` AS `eMail`,`tblchurch`.`Logo` AS `Logo` from `tblchurch` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_directory_family`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_directory_family` AS select `tblfamily`.`ID` AS `ID`,`tblfamily`.`ChurchID` AS `ChurchID`,`tblfamily`.`FamilyName` AS `FamilyName`,`tblfamily`.`MarriageStatus` AS `MarriageStatus`,`tblfamily`.`Image` AS `Image`,`tblfamily`.`Magazine` AS `Magazine`,`tblfamily`.`SpecialNotification` AS `SpecialNotification`,`tblfamily`.`Directory` AS `Directory` from `tblfamily` where `tblfamily`.`Directory` = 1 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_document`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_document` AS select `tbldocument`.`ID` AS `ID`,`tbldocument`.`ChurchID` AS `ChurchID`,`tbldocument`.`Title` AS `Title`,`tbldocument`.`Document` AS `Document`,`tbldocument`.`Date` AS `Date`,`tbldocument`.`DocumentType` AS `DocumentType`,`tbldocument`.`Description` AS `Description`,`tbldocument`.`Note` AS `Note` from `tbldocument` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_family_address`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_family_address` AS select `tblfamilyaddress`.`ID` AS `ID`,`tblfamilyaddress`.`FamilyID` AS `FamilyID`,`tblfamilyaddress`.`AddressLabel` AS `AddressLabel`,`tblfamilyaddress`.`Address` AS `Address`,`tblfamilyaddress`.`Address2` AS `Address2`,`tblfamilyaddress`.`City` AS `City`,`tblfamilyaddress`.`State` AS `State`,`tblfamilyaddress`.`Zip` AS `Zip`,`tblfamilyaddress`.`StartDate` AS `StartDate`,`tblfamilyaddress`.`EndDate` AS `EndDate`,`tblfamilyaddress`.`Unlisted` AS `Unlisted` from `tblfamilyaddress` where `tblfamilyaddress`.`Unlisted` = 0 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_family_contact`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_family_contact` AS select `tblfamilycontact`.`ID` AS `ID`,`tblfamilycontact`.`FamilyID` AS `FamilyID`,`tblfamilycontact`.`ContactLabel` AS `ContactLabel`,`tblfamilycontact`.`Type` AS `Type`,`tblfamilycontact`.`Contact` AS `Contact`,`tblfamilycontact`.`Unlisted` AS `Unlisted` from `tblfamilycontact` where `tblfamilycontact`.`Unlisted` = 0 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_favorite_hymn`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_favorite_hymn` AS select `h`.`ID` AS `HymnID`,`h`.`HymnalID` AS `HymnalID`,`y`.`Hymnal` AS `Hymnal`,coalesce(nullif(`h`.`PrintedReference`,''),`h`.`Hymn`) AS `PrintedReference`,`h`.`Title` AS `Title`,`h`.`Tune` AS `Tune`,`h`.`Category` AS `Category`,`h`.`BibleText` AS `BibleText` from (`tblhymn` `h` join `tblhymnal` `y` on(`y`.`ID` = `h`.`HymnalID`)) where `h`.`IsActive` = 1 and coalesce(`h`.`Note`,'') regexp '(^|[^[:alnum:]_])#favorite([^[:alnum:]_]|$)' */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_hymn`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_hymn` AS select `tblhymn`.`ID` AS `ID`,`tblhymn`.`HymnalID` AS `HymnalID`,`tblhymn`.`EntrySlot` AS `EntrySlot`,`tblhymn`.`PrintedReference` AS `PrintedReference`,`tblhymn`.`Hymn` AS `Hymn`,`tblhymn`.`Title` AS `Title`,`tblhymn`.`Tune` AS `Tune`,`tblhymn`.`BibleText` AS `BibleText`,`tblhymn`.`Category` AS `Category`,`tblhymn`.`PrintedStanzaCount` AS `PrintedStanzaCount`,`tblhymn`.`IsActive` AS `IsActive`,`tblhymn`.`FirstLine` AS `FirstLine`,`tblhymn`.`Meter` AS `Meter`,`tblhymn`.`Author` AS `Author`,`tblhymn`.`Translator` AS `Translator`,`tblhymn`.`Composer` AS `Composer`,`tblhymn`.`SourceNote` AS `SourceNote`,`tblhymn`.`TextCopyrightStatus` AS `TextCopyrightStatus`,`tblhymn`.`TuneCopyrightStatus` AS `TuneCopyrightStatus`,`tblhymn`.`SettingCopyrightStatus` AS `SettingCopyrightStatus`,`tblhymn`.`CopyrightOwner` AS `CopyrightOwner`,`tblhymn`.`CopyrightYear` AS `CopyrightYear`,`tblhymn`.`LicenseSource` AS `LicenseSource`,`tblhymn`.`LicenseReference` AS `LicenseReference`,`tblhymn`.`CopyrightNote` AS `CopyrightNote`,`tblhymn`.`CopyrightVerifiedDate` AS `CopyrightVerifiedDate`,`tblhymn`.`CopyrightVerifiedBy` AS `CopyrightVerifiedBy`,`tblhymn`.`Note` AS `Note` from `tblhymn` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_hymn_usage`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_hymn_usage` AS select `tblhymnusage`.`ID` AS `ID`,`tblhymnusage`.`ChurchID` AS `ChurchID`,`tblhymnusage`.`ServiceID` AS `ServiceID`,`tblhymnusage`.`HymnID` AS `HymnID`,`tblhymnusage`.`UsedAs` AS `UsedAs`,`tblhymnusage`.`Stanzas` AS `Stanzas`,`tblhymnusage`.`Note` AS `Note` from `tblhymnusage` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_individual_attendance`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_individual_attendance` AS select `a`.`ID` AS `ID`,`p`.`ChurchID` AS `ChurchID`,`p`.`ID` AS `PersonID`,`p`.`LastName` AS `LastName`,`p`.`FirstName` AS `FirstName`,`ae`.`DateTime` AS `DateTime`,`ae`.`Description` AS `Description`,`ae`.`AttendanceType` AS `AttendanceType`,`a`.`Communion` AS `Communion`,`a`.`Note` AS `Note` from ((`tblattendance` `a` join `tblperson` `p` on(`p`.`ID` = `a`.`PersonID`)) join `tblattendanceevent` `ae` on(`ae`.`ID` = `a`.`AttendanceEventID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_journal`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_journal` AS select `tbljournal`.`ID` AS `ID`,`tbljournal`.`ChurchID` AS `ChurchID`,`tbljournal`.`Event` AS `Event`,`tbljournal`.`Complete` AS `Complete`,`tbljournal`.`StartDate` AS `StartDate`,`tbljournal`.`EndDate` AS `EndDate`,`tbljournal`.`Note` AS `Note` from `tbljournal` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_member_attendance_followup`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_member_attendance_followup` AS select `p`.`ID` AS `PersonID`,`p`.`ChurchID` AS `ChurchID`,`p`.`LastName` AS `LastName`,`p`.`FirstName` AS `FirstName`,`p`.`Status` AS `Status`,`last_seen`.`LastAttended` AS `LastAttended`,count(distinct case when `last_seen`.`LastWeek` is null or `service_weeks`.`ServiceWeek` > `last_seen`.`LastWeek` then `service_weeks`.`ServiceWeek` end) AS `MissedWeeks` from ((`tblperson` `p` left join (select `a`.`PersonID` AS `PersonID`,max(`ae`.`DateTime`) AS `LastAttended`,max(cast(`ae`.`DateTime` as date) - interval dayofweek(`ae`.`DateTime`) - 1 day) AS `LastWeek` from (`tblattendance` `a` join `tblattendanceevent` `ae` on(`ae`.`ID` = `a`.`AttendanceEventID`)) where `ae`.`AttendanceType` = 'Worship Service' and `ae`.`DateTime` < curdate() + interval 1 day group by `a`.`PersonID`) `last_seen` on(`last_seen`.`PersonID` = `p`.`ID`)) left join (select distinct `tblattendanceevent`.`ChurchID` AS `ChurchID`,cast(`tblattendanceevent`.`DateTime` as date) - interval dayofweek(`tblattendanceevent`.`DateTime`) - 1 day AS `ServiceWeek` from `tblattendanceevent` where `tblattendanceevent`.`AttendanceType` = 'Worship Service' and `tblattendanceevent`.`DateTime` < curdate() + interval 1 day) `service_weeks` on(`service_weeks`.`ChurchID` = `p`.`ChurchID`)) where `p`.`Member` = 1 group by `p`.`ID`,`p`.`ChurchID`,`p`.`LastName`,`p`.`FirstName`,`p`.`Status`,`last_seen`.`LastAttended`,`last_seen`.`LastWeek` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_membership_person`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_membership_person` AS select `tblperson`.`ID` AS `ID`,`tblperson`.`ChurchID` AS `ChurchID`,`tblperson`.`FamilyID` AS `FamilyID`,`tblperson`.`FirstName` AS `FirstName`,`tblperson`.`MiddleName` AS `MiddleName`,`tblperson`.`LastName` AS `LastName`,`tblperson`.`Title` AS `Title`,`tblperson`.`Status` AS `Status`,`tblperson`.`MaritalStatus` AS `MaritalStatus`,`tblperson`.`MarriedTo` AS `MarriedTo`,`tblperson`.`Baptized` AS `Baptized`,`tblperson`.`Confirmed` AS `Confirmed`,`tblperson`.`Member` AS `Member`,`tblperson`.`AssociateMember` AS `AssociateMember`,`tblperson`.`Voter` AS `Voter`,`tblperson`.`Picture` AS `Picture`,`tblperson`.`Note` AS `Note` from `tblperson` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_participant`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_participant` AS select `tblparticipant`.`ID` AS `ID`,`tblparticipant`.`PersonID` AS `PersonID`,coalesce(nullif(`tblparticipant`.`DisplayName`,''),`tblparticipant`.`Name`) AS `Name`,`tblparticipant`.`Phone` AS `Phone`,`tblparticipant`.`eMail` AS `eMail`,`tblparticipant`.`Active` AS `Active`,`tblparticipant`.`ExternalParticipant` AS `ExternalParticipant`,`tblparticipant`.`Note` AS `Note` from `tblparticipant` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_pastor_report`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_pastor_report` AS select `tblpastor`.`ChurchID` AS `ChurchID`,`tblpastor`.`Date` AS `Date`,`tblpastor`.`Pastor` AS `Pastor`,`tblpastor`.`Reported` AS `Reported`,`tblpastor`.`Note` AS `Note` from `tblpastor` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_pastors_attendance_comparison`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_pastors_attendance_comparison` AS select `c`.`ID` AS `ChurchID`,`y`.`ReportYear` AS `ReportYear`,case when `y`.`ReportYear` < year(curdate()) then coalesce(sum(case when year(`ae`.`DateTime`) = `y`.`ReportYear` then `ae`.`HandCount` else 0 end),0) else NULL end AS `FullYearAttendance`,coalesce(sum(case when year(`ae`.`DateTime`) = `y`.`ReportYear` and date_format(`ae`.`DateTime`,'%m%d') <= date_format(curdate(),'%m%d') then `ae`.`HandCount` else 0 end),0) AS `ThroughDateAttendance`,sum(case when year(`ae`.`DateTime`) = `y`.`ReportYear` and date_format(`ae`.`DateTime`,'%m%d') <= date_format(curdate(),'%m%d') then 1 else 0 end) AS `EventsThroughDate`,coalesce(round(sum(case when year(`ae`.`DateTime`) = `y`.`ReportYear` and date_format(`ae`.`DateTime`,'%m%d') <= date_format(curdate(),'%m%d') then `ae`.`HandCount` else 0 end) / nullif(sum(case when year(`ae`.`DateTime`) = `y`.`ReportYear` and date_format(`ae`.`DateTime`,'%m%d') <= date_format(curdate(),'%m%d') then 1 else 0 end),0),1),0) AS `AverageThroughDate`,coalesce(sum(case when year(`ae`.`DateTime`) = `y`.`ReportYear` and date_format(`ae`.`DateTime`,'%m%d') <= date_format(curdate(),'%m%d') then `ae`.`HandCountCommunion` else 0 end),0) AS `CommunionThroughDate` from ((`tblchurch` `c` join (select year(curdate()) AS `ReportYear` union all select year(curdate()) - 1 AS `YEAR(CURDATE())-1` union all select year(curdate()) - 2 AS `YEAR(CURDATE())-2`) `y`) left join `tblattendanceevent` `ae` on(`ae`.`ChurchID` = `c`.`ID`)) group by `c`.`ID`,`y`.`ReportYear` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_person_address`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_person_address` AS select `tblpersonaddress`.`ID` AS `ID`,`tblpersonaddress`.`PersonID` AS `PersonID`,`tblpersonaddress`.`AddressLabel` AS `AddressLabel`,`tblpersonaddress`.`Address` AS `Address`,`tblpersonaddress`.`Address2` AS `Address2`,`tblpersonaddress`.`City` AS `City`,`tblpersonaddress`.`State` AS `State`,`tblpersonaddress`.`Zip` AS `Zip`,`tblpersonaddress`.`StartDate` AS `StartDate`,`tblpersonaddress`.`EndDate` AS `EndDate`,`tblpersonaddress`.`Unlisted` AS `Unlisted` from `tblpersonaddress` where `tblpersonaddress`.`Unlisted` = 0 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_person_contact`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_person_contact` AS select `tblpersoncontact`.`ID` AS `ID`,`tblpersoncontact`.`PersonID` AS `PersonID`,`tblpersoncontact`.`ContactLabel` AS `ContactLabel`,`tblpersoncontact`.`Type` AS `Type`,`tblpersoncontact`.`Contact` AS `Contact`,`tblpersoncontact`.`Unlisted` AS `Unlisted` from `tblpersoncontact` where `tblpersoncontact`.`Unlisted` = 0 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_person_date`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_person_date` AS select `tblpersondate`.`ID` AS `ID`,`tblpersondate`.`PersonID` AS `PersonID`,`tblpersondate`.`DateType` AS `DateType`,`tblpersondate`.`Date` AS `Date`,`tblpersondate`.`Note` AS `Note` from `tblpersondate` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_project`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_project` AS select `tblproject`.`ID` AS `ID`,`tblproject`.`ChurchID` AS `ChurchID`,`tblproject`.`Project` AS `Project`,`tblproject`.`Description` AS `Description`,`tblproject`.`Complete` AS `Complete`,`tblproject`.`CompletionDate` AS `CompletionDate`,`tblproject`.`ProjectCategory` AS `ProjectCategory`,`tblproject`.`Priority` AS `Priority`,`tblproject`.`StartDate` AS `StartDate`,`tblproject`.`EndDate` AS `EndDate`,`tblproject`.`AssignedTo` AS `AssignedTo`,`tblproject`.`AssignedToText` AS `AssignedToText`,`tblproject`.`Note` AS `Note` from `tblproject` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_propers`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_propers` AS select `tblpropers`.`ID` AS `ID`,`tblpropers`.`LectionarySystemID` AS `LectionarySystemID`,`tblpropers`.`Cycle` AS `Cycle`,`tblpropers`.`Sort` AS `Sort`,`tblpropers`.`Season` AS `Season`,`tblpropers`.`LiturgicalDate` AS `LiturgicalDate`,`tblpropers`.`Color` AS `Color`,`tblpropers`.`AltColor` AS `AltColor`,`tblpropers`.`Theme` AS `Theme`,`tblpropers`.`HymnSug` AS `HymnSug`,`tblpropers`.`Note` AS `Note` from `tblpropers` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_reading`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_reading` AS select `tblreading`.`ID` AS `ID`,`tblreading`.`PropersID` AS `PropersID`,`tblreading`.`Reading` AS `Reading`,`tblreading`.`Reference` AS `Reference`,`tblreading`.`Note` AS `Note` from `tblreading` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_report_catalog`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_report_catalog` AS select `tblreports`.`ID` AS `ID`,`tblreports`.`Report` AS `Report`,`tblreports`.`Title` AS `Title`,`tblreports`.`Params` AS `Params`,`tblreports`.`Batch` AS `Batch`,`tblreports`.`Note` AS `Note`,`tblreports`.`Available` AS `Available`,`tblreports`.`RequiredPermissionID` AS `RequiredPermissionID` from `tblreports` where `tblreports`.`Available` = 1 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_sermon`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_sermon` AS select `tblsermon`.`ID` AS `ID`,`tblsermon`.`Reference` AS `Reference`,`tblsermon`.`Title` AS `Title`,`tblsermon`.`Preacher` AS `Preacher`,`tblsermon`.`Author` AS `Author`,`tblsermon`.`Series` AS `Series`,`tblsermon`.`Date` AS `Date`,`tblsermon`.`Sermon` AS `Sermon`,`tblsermon`.`Outline` AS `Outline`,`tblsermon`.`Note` AS `Note` from `tblsermon` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_service`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_service` AS select `s`.`ID` AS `ID`,`s`.`ChurchID` AS `ChurchID`,`s`.`DateTime` AS `DateTime`,`s`.`Location` AS `Location`,`s`.`PropersID` AS `PropersID`,`s`.`LiturgicalDate` AS `LiturgicalDate`,`s`.`HolyCommunion` AS `HolyCommunion`,coalesce(`weekly_template`.`Name`,`service_template`.`Name`,'') AS `OrderofService`,`s`.`BulletinOrderTemplateID` AS `BulletinOrderTemplateID`,`s`.`OSNote` AS `OSNote`,`s`.`SermonID` AS `SermonID`,`s`.`Bulletin` AS `Bulletin`,`s`.`Attendance` AS `Attendance`,`s`.`CommunionAttendance` AS `CommunionAttendance`,`s`.`CountforAttendance` AS `CountforAttendance`,`s`.`Note` AS `Note` from (((`tblservice` `s` left join `tblservicebulletinorder` `weekly` on(`weekly`.`ServiceID` = `s`.`ID`)) left join `tblbulletinordertemplate` `weekly_template` on(`weekly_template`.`ID` = `weekly`.`TemplateID`)) left join `tblbulletinordertemplate` `service_template` on(`service_template`.`ID` = `s`.`BulletinOrderTemplateID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_service_role`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_service_role` AS select `sr`.`ID` AS `ID`,`sr`.`ServiceID` AS `ServiceID`,`sr`.`ParticipantID` AS `ParticipantID`,`sr`.`WorshipRoleID` AS `WorshipRoleID`,`wr`.`Name` AS `Role`,`sr`.`AssignmentStatus` AS `AssignmentStatus`,`sr`.`Note` AS `Note` from (`tblservicerole` `sr` join `tblworshiprole` `wr` on(`wr`.`ID` = `sr`.`WorshipRoleID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_sunday_announcement`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_sunday_announcement` AS select `tblannouncement`.`ID` AS `ID`,`tblannouncement`.`ChurchID` AS `ChurchID`,`tblannouncement`.`AnnouncementCategory` AS `AnnouncementCategory`,`tblannouncement`.`Announcement` AS `Announcement`,`tblannouncement`.`RequestBy` AS `RequestBy`,`tblannouncement`.`ScheduleText` AS `ScheduleText`,`tblannouncement`.`ScheduleRule` AS `ScheduleRule`,`tblannouncement`.`StartDate` AS `StartDate`,`tblannouncement`.`EndDate` AS `EndDate`,`tblannouncement`.`Note` AS `Note` from `tblannouncement` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_sunday_prayer`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_sunday_prayer` AS select `tblprayer`.`ID` AS `ID`,`tblprayer`.`ChurchID` AS `ChurchID`,`tblprayer`.`PrayerCategory` AS `PrayerCategory`,`tblprayer`.`RequestFor` AS `RequestFor`,`tblprayer`.`RequestBy` AS `RequestBy`,`tblprayer`.`ScheduleText` AS `ScheduleText`,`tblprayer`.`ScheduleRule` AS `ScheduleRule`,`tblprayer`.`StartDate` AS `StartDate`,`tblprayer`.`EndDate` AS `EndDate`,`tblprayer`.`Note` AS `Note` from `tblprayer` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_task`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_task` AS select `tbltask`.`ID` AS `ID`,`tbltask`.`Task` AS `Task`,`tbltask`.`Description` AS `Description`,`tbltask`.`Complete` AS `Complete`,`tbltask`.`CompletionDate` AS `CompletionDate`,`tbltask`.`Priority` AS `Priority`,`tbltask`.`ProjectID` AS `ProjectID`,`tbltask`.`DependencyID` AS `DependencyID`,`tbltask`.`StartDate` AS `StartDate`,`tbltask`.`EndDate` AS `EndDate`,`tbltask`.`Note` AS `Note` from `tbltask` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_task_worker`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_task_worker` AS select `tbltaskworker`.`ID` AS `ID`,`tbltaskworker`.`TaskID` AS `TaskID`,`tbltaskworker`.`PersonID` AS `PersonID`,`tbltaskworker`.`PersonText` AS `PersonText`,`tbltaskworker`.`Note` AS `Note` from `tbltaskworker` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_participant`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_participant` AS select `p`.`ID` AS `ID`,`p`.`PersonID` AS `PersonID`,coalesce(nullif(`p`.`DisplayName`,''),nullif(`p`.`Name`,''),trim(concat_ws(' ',`pe`.`FirstName`,`pe`.`LastName`))) AS `DisplayName`,`p`.`Phone` AS `Phone`,`p`.`eMail` AS `eMail`,`p`.`Active` AS `Active`,`p`.`ExternalParticipant` AS `ExternalParticipant`,`p`.`Note` AS `Note` from (`tblparticipant` `p` left join `tblperson` `pe` on(`pe`.`ID` = `p`.`PersonID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_planner_checklist`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_planner_checklist` AS select `i`.`ServiceID` AS `ServiceID`,`i`.`Sequence` AS `Sequence`,`i`.`Task` AS `Task`,`i`.`Required` AS `Required`,`i`.`Status` AS `Status`,coalesce(`i`.`Note`,'') AS `Note`,`i`.`CompletionSource` AS `CompletionSource` from `tblservicechecklistitem` `i` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_planner_checklist_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_planner_checklist_summary` AS select `tblservice`.`ID` AS `ServiceID`,coalesce(`tblservice`.`CheckListComplete`,0) AS `ManuallyConfirmed` from `tblservice` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_planner_hymn`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_planner_hymn` AS select `u`.`ID` AS `ID`,`u`.`ServiceID` AS `ServiceID`,`l`.`Sequence` AS `Sequence`,`u`.`HymnID` AS `HymnID`,`u`.`UsedAs` AS `UsedAs`,coalesce(`h`.`Hymn`,'') AS `HymnNumber`,coalesce(`h`.`Title`,'') AS `Title`,`u`.`Stanzas` AS `Stanzas`,coalesce(`l`.`ReferenceText`,`h`.`Hymn`,'') AS `ReferenceText`,trim(concat_ws(' ',nullif(coalesce(`l`.`ReferenceText`,`h`.`Hymn`),''),nullif(`h`.`Title`,''))) AS `Hymn` from ((`tblhymnusage` `u` join `tblhymn` `h` on(`h`.`ID` = `u`.`HymnID`)) left join `tblservicebulletinorderline` `l` on(`l`.`ID` = `u`.`ServiceBulletinOrderLineID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_planner_order`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_planner_order` AS select `tblservicebulletinorderline`.`ID` AS `ID`,`tblservicebulletinorderline`.`ServiceID` AS `ServiceID`,`tblservicebulletinorderline`.`Sequence` AS `Sequence`,`tblservicebulletinorderline`.`LineType` AS `LineType`,`tblservicebulletinorderline`.`Label` AS `Label`,coalesce(`tblservicebulletinorderline`.`WeeklyValue`,'') AS `WeeklyValue`,coalesce(`tblservicebulletinorderline`.`ReferenceText`,'') AS `ReferenceText`,coalesce(`tblservicebulletinorderline`.`Note`,'') AS `Note` from `tblservicebulletinorderline` where `tblservicebulletinorderline`.`Included` = 1 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_planner_participant`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_planner_participant` AS select `sr`.`ID` AS `ID`,`sr`.`ServiceID` AS `ServiceID`,`sr`.`WorshipRoleID` AS `WorshipRoleID`,`wr`.`Name` AS `Role`,coalesce(nullif(`p`.`DisplayName`,''),`p`.`Name`) AS `Name`,`sr`.`AssignmentStatus` AS `Status` from ((`tblservicerole` `sr` join `tblparticipant` `p` on(`p`.`ID` = `sr`.`ParticipantID`)) join `tblworshiprole` `wr` on(`wr`.`ID` = `sr`.`WorshipRoleID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_planner_reading`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_planner_reading` AS select `tblservicereadingsnapshot`.`ID` AS `ID`,`tblservicereadingsnapshot`.`ServiceID` AS `ServiceID`,`tblservicereadingsnapshot`.`Sequence` AS `SortOrder`,`tblservicereadingsnapshot`.`Reading` AS `Reading`,`tblservicereadingsnapshot`.`Reference` AS `Reference` from `tblservicereadingsnapshot` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_planner_required_position`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_planner_required_position` AS select `s`.`ID` AS `ServiceID`,`r`.`WorshipRoleID` AS `WorshipRoleID`,`wr`.`Name` AS `Role`,`r`.`RequiredCount` AS `RequiredCount` from ((`tblservice` `s` join `tblworshiprolerequirement` `r` on(`r`.`BulletinOrderTemplateID` = `s`.`BulletinOrderTemplateID` and `r`.`Active` = 1)) join `tblworshiprole` `wr` on(`wr`.`ID` = `r`.`WorshipRoleID`)) where `wr`.`Active` = 1 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_planner_service`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_planner_service` AS select `s`.`ID` AS `ID`,`s`.`ChurchID` AS `ChurchID`,`s`.`DateTime` AS `DateTime`,coalesce(`s`.`Location`,'') AS `Location`,coalesce(`s`.`LiturgicalDate`,`p`.`LiturgicalDate`,'') AS `LiturgicalDate`,`s`.`HolyCommunion` AS `HolyCommunion`,coalesce(`ls`.`Name`,'Not selected') AS `Lectionary`,coalesce(`p`.`Season`,'') AS `Season`,coalesce(nullif(trim(`s`.`LiturgicalColorOverride`),''),`p`.`Color`,'') AS `Color`,coalesce(`p`.`Theme`,'') AS `Theme`,coalesce(`t`.`Name`,'Not selected') AS `OrderOfService`,trim(concat_ws(' - ',nullif(`se`.`Reference`,''),nullif(`se`.`Title`,''))) AS `Sermon`,coalesce(`s`.`Bulletin`,'') AS `Bulletin`,coalesce(`s`.`OSNote`,'') AS `OSNote`,coalesce(`s`.`Note`,'') AS `Note` from ((((`tblservice` `s` left join `tblpropers` `p` on(`p`.`ID` = `s`.`PropersID`)) left join `tbllectionarysystem` `ls` on(`ls`.`ID` = `p`.`LectionarySystemID`)) left join `tblbulletinordertemplate` `t` on(`t`.`ID` = `s`.`BulletinOrderTemplateID`)) left join `tblsermon` `se` on(`se`.`ID` = `s`.`SermonID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_role`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_role` AS select `tblworshiprole`.`ID` AS `ID`,`tblworshiprole`.`Name` AS `Name`,`tblworshiprole`.`Description` AS `Description`,`tblworshiprole`.`DisplayOrder` AS `DisplayOrder`,`tblworshiprole`.`Active` AS `Active` from `tblworshiprole` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `rpt_worship_service_assignment`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `rpt_worship_service_assignment` AS select `sr`.`ID` AS `ID`,`sr`.`ServiceID` AS `ServiceID`,`sr`.`ParticipantID` AS `ParticipantID`,`sr`.`WorshipRoleID` AS `WorshipRoleID`,`wr`.`Name` AS `Role`,coalesce(nullif(`p`.`DisplayName`,''),`p`.`Name`) AS `Participant`,`sr`.`AssignmentStatus` AS `AssignmentStatus`,`sr`.`Note` AS `Note` from ((`tblservicerole` `sr` join `tblparticipant` `p` on(`p`.`ID` = `sr`.`ParticipantID`)) join `tblworshiprole` `wr` on(`wr`.`ID` = `sr`.`WorshipRoleID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `vmperson`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `vmperson` AS select `tblperson`.`ID` AS `ID`,`tblperson`.`ChurchID` AS `ChurchID`,`tblperson`.`FamilyID` AS `FamilyID`,`tblperson`.`FirstName` AS `FirstName`,`tblperson`.`MiddleName` AS `MiddleName`,`tblperson`.`LastName` AS `LastName`,`tblperson`.`Title` AS `Title`,`tblperson`.`Status` AS `Status`,`tblperson`.`MaritalStatus` AS `MaritalStatus`,`tblperson`.`MarriedTo` AS `MarriedTo`,`tblperson`.`Baptized` AS `Baptized`,`tblperson`.`Confirmed` AS `Confirmed`,`tblperson`.`Member` AS `Member`,`tblperson`.`AssociateMember` AS `AssociateMember`,`tblperson`.`Voter` AS `Voter`,`tblperson`.`Picture` AS `Picture`,`tblperson`.`Note` AS `Note` from `tblperson` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `vwattendance`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `vwattendance` AS select `ae`.`ID` AS `ID`,coalesce(`ae`.`DateTime`,`s`.`DateTime`) AS `dt`,`ae`.`Description` AS `Description`,`ae`.`AttendanceType` AS `AttendanceType` from (`tblattendanceevent` `ae` left join `tblservice` `s` on(`s`.`ID` = `ae`.`ServiceID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `vwlectionaryeditionlookup`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_uca1400_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `vwlectionaryeditionlookup` AS select `e`.`ID` AS `ID`,concat(`s`.`Name`,' — ',`e`.`Name`) AS `DisplayName` from ((`tbllectionaryedition` `e` join `tbllectionarysystem` `s` on(`s`.`ID` = `e`.`LectionarySystemID`)) left join `tbllectionarypackage` `p` on(`p`.`ID` = `e`.`PackageID`)) where `e`.`IsActive` = 1 and `s`.`Active` = 1 and (`e`.`PackageID` is null or `p`.`IsActive` = 1) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!50001 DROP VIEW IF EXISTS `vwproperslookup`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `vwproperslookup` AS select `p`.`ID` AS `ID`,concat(`ls`.`Name`,case when `p`.`Cycle` is null or trim(`p`.`Cycle`) = '' then '' else concat(' - Year ',`p`.`Cycle`) end,' - ',`p`.`LiturgicalDate`) AS `DisplayName`,`ls`.`Name` AS `SystemName`,`p`.`Cycle` AS `Cycle`,`p`.`Sort` AS `Sort` from (`tblpropers` `p` join `tbllectionarysystem` `ls` on(`ls`.`ID` = `p`.`LectionarySystemID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
