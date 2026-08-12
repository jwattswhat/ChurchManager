SELECT h.ID AS HymnID, 
       h.Hymn, 
       h.Title, 
       h.BibleText, 
       h.Category AS Season, 
       u.UsedAs, 
       u.Note, 
       s.DateTime AS FirstUsageDate
FROM tblHymn h
JOIN tblHymnUsage u 
    ON h.ID = u.HymnID
JOIN tblService s 
    ON u.ServiceID = s.ID
WHERE h.Category = 'Lent' 
AND YEAR(s.DateTime) = YEAR(CURDATE())  -- Filter for the current year
AND u.ID = (
    SELECT MIN(u2.ID) 
    FROM tblHymnUsage u2 
    JOIN tblService s2 ON u2.ServiceID = s2.ID
    WHERE u2.HymnID = u.HymnID
    AND YEAR(s2.DateTime) = YEAR(CURDATE())  -- Ensure first usage is from this year
)
ORDER BY FirstUsageDate DESC; 