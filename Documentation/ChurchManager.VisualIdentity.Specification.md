# ChurchManager visual identity specification

Status: Approved
Approved by: Rev. Jonathan C. Watt
Prepared: August 18, 2026

## Identity idea

ChurchManager's visual identity combines two ideas already present in the
application icon:

- a simple church building represents congregation and ministry;
- three orderly lines represent records, planning, reports, and accounting.

The identity should feel trustworthy, practical, calm, and welcoming. It should
not resemble a commercial financial product, a denominational seal, or the logo
of a particular congregation.

## Positioning line

The approved public positioning line is:

> Local-first church administration for Windows

Use it with the horizontal logo, repository introduction, website metadata,
release pages, and directory listings when space permits. `Local-first` means
that ChurchManager is installed and operated under the congregation's control;
it does not imply that backups, database administration, or appropriate network
security are optional. The shorter phrase `Church administration for Windows`
may be used where space is constrained.

## Primary mark

The primary mark is a white church above three gold record lines inside a deep
blue rounded square with a gold border. It is a simplified, vector-ready
refinement of the existing ChurchManager icon rather than a different symbol.

The three lines are intentionally broad enough to remain visible at small
sizes. The church has no congregation-specific text, date, initials, or
denominational symbol beyond the broadly recognizable cross and church form.

## Logo forms

The maintained identity family contains:

1. **Application mark** — square symbol for the application, installer,
   shortcut, favicon, profile image, and small placements.
2. **Horizontal logo** — mark plus `ChurchManager` for the website, README,
   documentation covers, installer welcome screen, and release pages.
3. **One-color mark** — solid version for monochrome printing, engraving,
   stamps, or contexts where blue and gold are unavailable.
4. **Text wordmark** — `ChurchManager` set in a clear, sturdy system sans serif
   when the symbol is unnecessary.

These forms must not be redrawn separately for each use. Approved source assets
are the authority, with exported PNG and ICO sizes derived from them.

## Color palette

| Name | Value | Primary use |
|---|---|---|
| ChurchManager Navy | `#0B315B` | mark background, headings, primary actions |
| ChurchManager Gold | `#F2B632` | mark border, record lines, restrained highlights |
| Ministry Blue | `#1F6F9F` | links, secondary accents, selected states |
| Quiet Blue | `#EAF3F8` | pale section and information backgrounds |
| Ink | `#17232C` | body text |
| White | `#FFFFFF` | church symbol, reversed text, open space |

Navy and white carry most of the identity. Gold is an accent, not a large page
background. Red remains reserved for errors, warnings, and required attention.

## Typography

Use `Segoe UI` on Windows and a normal system sans-serif fallback elsewhere.
The wordmark uses a semibold or bold weight. Public documents and the website
do not require a downloaded commercial font.

## Clear space and minimum size

- Keep clear space around the mark equal to at least one quarter of its width.
- Do not place text, borders, or other logos inside that space.
- Do not use the detailed primary mark below 24 pixels wide.
- At 16 pixels, use a separately checked small-size export from the approved
  vector source rather than allowing an application to improvise scaling.
- Keep the horizontal logo at least 150 pixels wide on screen.

## Approved backgrounds

- Use the standard mark on white, Quiet Blue, or another very pale neutral.
- Use the reversed horizontal logo on ChurchManager Navy or a sufficiently dark
  photograph only when contrast has been checked.
- Use the one-color mark in navy or black for monochrome output.

## Do not

- substitute a congregation logo or test-system logo;
- add a denominational seal, cross style, publication artwork, or church name;
- stretch, skew, rotate, outline, emboss, or add a drop shadow;
- change the church and record-line relationship;
- recolor the mark with liturgical colors;
- put the logo on a busy photograph without a quiet background area;
- use generated approximations when an approved asset exists.

## Maintained assets

Draft vector assets are stored in `assets/brand/`:

- `ChurchManager-mark.svg`
- `ChurchManager-logo-horizontal.svg`
- `ChurchManager-mark-monochrome.svg`

The approved identity is applied to `cm.ico`, the maintained application PNG,
and the public website. Raster and Windows icon exports are generated from the
same approved geometry by `tools/build_brand_assets.py`.

## Maintained export set

- Windows ICO containing 16, 24, 32, 48, 64, 128, and 256 pixel sizes;
- transparent PNG mark at 32, 64, 128, 256, 512, and 1024 pixels;
- horizontal transparent PNG at 600 and 1200 pixels wide;
- favicon PNG and ICO;
- social-preview image for public release pages;
- SVG originals retained as the authoritative web and print sources.

Each export must be visually checked before release when its geometry or colors
change.
