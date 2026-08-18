# ChurchManager public website specification

Status: Approved
Approved by: Rev. Jonathan C. Watt
Prepared: August 18, 2026

## Purpose

The ChurchManager website introduces the application, establishes trust, and
directs visitors to downloads, documentation, source code, and support. It is
not part of the ChurchManager application and must never store congregation
data, user accounts, passwords, or support logs.

The first version is deliberately a small, static website. It can be hosted on
GitHub Pages, Codeberg Pages, a conventional web host, or another static host
without changing its design.

## Audience

The primary audience is pastors, treasurers, church secretaries, and volunteer
administrators in small congregations. They should be able to understand the
site without knowing Python, MariaDB, GitHub, or software-development terms.

## Core message

**Church administration built for small congregations.**

ChurchManager is an open-source Windows desktop application that keeps a
congregation's information under its own control. It brings people records,
worship planning, attendance, reporting, fund accounting, backup, and security
together without requiring a cloud subscription.

This wording may be refined during beta testing, but the site should retain a
plain, practical, non-commercial tone.

## Information architecture

Version 1 is one responsive page with these sections:

1. **Header** — ChurchManager name, compact navigation, and current beta status.
2. **Introduction** — one-sentence purpose and two actions: download and learn
   more.
3. **Trust summary** — open source, Windows desktop, congregation-controlled
   data, and designed for small congregations.
4. **Capabilities** — six short summaries covering people, worship, attendance,
   accounting, reports, and backup/security.
5. **Screenshots** — three maintained images: main menu, worship planning, and
   an accounting report. Placeholders remain until approved screenshots exist.
6. **Beta participation** — honest pre-release status, appropriate expectations,
   and a link to testing instructions.
7. **Documentation and help** — user guide, installation guide, support,
   security reporting, and treasurer guidance.
8. **Data ownership and copyright boundary** — no hosted congregation database;
   ChurchManager stores planning metadata and outlines rather than copyrighted
   worship or hymn text.
9. **Footer** — version, license, source, support, privacy, and copyright.

The page also includes a compact **Upcoming Updates** section between
Capabilities and Screenshots. It may name only work backed by an approved
repository specification, and it must clearly distinguish planned work from
features available in the current release. The initial entries are Pastoral
Care and Member Giving and Envelopes.

No blog, news system, testimonials, mailing list, search, account area, shopping
cart, live chat, or content-management system is needed for the initial site.

## Required placeholders before publication

The local prototype intentionally uses placeholders for:

- public download URL and SHA-256 checksum;
- public source repository and issue tracker;
- final support and security contact destinations;
- final domain name and canonical site URL;
- approved main-menu, worship-planning, and report screenshots;
- final PDF URLs for the User Guide and Treasurer Guide;
- privacy notice and beta-testing instructions if separate public pages are
  later preferred.

Placeholders must be visibly labeled and must not lead visitors to an old,
development-only, or unverified installer.

## Visual direction

- Warm, trustworthy, restrained, and readable rather than corporate.
- Deep blue is the primary color, with warm gold used sparingly.
- White and pale blue-gray surfaces keep the page calm and printable.
- The system font stack avoids web-font downloads and maintenance.
- Rounded cards and thin borders organize information without excessive visual
  effects.
- The first screen must clearly show the product name, purpose, beta status, and
  primary action on both desktop and mobile.
- The congregation test logo must not be used as the ChurchManager product
  identity. The existing ChurchManager application icon may be adopted after a
  separate web-asset review.

## Accessibility and responsive behavior

- Semantic headings, landmarks, lists, links, and buttons.
- A keyboard-visible skip link and clear focus indicators.
- Sufficient text/background contrast; color is never the sole status cue.
- Useful alternative text for approved screenshots.
- Comfortable touch targets and a single-column mobile layout.
- Respect reduced-motion preferences; the first version requires no animation.

## Privacy, security, and maintenance boundaries

- No analytics, tracking pixels, cookies, forms, or third-party scripts.
- No congregation or beta-tester personal information.
- No database connection or application login.
- No secrets, email credentials, error logs, or downloadable database samples.
- Only verified release installers may be linked.
- The displayed version must match ChurchManager's authoritative release
  version.
- Download pages must show the file size and SHA-256 checksum.
- Security reports should use the maintained security instructions rather than
  a public issue containing sensitive details.
- Copyrighted hymn lyrics, music, liturgical wording, prayers, publication
  images, or protected lectionary content must not appear on the site.

## Technical design

The first version uses plain HTML and CSS with relative links. It has no build
step, package manager, JavaScript dependency, database, or hosting-specific
configuration. This makes the site inexpensive to host, easy to audit, and
simple to move later.

Files live in `website/`:

- `index.html` — page structure and public wording;
- `styles.css` — responsive visual design;
- `README.md` — placeholder inventory and maintenance instructions.

When a destination is chosen, hosting configuration should be added separately
without changing the portable source unnecessarily.

## Publication acceptance checklist

- Replace or deliberately retain every marked placeholder.
- Review every public claim against the current application.
- Build or copy the release through the approved release process.
- Verify installer name, size, version, checksum, and download target.
- Review source history for credentials, congregation data, database dumps, and
  copyrighted catalog content before making a repository public.
- Render and visually inspect the page at desktop and mobile widths.
- Test all keyboard navigation and all links.
- Verify that no network request is made except for the page's own static files.
- Confirm the User Guide, support, security, license, and privacy information.
- Obtain final approval before publishing.

## Future additions only when justified

A separate release-history page, frequently asked questions, or translated
content may be added after beta feedback demonstrates a need. The site should
remain static and small unless an actual requirement cannot be met that way.
