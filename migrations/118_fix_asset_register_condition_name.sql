-- Use a non-reserved report field name for the asset's physical condition.
CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_asset_register AS
SELECT a.ChurchID,a.ID AssetID,a.AssetNumber,a.AssetName,a.Category,a.Quantity,
       l.LocationName,TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)) ResponsiblePerson,
       g.Name ResponsibleGroup,a.`Condition` ConditionName,a.Status,
       a.NextMaintenanceDate,a.ReplacementReviewDate
FROM tblAsset a
LEFT JOIN tblAssetLocation l ON l.ID=a.LocationID
LEFT JOIN tblPerson p ON p.ID=a.ResponsiblePersonID
LEFT JOIN tblGroup g ON g.ID=a.ResponsibleGroupID;
