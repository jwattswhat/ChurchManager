DELETE old_role
FROM tblProperHymnSuggestion old_role
JOIN tblProperHymnSuggestion new_role
  ON new_role.PropersID = old_role.PropersID
 AND new_role.HymnID = old_role.HymnID
 AND new_role.SuggestedAs = CASE old_role.SuggestedAs
     WHEN 'Entrance' THEN 'Hymn of Invocation'
     WHEN 'Of the Day' THEN 'Hymn of the Day'
 END
WHERE old_role.SuggestedAs IN ('Entrance', 'Of the Day');

UPDATE tblProperHymnSuggestion
SET SuggestedAs = CASE SuggestedAs
    WHEN 'Entrance' THEN 'Hymn of Invocation'
    WHEN 'Of the Day' THEN 'Hymn of the Day'
END
WHERE SuggestedAs IN ('Entrance', 'Of the Day');
