"""Generate a synthetic edge-case PDF for Member Directory visual QA."""

from pathlib import Path

import JSForm

from visual_reports.directory_dataset import DIRECTORY_CONTRACT


ROOT = Path(__file__).resolve().parent


def edge_case_dataset():
    collections = {collection.name: [] for collection in DIRECTORY_CONTRACT.collections}
    collections["church"] = [{
        "ID": 1,
        "Church": "Reformation Lutheran Church with an Intentionally Long Congregational Name",
        "Address": "123 Reformation Way",
        "Address2": "",
        "City": "Testville",
        "State": "MN",
        "Zip": "55000",
        "Pastor": "Pastor Example",
        "Phone": "2183871200",
        "eMail": "office@example.invalid",
        "Logo": None,
    }]
    rows = []
    for number in range(42):
        if number == 0:
            family = "Alexanderson-Montgomery-Worthington Family with a Very Long Household Name"
            members = ", ".join(
                f"Member {index} Alexanderson-Montgomery-Worthington" for index in range(1, 11)
            )
            address = "9876 An Intentionally Long Street Name for Wrapping Tests\nApartment 12345\nTestville, Minnesota 55000-1234"
            contacts = "Home: (218) 555-0100\nEmail: extraordinarily.long.directory.address@example.invalid"
        elif number == 1:
            family = "Empty-Details Household"
            members = address = contacts = ""
        else:
            family = f"Fictional Family {number:02d}"
            members = f"Adult {number}, Child {number}"
            address = f"{100 + number} Test Street\nTestville, MN 55000"
            contacts = f"Home: (218) 555-{number:04d}"
        rows.append({
            "FamilyID": number + 1,
            "FamilyName": family,
            "MemberNames": members,
            "AddressLines": address,
            "ContactLines": contacts,
        })
    collections["directory_entries"] = rows
    return JSForm.ReportDataset.create(DIRECTORY_CONTRACT, collections)


def main():
    definition = JSForm.ReportDefinitionLoader().load(
        ROOT / "visual_reports" / "definitions" / "CMMD01.json"
    )
    output = ROOT / "Reports" / "CMMD01.edge-case-proof.pdf"
    JSForm.PDFReportRenderer().render(definition, edge_case_dataset(), output)
    print(output)


if __name__ == "__main__":
    main()
