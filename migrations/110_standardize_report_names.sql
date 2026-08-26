-- Give every active report a stable CMss99 code and a subsystem-first title.

CREATE TEMPORARY TABLE cm_report_rename (
    ReportID INT NOT NULL PRIMARY KEY,
    NewCode VARCHAR(16) NOT NULL,
    NewTitle VARCHAR(160) NOT NULL
);

INSERT INTO cm_report_rename (ReportID, NewCode, NewTitle)
SELECT ID,
    CASE Report
        WHEN 'CMAS01' THEN 'CMGN01' WHEN 'CMDO01' THEN 'CMGN02' WHEN 'CMRP01' THEN 'CMGN03'
        WHEN 'CMWP01' THEN 'CMWS01' WHEN 'CMWS01' THEN 'CMWS02'
        WHEN 'CMHU01' THEN 'CMWS03' WHEN 'CMHU02' THEN 'CMWS04' WHEN 'CMHU03' THEN 'CMWS05'
        WHEN 'CMHU04' THEN 'CMWS06' WHEN 'CMHU05' THEN 'CMWS07'
        WHEN 'CMMD01' THEN 'CMMB01' WHEN 'CMMI01' THEN 'CMMB02' WHEN 'CMMI02' THEN 'CMMB03'
        WHEN 'CMMI03' THEN 'CMMB04' WHEN 'CMML01' THEN 'CMMB05' WHEN 'CMML02' THEN 'CMMB06'
        WHEN 'CMPE01' THEN 'CMMB07' WHEN 'CMPH02' THEN 'CMMB08' WHEN 'CMML03' THEN 'CMMB09'
        WHEN 'CMML04' THEN 'CMMB10'
        WHEN 'CMJR01' THEN 'CMPC03' WHEN 'CMPA01' THEN 'CMPC04' WHEN 'CMPR01' THEN 'CMPC05'
    END,
    CASE Report
        WHEN 'CMAS01' THEN 'General - Asset Listing'
        WHEN 'CMDO01' THEN 'General - Document Listing'
        WHEN 'CMRP01' THEN 'General - Available Reports'
        WHEN 'CMWP01' THEN 'Worship - Service Planner'
        WHEN 'CMWS01' THEN 'Worship - Services by Date'
        WHEN 'CMHU01' THEN 'Worship - Hymn Usage by Service'
        WHEN 'CMHU02' THEN 'Worship - Hymn Usage by Hymn'
        WHEN 'CMHU03' THEN 'Worship - Selected Hymn Usage'
        WHEN 'CMHU04' THEN 'Worship - Recent Hymn Usage'
        WHEN 'CMHU05' THEN 'Worship - Favorite Hymns'
        WHEN 'CMMD01' THEN 'Membership - Directory'
        WHEN 'CMMI01' THEN 'Membership - Member Information'
        WHEN 'CMMI02' THEN 'Membership - Information Listing'
        WHEN 'CMMI03' THEN 'Membership - Update Forms'
        WHEN 'CMML01' THEN 'Membership - Status List'
        WHEN 'CMML02' THEN 'Membership - Date Listing'
        WHEN 'CMPE01' THEN 'Membership - Transfers'
        WHEN 'CMPH02' THEN 'Membership - Contact Listing'
        WHEN 'CMML03' THEN 'Membership - Family Mailing Labels'
        WHEN 'CMML04' THEN 'Membership - Member Mailing Labels'
        WHEN 'CMJR01' THEN 'Pastoral Care - Journal'
        WHEN 'CMPA01' THEN 'Pastoral Care - Pastor''s Report'
        WHEN 'CMPR01' THEN 'Pastoral Care - Prayer Requests'
    END
FROM tblReports
WHERE Report IN (
    'CMAS01','CMDO01','CMRP01','CMWP01','CMWS01','CMHU01','CMHU02','CMHU03','CMHU04','CMHU05',
    'CMMD01','CMMI01','CMMI02','CMMI03','CMML01','CMML02','CMPE01','CMPH02','CMML03','CMML04',
    'CMJR01','CMPA01','CMPR01'
);

-- Temporary codes prevent the former CMWP01/CMWS01 pair from colliding.
UPDATE tblReports report
JOIN cm_report_rename mapping ON mapping.ReportID=report.ID
SET report.Report=CONCAT('ZZ', report.ID);

UPDATE tblReports report
JOIN cm_report_rename mapping ON mapping.ReportID=report.ID
SET report.Report=mapping.NewCode, report.Title=mapping.NewTitle;

UPDATE tblReports SET Title='Attendance - Event Listing' WHERE Report='CMAT01';
UPDATE tblReports SET Title='Attendance - Weekly Summary' WHERE Report='CMAT02';
UPDATE tblReports SET Title='Attendance - Individual History' WHERE Report='CMAT03';
UPDATE tblReports SET Title='Attendance - Pastor''s Comparison' WHERE Report='CMAT04';
UPDATE tblReports SET Title='Attendance - Member Follow-up' WHERE Report='CMAT05';
UPDATE tblReports SET Title='Groups - Current Roster' WHERE Report='CMGR01';
UPDATE tblReports SET Title='Groups - Person Participation History' WHERE Report='CMGR02';
UPDATE tblReports SET Title='Groups - Meeting Attendance' WHERE Report='CMGR03';
UPDATE tblReports SET Title='Groups - Attendance Sheet' WHERE Report='CMGR04';
UPDATE tblReports SET Title='Pastoral Care - Work List' WHERE Report='CMPC01';
UPDATE tblReports SET Title='Pastoral Care - Activity Summary' WHERE Report='CMPC02';

DROP TEMPORARY TABLE cm_report_rename;
