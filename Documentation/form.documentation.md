# ChurchManager JSON Form Definition Reference

## Overview

ChurchManager screens are defined in JSON files stored in the `Forms` directory. Each file is a blueprint that tells the JSForm framework how to:

- create and size a window;
- place fields, labels, buttons, lists, and other controls;
- retrieve and update records in the ChurchDB database;
- provide record navigation and validation; and
- display embedded subforms or open related forms.

This approach allows most ChurchManager screens to be created or changed by editing a JSON definition instead of writing a separate Python class for every screen.

The original `form.documentation.txt` file is a descriptive schema. It resembles JSON, but it is not valid JSON: expressions such as `(string)` identify an expected data type, and explanatory comments describe the properties.

## Basic form structure

A form definition contains a named form with two principal sections:

```json
{
    "frmExampleFORM": {
        "FORM": {
            "name": "frmExample",
            "type": "Panel",
            "title": "Example"
        },
        "CONTROLS": {
        }
    }
}
```

- `FORM` describes the window, its database source, and its relationships to other forms.
- `CONTROLS` describes the visible components inside the window.

## The `FORM` section

### Identity and form type

| Property | Type | Description |
| --- | --- | --- |
| `name` | String | Internal name of the form. |
| `type` | String | Kind of form to create. |
| `title` | String | Text displayed in the title bar. |

Supported form types are:

- `Panel`: a normal application screen.
- `Dialog`: a modal linked form. The user handles or closes it before returning to the parent form.
- `StaticBox`: an embedded, bordered subform placed within a parent form.

### Responsive layout, position, and size

New and migrated forms should use JSForm's responsive layout mode:

```json
"layout": {
    "type": "responsive",
    "border": 2,
    "gap": 2
}
```

In responsive mode, `posch` supplies logical row and column ordering only.
JSForm uses a wxPython sizer to calculate the actual pixel positions. Fields
widen with the window, multiline fields and lists can grow vertically, the
navigation controls occupy a final row, and forms become scrollable when their
minimum contents exceed the available screen area. The initial window is also
limited to 95 percent of the active display.

JSForm also enables responsive layout automatically when a form has one unique
logical position per control and does not contain a `StaticBox` grouping. A form
can force either behavior with `layout.type = "responsive"` or
`layout.type = "legacy"`. The compatibility mode allows complex forms to be
migrated and visually checked in manageable groups.

JSForm preserves `StaticBox` sections by placing their contained controls in
nested sizers. The unfinished financial forms, including the legacy
`frmCheckRegister` layout, were removed from ChurchManager in August 2026.

| Property | Format | Description |
| --- | --- | --- |
| `pos` | `[x, y]` | Position in pixels. Overrides `posch`. |
| `size` | `[width, height]` | Size in pixels. Overrides `sizech`. |
| `posch` | `[x, y]` | Position in character-based units. |
| `sizech` | `[width, height]` | Size in character-based units. |

For responsive forms, use `posch` instead of `pos`. Pixel values should now be
reserved for legacy forms or exceptional controls where exact placement is
genuinely required.

An individual control can refine its responsive behavior with:

```json
"layout": {
    "row": 2,
    "column": 1,
    "row_span": 1,
    "column_span": 2,
    "expand": true,
    "proportion": 1
}
```

These properties are optional. Without them, JSForm derives the grid from the
existing `posch` values and selects sensible growth behavior from the control
type.

Responsive layouts use compact defaults of two pixels between grid cells and
one pixel of per-control padding. Increase these values only for a form that
needs deliberate visual separation; large values accumulate across every row
and column. JSForm calculates control minimum sizes from the configured font.
Calling a form's `refresh_layout()` method reapplies the current font and
recalculates an already-open responsive form.

### Database table definition

The optional `table` object describes the records displayed or edited by the form:

```json
"table": {
    "name": "tblPerson",
    "fields": ["ID", "FirstName", "LastName"],
    "condition": "ID = {id}",
    "orderby": "LastName, FirstName"
}
```

| Property | Type | Description |
| --- | --- | --- |
| `name` | String | SQL table or view name. |
| `fields` | List of strings | Columns retrieved for the form. |
| `condition` | String | Optional SQL `WHERE` expression. Placeholders such as `{id}` are filled by the application. |
| `orderby` | String | Optional SQL `ORDER BY` expression. |

Control names commonly match names in `fields`. This lets JSForm move values between the current database record and the corresponding screen controls.

### Standard form controls

