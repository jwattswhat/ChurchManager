-- source: 003_add_user_security.sql
INSERT INTO tblRole (Name, Description, SystemRole) VALUES
('Master Administrator', 'Complete ChurchManager administration and emergency authority.', 1),
('Pastor/Staff', 'Congregational and ministry work as explicitly permitted.', 1),
('Volunteer', 'Limited assigned operational work.', 1),
('Accounting Viewer', 'View permitted posted accounting records and reports.', 1),
('Accounting Entry Clerk', 'Create and edit permitted accounting drafts.', 1),
('Treasurer', 'Create, review, post, reconcile, and report.', 1),
('Accounting Approver', 'Approve accounting transactions under policy.', 1),
('Accounting Administrator', 'Maintain accounting configuration and periods.', 1),
('Auditor', 'Read-only accounting and audit access.', 1);

-- source: 003_add_user_security.sql
INSERT INTO tblPermission (Name, Description, IsSensitive) VALUES
('security.users.view', 'View ChurchManager users.', 1),
('security.users.manage', 'Create, disable, unlock, and reset ChurchManager users.', 1),
('security.roles.view', 'View roles and permission assignments.', 1),
('security.roles.manage', 'Manage roles and permission assignments.', 1),
('security.audit.view', 'View the security audit history.', 1),
('application.config.manage', 'Manage ChurchManager configuration.', 1),
('application.backup.run', 'Create a ChurchManager database backup.', 1),
('accounting.transactions.view', 'View permitted accounting transactions.', 1),
('accounting.transactions.create', 'Create accounting drafts.', 1),
('accounting.transactions.edit_own_draft', 'Edit accounting drafts created by the user.', 1),
('accounting.transactions.edit_any_draft', 'Edit any permitted accounting draft.', 1),
('accounting.transactions.delete_draft', 'Delete a permitted accounting draft with audit.', 1),
('accounting.transactions.mark_ready', 'Submit an accounting draft for review.', 1),
('accounting.transactions.approve', 'Approve an accounting transaction under policy.', 1),
('accounting.transactions.post', 'Post a validated accounting transaction.', 1),
('accounting.transactions.reverse', 'Reverse a posted accounting transaction.', 1),
('accounting.reports.run', 'Run permitted accounting reports.', 1),
('accounting.reconciliation.manage', 'Manage bank reconciliations.', 1),
('accounting.master_data.manage', 'Manage accounts, funds, functions, and related setup.', 1),
('accounting.periods.override', 'Perform controlled accounting period overrides.', 1),
('accounting.audit.view', 'View detailed accounting audit history.', 1);

-- source: 004_add_main_menu_permissions.sql
INSERT IGNORE INTO tblPermission (Name, Description, IsSensitive) VALUES
('church.manage', 'Manage congregation-level church records.', 0),
('worship.manage', 'Manage worship services, sermons, propers, prayers, schedules, and service outputs.', 0),
('membership.manage', 'Manage people and family records.', 1),
('attendance.events.manage', 'Create and maintain attendance events.', 0),
('attendance.record', 'Record attendance for existing events.', 0),
('ministry.manage', 'Manage projects, tasks, documents, announcements, and journal entries.', 0),
('reports.run', 'Run ordinary ChurchManager reports.', 1),
('application.enhancements.manage', 'View and maintain enhancement and bug records.', 0);

-- source: 004_add_main_menu_permissions.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name IN (
    'church.manage', 'worship.manage', 'membership.manage',
    'attendance.events.manage', 'attendance.record', 'ministry.manage',
    'reports.run'
)
WHERE r.Name='Pastor/Staff';

-- source: 004_add_main_menu_permissions.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name='attendance.record'
WHERE r.Name='Volunteer';

-- source: 006_add_accounting_ledger_foundation.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.reports.run')
WHERE r.Name='Accounting Viewer';

-- source: 006_add_accounting_ledger_foundation.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.transactions.create','accounting.transactions.edit_own_draft','accounting.transactions.delete_draft','accounting.transactions.mark_ready')
WHERE r.Name='Accounting Entry Clerk';

-- source: 006_add_accounting_ledger_foundation.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.transactions.create','accounting.transactions.edit_any_draft','accounting.transactions.delete_draft','accounting.transactions.mark_ready','accounting.transactions.post','accounting.transactions.reverse','accounting.reports.run','accounting.reconciliation.manage')
WHERE r.Name='Treasurer';

