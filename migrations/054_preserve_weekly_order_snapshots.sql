ALTER TABLE tblServiceBulletinOrder
    DROP FOREIGN KEY IF EXISTS fk_service_bulletin_order_template;

ALTER TABLE tblServiceBulletinOrder
    MODIFY COLUMN TemplateID int NULL,
    ADD COLUMN IF NOT EXISTS TemplateName varchar(255) NULL AFTER TemplateID;

UPDATE tblServiceBulletinOrder o
JOIN tblBulletinOrderTemplate t ON t.ID=o.TemplateID
SET o.TemplateName=t.Name
WHERE o.TemplateName IS NULL;

ALTER TABLE tblServiceBulletinOrder
    ADD CONSTRAINT fk_service_bulletin_order_template
    FOREIGN KEY (TemplateID) REFERENCES tblBulletinOrderTemplate(ID)
    ON DELETE SET NULL;

ALTER TABLE tblServiceBulletinOrderLine
    ADD COLUMN IF NOT EXISTS ConditionType varchar(40) NOT NULL DEFAULT 'ALWAYS' AFTER TabLeader,
    ADD COLUMN IF NOT EXISTS ConditionValue varchar(100) NULL AFTER ConditionType;

UPDATE tblServiceBulletinOrderLine weekly
JOIN tblBulletinOrderLine template_line ON template_line.ID=weekly.TemplateLineID
SET weekly.ConditionType=template_line.ConditionType,
    weekly.ConditionValue=template_line.ConditionValue;

UPDATE tblServiceBulletinOrderLine weekly
JOIN tblService service ON service.ID=weekly.ServiceID
LEFT JOIN tblPropers proper ON proper.ID=service.PropersID
SET weekly.Included=CASE
    WHEN weekly.ConditionType='ALWAYS' THEN 1
    WHEN weekly.ConditionType='COMMUNION' THEN service.HolyCommunion
    WHEN weekly.ConditionType='NO_COMMUNION' THEN NOT service.HolyCommunion
    WHEN weekly.ConditionType='INCLUDE_SEASON' THEN LOWER(COALESCE(proper.Season,''))=LOWER(COALESCE(weekly.ConditionValue,''))
    WHEN weekly.ConditionType='EXCLUDE_SEASON' THEN LOWER(COALESCE(proper.Season,''))<>LOWER(COALESCE(weekly.ConditionValue,''))
    ELSE 0
END;
