DELETE old_role
FROM tblProperHymnSuggestion old_role
JOIN tblProperHymnSuggestion new_role
  ON new_role.PropersID = old_role.PropersID
 AND new_role.HymnID = old_role.HymnID
 AND new_role.SuggestedAs = 'Distribution Hymn'
WHERE old_role.SuggestedAs = 'Communion';

UPDATE tblProperHymnSuggestion
SET SuggestedAs = 'Distribution Hymn'
WHERE SuggestedAs = 'Communion';

ALTER TABLE tblHymnUsage
    ADD COLUMN ServiceBulletinOrderLineID int NULL AFTER ServiceID,
    ADD KEY ix_hymn_usage_weekly_line (ServiceBulletinOrderLineID),
    ADD CONSTRAINT fk_hymn_usage_weekly_line
        FOREIGN KEY (ServiceBulletinOrderLineID)
        REFERENCES tblServiceBulletinOrderLine(ID) ON DELETE CASCADE;

UPDATE tblBulletinOrderLine l
JOIN tblBulletinOrderTemplate t ON t.ID = l.TemplateID
SET l.Label = 'Distribution Hymn',
    l.ValueKey = 'Distribution Hymn'
WHERE t.SourceLegacyName = 'STARTER:LCMS-DS1'
  AND l.Sequence = 240
  AND l.LineType = 'HYMN';

INSERT INTO tblBulletinOrderLine
    (TemplateID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,
     StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,
     TabLeader,ConditionType,ConditionValue,Note,NeedsReview)
SELECT t.ID,241,'HYMN','Distribution Hymn','SERVICE_HYMN','Distribution Hymn',NULL,
       'Normal',0,1,0,0,4.75,'RIGHT','NONE','COMMUNION',NULL,NULL,0
FROM tblBulletinOrderTemplate t
WHERE t.SourceLegacyName = 'STARTER:LCMS-DS1'
  AND NOT EXISTS (
      SELECT 1 FROM tblBulletinOrderLine l
      WHERE l.TemplateID=t.ID AND l.Sequence=241
  );

INSERT INTO tblBulletinOrderLine
    (TemplateID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,
     StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,
     TabLeader,ConditionType,ConditionValue,Note,NeedsReview)
SELECT t.ID,242,'HYMN','Distribution Hymn','SERVICE_HYMN','Distribution Hymn',NULL,
       'Normal',0,1,0,0,4.75,'RIGHT','NONE','COMMUNION',NULL,NULL,0
FROM tblBulletinOrderTemplate t
WHERE t.SourceLegacyName = 'STARTER:LCMS-DS1'
  AND NOT EXISTS (
      SELECT 1 FROM tblBulletinOrderLine l
      WHERE l.TemplateID=t.ID AND l.Sequence=242
  );

UPDATE tblBulletinOrderTemplate
SET Version = Version + 1
WHERE SourceLegacyName = 'STARTER:LCMS-DS1';
