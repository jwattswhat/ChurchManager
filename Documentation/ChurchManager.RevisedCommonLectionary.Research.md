# Revised Common Lectionary Research and ChurchManager Recommendations

**Status:** Research and design recommendation; not approved for implementation  
**Prepared:** August 14, 2026  
**Scope:** Development ChurchManager only. The separate Frozen ChurchManager application is outside scope.

## Executive conclusion

ChurchManager can support the Revised Common Lectionary (RCL) alongside the existing Lutheran Service Book (LSB) lectionaries. Its normalized `tblLectionarySystem`, `tblPropers`, and `tblReading` structure already provides a useful foundation.

The RCL should not, however, be imported as a simple additional list of A/B/C propers. Proper support requires explicit handling of the RCL's complementary and semicontinuous Old Testament tracks, their paired psalms, alternate and optional readings, edition/version information, and the readings actually selected for a particular service.

The recommended approach is to preserve the existing LSB catalogs unchanged, add the stable 1992 RCL as a separate versioned lectionary system, and treat the provisional update that began trial use in Advent 2025 as an optional overlay rather than as a silent replacement.

## 1. What the Revised Common Lectionary is

The RCL is an ecumenical schedule of readings for Sundays and major festivals, published by the Consultation on Common Texts (CCT) in 1992. It developed from:

1. The Roman Catholic three-year Lectionary for Mass of 1969.
2. Protestant adaptations produced during the 1970s.
3. The experimental Common Lectionary published in 1983.
4. Two complete three-year cycles of testing and consultation before publication of the revised edition.

The RCL is a table of biblical citations, not a Bible translation or a required full-text lectionary. Its versification follows the New Revised Standard Version, although denominations and publishers may use other translations with necessary adjustments.

The standard Sunday pattern is:

1. A reading from the Old Testament, or Acts during Eastertide in the 1992 arrangement.
2. A psalm or biblical canticle responding to the first reading.
3. A New Testament reading from an epistle or Revelation.
4. A Gospel reading.

The three-year cycle is:

- **Year A:** centered on Matthew.
- **Year B:** centered on Mark, supplemented substantially by John.
- **Year C:** centered on Luke.
- **John:** read in all three years, especially around Christmas, Lent, and Easter.

The church year begins with the First Sunday in Advent. Advent 2025 through the end of the church year in November 2026 is Year A.

## 2. The two Old Testament tracks

From Advent through Trinity Sunday, the first reading is normally selected in relation to the Gospel.

For the Sundays after Trinity through the end of the church year, the RCL provides two equal alternatives:

- **Complementary track:** The Old Testament reading relates thematically, typologically, or by contrast to the Gospel.
- **Semicontinuous track:** Successive Sundays move through larger portions of the Old Testament in sequence.

Each first reading has an associated psalm or canticle. The selected psalm is therefore part of the selected track, not an independent interchangeable reading.

The CCT states that the two post-Pentecost tracks should not be mixed casually. A denomination or congregation should normally select the track that serves its needs and follow it consistently.

## 3. Other RCL selection rules

The RCL contains several kinds of choices that ChurchManager must be able to distinguish:

- A choice between the complementary and semicontinuous tracks.
- A psalm or canticle tied to the selected first reading.
- Alternate readings, including canonical alternatives where a deuterocanonical reading is offered.
- Optional extensions printed in parentheses or brackets.
- Denominational adaptations and local observances.
- Different naming and numbering conventions, such as `Proper 15` and `Ordinary 20`, for the same appointment.

The RCL permits readings to be shortened or lengthened with discretion. Consequently, the citation selected for a service may differ legitimately from the default citation stored in the catalog.

## 4. The provisional update under trial

The CCT approved a provisional RCL update for a three-year trial beginning in Advent 2025. The supporting report was updated April 21, 2026.

The update responds particularly to the history of anti-Jewish interpretation and misuse of Holy Week and Easter readings. It proposes:

- Alternate Gospel readings for Palm/Passion Sunday and Good Friday.
- Hebrew Scripture readings during Eastertide as alternatives to replacing the first reading with Acts.
- Selected Acts readings after Pentecost as alternatives to the Epistle.
- Pastoral guidance for preaching, translation, dramatic reading, and printed explanations of passages historically misused against Jewish people.

This is provisional trial material. ChurchManager should distinguish it from the stable 1992 RCL and should not overwrite the established appointments with it.

Recommended names are:

- `Revised Common Lectionary (1992)`
- `RCL Provisional Update (2025 trial)`

The second may ultimately work better as an edition overlay or option set than as a completely independent lectionary catalog.

## 5. Denominational use and variation

The RCL is used, recommended, or adapted by many Anglican, Episcopal, Lutheran, Methodist, Presbyterian, Reformed, United, Baptist, and other church bodies around the world. Individual denominations commonly publish adaptations for their calendars and practices.

