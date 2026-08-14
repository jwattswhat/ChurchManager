-- LSB convention: liturgical material on pages 151-330 uses "LSB p. ...".
-- Psalms carry no page reference, while hymn numbers 331 and above remain "LSB ...".
UPDATE tblBulletinOrderLine line
JOIN tblBulletinOrderTemplate template ON template.ID=line.TemplateID
SET line.ReferenceText=CONCAT('LSB p. ',SUBSTRING(line.ReferenceText,5))
WHERE template.IsStarter=1
  AND line.ReferenceText REGEXP '^LSB (1[5-9][0-9]|2[0-9][0-9]|3[0-2][0-9]|330)(-[0-9]+)?$';

UPDATE tblBulletinOrderLine line
JOIN tblBulletinOrderTemplate template ON template.ID=line.TemplateID
SET line.ReferenceText=NULL
WHERE template.IsStarter=1
  AND line.Label='Psalm'
  AND line.LineType='READING';
