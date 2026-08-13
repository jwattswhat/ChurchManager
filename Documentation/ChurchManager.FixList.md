# ChurchManager fix list

## Deferred user-interface work

- Redesign the Propers form. Its current layout is visually awkward and needs a deliberate usability and spacing pass rather than isolated coordinate tweaks.
- Correct the Worship Service form's usable width. Characters at the right edge are clipped, apparently because the specified form width does not reserve space for the vertical scrollbar. Determine whether the general fix belongs in JSForm's layout sizing before applying a form-specific adjustment.
- Develop a visual screen designer for JSForm/ChurchManager forms. It should use the same JSON format as existing JSForm screens and provide user-friendly visual layout, control placement, property editing, validation, and preview capabilities. This is a future project; no implementation has begun.

## Deferred installation and starter-data work

- During a new ChurchManager installation, ask which hymnals and lectionary systems the congregation wants installed. Permit multiple selections and an explicit "none" choice for each catalog. Install only the selected starter datasets, then let setup choose the church's primary hymnal and default lectionary independently. The installer must remain denomination-neutral: LSB and its lectionaries are optional packages, not hard-coded requirements.
