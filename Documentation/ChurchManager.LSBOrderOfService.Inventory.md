# LSB Order of Service Package Inventory

**Status:** Implemented as validated package `lsb-services-1.0.0.json`

**Prepared:** August 16, 2026

## Purpose

The first Lutheran Service Book Order of Service package will not stop with one
Divine Service starter. It will provide a named metadata-only outline for every
supported LSB service form appropriate to ChurchManager planning. Every display
name begins with `LSB ` (the abbreviation followed by one space).

## Package template inventory

### Divine Service

1. `LSB Divine Service, Setting One`
2. `LSB Divine Service, Setting Two`
3. `LSB Divine Service, Setting Three`
4. `LSB Divine Service, Setting Four`
5. `LSB Divine Service, Setting Five`

### Daily Office

6. `LSB Matins`
7. `LSB Vespers`
8. `LSB Morning Prayer`
9. `LSB Evening Prayer`
10. `LSB Compline`

### Other congregational services

11. `LSB Service of Prayer and Preaching`
12. `LSB Responsive Prayer 1—Suffrages`
13. `LSB Responsive Prayer 2`
14. `LSB The Litany`
15. `LSB Corporate Confession and Absolution`

### Pastoral and occasional rites usable as planned services

16. `LSB Holy Baptism`
17. `LSB Holy Baptism—Alternate Form`
18. `LSB Confirmation`
19. `LSB Holy Matrimony`
20. `LSB Entrance of the Body into the Church`
21. `LSB Funeral Service`
22. `LSB Individual Confession and Absolution`

Daily Prayer for Individuals and Families, the Small Catechism, psalms,
lectionaries, prayers, canticles, and stand-alone resources are not Order of
Service templates. They may be separately represented only if a later approved
ChurchManager feature requires them.

## Source verification

The inventory is based on official LCMS and Concordia Publishing House sources:

- [Lutheran Service Book contents excerpt](https://s3.amazonaws.com/cph-org-assets/media/pdf/031202.pdf)
- [LCMS Worship liturgy audio inventory](https://www.lcms.org/worship/church-music/liturgy-audio-files)
- [Concordia Publishing House LSB Pew Edition](https://www.cph.org/lutheran-service-book-pew-edition)

These sources verify names and scope. They do not authorize ChurchManager to
copy the wording, music, rubrics, prayers, or other protected content.

## Curation rules

- Each template contains short original outline labels and references only.
- Page references from the services section use the established `LSB p. 151`
  style; hymn references use `LSB 331` style.
- No template contains complete liturgical text, prayer text, responsive text,
  Scripture text, music, notation, images, or publisher files.
- Every package record must pass the metadata-only validator.
- Exact line sequences require review against a legitimately held printed or
  electronic LSB, but the resulting package remains an outline rather than a
  reproduction.
- The complete set is installed or upgraded transactionally as one package.

## Delivered package

The reproducible package source is
`packages/order_of_service/lsb-services-1.0.0.json`. It contains 22 templates
and 338 planning lines. Its checksum, prefix, dependencies, field lengths,
line types, conditions, and content boundary are checked before any database
write. Starter templates deliberately contain no required participant roles;
roles may be added to local customized templates.

Use these commands from the ChurchManager project directory:

```powershell
.\.runtime-venv\Scripts\python.exe install_order_of_service_package.py
.\.runtime-venv\Scripts\python.exe install_order_of_service_package.py --apply
```

The first command performs validation only. The second installs or upgrades
the package atomically and is hard-limited to local `ChurchDBTest`.
