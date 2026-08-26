-- Approved custom-profile values exposed through one church-scoped safe report view.

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_custom_profile_value AS
SELECT d.ChurchID,
       'Person' AS ProfileType,
       p.ID AS ProfileID,
       TRIM(CONCAT_WS(', ',p.LastName,TRIM(CONCAT_WS(' ',p.FirstName,p.MiddleName)))) AS ProfileName,
       d.FieldKey,
       d.Label AS FieldLabel,
       d.DataType AS FieldType,
       CASE d.DataType
           WHEN 'SHORT_TEXT' THEN v.TextValue
           WHEN 'LONG_TEXT' THEN v.TextValue
           WHEN 'INTEGER' THEN CAST(v.IntegerValue AS CHAR)
           WHEN 'DECIMAL' THEN CAST(v.DecimalValue AS CHAR)
           WHEN 'DATE' THEN DATE_FORMAT(v.DateValue,'%Y-%m-%d')
           WHEN 'BOOLEAN' THEN IF(v.BooleanValue=1,'Yes','No')
           WHEN 'SINGLE_CHOICE' THEN choice_value.Label
           ELSE NULL
       END AS DisplayValue,
       d.LifecycleStatus AS FieldStatus,
       d.PrivacyClass
FROM tblPersonCustomFieldValue v
JOIN tblCustomFieldDefinition d ON d.ID=v.DefinitionID AND d.EntityType='PERSON'
JOIN tblPerson p ON p.ID=v.PersonID AND p.ChurchID=d.ChurchID
LEFT JOIN tblCustomFieldOption choice_value ON choice_value.ID=v.OptionID
WHERE d.ReportAllowed=1
  AND d.LifecycleStatus IN ('ACTIVE','RETIRED')
UNION ALL
SELECT d.ChurchID,
       'Family',
       f.ID,
       f.FamilyName,
       d.FieldKey,
       d.Label,
       d.DataType,
       CASE d.DataType
           WHEN 'SHORT_TEXT' THEN v.TextValue
           WHEN 'LONG_TEXT' THEN v.TextValue
           WHEN 'INTEGER' THEN CAST(v.IntegerValue AS CHAR)
           WHEN 'DECIMAL' THEN CAST(v.DecimalValue AS CHAR)
           WHEN 'DATE' THEN DATE_FORMAT(v.DateValue,'%Y-%m-%d')
           WHEN 'BOOLEAN' THEN IF(v.BooleanValue=1,'Yes','No')
           WHEN 'SINGLE_CHOICE' THEN choice_value.Label
           ELSE NULL
       END,
       d.LifecycleStatus,
       d.PrivacyClass
FROM tblFamilyCustomFieldValue v
JOIN tblCustomFieldDefinition d ON d.ID=v.DefinitionID AND d.EntityType='FAMILY'
JOIN tblFamily f ON f.ID=v.FamilyID AND f.ChurchID=d.ChurchID
LEFT JOIN tblCustomFieldOption choice_value ON choice_value.ID=v.OptionID
WHERE d.ReportAllowed=1
  AND d.LifecycleStatus IN ('ACTIVE','RETIRED')
UNION ALL
SELECT d.ChurchID,
       'Person',
       p.ID,
       TRIM(CONCAT_WS(', ',p.LastName,TRIM(CONCAT_WS(' ',p.FirstName,p.MiddleName)))),
       d.FieldKey,
       d.Label,
       d.DataType,
       GROUP_CONCAT(o.Label ORDER BY o.DisplayOrder,o.Label SEPARATOR ', '),
       d.LifecycleStatus,
       d.PrivacyClass
FROM tblPersonCustomFieldOptionValue v
JOIN tblCustomFieldDefinition d ON d.ID=v.DefinitionID AND d.EntityType='PERSON'
JOIN tblPerson p ON p.ID=v.PersonID AND p.ChurchID=d.ChurchID
JOIN tblCustomFieldOption o ON o.ID=v.OptionID
WHERE d.ReportAllowed=1
  AND d.LifecycleStatus IN ('ACTIVE','RETIRED')
GROUP BY d.ChurchID,p.ID,p.LastName,p.FirstName,p.MiddleName,d.FieldKey,d.Label,
         d.DataType,d.LifecycleStatus,d.PrivacyClass
UNION ALL
SELECT d.ChurchID,
       'Family',
       f.ID,
       f.FamilyName,
       d.FieldKey,
       d.Label,
       d.DataType,
       GROUP_CONCAT(o.Label ORDER BY o.DisplayOrder,o.Label SEPARATOR ', '),
       d.LifecycleStatus,
       d.PrivacyClass
FROM tblFamilyCustomFieldOptionValue v
JOIN tblCustomFieldDefinition d ON d.ID=v.DefinitionID AND d.EntityType='FAMILY'
JOIN tblFamily f ON f.ID=v.FamilyID AND f.ChurchID=d.ChurchID
JOIN tblCustomFieldOption o ON o.ID=v.OptionID
WHERE d.ReportAllowed=1
  AND d.LifecycleStatus IN ('ACTIVE','RETIRED')
GROUP BY d.ChurchID,f.ID,f.FamilyName,d.FieldKey,d.Label,d.DataType,
         d.LifecycleStatus,d.PrivacyClass;

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMMB11','Membership - Custom Profile Listing','[ChurchID]',NULL,
       'Report-approved custom Person and Family values. Restricted values require separate authorization.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.membership.contact'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),
Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);
