SELECT f.FamilyName, a.Address, a.Address2, a.City, a.State, a.zip
from ChurchDB.tblFamily f
inner JOIN ChurchDB.tblFamilyAddress a on a.FamilyID = f.ID 
where f.SpecialNotification = 1
order by FamilyName;
