ALTER TABLE tblServiceBulletinOrder
    DROP FOREIGN KEY fk_service_bulletin_order_template;

ALTER TABLE tblServiceBulletinOrder
    MODIFY COLUMN TemplateID int NULL;

ALTER TABLE tblServiceBulletinOrder
    ADD CONSTRAINT fk_service_bulletin_order_template
    FOREIGN KEY (TemplateID) REFERENCES tblBulletinOrderTemplate(ID)
    ON DELETE SET NULL;
