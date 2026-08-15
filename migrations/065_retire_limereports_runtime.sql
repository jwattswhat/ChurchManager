-- Retire ChurchManager's external LimeReports runtime after all supported
-- catalog reports were converted to JSForm visual-report definitions.

UPDATE tblReports
SET Available=0,
    Note=CONCAT_WS(' ', NULLIF(TRIM(Note), ''),
                   'Retired when ChurchManager removed the LimeReports runtime.')
WHERE Report IN (
    'CMAD01','CMPH01','CMSM01','CMBATCH00',
    'CMFD01','CMCL01','CMDN01','CMDN02',
    'CFCA01','CFCR01','CFGR01'
);

DELETE FROM tblConfig
WHERE ConfigFamily='Location'
  AND ConfigType IN ('LimeReport','LimeReportPattern','ReportDescription');
