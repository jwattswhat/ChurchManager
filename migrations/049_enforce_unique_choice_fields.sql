DELETE duplicate_row
FROM tblChoices duplicate_row
JOIN tblChoices retained_row
  ON retained_row.Field=duplicate_row.Field
 AND retained_row.ID < duplicate_row.ID;

ALTER TABLE tblChoices
    ADD CONSTRAINT uq_choices_field UNIQUE (Field);
