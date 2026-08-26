# ChurchManager simple asset management specification

**Status:** Approved

**Version:** 1.0

**Date:** August 25, 2026

**Approved by:** Rev. Jonathan C. Watt

**Target application:** ChurchManager

**Application framework:** JSForm

**Database:** MariaDB/MySQL

## 1. Purpose

ChurchManager will provide a small, understandable register of property owned
or managed by a congregation. It will answer five practical questions:

1. What do we own?
2. Where is it?
3. Who is responsible for it?
4. Does it need maintenance or replacement?
5. What happened to it over time?

The subsystem is intended for congregations that need more than a spreadsheet
but do not need a full inventory, facilities, or enterprise asset-management
system.

## 2. First-release scope

Version 1 includes:

- an asset register for equipment, furniture, technology, vehicles, musical
  instruments, appliances, and significant property items;
- congregation-defined asset categories and conditions;
- reusable buildings, rooms, storage areas, and other asset locations;
- an optional responsible Person or Group;
- identifying information such as manufacturer, model, and serial number;
- purchase, donation, warranty, expected-replacement, and retirement details;
- maintenance, inspection, repair, transfer, and disposal history;
- maintenance-due and replacement-review dates;
- links to existing ChurchManager Document records when supporting material is
  available;
- simple search, filtering, reports, permissions, auditing, backup, restore,
  import, and export; and
- preservation of history when an asset is retired or disposed.

Version 1 excludes:

- depreciation, capitalization, journal entries, or tax accounting;
- purchase orders, invoices, vendors, bids, or approval workflows;
- consumable supplies, pantry stock, office supplies, or quantity-on-hand
  inventory;
- barcode scanners, RFID, GPS, or automatic discovery of equipment;
- reservations, room booking, vehicle scheduling, or lending/check-out;
- insurance claims or a complete insurance-policy system;
- building work orders or a facilities help desk;
- automatic email, text, or calendar reminders; and
- storage of passwords, alarm codes, door codes, keys, or other access secrets.

## 3. Design principles

1. **Keep one practical record.** A normal user should be able to create an
   asset without understanding accounting or inventory terminology.
2. **Use a stable asset number.** The database ID is internal. Each asset also
   receives a unique, readable number within its congregation, such as
   `AST-0001`.
3. **Preserve history.** Moving, repairing, retiring, or disposing of an asset
   creates history; it does not erase the asset.
4. **Allow grouped property.** One record may represent a reasonable group of
   identical low-risk items, such as 25 folding tables. Individually serialized
   or valuable items receive separate records.
5. **Do not duplicate accounting.** Purchase cost is optional reference
   information only and never posts to the general ledger.
6. **Do not duplicate documents.** Manuals, receipts, photographs, and warranty
   records use the existing Document subsystem and are linked to an asset.
7. **Use controlled choices.** Category, condition, activity type, acquisition
   method, and status use maintained choice lists.
8. **Respect congregation boundaries.** An asset, its location, responsible
   party, Documents, and history must belong to the same Church record.

## 4. Data model

### 4.1 `tblAssetLocation`

Stores reusable physical locations.

| Field | Purpose |
| --- | --- |
| `ID` | Internal positive primary key. |
| `ChurchID` | Required owning congregation. |
| `LocationName` | Required name, such as Sanctuary, Office, or Storage Room. |
| `ParentLocationID` | Optional containing location, such as a room in a building. |
| `Address` | Optional address when different from the Church address. |
| `IsActive` | False prevents new assignments while preserving history. |
| `Note` | Ordinary nonconfidential administrative note. |

`LocationName` is unique among active locations within the same Church and
parent location. Circular parent relationships are rejected.

### 4.2 `tblAsset`

Stores the current identity and state of each asset.

| Field | Purpose |
| --- | --- |
| `ID` | Internal positive primary key. |
| `ChurchID` | Required owning congregation. |
| `AssetNumber` | Required readable identifier, unique within the Church. |
| `AssetName` | Required plain-language name. |
| `Category` | Required controlled choice. |
| `Description` | Optional short description. |
| `Quantity` | Positive whole number; defaults to 1. |
| `Manufacturer` | Optional manufacturer. |
| `Model` | Optional model. |
| `SerialNumber` | Optional serial, VIN, or other identifying number. |
| `LocationID` | Optional current active location. |
| `ResponsiblePersonID` | Optional responsible Person. |
| `ResponsibleGroupID` | Optional responsible Group. |
| `AcquisitionMethod` | Controlled choice: Purchased, Donated, Transferred, or Other. |
| `AcquisitionDate` | Optional date acquired. |
| `ReferenceValue` | Optional historical purchase or donor-supplied reference value. |
| `Condition` | Controlled choice such as Excellent, Good, Fair, Poor, or Unknown. |
| `Status` | Active, In Storage, Loaned, Under Repair, Retired, Lost, or Disposed. |
| `WarrantyExpires` | Optional date. |
| `NextMaintenanceDate` | Optional next action date. |
| `ReplacementReviewDate` | Optional date to reconsider repair or replacement. |
| `RetiredDate` | Required when status becomes Retired, Lost, or Disposed. |
| `Note` | Ordinary nonconfidential administrative note. |