The `controls` list requests controls supplied automatically by JSForm:

```json
"controls": ["Close", "Navigation"]
```

- `Close` adds a form-closing button.
- `Navigation` adds New, Update, First, Previous, Next, and Last controls.

### Form styles

The `stylelist` property changes the appearance or behavior of the form:

| Style | Effect |
| --- | --- |
| `CAPTION` | Displays a title-bar caption. Required by several other frame styles. |
| `MINIMIZEBOX` | Displays a minimize button. |
| `MAXIMIZEBOX` | Displays a maximize button. |
| `CLOSEBOX` | Displays a close button. |
| `READONLY` | Prevents editing on the form. |

Example:

```json
"stylelist": ["CAPTION", "CLOSEBOX", "READONLY"]
```

## Subforms and linked forms

### Subforms

A subform is displayed inside its parent form and is data-linked to the parent's current record. For example, a family form could contain a subform showing the people belonging to the selected family.

The subform uses the same general form properties described above. Its `StaticBox` form type provides a visual border when appropriate.

### Linked forms

A linked form opens separately while remaining data-linked to its parent. The `bindbtn` property names the parent control that opens it:

```json
"linkedforms": {
    "frmPersonAddressFORM": {
        "FORM": {
            "name": "frmPersonAddress",
            "type": "Dialog",
            "bindbtn": "btnOpenAddress"
        }
    }
}
```

The named button must exist in the parent's `CONTROLS` section.

## The `CONTROLS` section

Each member of `CONTROLS` defines an item displayed inside the form:

```json
"CONTROLS": {
    "FirstName": {
        "name": "FirstName",
        "type": "TextCtrl",
        "posch": [2, 3],
        "sizech": [20, 1],
        "required": true
    }
}
```

The object key and `name` normally use the same value. When the control represents database data, that value generally matches a field in the form's table definition.

### Common control properties

Most control types support the following properties:

| Property | Type | Description |
| --- | --- | --- |
| `name` | String | Internal control name. |
| `type` | String | Type of wxPython or custom JSForm control. |
| `pos` | `[x, y]` | Position in pixels; overrides `posch`. |
| `size` | `[width, height]` | Size in pixels; overrides `sizech`. |
| `posch` | `[x, y]` | Position in character-based units. |
| `sizech` | `[width, height]` | Size in character-based units. |
| `stylelist` | List of strings | Control-specific appearance and behavior options. |
| `validatorstr` | String | Validator used to check entered data. |
| `required` | Boolean | When `true`, a value must be entered. The default is `false`. |

Common text-control styles include:

| Style | Effect |
| --- | --- |
| `MULTILINE` | Accepts multiple lines of text. |
| `DONTWRAP` | Does not wrap long lines. Used with `MULTILINE`. |
| `WORDWRAP` | Wraps text at the control margin. Used with `MULTILINE`. |
| `PROCESSENTER` | Processes Enter as part of control input. |
| `PROCESSTAB` | Processes Tab as part of control input. |
| `READONLY` | Displays the value without permitting edits. |

`navButton` is reserved for internal framework use.

## Control types

### `StaticBox`

Draws a labeled border around a related group of controls.

Additional property:

- `label`: text displayed on the border.

### `StaticText`

Displays fixed text, such as a field label or instruction.

Additional property:

- `value`: initial displayed text. Some existing forms use `label` for visible static text.

### `TextCtrl`

Provides an ordinary text-entry field.

Additional properties:

- `value`: initial value.
- `lookupchoices`: optional database query used to provide possible values.

A lookup is defined as follows:

```json
"lookupchoices": {
    "name": "tblStates",
    "fields": ["Abbreviation", "StateName"],
    "condition": "Active = 1",
    "orderby": "StateName"
}
```

### `MultiMine`

`MultiMine` is a custom control for handling several lines or selected values within one database field. It follows the general `TextCtrl` definition.

The documented storage format resembles:

```text
[data1\rdata2\rdata3]
```

This is an application-specific serialized format rather than separate relational database records.

### `ComboBox`

Displays a drop-down selection. Choices can be written directly in the form:

```json
"choices": ["Member", "Guest", "Other"]
```

Alternatively, `lookupchoices` can retrieve them from a database table.

Additional property:

- `refreshform`: when `true`, refreshes the form after the selected value changes. The default is `false`.

### `CheckBox`

Displays a Boolean or yes/no selection.

Additional property:

- `value`: initial state or value.

### `CheckListBox`

