# ChurchManager Development Boundary

- `C:\Users\Pastor\Documents\ChurchManager-Legacy` is the separate Frozen ChurchManager application.
- Never edit, delete, migrate, synchronize, import from, or copy development files into the Frozen application tree from this project.
- Never use the Frozen application's runtime, JSForm copy, forms, configuration, or production database for development work.
- Development ChurchManager uses this project, `C:\Users\Pastor\Documents\JSForm`, its own `.runtime-venv`, and the guarded development/test database configuration.
- Read-only inspection of the Frozen application is allowed only when the user explicitly requests verification.
- Any Frozen application change must be performed from its separate project, not from this project.
- In this project, "legacy" means obsolete JSForm-era behavior inside development. It never means the separate Frozen application and never authorizes changes there.
- The Frozen application becomes defunct on January 1 and is not a supported
  ChurchManager platform. Do not add compatibility code, migration paths, shared
  files, shared database structures, launchers, documentation, tests, or product
  requirements for it.
- Design the current ChurchManager as an entirely new, independent system. The
  only continuing relationship is the safety boundary that prevents accidental
  access to or modification of the old application before it is retired.

## Documentation maintenance

- Treat documentation as part of every implementation change.
- Update relevant public guides, specifications, inventories, docstrings, and tests in the same commit as changed behavior.
- Keep terminology consistent across Python, JSON definitions, database choices, screens, reports, and documentation.
- New top-level Python modules require module docstrings; public interfaces require useful contract docstrings.
- Do not claim GUI or report layout is visually verified unless it was rendered and inspected.

## Outline-only worship-content boundary

- ChurchManager is an outline and planning system. Do not add storage, package
  fields, imports, attachments, editors, reports, or generated output for full
  liturgical or musical content.
- Prohibited content includes full liturgical wording; published prayers or
  collects; responsive pastor-and-congregation text; meaningful-length verbatim
  rubrics; psalm or canticle text; psalm tones or musical settings; hymn lyrics;
  music notation; accompaniment material; and publisher artwork or page images.
- Order of Service and hymnal structures may store only short labels, titles,
  printed references, sequence, item types, conditions, inclusion choices,
  participant requirements, stanza counts or selections, and brief planning or
  source notes.
- Treat this as a schema and validation boundary, not a user preference or
  licensing mode. New and changed package schemas must reject prohibited content
  fields and attachments, and tests must cover those rejections.