At most one responsible Person and one responsible Group may be recorded. Both
may be blank; if both are present, the Group has organizational responsibility
and the Person is the current contact.

### 4.3 `tblAssetActivity`

Stores dated asset history.

| Field | Purpose |
| --- | --- |
| `ID` | Internal positive primary key. |
| `AssetID` | Required asset. |
| `ActivityDate` | Required date. |
| `ActivityType` | Maintenance, Inspection, Repair, Transfer, Condition Review, Retirement, Disposal, Loss, or Note. |
| `Summary` | Required concise description. |
| `Cost` | Optional reference cost; no accounting entry is created. |
| `LocationID` | Optional resulting location for a transfer. |
| `NextActionDate` | Optional next maintenance or review date. |
| `DocumentID` | Optional link to an existing supporting Document. |
| `RecordedByUserID` | User who recorded the activity. |
| `CreatedAt` | Creation timestamp. |

Saving an activity with a resulting location or next-action date updates the
current Asset record in the same transaction. Existing activities are not
silently edited after they have become part of the asset history; corrections
are recorded as another activity.

## 5. User interface

### 5.1 Main-menu box

Add an **Assets** box containing:

- Assets
- Asset Locations
- Maintenance Due
- Asset Reports

The box is added only when the subsystem is implemented and the user has at
least one related permission.

### 5.2 Asset register

The main screen is a sortable grid with these default columns:

- Asset number
- Asset
- Category
- Location
- Responsible contact
- Condition
- Status
- Next maintenance

Filters are limited to Church, category, location, status, and a text search.
Double-click opens the selected asset. A clear **New Asset** button creates a
blank record.

### 5.3 Asset editor

The editor uses three visually simple areas:

1. **Identity** — number, name, category, description, and quantity;
2. **Current information** — location, responsibility, condition, status, and
   important dates; and
3. **History** — activity grid with Add Activity and Open Activity.

Manufacturer, model, serial number, acquisition information, and notes remain
available without dominating the screen. Retiring or disposing of an asset
requires confirmation, a date, and a history summary.

### 5.4 Maintenance due

This is a read-only work list of active assets whose `NextMaintenanceDate` or
`ReplacementReviewDate` is due within a user-selected number of days. It is not
a strict close checklist. Opening an item goes directly to the asset history so
the user may record what was done, reschedule it, or explain that no action was
needed.

## 6. Reports

Reports use the approved subsystem-first title and `CMss99` naming convention.
The Asset Management subsystem abbreviation is `AM`.

| Code | Title | Purpose |
| --- | --- | --- |
| `CMAM01` | Asset Management - Asset Register | Current assets, location, responsibility, condition, and status. |
| `CMAM02` | Asset Management - Maintenance Due | Due and upcoming maintenance and replacement reviews. |
| `CMAM03` | Asset Management - Asset History | Selected asset identity and dated activity history. |

Reports never expose unrelated Person contact details, confidential pastoral
information, application credentials, or access-security information.

## 7. Permissions and audit

Use these permissions:

- `assets.view` — view assets, locations, history, and reports;
- `assets.manage` — create and update assets, locations, and activities; and
- `assets.retire` — retire, mark lost, or dispose of an asset.

Creating an asset, changing its identifying number, transferring it, changing
responsibility, recording an activity, retiring it, or restoring it to active
status is audited. Audit details contain IDs and ordinary administrative
values, but not linked Document content.

## 8. Validation and lifecycle rules

- Asset numbers are trimmed, case-insensitively unique within one Church, and
  leading zeros are preserved because the number is an identifier, not a
  quantity.
- Quantity, reference value, and activity cost cannot be negative.
- A retired, lost, or disposed asset cannot receive ordinary maintenance or
  transfer activity until explicitly restored to an active status.
- A location cannot be deleted while referenced; it may be made inactive.
- A Person or Group link may be cleared without deleting asset history.
- Deleting an asset is not available after history exists. Test-only cleanup
  remains outside the normal user interface.
- Changes spanning the asset and its history use one database transaction.

## 9. Import, export, backup, and recovery

A reviewed CSV import may create Assets and match locations by exact normalized
name. It does not import activity history, Documents, or secret information.
Preview identifies duplicates by asset number and warns about repeated serial
numbers.

CSV export contains the current asset register. The normal ChurchManager SQL
backup and restore include all asset tables and links. Restore does not require
a separate asset recovery process.

## 10. Acceptance criteria

Version 1 is complete when:

1. a user can create, find, update, transfer, maintain, and retire an asset;
2. locations and responsibilities are validated within the selected Church;
3. activity history remains intact after current details change;
4. maintenance and replacement dates appear on a usable due list;
5. the three starter reports render correctly and may be customized;
6. permissions and audit records are enforced in services, not only hidden in
   the interface;
7. CSV preview prevents duplicate asset numbers and exposes no confidential
   information;
8. backup and restore preserve the complete subsystem;
9. automated migration, service, validation, permission, report, import, and
   recovery tests pass; and
10. the screens and reports receive explicit visual approval.

## 11. Deferred possibilities

Future projects may add calendar reminders, room or vehicle scheduling,
check-out, insurance schedules, barcode labels, or accounting integration.
Those capabilities are not implied by this specification and require separate
approval before implementation.
