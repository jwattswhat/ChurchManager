# Imported reference metadata

`lsb_printed_hymn_tunes.csv` contains the hymn number, title, and tune name for
the 636 hymns printed in *Lutheran Service Book* (331-966). It was obtained from
the public Lutheran Hymndex spreadsheet:

https://lutheran-hymndex.web.app/hymnals/lsb/

ChurchManager imports tune names only when the local LSB hymn number is within
that printed range. Service Builder-only records remain blank.

`lsb_printed_hymn_review.csv` is the maintained human-review ledger for the
future curated LSB package. Its catalog identity is generated from the file
above, but a reviewer must enter each printed stanza count, mark the row
`VERIFIED`, and record the source, reviewer, and ISO date. The package builder
fails closed while any row is pending or lacks evidence. The ledger contains
metadata only; it must never contain lyrics, music, or published service text.