-- source: 006_add_accounting_ledger_foundation.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.transactions.approve')
WHERE r.Name='Accounting Approver';

-- source: 006_add_accounting_ledger_foundation.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.reports.run','accounting.reconciliation.manage','accounting.master_data.manage','accounting.periods.override','accounting.audit.view')
WHERE r.Name='Accounting Administrator';

-- source: 006_add_accounting_ledger_foundation.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.reports.run','accounting.audit.view')
WHERE r.Name='Auditor';

-- source: 009_add_audited_solo_approval.sql
INSERT IGNORE INTO tblPermission (Name, Description, Active) VALUES
('accounting.approval.override', 'Use a reason-required audited solo approval override.', 1);

-- source: 009_add_audited_solo_approval.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p
  ON p.Name='accounting.approval.override'
WHERE r.Name='Treasurer';

-- source: 013_add_accounting_budgets.sql
INSERT IGNORE INTO tblPermission (Name, Description, Active) VALUES
('accounting.budgets.manage', 'Create and edit draft accounting budgets.', 1),
('accounting.budgets.adopt', 'Propose, adopt, supersede, and amend accounting budgets.', 1);

-- source: 013_add_accounting_budgets.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p
  ON p.Name IN ('accounting.budgets.manage','accounting.budgets.adopt')
WHERE r.Name IN ('Treasurer','Accounting Administrator');

-- source: 013_add_accounting_budgets.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p
  ON p.Name='accounting.reports.run'
WHERE r.Name IN ('Accounting Viewer','Auditor');

-- source: 015_add_report_permissions.sql
INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('reports.general.run','Run low-sensitivity administration reports.',0,1),
('reports.attendance.run','Run attendance summaries and event reports.',0,1),
('reports.membership.run','Run membership lists and aggregate reports.',1,1),
('reports.membership.contact','Run reports containing member contact or address information.',1,1),
('reports.worship.run','Run worship, hymn, reading, and service reports.',0,1),
('reports.ministry.run','Run project, task, and ministry-operation reports.',0,1),
('reports.pastoral.confidential','Run confidential pastoral, prayer, visit, and personal-history reports.',1,1)
ON DUPLICATE KEY UPDATE
Description=VALUES(Description),IsSensitive=VALUES(IsSensitive),Active=1;

-- source: 015_add_report_permissions.sql
UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.general.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMAS01','CMDO01','CMEN01','CMRP01');

-- source: 015_add_report_permissions.sql
UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.attendance.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMAT01');

-- source: 015_add_report_permissions.sql
UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.membership.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMML01','CMML02','CMPE01');

-- source: 015_add_report_permissions.sql
UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.membership.contact'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMMD01','CMMI01','CMMI02','CMMI03','CMPH02');

-- source: 015_add_report_permissions.sql
UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.worship.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMHU01','CMHU02','CMHU03','CMHU04','CMSM01','CMWP01','CMWS01');

-- source: 015_add_report_permissions.sql
UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.ministry.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMPJ01','CMPJ02','CMPJ03','CMPJ04');

-- source: 015_add_report_permissions.sql
UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.pastoral.confidential'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMBATCH00','CMJR01','CMPA01','CMPR01');

-- source: 015_add_report_permissions.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator'
AND p.Name IN ('reports.general.run','reports.attendance.run','reports.membership.run',
               'reports.membership.contact','reports.worship.run','reports.ministry.run',
               'reports.pastoral.confidential');

-- source: 015_add_report_permissions.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Pastor/Staff'
AND p.Name IN ('reports.general.run','reports.attendance.run','reports.membership.run',
               'reports.membership.contact','reports.worship.run','reports.ministry.run',
               'reports.pastoral.confidential');

-- source: 015_add_report_permissions.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p ON p.Name='reports.worship.run'
WHERE r.Name='Volunteer';

-- source: 015_add_report_permissions.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p
ON p.Name IN ('reports.general.run','reports.attendance.run')
WHERE r.Name='Auditor';

-- source: 016_grant_report_screen_access.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name='reports.run'
WHERE r.Name IN ('Master Administrator','Pastor/Staff','Volunteer','Auditor');

-- source: 018_add_report_designer_permission.sql
INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('reports.design','Customize approved ChurchManager report layouts.',1,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),IsSensitive=1,Active=1;

-- source: 018_add_report_designer_permission.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name='reports.design';

