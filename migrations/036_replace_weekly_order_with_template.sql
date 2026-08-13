DELETE l
FROM tblServiceBulletinOrderLine l
JOIN tblServiceBulletinOrder o ON o.ServiceID=l.ServiceID
WHERE o.TemplateID IS NULL;

DELETE FROM tblServiceBulletinOrder
WHERE TemplateID IS NULL;

ALTER TABLE tblServiceBulletinOrder
    DROP FOREIGN KEY fk_service_bulletin_order_template;

ALTER TABLE tblServiceBulletinOrder
    MODIFY COLUMN TemplateID int NOT NULL;

ALTER TABLE tblServiceBulletinOrder
    ADD CONSTRAINT fk_service_bulletin_order_template
    FOREIGN KEY (TemplateID) REFERENCES tblBulletinOrderTemplate(ID)
    ON DELETE RESTRICT;
