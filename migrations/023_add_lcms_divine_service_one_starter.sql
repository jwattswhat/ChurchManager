INSERT INTO tblBulletinOrderTemplate
    (ChurchID,Name,Description,Active,IsStarter,SourceLegacyName,Version)
SELECT NULL,
       'LCMS Divine Service One',
       'Starter bulletin order for Divine Service, Setting One. Page references are to Lutheran Service Book.',
       1,1,'STARTER:LCMS-DS1',1
WHERE NOT EXISTS (
    SELECT 1 FROM tblBulletinOrderTemplate WHERE SourceLegacyName='STARTER:LCMS-DS1'
);

INSERT INTO tblBulletinOrderLine
    (TemplateID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,
     StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,
     TabLeader,ConditionType,ConditionValue,Note,NeedsReview)
SELECT t.ID,v.Sequence,v.LineType,v.Label,v.ValueSource,v.ValueKey,v.ReferenceText,
       v.StyleName,v.LabelBold,v.ValueBold,v.Italic,v.IndentLevel,v.TabPosition,
       v.TabAlignment,v.TabLeader,v.ConditionType,v.ConditionValue,v.Note,0
FROM tblBulletinOrderTemplate t
JOIN (
    SELECT 10 Sequence,'HEADING' LineType,'Divine Service, Setting One' Label,
           NULL ValueSource,NULL ValueKey,'LSB 151' ReferenceText,'Section Heading' StyleName,
           1 LabelBold,0 ValueBold,0 Italic,0 IndentLevel,4.75 TabPosition,'RIGHT' TabAlignment,
           'NONE' TabLeader,'ALWAYS' ConditionType,NULL ConditionValue,NULL Note
    UNION ALL SELECT 20,'HYMN','Hymn of Invocation','SERVICE_HYMN','Entrance',NULL,'Normal',0,1,0,0,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 30,'HEADING','Confession and Absolution',NULL,NULL,NULL,'Section Heading',1,0,0,0,NULL,'LEFT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 40,'LITURGY','Confession and Absolution',NULL,NULL,'LSB 151','Normal',0,0,0,0,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 50,'HEADING','Service of the Word',NULL,NULL,NULL,'Section Heading',1,0,0,0,NULL,'LEFT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 60,'TEXT','Introit',NULL,NULL,'Bulletin','Normal',0,0,0,0,4.75,'RIGHT','NONE','USER_CHOICE','Introit or Psalm','Use either this line or the Psalm line as appropriate.'
    UNION ALL SELECT 70,'READING','Psalm','SERVICE_READING','Psalm',NULL,'Normal',0,1,0,0,4.75,'RIGHT','NONE','USER_CHOICE','Introit or Psalm','Use either this line or the Introit line as appropriate.'
    UNION ALL SELECT 80,'LITURGY','Kyrie',NULL,NULL,'LSB 152','Normal',0,0,0,0,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 90,'LITURGY','Gloria in Excelsis',NULL,NULL,'LSB 154','Normal',0,0,0,0,4.75,'RIGHT','NONE','USER_CHOICE','Canticle of Praise','Normally omitted during Advent and Lent.'
    UNION ALL SELECT 100,'LITURGY','This Is the Feast',NULL,NULL,'LSB 155','Normal',0,0,0,0,4.75,'RIGHT','NONE','USER_CHOICE','Canticle of Praise','Alternative canticle of praise.'
    UNION ALL SELECT 110,'LITURGY','Salutation and Collect of the Day',NULL,NULL,'LSB 156','Normal',0,0,0,0,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 120,'READING','Old Testament Reading','SERVICE_READING','Old Testament',NULL,'Normal',0,1,0,1,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 130,'READING','Epistle','SERVICE_READING','Epistle',NULL,'Normal',0,1,0,1,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 140,'READING','Holy Gospel','SERVICE_READING','Gospel',NULL,'Normal',0,1,0,1,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 150,'LITURGY','Creed',NULL,NULL,NULL,'Normal',0,0,0,0,NULL,'LEFT','NONE','USER_CHOICE','Creed',NULL
    UNION ALL SELECT 160,'HYMN','Hymn of the Day','SERVICE_HYMN','Of the Day',NULL,'Normal',0,1,0,0,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 170,'SERMON','Sermon',NULL,NULL,NULL,'Normal',0,0,0,0,NULL,'LEFT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 180,'LITURGY','Offertory',NULL,NULL,'LSB 159','Normal',0,0,0,0,4.75,'RIGHT','NONE','USER_CHOICE','Offertory',NULL
    UNION ALL SELECT 190,'OFFERING','Offering',NULL,NULL,NULL,'Normal',0,0,0,0,NULL,'LEFT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 200,'LITURGY','Prayer of the Church',NULL,NULL,NULL,'Normal',0,0,0,0,NULL,'LEFT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 210,'HEADING','Service of the Sacrament',NULL,NULL,NULL,'Section Heading',1,0,0,0,NULL,'LEFT','NONE','COMMUNION',NULL,NULL
    UNION ALL SELECT 220,'LITURGY','Preface through Agnus Dei',NULL,NULL,'LSB 160-163','Normal',0,0,0,0,4.75,'RIGHT','NONE','COMMUNION',NULL,NULL
    UNION ALL SELECT 230,'COMMUNION','Distribution',NULL,NULL,NULL,'Normal',0,0,0,0,NULL,'LEFT','NONE','COMMUNION',NULL,NULL
    UNION ALL SELECT 240,'HYMN','Distribution Hymn','SERVICE_HYMN','Communion',NULL,'Normal',0,1,0,0,4.75,'RIGHT','NONE','COMMUNION',NULL,NULL
    UNION ALL SELECT 250,'LITURGY','Post-Communion Canticle',NULL,NULL,'LSB 164-165','Normal',0,0,0,0,4.75,'RIGHT','NONE','COMMUNION',NULL,'Thank the Lord or Nunc Dimittis.'
    UNION ALL SELECT 260,'LITURGY','Post-Communion Collect',NULL,NULL,'LSB 166','Normal',0,0,0,0,4.75,'RIGHT','NONE','COMMUNION',NULL,NULL
    UNION ALL SELECT 270,'LITURGY','Benediction',NULL,NULL,'LSB 166','Normal',0,0,0,0,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
    UNION ALL SELECT 280,'HYMN','Closing Hymn','SERVICE_HYMN','Closing',NULL,'Normal',0,1,0,0,4.75,'RIGHT','NONE','ALWAYS',NULL,NULL
) v
WHERE t.SourceLegacyName='STARTER:LCMS-DS1'
  AND NOT EXISTS (
      SELECT 1 FROM tblBulletinOrderLine l WHERE l.TemplateID=t.ID
  );