-- source: 019_register_visual_report_inventory.sql
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAT02','Weekly Attendance Listing','[ChurchID\r\nAttendanceType\r\nStartDate\r\nEndDate]',NULL,
       'Standard editable visual report starter.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.attendance.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

-- source: 019_register_visual_report_inventory.sql
UPDATE tblReports SET Available=0 WHERE Report='CMSM01';

-- source: 020_add_accounting_report_designer_permission.sql
INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('accounting.reports.design','Customize approved accounting report layouts.',1,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),IsSensitive=1,Active=1;

-- source: 020_add_accounting_report_designer_permission.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name='accounting.reports.design';

-- source: 021_add_screen_designer_permission.sql
INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('screens.design','Customize approved ChurchManager screen layouts.',1,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),IsSensitive=1,Active=1;

-- source: 021_add_screen_designer_permission.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name='screens.design';

-- source: 047_normalize_sunday_content_categories.sql
INSERT INTO tblChoices (Field,Choices,Note)
SELECT 'PrayerCategory',
       COALESCE(CONCAT('[',GROUP_CONCAT(DISTINCT PrayerCategory ORDER BY PrayerCategory SEPARATOR '\n'),']'),'[General]'),
       'Categories used to group weekly prayers.'
FROM tblPrayer
WHERE PrayerCategory IS NOT NULL AND TRIM(PrayerCategory) <> ''
HAVING NOT EXISTS (SELECT 1 FROM tblChoices WHERE Field='PrayerCategory');

-- source: 047_normalize_sunday_content_categories.sql
INSERT INTO tblChoices (Field,Choices,Note)
SELECT 'AnnouncementCategory','[General]','Categories used to group weekly announcements.'
WHERE NOT EXISTS (SELECT 1 FROM tblChoices WHERE Field='AnnouncementCategory');

-- source: 048_clean_and_complete_choices.sql
DELETE FROM tblChoices
WHERE Field IN ('AccountType','OrderofService','PsalmorIntroit','Roles','EnteredBy','GroupType');

-- source: 048_clean_and_complete_choices.sql
DELETE FROM tblChoices
WHERE Field IN ('UsedAs','AnnouncementCategory','AddressLabel','Reading','Season','Category');

-- source: 048_clean_and_complete_choices.sql
INSERT INTO tblChoices (Field,Choices,Note) VALUES
('UsedAs',
 '[Hymn of Invocation\nKyrie\nGloria in Excelsis\nHymn of the Day\nCreed\nDistribution Hymn\nSanctus\nAgnus Dei\nNunc Dimittis\nMagnificat\nPost Communion\nClosing Hymn\nHymn\nOffice\nSermon]',
 'Controlled descriptions for hymn usage and worship planning.'),
('AnnouncementCategory',
 '[General\nBuilding\nCommunion\nDonations\nLCMS\nMeetings\nRadio\nWebsite]',
 'Categories used to group weekly announcements.'),
('AddressLabel',
 '[Main\nHome\nMailing\nBusiness\nOther]',
 'Labels used for person and family addresses.'),
('Reading',
 '[Old Testament\nEpistle\nGospel]',
 'Reading roles used by the lectionary and weekly order of service.');

-- source: 048_clean_and_complete_choices.sql
INSERT INTO tblChoices (Field,Choices,Note)
SELECT 'Season',
       COALESCE(CONCAT('[',GROUP_CONCAT(DISTINCT Season ORDER BY Season SEPARATOR '\n'),']'),'[Advent\nChristmas\nEpiphany\nLent\nEaster\nPentecost]'),
       'Liturgical seasons currently present in the Propers table.'
FROM tblPropers
WHERE Season IS NOT NULL AND TRIM(Season) <> '';

-- source: 048_clean_and_complete_choices.sql
INSERT INTO tblChoices (Field,Choices,Note)
SELECT 'Category',
       COALESCE(CONCAT('[',GROUP_CONCAT(DISTINCT Category ORDER BY Category SEPARATOR '\n'),']'),'[General]'),
       'Hymn categories currently present in the Hymn table.'
FROM tblHymn
WHERE Category IS NOT NULL AND TRIM(Category) <> '';

-- source: 049_enforce_unique_choice_fields.sql
DELETE duplicate_row
FROM tblChoices duplicate_row
JOIN tblChoices retained_row
  ON retained_row.Field=duplicate_row.Field
 AND retained_row.ID < duplicate_row.ID;

