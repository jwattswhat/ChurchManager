# ChurchManager Hymnal Research and Recommendations

**Status:** Saved for future design and implementation  
**Prepared:** August 14, 2026  
**Scope:** Development ChurchManager only  
**Out of scope:** Production ChurchDB

## Executive conclusion

ChurchManager should support multiple hymnals through a general music-catalog model, but it should import hymnals selectively. The most useful near-term additions are historical LCMS hymnals, followed by current Lutheran hymnals needed by actual congregations.

The central design requirement is to distinguish the underlying hymn from its numbered appearance in a particular hymnal. The same hymn may appear in several books with different numbers, translations, tunes, harmonizations, stanza counts, and copyright conditions. Proper hymn suggestions should ultimately identify the underlying hymn and then resolve it to the congregation's selected hymnal.

ChurchManager's purpose is to prepare service and bulletin outlines, not to
print complete services. Full lyrics, stanza text, liturgical text, music
images, harmonizations, arrangements, recordings, and other protected content
must not be imported merely because ChurchManager can store them. Each type of
content requires separate copyright and license review.

### Non-negotiable identifier rule

ChurchManager will use permanent, explicitly assigned numeric hymn identifiers.
Each hymnal owns a permanent 5,000-number block, and the same entry has the same
`HymnID` in every installation. Official package IDs are never auto-incremented,
renumbered, reused, or translated according to installation order.

Local user-entered hymns occupy their own permanent range. Textual codes such as
`lsb` remain package metadata and secondary validation, not replacement foreign
keys. The complete design is defined in
[Permanent Hymn Identifier Specification](ChurchManager.PermanentHymnIdentifiers.Specification.md).

The proposed operational workflow for preparing, validating, packaging,
installing, upgrading, and locally importing hymnals is documented in
[Suggested Hymnal Import Process](ChurchManager.HymnalImportProcess.md).

## 1. Existing ChurchManager support

ChurchManager already provides a useful foundation:

- `tblHymnal` represents a hymnal or music source.
- `tblHymn` associates a numbered hymn entry with a hymnal.
- `tblChurch.PrimaryHymnalID` supplies a congregation default.
- Bulletin-order templates may be associated with a hymnal.
- `tblProperHymnSuggestion` associates suggested hymns with Propers and liturgical uses.
- `tblHymnUsage` records a selected hymn and its service-order position.
- The worship planner filters the hymn catalog using the congregation's primary hymnal.
- The hymn record includes title, tune, Scripture references, category, file, and notes.
- Tune information can be used to detect undesirable repetition within a service.

The legacy catalog contains hymnal or publisher records for:

- `LSB` — *Lutheran Service Book*
- `TLH` — *The Lutheran Hymnal*
- `kingsway` — Kingsway/Thankyou Music

The third item illustrates an existing conceptual problem: Kingsway/Thankyou Music is closer to a publisher or song catalog than a bound hymnal.

## 2. Recommended catalog priorities

### 2.1 First priority: LCMS books

These have the greatest immediate value for Life in Christ, existing ChurchManager records, and the sermon and worship archive.

1. **Lutheran Service Book (LSB, 2006)**
   - Preserve as the primary current catalog.
   - Complete and verify its existing metadata before broad expansion.

2. **The Lutheran Hymnal (TLH, 1941)**
   - Complete and verify the existing hymnal record and hymn catalog.
   - Useful for older sermon, funeral, service, and congregational records.

3. **Lutheran Worship (LW, 1982)**
   - Recommended as the next historical LCMS catalog.
   - Necessary for records created between widespread TLH and LSB use.

4. **Documented supplements actually used locally**
   - Add only when Life in Christ records or archived services demonstrate real use.
   - Avoid speculative catalogs that would require maintenance without serving a known need.

### 2.2 Second priority: current Lutheran hymnals

5. **Evangelical Lutheran Worship (ELW, 2006)**
   - Natural companion to support for RCL-using Lutheran congregations.

