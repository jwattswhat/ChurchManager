UPDATE tblServiceBulletinOrderLine weekly_line
JOIN tblHymnUsage hymn_usage ON hymn_usage.ServiceBulletinOrderLineID=weekly_line.ID
JOIN tblHymn hymn_record ON hymn_record.ID=hymn_usage.HymnID
SET weekly_line.WeeklyValue=NULLIF(TRIM(COALESCE(hymn_record.Title,'')),''),
    weekly_line.ReferenceText=NULLIF(TRIM(COALESCE(hymn_record.Hymn,'')),'')
WHERE weekly_line.ValueSource='SERVICE_HYMN';