Membership in the CCT does not necessarily mean that a church body has adopted the RCL without modification. ChurchManager should therefore identify the exact lectionary and edition used by a congregation rather than inferring it from denomination alone.

## 6. Relationship to the LSB Three-Year Lectionary

The Lutheran Church—Missouri Synod did not adopt the RCL in full. The LSB Three-Year Lectionary agrees with the RCL much of the time but deliberately restores or substitutes readings that the LCMS lectionary committee considered important for Lutheran proclamation and catechesis.

The LCMS specifically identifies RCL omissions that influenced its decision, including:

- Ephesians 5:22–33
- Romans 13:1–7
- 1 Corinthians 10:16–17 and 11:27–32
- Galatians 2:11–14 and 6:1–6
- Philippians 4:10–20
- Hebrews 12:4–13
- 1 John 4:1–6
- Luke 13:22–30

The RCL and LSB catalogs must therefore remain separate even when many appointments coincide.

### Example: Proper 15, Year A, August 16, 2026

| Role | RCL complementary track | LSB Series A |
|---|---|---|
| First reading | Isaiah 56:1, 6–8 | Isaiah 56:1, 6–8 |
| Psalm | Psalm 67 | Psalm 67 is available as the appointed Psalm |
| Epistle | Romans 11:1–2a, 29–32 | Romans 11:1–2a, 13–15, 28–32 |
| Gospel | Matthew 15:(10–20), 21–28 | Matthew 15:21–28 |

This illustrates both the broad agreement and the meaningful differences that must be preserved.

## 7. Existing ChurchManager support

ChurchManager already has several capabilities needed for RCL support:

- `tblLectionarySystem` represents reusable lectionary systems.
- `CycleType='ABC'` represents a three-year cycle.
- `tblPropers.LectionarySystemID` keeps different lectionary catalogs separate.
- `tblPropers.Cycle` can store A, B, or C.
- `tblReading` stores multiple citations associated with a proper.
- `tblChurch.PrimaryLectionarySystemID` allows a congregation to choose a default system.
- The unified worship-service dialog filters propers using the congregation's default lectionary.
- The weekly worship planner and reports retrieve readings from the selected proper.

This means the stable RCL can be added without replacing or altering existing LSB proper records.

## 8. Current design gaps

### 8.1 Track selection

The current data model cannot identify a reading as common, complementary, or semicontinuous. Importing both tracks as ordinary readings would cause the user interface and reports to display all of them as if they were all appointed for the service.

### 8.2 Paired first reading and psalm

The model does not express that a particular psalm belongs with a particular first-reading option. This relationship is essential to the RCL.

### 8.3 Reading roles

Existing LSB normalization emphasizes `Old Testament`, `Epistle`, and `Gospel`. Proper RCL support also requires a first-class `Psalm/Canticle` role and should tolerate `Acts` as either the first reading or, in the provisional update, an alternative to the Epistle.

### 8.4 Alternate and optional readings

`tblReading` can contain multiple rows, but it does not identify whether rows are cumulative, mutually exclusive, alternate translations, optional extensions, or denominational variants.

### 8.5 Service-level persistence

The current worship-planning code derives readings from the selected proper. It does not persist the actual service-level selection. Editing a proper later could therefore change what appears to have been selected for an already-planned or historical service.

### 8.6 Edition and source provenance

`tblLectionarySystem` does not provide structured fields for edition, publication date, trial status, source, copyright statement, or import version.

### 8.7 Automatic calendar resolution

The present selection list is ordered by system, cycle, and sort value, but ChurchManager does not appear to calculate automatically:

- The correct A/B/C year at Advent.
- Moveable dates based on Easter.
- The correct Proper after Pentecost.
- Festival precedence, transfer, or denominational variation.

## 9. Recommended target design

The following is a product recommendation, not an approved migration specification.

### 9.1 Preserve lectionary catalogs

- Keep `LSB Three-Year Lectionary` unchanged.
- Keep `LSB One-Year Lectionary` unchanged.
- Add `Revised Common Lectionary (1992)` as a distinct active ABC system.
- Treat provisional or future editions as versioned data, not edits to the 1992 records.

### 9.2 Add edition metadata

Add structured lectionary-edition data capable of storing:

- System name
- Edition name and year
- Publisher or responsible body
- Source URL
- Stable, provisional, or retired status
- Trial start and end dates when applicable
- Copyright and permissions note
- Import date and import-data version

### 9.3 Add structured reading choices

Each reading appointment should be able to store:

- Role: first reading, psalm/canticle, second reading, or Gospel
- Track: common, complementary, semicontinuous, or edition-specific
- Option group
- Option type: default, alternate, optional extension, or denominational variant
- Sequence within the service
- Display citation
- Normalized citation for search and matching
- The reading or option with which it is paired
- Explanatory note

