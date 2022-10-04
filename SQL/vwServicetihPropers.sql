CREATE VIEW vwServicewithPropers AS SELECT
    S.ChurchID,
    S.DateTime,
    S.PropersID,
    S.LiturgicalDate,
    S.HolyCommunion,
    S.OrderofService,
    S.OSNote,
    S.PsalmorIntroit,
    S.SermonID,
    S.Bulletin,
    S.InsertDocument,
    S.Note,
    P.ID,
    P.Lectionary,
    P.Season,
    P.Color,
    P.Theme,
    P.Introit
FROM
    tblService AS S
INNER JOIN tblPropers AS P
ON
    S.PropersID = P.ID;