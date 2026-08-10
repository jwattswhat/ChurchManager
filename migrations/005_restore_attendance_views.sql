-- Compatibility views required by frmRecordAttendance.

CREATE OR REPLACE VIEW vwattendance AS
SELECT
    ae.ID AS ID,
    COALESCE(ae.DateTime, s.DateTime) AS dt,
    ae.Description AS Description,
    ae.AttendanceType AS AttendanceType
FROM tblAttendanceEvent ae
LEFT JOIN tblService s ON s.ID=ae.ServiceID;

CREATE OR REPLACE VIEW vmperson AS
SELECT
    ID,
    ChurchID,
    FamilyID,
    FirstName,
    MiddleName,
    LastName,
    Title,
    Status,
    MaritalStatus,
    MarriedTo,
    Baptized,
    Confirmed,
    Member,
    AssociateMember,
    Voter,
    Picture,
    Note
FROM tblPerson;