6. **All Creation Sings (ACS, 2020)**
   - A supplement to ELW rather than an independent replacement hymnal.
   - Adds 200 hymns and songs, numbered 901–1100 in continuation of the ELW pattern.

7. **Christian Worship: Hymnal (CW21)**
   - Current WELS hymnal, adopted in 2021.
   - Part of a broader suite that includes a psalter, service material, accompaniment resources, and a digital Service Builder.

8. **Lutheran Book of Worship (LBW, 1978)**
   - Primarily valuable for historical records and congregations that continue to use it.

These books would test whether ChurchManager can serve multiple North American Lutheran traditions without making the application dependent on one hymnal's structure.

### 2.3 Third priority: ecumenical hymnals

Add these only in response to an identified congregation or product audience:

- *The Hymnal 1982* — Episcopal Church
- *Glory to God* — Presbyterian Church (U.S.A.)
- *The United Methodist Hymnal*
- *Chalice Hymnal* — Christian Church (Disciples of Christ)
- *Gather* and other Roman Catholic worship resources
- Denominational bilingual hymnals and supplements
- Specialized cultural or ethnic collections

ChurchManager should be capable of representing these catalogs, but maintaining every denominational hymnal would create ongoing editorial, licensing, and versioning work.

## 3. Contemporary worship music

Contemporary songs often do not belong to one stable printed hymnal. They should be represented as a congregation's licensed song library rather than forced into the hymnal model.

Useful metadata includes:

- Standard song title
- First line
- Songwriters
- Publisher and copyright administrator
- Original publication year
- CCLI song number
- ONE LICENSE identifier when one exists
- Local arrangement or preferred key
- Lead-sheet or accompaniment source
- License coverage
- Reporting status
- Congregation-specific notes

CCLI and ONE LICENSE are licensing and reporting systems, not hymnals. ChurchManager should distinguish:

- Hymnal
- Supplement
- Publisher catalog
- Congregational song library
- Licensed online catalog
- Local composition

## 4. The canonical music model

### 4.1 Hymn work

The hymn work is the general identity shared across hymnals.

Recommended fields:

- Standard title
- First line
- Original title
- Original language
- Text author
- Original date or approximate period
- Scripture associations
- Liturgical and theological topics
- Public-domain or copyright summary

Example:

```text
Hymn work: A Mighty Fortress Is Our God
    +-- LSB 656
    +-- TLH 262
    +-- LW 298
    +-- ELW 504
```

Each numbered entry may use a different translation, revision, tune, harmonization, or stanza selection.

### 4.2 Hymn text version

A text version represents a particular original-language text, translation, or revision.

Recommended fields:

- Hymn work
- Language
- Translator or reviser
- Text incipit
- Stanza count
- Copyright year
- Copyright holder or administrator
- Public-domain status
- License source
- Notes on altered or omitted stanzas

ChurchManager should not assume that two hymnals with the same English title print identical words.

### 4.3 Tune

Tune identity should be independent of hymnal entries.

Recommended fields:

- Tune name
- Alternate tune names
- Composer or source
- Meter
- Key or mode
- Composition date
- Copyright information
- Notes

One text can be paired with several tunes, and one tune can carry several texts.

### 4.4 Musical setting or harmonization

A setting describes the particular musical realization used in a publication or service.

Recommended fields:

- Tune
- Arranger or harmonizer
- Voicing
- Instrumentation
- Key
- Copyright
- Source publication
- File or licensed-resource reference

The religious-services exemption for performance does not make copyrighted arrangements free to reproduce, distribute, or stream.

### 4.5 Hymnal edition

Extend the concept currently represented by `tblHymnal` with:

- Abbreviation
- Full title
- Edition year
- Denomination or sponsoring body
- Publisher
- ISBN
- Primary hymnal, supplement, psalter, or service book type
- Parent hymnal when it is a supplement
- Active or historical status
- Source and import version
- Permission and copyright note

The edition year matters. Reusing a title or abbreviation must not cause one edition to overwrite another.

### 4.6 Hymnal entry

A hymnal entry represents the appearance of a work, text, tune, and setting under one number in one edition.

Recommended fields:

