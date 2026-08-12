-- Controlled non-accounting reporting surface. No user-security or accounting data.

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_church_identity AS
SELECT ID,Church,Address,Address2,City,State,Zip,Pastor,Phone,eMail,Logo
FROM tblChurch;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_asset AS
SELECT ID,ChurchID,AssetID,Description,Reserve,PurchaseDate,Depreciate,Note
FROM tblAsset;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_document AS
SELECT ID,ChurchID,Title,Document,Date,DocumentType,Description,Note
FROM tblDocument;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_attendance_event AS
SELECT ID,ChurchID,ServiceID,DateTime,Description,AttendanceType,
       CommunionOffered,HandCount,HandCountCommunion,Note
FROM tblAttendanceEvent;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_attendance AS
SELECT ID,PersonID,AttendanceEventID,Communion
FROM tblAttendance;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_service AS
SELECT ID,ChurchID,DateTime,Location,PropersID,LiturgicalDate,HolyCommunion,
       OrderofService,OSNote,PsalmorIntroit,SermonID,Bulletin,Attendance,
       CommunionAttendance,CountforAttendance,Note
FROM tblService;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_membership_person AS
SELECT ID,ChurchID,FamilyID,FirstName,MiddleName,LastName,Title,Status,
       MaritalStatus,MarriedTo,Baptized,Confirmed,Member,AssociateMember,
       Voter,Picture,Note
FROM tblPerson;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_person_date AS
SELECT ID,PersonID,DateType,Date,Note
FROM tblPersonDate;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_person_contact AS
SELECT ID,PersonID,ContactLabel,Type,Contact,Unlisted
FROM tblPersonContact WHERE Unlisted=0;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_person_address AS
SELECT ID,PersonID,AddressLabel,Address,Address2,City,State,Zip,StartDate,EndDate,Unlisted
FROM tblPersonAddress WHERE Unlisted=0;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_directory_family AS
SELECT ID,ChurchID,FamilyName,MarriageStatus,Image,Magazine,SpecialNotification,Directory
FROM tblFamily WHERE Directory=1;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_family_address AS
SELECT ID,FamilyID,AddressLabel,Address,Address2,City,State,Zip,StartDate,EndDate,Unlisted
FROM tblFamilyAddress WHERE Unlisted=0;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_family_contact AS
SELECT ID,FamilyID,ContactLabel,Type,Contact,Unlisted
FROM tblFamilyContact WHERE Unlisted=0;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_hymn AS
SELECT ID,HymnalID,Hymn,Title,BibleText,Category,File,Image,Note
FROM tblHymn;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_hymn_usage AS
SELECT ID,ChurchID,ServiceID,HymnID,UsedAs,Note
FROM tblHymnUsage;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_propers AS
SELECT ID,LectionarySystemID,Cycle,Sort,Season,LiturgicalDate,Color,AltColor,
       Theme,Introit,HymnSug,Note
FROM tblPropers;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_reading AS
SELECT ID,PropersID,Reading,Reference,Note FROM tblReading;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_alt_reading AS
SELECT ID,ServiceID,Reading,Reference,Note FROM tblAltReading;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_participant AS
SELECT ID,PersonID,Name,Roles,Schedule FROM tblParticipant;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_service_role AS
SELECT ID,ServiceID,ParticipantID,Role FROM tblServiceRole;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_project AS
SELECT ID,ChurchID,Project,Description,Complete,CompletionDate,ProjectCategory,
       Priority,StartDate,EndDate,AssignedTo,AssignedToText,Note
FROM tblProject;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_task AS
SELECT ID,Task,Description,Complete,CompletionDate,Priority,ProjectID,
       DependencyID,StartDate,EndDate,Note
FROM tblTask;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_task_worker AS
SELECT ID,TaskID,PersonID,PersonText,Note FROM tblTaskWorker;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_journal AS
SELECT ID,ChurchID,Event,Complete,StartDate,EndDate,Note FROM tblJournal;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_pastor_report AS
SELECT ChurchID,Date,Pastor,Reported,Note FROM tblPastor;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_report_catalog AS
SELECT ID,Report,Title,Params,Batch,Note,Available,RequiredPermissionID
FROM tblReports WHERE Available=1;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_sermon AS
SELECT ID,Reference,Title,Preacher,Author,Series,Date,Sermon,Outline,Note
FROM tblSermon;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_enhancement AS
SELECT ID,Description,Priority,Module,Screen,DateEntered,DateDue,EnteredBy,
       Complete,CompleteDate,Note
FROM tblEnhancement;
