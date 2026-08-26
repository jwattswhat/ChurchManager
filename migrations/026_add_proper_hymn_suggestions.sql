CREATE TABLE IF NOT EXISTS tblProperHymnSuggestion (
    ID int NOT NULL AUTO_INCREMENT,
    PropersID int NOT NULL,
    HymnID int NOT NULL,
    SuggestedAs varchar(100) NOT NULL DEFAULT '',
    Priority smallint unsigned NOT NULL DEFAULT 100,
    Note text NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_proper_hymn_suggestion (PropersID,HymnID,SuggestedAs),
    KEY ix_proper_hymn_suggestion_hymn (HymnID),
    CONSTRAINT fk_proper_hymn_suggestion_propers FOREIGN KEY (PropersID)
        REFERENCES tblPropers(ID) ON DELETE CASCADE,
    CONSTRAINT fk_proper_hymn_suggestion_hymn FOREIGN KEY (HymnID)
        REFERENCES tblHymn(ID) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;
