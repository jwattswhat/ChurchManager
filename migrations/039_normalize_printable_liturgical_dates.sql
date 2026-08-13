-- Make Proper titles suitable for direct use as printable service titles.
-- The replacements are intentionally limited to known legacy title patterns.

UPDATE tblPropers
SET LiturgicalDate = TRIM(
    REPLACE(
    REPLACE(
    REPLACE(
    REPLACE(
    REPLACE(
    REPLACE(
    REPLACE(
    REPLACE(
    REPLACE(
    REPLACE(LiturgicalDate,
        ' S. a. the ', ' Sunday after the '),
        ' S. a the ', ' Sunday after the '),
        ' S. a. ', ' Sunday after '),
        ' Sunday a. ', ' Sunday after '),
        ' S. after ', ' Sunday after '),
        ' S. After ', ' Sunday after '),
        ' S. in ', ' Sunday in '),
        ' S. of ', ' Sunday of '),
        'Resurrecition', 'Resurrection'),
        'Tusday', 'Tuesday')
)
WHERE LiturgicalDate IS NOT NULL;

UPDATE tblPropers
SET LiturgicalDate = REPLACE(LiturgicalDate, 'Eight Sunday', 'Eighth Sunday')
WHERE LiturgicalDate LIKE '%Eight Sunday%';
