-- Stable permissions for the existing ChurchManager main menu.

INSERT IGNORE INTO tblPermission (Name, Description, IsSensitive) VALUES
('church.manage', 'Manage congregation-level church records.', 0),
('worship.manage', 'Manage worship services, sermons, propers, prayers, schedules, and service outputs.', 0),
('membership.manage', 'Manage people and family records.', 1),
('attendance.events.manage', 'Create and maintain attendance events.', 0),
('attendance.record', 'Record attendance for existing events.', 0),
('ministry.manage', 'Manage projects, tasks, documents, announcements, and journal entries.', 0),
('reports.run', 'Run ordinary ChurchManager reports.', 1),
('application.enhancements.manage', 'View and maintain enhancement and bug records.', 0);

-- Pastor/Staff receives ordinary ministry access, but not security,
-- configuration, backup, or accounting authority.
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name IN (
    'church.manage', 'worship.manage', 'membership.manage',
    'attendance.events.manage', 'attendance.record', 'ministry.manage',
    'reports.run'
)
WHERE r.Name='Pastor/Staff';

-- Volunteers begin with the narrow attendance-entry task only.
INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name='attendance.record'
WHERE r.Name='Volunteer';
