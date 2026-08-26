-- Convert test or imported participants added after migration 041. Current
-- participant maintenance writes only the normalized relationship tables.

INSERT INTO tblWorshipRole (Name,Description,DisplayOrder,Active)
SELECT 'Usher','Assists worshipers and supports the service',130,1
WHERE EXISTS (
    SELECT 1 FROM tblParticipant
    WHERE FIND_IN_SET('Usher',REPLACE(REPLACE(REPLACE(COALESCE(Roles,''),';',','),CHAR(13),','),CHAR(10),','))>0
)
ON DUPLICATE KEY UPDATE Active=VALUES(Active);

INSERT IGNORE INTO tblParticipantRole (ParticipantID,WorshipRoleID)
SELECT p.ID,r.ID
FROM tblParticipant p
JOIN tblWorshipRole r ON FIND_IN_SET(
    r.Name,
    REPLACE(REPLACE(REPLACE(COALESCE(p.Roles,''),';',','),CHAR(13),','),CHAR(10),',')
)>0;

INSERT IGNORE INTO tblParticipantRole (ParticipantID,WorshipRoleID)
SELECT p.ID,r.ID
FROM tblParticipant p
JOIN tblWorshipRole r ON r.Name='Preacher'
WHERE FIND_IN_SET(
    'Pastor',
    REPLACE(REPLACE(REPLACE(COALESCE(p.Roles,''),';',','),CHAR(13),','),CHAR(10),',')
)>0;

-- The post-migration sample records used friendly rotation labels that were
-- never implemented as actual schedule-pattern rules. Preserve their Sunday
-- eligibility by assigning the current Sunday Divine Service pattern.
INSERT IGNORE INTO tblParticipantAvailability
    (ParticipantID,WorshipRoleID,SchedulePatternID)
SELECT pr.ParticipantID,pr.WorshipRoleID,sp.ID
FROM tblParticipantRole pr
JOIN tblParticipant p ON p.ID=pr.ParticipantID
JOIN tblWorshipSchedulePattern sp ON sp.Description='Sunday Divine Service'
WHERE TRIM(COALESCE(p.Schedule,''))<>'';