Displays a list in which multiple items can be selected.

Additional properties:

- `label`: visible label.
- `choices`: list of displayed choices.

### `Button`

Creates an action button.

Additional properties:

| Property | Description |
| --- | --- |
| `id` | Optional wxPython control identifier. The default is `wx.ID_ANY`. |
| `label` | Text displayed on the button. |
| `open` | Opens the file selected by the named `FilePickerCtrl`. This may represent an older form-definition convention; newer definitions may use `bindbtn`. |

Button size is optional.

### `DataViewListCtrl`

Displays multiple database records in a grid or list. Its documented general properties are limited to position, size, and style, together with its table and column definitions.

```json
"Results": {
    "name": "Results",
    "type": "DataViewListCtrl",
    "posch": [2, 5],
    "sizech": [45, 15],
    "table": {
        "name": "tblPerson",
        "fields": ["ID", "LastName", "FirstName"],
        "orderby": "LastName, FirstName"
    },
    "column": [
        {
            "name": "LastName",
            "label": "Last Name",
            "width": 150
        },
        {
            "name": "FirstName",
            "label": "First Name",
            "width": 150
        }
    ]
}
```

Each column contains:

- `name`: a field included in `table.fields`;
- `label`: the displayed column heading; and
- `width`: displayed width in pixels.

### Date and time controls

| Type | Purpose | Initial-value property |
| --- | --- | --- |
| `DateTime` | Combined date and time value. | `dt` |
| `DatePickerCtrl` | Date selection. | `dt` |
| `TimePickerCtrl` | Time selection. | `dt` |
| `CalendarCtrl` | Visual calendar selection. | `date` |

Each may also specify an optional wxPython `id`. The default is `wx.ID_ANY`.

### `FilePickerCtrl`

Allows the user to select a file.

| Property | Description |
| --- | --- |
| `id` | Optional wxPython control identifier. |
| `path` | Initial file path. |
| `message` | Message displayed in the file chooser. |
| `wildcard` | File-type filter supported by wxPython. |

## Form processing lifecycle

When ChurchManager opens a JSON-defined form, JSForm generally performs the following work:

1. Reads the form's `FORM` definition.
2. Creates the requested panel, dialog, or subform.
3. Connects the form to its specified database table or view.
4. Retrieves the requested fields using the condition and sort order.
5. Creates each item in the `CONTROLS` section.
6. Associates named controls with matching database fields.
7. Loads the current record into those controls.
8. Adds requested navigation and close controls.
9. Connects buttons to linked forms or custom Python actions.
10. Validates required fields and writes approved changes to the database.

## Complete simplified example

```json
{
    "frmPersonFORM": {
        "FORM": {
            "name": "frmPerson",
            "type": "Panel",
            "title": "Person",
            "sizech": [45, 20],
            "controls": ["Close", "Navigation"],
            "stylelist": ["CAPTION", "CLOSEBOX"],
            "table": {
                "name": "tblPerson",
                "fields": ["ID", "FirstName", "LastName"],
                "orderby": "LastName, FirstName"
            }
        },
        "CONTROLS": {
            "lblFirstName": {
                "name": "lblFirstName",
                "type": "StaticText",
                "posch": [2, 2],
                "label": "First name"
            },
            "FirstName": {
                "name": "FirstName",
                "type": "TextCtrl",
                "posch": [15, 2],
                "sizech": [20, 1],
                "required": true
            },
            "lblLastName": {
                "name": "lblLastName",
                "type": "StaticText",
                "posch": [2, 4],
                "label": "Last name"
            },
            "LastName": {
                "name": "LastName",
                "type": "TextCtrl",
                "posch": [15, 4],
                "sizech": [20, 1],
                "required": true
            }
        }
    }
}
```

In this example, JSForm creates a Person screen, retrieves records from `tblPerson`, connects the `FirstName` and `LastName` controls to matching database columns, requires both values, and supplies standard record navigation and closing controls.

## Maintenance notes

- SQL conditions and sort expressions are inserted into generated queries, so form authors should use valid SQL and trusted values.
- A control representing a database column should normally have the same name as that column.
- Fields used by a control or displayed list column should be included in the appropriate `table.fields` list.
- Use `posch` and `sizech` for font-aware layouts; use pixel values only when exact dimensions are necessary.
- The original reference contains spelling errors and a few signs of older conventions. Existing form files and the current JSForm implementation remain the authoritative source when behavior differs from this guide.
