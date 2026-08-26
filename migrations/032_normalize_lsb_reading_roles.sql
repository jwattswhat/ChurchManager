UPDATE tblReading r
JOIN tblPropers p ON p.ID = r.PropersID
JOIN tblLectionarySystem ls ON ls.ID = p.LectionarySystemID
SET r.Reading = CASE LOWER(TRIM(r.Reading))
    WHEN 'first' THEN 'Old Testament'
    WHEN 'first reading' THEN 'Old Testament'
    WHEN 'second' THEN 'Epistle'
    WHEN 'second reading' THEN 'Epistle'
    WHEN 'third' THEN 'Gospel'
    WHEN 'third reading' THEN 'Gospel'
END
WHERE ls.Name LIKE 'LSB %'
  AND LOWER(TRIM(r.Reading)) IN (
      'first', 'first reading',
      'second', 'second reading',
      'third', 'third reading'
  );