- Hymnal edition
- Printed number
- Hymn work
- Text version
- Tune
- Setting or harmonization
- Number of printed stanzas
- Category in that hymnal
- Service-music designation
- Printed copyright line
- Notes

The natural uniqueness rule is hymnal edition plus printed number. The displayed hymn-number string should not be globally unique across every hymnal.

## 5. Proper hymn suggestions

The present Proper suggestion points directly to a `tblHymn` entry. That makes the suggestion hymnal-specific.

The long-term model should support two levels:

1. **Canonical suggestion:** Recommend the underlying hymn work for a Proper and liturgical position.
2. **Edition resolution:** Show the corresponding numbered entry available in the congregation's selected hymnal.

Example:

```text
Proper recommendation: A Mighty Fortress Is Our God
Congregation's primary hymnal: LSB
Resolved selection: LSB 656
```

If the hymn is unavailable in the selected hymnal, ChurchManager should say so and may show entries from secondary hymnals authorized for that congregation.

Suggestions may still need edition-specific exceptions when a particular translation, tune, or stanza is the reason for the recommendation.

## 6. Service-level hymn selection

Every selected service hymn should preserve:

- Hymn work
- Selected hymnal entry
- Hymnal abbreviation and number
- Liturgical use: entrance, hymn of the day, distribution, closing, and so forth
- Stanzas selected
- Tune and setting actually used when known
- Accompaniment source
- Language
- Whether words or music were printed or projected
- Whether the service was streamed or recorded
- Applicable license and reporting status
- Free-form planning note

This service-owned information must remain historically stable if the catalog is corrected later.

## 7. Stanza selections

Stanza selection is a separate approved-design candidate documented in:

`Documentation/ChurchManager.HymnStanzaSelection.Specification.md`

The proposed first implementation stores a normalized expression such as `1,3,11-12` on the service's `tblHymnUsage` row and renders it as:

- `st. 3`
- `sts. 1–4`
- `sts. 1, 3, 11–12`

This is deliberately service-specific. The same hymn can use different stanzas in different services.

Every imported hymnal entry must provide `PrintedStanzaCount` for that edition;
zero identifies an entry that is not stanza-based. This supports warnings when
a service selection exceeds the stanzas printed in that edition. It must not
assume that every hymnal prints the same stanza set, and the count does not
authorize storing or reproducing stanza text.

## 8. Services may use more than one hymnal

A congregation's `PrimaryHymnalID` is a useful default, not an exclusive restriction.

A service may legitimately use:

- The primary hymnal
- A denominational supplement
- A psalter
- A locally licensed contemporary song
- A choir or instrumental source
- A historical hymn from another authorized book

The worship planner should therefore:

- Search the primary hymnal first.
- Permit secondary sources authorized by the congregation.
- Display source abbreviation and number clearly.
- Warn, but not necessarily prohibit, selection from an unauthorized or inactive source.
- Preserve the exact source used for the service.

Bulletin-order templates may have a primary hymnal association while individual service lines use other sources.

## 9. Service music requires a broader type system

Hymnals contain more than metrical hymns:

- Divine Service settings
- Psalms and psalm tones
- Canticles
- Introits
- Graduals
- Alleluia and verse settings
- Liturgical responses
- Chants
- Short refrains
- Instrumental and choral material

These should not all be classified simply as hymns.

Recommended music-item types include:

- Hymn
- Song
- Psalm setting
- Canticle
- Liturgical music
- Acclamation or response
- Chant
- Choir piece
- Instrumental piece

An item may still appear under a printed number in a hymnal or service book.

## 10. Copyright and licensing boundaries

### 10.1 Metadata

ChurchManager can be designed to store basic planning and catalog metadata, including title, authorship, source, number, tune name, public-domain status, copyright owner, license identifiers, and selected stanzas.

### 10.2 Content requiring review

Do not import or distribute the following without verified permission:

- Complete lyrics
- Melody images
- Harmonizations or accompaniment music
- Choral or instrumental parts
- Publisher-supplied recordings
- Practice tracks
- Service music
- Copyrighted translations or revisions