-- source: 050_normalize_worship_preparation_checklists.sql
INSERT INTO tblWorshipChecklistTemplate (ChurchID,Name,IsStarter,Active,Note)
VALUES (NULL,'Standard Worship Preparation',1,1,
        'A flexible reminder list. Items may be marked not needed for a particular service.');

-- source: 050_normalize_worship_preparation_checklists.sql
INSERT INTO tblWorshipChecklistTemplateItem
    (TemplateID,Sequence,Task,CompletionSource,Required,Active)
SELECT t.ID,source.ItemOrder,source.Task,source.CompletionSource,1,1
FROM tblWorshipChecklistTemplate t
JOIN (
    SELECT 1 ItemOrder,'Complete weekly Order of Service' Task,'ORDER' CompletionSource UNION ALL
    SELECT 2,'Select hymns','HYMNS' UNION ALL
    SELECT 3,'Assign participants','PARTICIPANTS' UNION ALL
    SELECT 4,'Prepare sermon','MANUAL' UNION ALL
    SELECT 5,'Review prayers','MANUAL' UNION ALL
    SELECT 6,'Prepare bulletin','MANUAL' UNION ALL
    SELECT 7,'Proofread bulletin','MANUAL' UNION ALL
    SELECT 8,'Complete bulletin','MANUAL' UNION ALL
    SELECT 9,'Print or distribute bulletin','MANUAL' UNION ALL
    SELECT 10,'Notify participants','MANUAL'
) source
WHERE t.ChurchID IS NULL AND t.Name='Standard Worship Preparation';

-- source: 051_add_database_restore_permission.sql
INSERT IGNORE INTO tblPermission (Name,Description,IsSensitive,Active)
VALUES ('application.database.restore',
        'Restore the active ChurchManager database from a verified backup.',1,1);

-- source: 051_add_database_restore_permission.sql
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name='application.database.restore';

-- source: 057_improve_attendance_reports.sql
UPDATE tblReports
SET Title='Weekly Attendance Summary'
WHERE Report='CMAT02';

-- source: 058_add_individual_attendance_report.sql
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAT03','Individual Attendance History',
       '[ChurchID\r\nPersonID\r\nStartDate\r\nEndDate]',NULL,
       'Named-person attendance and Communion history.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.attendance.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

-- source: 059_add_pastors_attendance_comparison.sql
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAT04','Pastor''s Attendance Comparison','[ChurchID]',NULL,
       'Current year-to-date compared with the same period in the prior two years, including prior full-year totals.',
       1,p.ID
FROM tblPermission p WHERE p.Name='reports.attendance.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

-- source: 060_add_member_attendance_followup.sql
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAT05','Member Attendance Follow-up','[ChurchID\r\nMissedWeeks]',NULL,
       'Current members with consecutive missed recorded worship weeks; threshold-reaching rows are red.',
       1,p.ID
FROM tblPermission p WHERE p.Name='reports.attendance.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

-- source: 061_group_attendance_report_titles.sql
UPDATE tblReports SET Title='Attendance - Event Listing' WHERE Report='CMAT01';

-- source: 061_group_attendance_report_titles.sql
UPDATE tblReports SET Title='Attendance - Weekly Summary' WHERE Report='CMAT02';

-- source: 061_group_attendance_report_titles.sql
UPDATE tblReports SET Title='Attendance - Individual History' WHERE Report='CMAT03';

-- source: 061_group_attendance_report_titles.sql
UPDATE tblReports SET Title='Attendance - Pastor''s Comparison' WHERE Report='CMAT04';

-- source: 061_group_attendance_report_titles.sql
UPDATE tblReports SET Title='Attendance - Member Follow-up' WHERE Report='CMAT05';

-- source: 062_add_support_diagnostics_permission.sql
INSERT INTO tblPermission (Name, Description, IsSensitive)
SELECT 'application.support.create',
       'Create a local privacy-safe ChurchManager support package.', 0
WHERE NOT EXISTS (
    SELECT 1 FROM tblPermission WHERE Name='application.support.create'
);

-- source: 062_add_support_diagnostics_permission.sql
INSERT INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name='application.support.create'
LEFT JOIN tblRolePermission rp ON rp.RoleID=r.ID AND rp.PermissionID=p.ID
WHERE r.Active=1 AND rp.RoleID IS NULL;

