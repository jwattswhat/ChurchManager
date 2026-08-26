UPDATE tblLectionarySystem
SET Name = CASE Name
    WHEN 'Lutheran Service Book Three-Year Lectionary' THEN 'LSB Three-Year Lectionary'
    WHEN 'Lutheran Service Book One-Year Lectionary' THEN 'LSB One-Year Lectionary'
    WHEN 'Lutheran Service Book Feasts and Festivals' THEN 'LSB Feasts and Festivals'
    WHEN 'Lutheran Service Book Occasions' THEN 'LSB Occasions'
    ELSE Name
END
WHERE Name IN (
    'Lutheran Service Book Three-Year Lectionary',
    'Lutheran Service Book One-Year Lectionary',
    'Lutheran Service Book Feasts and Festivals',
    'Lutheran Service Book Occasions'
);
