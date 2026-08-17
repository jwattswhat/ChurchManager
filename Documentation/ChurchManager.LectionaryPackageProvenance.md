# ChurchManager Lectionary Package Provenance Decision

**Reviewed:** August 17, 2026  
**Status:** Distribution blocked pending written permission

## Decision

ChurchManager will not bundle an LSB or Revised Common Lectionary package in its
public open-source repository until the appropriate rights administrator gives
written permission for electronic redistribution of the citation and calendar
metadata.

This is deliberately narrower than reproducing a publication. A ChurchManager
package would contain only names, calendar rules, roles, Scripture citations,
option relationships, colors, and short source/permission notices. It would not
contain Scripture text, psalm text, prayers, collects, liturgical wording,
rubrics, hymn lyrics, music, notation, artwork, media, or page images. Even so,
the compilation or table itself may be protected, so the metadata-only boundary
does not by itself establish redistribution authority.

## Revised Common Lectionary

The Consultation on Common Texts identifies the RCL as a copyrighted table of
citations. Its [permissions policy](https://www.commontexts.org/rcl/permissions/)
allows individual congregations and similar nonprofit groups to reproduce the
table for their own worship and educational activity. It separately says other
organizations wishing to include the table in electronic resources must obtain
written permission through its copyright administrator, Augsburg Fortress.

The official [download page](https://www.commontexts.org/rcl/download/) also
limits the provided electronic files to local nonprofit worship/educational use
and says they may not be reposted on a website without permission. Therefore:

- a congregation may create a `LOCAL_ONLY` package after documenting its own
  lawful local-use basis and including the required notice;
- ChurchManager must not commit or distribute that local package; and
- a public RCL package remains blocked until CCT/Augsburg Fortress grants
  written electronic-redistribution permission.

## Lutheran Service Book lectionaries

Concordia Publishing House's
[copyright and permissions page](https://www.cph.org/copyrights-permissions)
directs users to its Rights and Permissions Department when the requested use
is not clearly licensed. The published
[Lutheran Service Builder license](https://music.cph.org/lutheran-service-builder/license-agreement)
grants licensed congregations specified reproduction rights for congregational
life; it does not state that an unrelated open-source project may redistribute
an electronic LSB lectionary catalog.

Therefore:

- an ordinary CPH or congregational license is not treated as permission to
  place an LSB package in ChurchManager's public repository;
- ChurchManager will request written permission specifically for a citation-only
  electronic metadata package; and
- no LSB package will be marked `REDISTRIBUTABLE` until that permission is
  received and preserved with the package provenance record.

## Permission request: CCT / Augsburg Fortress

**Subject:** Permission request for citation-only Revised Common Lectionary metadata in an open-source church application

ChurchManager is a proposed open-source, noncommercial church-management
application. We request written permission to distribute a machine-readable
metadata package representing the 1992 Revised Common Lectionary.

The package would contain only the names of Sundays and festivals, calendar and
cycle identifiers, Scripture citation references, reading roles, option/track
relationships, and the copyright notice you require. It would not contain any
Scripture text or translation, psalm text, prayers, liturgical text, commentary,
music, artwork, page images, or copies of your downloadable files. The package
would be freely available as part of the application's public source repository
and would not be sold.

May ChurchManager distribute that citation-only metadata package? If so, please
provide the exact notice, attribution, version limits, and any conditions you
require.

## Permission request: Concordia Publishing House

**Subject:** Permission request for citation-only LSB lectionary metadata in an open-source church application

ChurchManager is a proposed open-source, noncommercial church-management
application. We request written permission to distribute machine-readable
metadata packages for the Lutheran Service Book Three-Year and One-Year
lectionaries.

The packages would contain only the names of Sundays and festivals, cycle and
calendar identifiers, Scripture citation references, reading roles, optional
reading relationships, liturgical colors, and the copyright/permission notice
you require. They would not contain Scripture text, psalm or canticle text,
collects, prayers, liturgical wording, rubrics, hymn lyrics, music, notation,
artwork, page images, or Lutheran Service Book page reproductions. The packages
would be freely available as part of the application's public source repository
and would not be sold.

May ChurchManager distribute those citation-only metadata packages? If so,
please provide the exact notice, attribution, edition limits, and any conditions
you require.

## Implementation consequence

The validator, builder, package manager, local-only scope, calendar resolver,
and service snapshots remain useful now. Installation may accept a congregation's
lawfully prepared `LOCAL_ONLY` package, but ChurchManager's maintained public
package inventory remains empty until written permission is documented.