Owning printed hymnals does not automatically authorize reproduction of their contents.

### 10.3 License distinctions

ChurchManager must not treat a license as a universal permission. Relevant activities may require different coverage:

- Printing words in a bulletin
- Printing melody or music
- Projection
- Streaming a live performance
- Archiving a recording
- Playing a publisher or artist recording
- Distributing rehearsal material
- Creating or copying an arrangement

CCLI instructs churches to report covered songs when words are reproduced, projected, copied, or pasted for congregational use. ONE LICENSE distinguishes reprint, podcast/streaming, and recorded-audio permissions.

ChurchManager should initially record relevant facts and reporting status. Automatic submission to licensing services is a separate future integration.

## 11. Recommended implementation sequence

1. Finish and verify the existing LSB catalog and usage paths.
2. Implement and test service-level stanza selection after specification approval.
3. Complete the TLH catalog needed for historical records.
4. Add Lutheran Worship for LCMS archive continuity.
5. Design canonical hymn work, text version, tune, setting, hymnal edition, and hymnal-entry tables.
6. Preserve compatibility with existing `tblHymn` IDs while data is migrated or bridged.
7. Change Proper suggestions to support canonical-hymn recommendations with edition-specific exceptions.
8. Allow congregations to define primary and authorized secondary music sources.
9. Add ELW and All Creation Sings if RCL-using congregations are in product scope.
10. Add Christian Worship 2021 if WELS congregations are in product scope.
11. Model contemporary songs as a licensed song library rather than a synthetic hymnal.
12. Add ecumenical hymnals only for identified congregational needs.
13. Add copyright-reporting assistance only after the underlying service-usage data is reliable.

All schema work must use guarded migrations and isolated ChurchDBTest data first. Production deployment remains a separate approved action.

## 12. Validation scenarios

The future model should be tested with at least these cases:

1. One hymn appearing in LSB, TLH, LW, and ELW under different numbers.
2. One text appearing with different tunes.
3. One tune carrying different texts.
4. Different stanza counts or translations in different hymnals.
5. A Proper suggestion resolving automatically to the congregation's primary hymnal.
6. A suggestion unavailable in the primary hymnal but available in an authorized supplement.
7. A service using hymns from both a primary hymnal and a supplement.
8. A contemporary song identified by CCLI number rather than hymnal number.
9. A public-domain text paired with a copyrighted harmonization.
10. A hymn sung with selected stanzas and preserved in service history.
11. A liturgical canticle or service-music item that should not be classified as a hymn.
12. Historical service records remaining stable after catalog corrections.

## 13. Recommended product test

The foundational acceptance question is:

> Can ChurchManager recommend one hymn for a Proper and correctly show the available number, text version, tune, and selected stanzas in whichever hymnal or authorized music source that congregation uses?

If ChurchManager can do this while preserving the exact service selection and copyright metadata, it will have a durable multi-hymnal foundation rather than a collection of unrelated numbered lists.

## 14. Authoritative reference links

- WELS, **Christian Worship resources**:  
  <https://christianworship.com/>
- WELS, **Presentation and adoption of Christian Worship: Hymnal**:  
  <https://wels.net/new-wels-hymnal-presented/>
- Augsburg Fortress, **All Creation Sings hymn list and introduction**:  
  <https://ms.augsburgfortress.org/downloads/9781506449616%20ACS_Full_Hymn_List.pdf>
- Church Publishing, **The Hymnal 1982**:  
  <https://prod.churchpublishing.org/hymnalpewblue>
- CCLI, **Church Copyright License overview**:  
  <https://go.ccli.com/license-us>
- CCLI, **Usage reporting guidance**:  
  <https://ccli.com/us/en/reporting>
- ONE LICENSE, **Reprint, streaming, and recorded-audio licensing**:  
  <https://www.onelicense.net/>

## 15. Approval boundary

This document preserves research and recommendations for later. It does not authorize schema changes, catalog imports, acquisition of copyrighted content, external licensing actions, or production deployment.