### 9.4 Persist service readings

Add service-level reading selections. When a proper is applied to a service, ChurchManager should copy or reference the selected appointments into service-owned rows.

This would permit the planner to:

1. Begin with defaults from the chosen proper.
2. Select a track and valid alternatives.
3. Edit a citation when a permitted shorter or longer form is used.
4. Preserve the final selection for historical accuracy.
5. Produce the same readings consistently in the bulletin, worship plan, reports, and sermon-search tools.

### 9.5 Add congregation defaults

In addition to `PrimaryLectionarySystemID`, a congregation using the RCL may need defaults for:

- Lectionary edition
- Post-Pentecost track
- Preferred numbering or display terminology
- Preferred Scripture translation
- Use of provisional options

Service-level choices should still be able to override these defaults explicitly.

### 9.6 Add a calendar resolver

The resolver should return candidate appointments for a date rather than choosing silently when precedence or denominational practice is ambiguous. Its result should include:

- Civil date
- Liturgical date
- Season
- Cycle year
- Proper or ordinary-time number
- Festival or special-day alternatives
- Lectionary system and edition
- Reason the appointment was selected

## 10. Recommended implementation sequence

1. **Approve the functional design.** Settle whether RCL support is intended for general ecumenical use, a particular congregation, or both.
2. **Design the normalized option model.** Do not import data until track, pairing, alternate, and service-selection behavior is defined.
3. **Create guarded migrations in ChurchDBTest only.** Production ChurchDB and the Frozen application remain out of scope.
4. **Add service-level reading selection and persistence.** Make one source feed all worship outputs.
5. **Build a reproducible importer from the official CCT citation tables.** Do not manually transcribe the full lectionary.
6. **Import the stable 1992 RCL first.** Keep the provisional update disabled or separately selectable.
7. **Validate all three cycles.** Check every proper, role, track, paired psalm, alternative, optional range, festival, and date boundary.
8. **Test UI and reports with isolated representative services.** Include post-Pentecost track selection and Easter provisional alternatives.
9. **Document permissions and provenance.** Scripture text must not be imported unless the selected translation's license permits it.
10. **Obtain explicit approval before any production deployment.**

## 11. Validation requirements

An RCL implementation should not be considered complete until tests demonstrate:

- A, B, and C resolve correctly at Advent boundaries.
- Every RCL proper has the expected common readings.
- Both post-Pentecost tracks are available without being combined.
- Each first-reading option returns its correct psalm or canticle.
- Alternate and optional readings are visibly identified.
- The 1992 edition remains stable when provisional options are enabled.
- A service preserves its selected readings after catalog changes.
- Bulletin, worship planner, reporting, and sermon matching use the same service-level selection.
- LSB data and behavior remain unchanged.
- No development action touches the separate Frozen application or its database.

## 12. Copyright and data-source boundaries

The RCL arrangement of citations is copyrighted by the Consultation on Common Texts. The CCT publishes a permissions policy for reproduction of the citation tables. Copyright for the wording of biblical texts belongs to the holder of the chosen Bible translation and is governed separately.

The recommended ChurchManager catalog should initially store citations, roles, choices, and explanatory metadata rather than full Scripture text. Any future full-text feature requires a separate translation-license review.

## 13. Authoritative sources

- Consultation on Common Texts, **Revised Common Lectionary introduction**:  
  <https://www.commontexts.org/wp-content/uploads/2015/11/RCL_Introduction_Web.pdf>
- Consultation on Common Texts, **Using the Revised Common Lectionary**:  
  <https://www.commontexts.org/rcl/using-rcl/>
- Consultation on Common Texts, **RCL downloads**:  
  <https://www.commontexts.org/rcl/download/>
- Consultation on Common Texts, **RCL permissions policy**:  
  <https://www.commontexts.org/rcl/permissions/>
- Consultation on Common Texts, **Worldwide usage**:  
  <https://www.commontexts.org/rcl/usage/>
- Consultation on Common Texts, **Addressing Anti-Judaism: provisional update**:  
  <https://www.commontexts.org/2025-update/>
- Consultation on Common Texts, **Report updated April 21, 2026**:  
  <https://www.commontexts.org/wp-content/uploads/2026/04/CCT-Addressing-Anti-Judaism-Update-2026.pdf>
- The Lutheran Church—Missouri Synod, **Lectionary Series: Scripture Readings**:  
  <https://www.lcms.org/worship/lectionary-series>

## 14. Decision still required

Before implementation, the product owner should decide:

> Should ChurchManager implement the RCL as a general reusable lectionary platform for multiple congregations, or only add enough RCL behavior for one known congregation's selected edition and track?

The general platform requires more design work but avoids another lectionary-specific implementation later.