-- source: 065_retire_limereports_runtime.sql
UPDATE tblReports
SET Available=0,
    Note=CONCAT_WS(' ', NULLIF(TRIM(Note), ''),
                   'Retired when ChurchManager removed the LimeReports runtime.')
WHERE Report IN (
    'CMAD01','CMPH01','CMSM01','CMBATCH00',
    'CMFD01','CMCL01','CMDN01','CMDN02',
    'CFCA01','CFCR01','CFGR01'
);

-- source: 066_retire_enhancement_tracker.sql
DELETE FROM tblReports
WHERE Report='CMEN01';

-- source: 066_retire_enhancement_tracker.sql
DELETE rp
FROM tblRolePermission rp
JOIN tblPermission p ON p.ID=rp.PermissionID
WHERE p.Name='application.enhancements.manage';

-- source: 066_retire_enhancement_tracker.sql
DELETE FROM tblPermission
WHERE Name='application.enhancements.manage';

-- source: 071_add_secure_mail_settings.sql
INSERT IGNORE INTO tblMailSettings (ID) VALUES (1);

-- source: 075_add_favorite_hymns_report.sql
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMHU05','Favorite Hymns','[ChurchID\r\nHymnalID]',NULL,
       'Favorite hymns in the selected hymnal, identified by the #favorite note tag.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.worship.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

-- source: 085_add_confidential_member_giving.sql
INSERT IGNORE INTO tblRole (Name, Description, SystemRole, Active) VALUES
('Giving Entry Clerk', 'Enter confidential contribution batches and maintain contributor records.', 1, 1),
('Giving Administrator', 'Administer confidential giving, posting, statements, and reports.', 1, 1);

-- source: 085_add_confidential_member_giving.sql
INSERT IGNORE INTO tblPermission (Name, Description, IsSensitive, Active) VALUES
('giving.contributors.manage', 'Maintain confidential contributors and envelope assignments.', 1, 1),
('giving.batches.enter', 'Create and edit confidential draft contribution batches.', 1, 1),
('giving.batches.review', 'Review and mark contribution batches ready.', 1, 1),
('giving.batches.post', 'Post and correct contribution batches.', 1, 1),
('giving.history.view', 'View contributor-level giving history.', 1, 1),
('giving.statements.generate', 'Generate confidential contribution statements.', 1, 1),
('giving.reports.summary', 'Run giving summary reports without contributor identity.', 1, 1),
('giving.reports.confidential', 'Run donor-identifying giving reports.', 1, 1),
('giving.purposes.manage', 'Maintain approved congregational contribution purposes.', 1, 1);

-- source: 085_add_confidential_member_giving.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name IN (
    'giving.contributors.manage','giving.batches.enter','giving.batches.review',
    'giving.batches.post','giving.history.view','giving.statements.generate',
    'giving.reports.summary','giving.reports.confidential','giving.purposes.manage'
)
WHERE r.Name IN ('Master Administrator','Treasurer','Giving Administrator');

-- source: 085_add_confidential_member_giving.sql
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name IN (
    'giving.contributors.manage','giving.batches.enter','giving.batches.review',
    'giving.history.view','giving.reports.summary'
)
WHERE r.Name='Giving Entry Clerk';

-- source: 088_add_member_and_family_mailing_labels.sql
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMML03','Mailing Labels - Families','[ChurchID]',NULL,
       'Three-column family mailing labels using listed family addresses.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.membership.contact'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

-- source: 088_add_member_and_family_mailing_labels.sql
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMML04','Mailing Labels - Members','[ChurchID]',NULL,
       'Three-column individual mailing labels using listed family addresses.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.membership.contact'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

-- source: current-schema starter policy
INSERT INTO tblWorshipRole (Name,Description,DisplayOrder,Active) VALUES
('Liturgist',NULL,10,1),('Crucifer','Carries the cross',20,1),
('Preacher',NULL,30,1),('Thurifer','Carries the thurible',40,1),
('Candle-Bearer',NULL,50,1),('Acolyte','Lights candles',60,1),
('Reader',NULL,70,1),('Cantor',NULL,80,1),
('Lector','Reads the lessons',90,1),('Organist',NULL,100,1),
('Accompanist',NULL,110,1),('Elder',NULL,120,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),DisplayOrder=VALUES(DisplayOrder),Active=VALUES(Active);
