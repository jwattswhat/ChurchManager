"""Secure Member Directory dataset for the visual report system."""

from JSForm.report_dataset import (
    ReportCollection, ReportDataset, ReportDatasetContract, ReportField,
)


def field(name, label, data_type="text", sensitivity="ordinary"):
    return ReportField(name, label, data_type, sensitivity)


def contact_line(contact):
    label = contact.get("ContactLabel") or contact.get("Type") or "Contact"
    value = contact.get("Contact") or ""
    return f"{value} ({label})"


DIRECTORY_CONTRACT = ReportDatasetContract(
    name="membership.directory",
    version=1,
    required_permission="reports.membership.contact",
    collections=(
        ReportCollection("church", "Church", (
            field("ID", "Church ID", "integer"), field("Church", "Church Name"),
            field("Address", "Address", sensitivity="contact"),
            field("Address2", "Address 2", sensitivity="contact"),
            field("City", "City", sensitivity="contact"),
            field("State", "State", sensitivity="contact"),
            field("Zip", "ZIP", sensitivity="contact"),
            field("Pastor", "Pastor"), field("Phone", "Phone", "phone", "contact"),
            field("eMail", "Email", "text", "contact"),
            field("Logo", "Church Logo", "image"),
            field("AddressLines", "Church Address", "address", "contact"),
        )),
        ReportCollection("families", "Families", (
            field("ID", "Family ID", "integer"), field("ChurchID", "Church ID", "integer"),
            field("FamilyName", "Family Name"), field("MarriageStatus", "Marriage Status"),
            field("Image", "Family Image", "image"),
        )),
        ReportCollection("family_addresses", "Family Addresses", (
            field("ID", "Address ID", "integer"), field("FamilyID", "Family ID", "integer"),
            field("AddressLabel", "Label"), field("Address", "Address", sensitivity="contact"),
            field("Address2", "Address 2", sensitivity="contact"),
            field("City", "City", sensitivity="contact"), field("State", "State", sensitivity="contact"),
            field("Zip", "ZIP", sensitivity="contact"),
        ), "families", "FamilyID"),
        ReportCollection("family_contacts", "Family Contacts", (
            field("ID", "Contact ID", "integer"), field("FamilyID", "Family ID", "integer"),
            field("ContactLabel", "Label"), field("Type", "Type"),
            field("Contact", "Contact", sensitivity="contact"),
        ), "families", "FamilyID"),
        ReportCollection("people", "People", (
            field("ID", "Person ID", "integer"), field("FamilyID", "Family ID", "integer"),
            field("Title", "Title"), field("FirstName", "First Name"),
            field("MiddleName", "Middle Name"), field("LastName", "Last Name"),
            field("Picture", "Picture", "image"), field("DisplayName", "Display Name"),
            field("Member", "Member", "boolean"),
            field("AssociateMember", "Associate Member", "boolean"),
            field("Status", "Status"), field("MaritalStatus", "Marital Status"),
        ), "families", "FamilyID"),
        ReportCollection("person_addresses", "Personal Addresses", (
            field("ID", "Address ID", "integer"), field("PersonID", "Person ID", "integer"),
            field("AddressLabel", "Label"), field("Address", "Address", sensitivity="contact"),
            field("Address2", "Address 2", sensitivity="contact"),
            field("City", "City", sensitivity="contact"), field("State", "State", sensitivity="contact"),
            field("Zip", "ZIP", sensitivity="contact"),
        ), "people", "PersonID"),
        ReportCollection("person_contacts", "Personal Contacts", (
            field("ID", "Contact ID", "integer"), field("PersonID", "Person ID", "integer"),
            field("ContactLabel", "Label"), field("Type", "Type"),
            field("Contact", "Contact", sensitivity="contact"),
        ), "people", "PersonID"),
        ReportCollection("directory_entries", "Directory Entries", (
            field("FamilyID", "Family ID", "integer"), field("FamilyName", "Family Name"),
            field("MemberNames", "Household Members"),
            field("AddressLines", "Listed Address", "address", "contact"),
            field("ContactLines", "Listed Contacts", "text", "contact"),
            field("FamilyImage", "Family Photograph", "image"),
            field("MarriageStatus", "Marriage Status"),
            field("MemberDetails", "Member Details", "text", "contact"),
            field("FamilyAddressLines", "Family Addresses", "address", "contact"),
            field("FamilyContactLines", "Family Contacts", "text", "contact"),
        )),
        ReportCollection("directory_people", "Directory Households and People", (
            field("FamilyID", "Family ID", "integer"), field("FamilyName", "Family Name"),
            field("FamilyImage", "Family Photograph", "image"),
            field("MarriageStatus", "Marriage Status"),
            field("FamilyAddressLines", "Family Addresses", "address", "contact"),
            field("FamilyContactLines", "Family Contacts", "text", "contact"),
            field("PersonID", "Person ID", "integer"), field("PersonName", "Individual Name"),
            field("Relationship", "Membership Relationship"),
            field("PersonalDetails", "Individual Contact Details", "text", "contact"),
        )),
    ),
)


class DirectoryDatasetProvider:
    def __init__(self, connection, authorization):
        self.connection = connection
        self.authorization = authorization
        self.marker = "%s" if "mysql.connector" in type(connection).__module__ else "?"

    def build(self, church_id):
        self.authorization.require(
            DIRECTORY_CONTRACT.required_permission,
            operation="Create Member Directory dataset",
        )
        queries = {
            "church": (
                "SELECT ID,Church,Address,Address2,City,State,Zip,Pastor,Phone,eMail,Logo "
                f"FROM rpt_church_identity WHERE ID={self.marker}", (church_id,)
            ),
            "families": (
                "SELECT ID,ChurchID,FamilyName,MarriageStatus,Image FROM rpt_directory_family "
                f"WHERE ChurchID={self.marker} ORDER BY FamilyName", (church_id,)
            ),
            "family_addresses": (
                "SELECT a.ID,a.FamilyID,a.AddressLabel,a.Address,a.Address2,a.City,a.State,a.Zip "
                "FROM rpt_family_address a JOIN rpt_directory_family f ON f.ID=a.FamilyID "
                f"WHERE f.ChurchID={self.marker} ORDER BY a.FamilyID,a.ID", (church_id,)
            ),
            "family_contacts": (
                "SELECT c.ID,c.FamilyID,c.ContactLabel,c.Type,c.Contact "
                "FROM rpt_family_contact c JOIN rpt_directory_family f ON f.ID=c.FamilyID "
                f"WHERE f.ChurchID={self.marker} ORDER BY c.FamilyID,c.ID", (church_id,)
            ),
            "people": (
                "SELECT p.ID,p.FamilyID,p.Title,p.FirstName,p.MiddleName,p.LastName,p.Picture,"
                "p.Member,p.AssociateMember,p.Status,p.MaritalStatus "
                "FROM rpt_membership_person p JOIN rpt_directory_family f ON f.ID=p.FamilyID "
                f"WHERE f.ChurchID={self.marker} ORDER BY p.FamilyID,p.FirstName,p.LastName", (church_id,)
            ),
            "person_addresses": (
                "SELECT a.ID,a.PersonID,a.AddressLabel,a.Address,a.Address2,a.City,a.State,a.Zip "
                "FROM rpt_person_address a JOIN rpt_membership_person p ON p.ID=a.PersonID "
                "JOIN rpt_directory_family f ON f.ID=p.FamilyID "
                f"WHERE f.ChurchID={self.marker} ORDER BY a.PersonID,a.ID", (church_id,)
            ),
            "person_contacts": (
                "SELECT c.ID,c.PersonID,c.ContactLabel,c.Type,c.Contact "
                "FROM rpt_person_contact c JOIN rpt_membership_person p ON p.ID=c.PersonID "
                "JOIN rpt_directory_family f ON f.ID=p.FamilyID "
                f"WHERE f.ChurchID={self.marker} ORDER BY c.PersonID,c.ID", (church_id,)
            ),
        }
        cursor = self.connection.cursor()
        try:
            collections = {}
            for name, (sql, values) in queries.items():
                cursor.execute(sql, values)
                columns = tuple(description[0] for description in cursor.description)
                collections[name] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
        church = collections["church"][0] if collections["church"] else None
        if church is not None:
            city_line = ", ".join(part for part in (church.get("City"), church.get("State")) if part)
            if church.get("Zip"):
                city_line = (city_line + " " + str(church["Zip"])).strip()
            church["AddressLines"] = "\n".join(
                str(line) for line in (church.get("Address"), church.get("Address2"), city_line)
                if line
            )
        people = {}
        people_by_id = {}
        for person in collections["people"]:
            parts = [person.get("Title"), person.get("FirstName"), person.get("MiddleName"), person.get("LastName")]
            person["DisplayName"] = " ".join(str(part) for part in parts if part)
            people.setdefault(person["FamilyID"], []).append(person)
            people_by_id[person["ID"]] = person
        addresses = {}
        for address in collections["family_addresses"]:
            city_line = ", ".join(part for part in (address.get("City"), address.get("State")) if part)
            if address.get("Zip"):
                city_line = (city_line + " " + str(address["Zip"])).strip()
            lines = [address.get("Address"), address.get("Address2"), city_line]
            addresses.setdefault(address["FamilyID"], []).append("\n".join(str(line) for line in lines if line))
        contacts = {}
        for contact in collections["family_contacts"]:
            contacts.setdefault(contact["FamilyID"], []).append(contact_line(contact))
        person_addresses = {}
        for address in collections["person_addresses"]:
            city_line = ", ".join(part for part in (address.get("City"), address.get("State")) if part)
            if address.get("Zip"):
                city_line = (city_line + " " + str(address["Zip"])).strip()
            lines = [address.get("Address"), address.get("Address2"), city_line]
            value = ", ".join(str(line) for line in lines if line)
            if value:
                label = address.get("AddressLabel") or "Address"
                person_addresses.setdefault(address["PersonID"], []).append(f"{label}: {value}")
        person_contacts = {}
        for contact in collections["person_contacts"]:
            if contact.get("Contact"):
                person_contacts.setdefault(contact["PersonID"], []).append(
                    contact_line(contact)
                )

        def member_detail(person):
            if person.get("Member"):
                relationship = "Member"
            elif person.get("AssociateMember"):
                relationship = "Associate Member"
            else:
                relationship = "Non-Member"
            lines = [f"{person['DisplayName']} - {relationship}"]
            lines.extend(f"  {value}" for value in person_addresses.get(person["ID"], []))
            lines.extend(f"  {value}" for value in person_contacts.get(person["ID"], []))
            return "\n".join(lines)

        def relationship(person):
            if person.get("Member"):
                return "Member"
            if person.get("AssociateMember"):
                return "Associate Member"
            return "Non-Member"

        collections["directory_entries"] = [{
            "FamilyID": family["ID"], "FamilyName": family.get("FamilyName") or "",
            "MemberNames": ", ".join(
                person["DisplayName"] for person in people.get(family["ID"], [])
            ),
            "AddressLines": "\n".join(addresses.get(family["ID"], [])),
            "ContactLines": "\n".join(contacts.get(family["ID"], [])),
            "FamilyImage": family.get("Image"),
            "MarriageStatus": family.get("MarriageStatus") or "",
            "MemberDetails": "\n".join(
                member_detail(person) for person in people.get(family["ID"], [])
            ),
            "FamilyAddressLines": "\n".join(addresses.get(family["ID"], [])),
            "FamilyContactLines": "\n".join(contacts.get(family["ID"], [])),
        } for family in collections["families"]]
        collections["directory_people"] = []
        for family in collections["families"]:
            family_people = people.get(family["ID"], []) or [None]
            for person in family_people:
                personal_details = []
                if person is not None:
                    personal_details.extend(person_addresses.get(person["ID"], []))
                    personal_details.extend(person_contacts.get(person["ID"], []))
                collections["directory_people"].append({
                    "FamilyID": family["ID"],
                    "FamilyName": family.get("FamilyName") or "",
                    "FamilyImage": family.get("Image"),
                    "MarriageStatus": family.get("MarriageStatus") or "",
                    "FamilyAddressLines": "\n".join(addresses.get(family["ID"], [])),
                    "FamilyContactLines": "\n".join(contacts.get(family["ID"], [])),
                    "PersonID": person.get("ID") if person is not None else 0,
                    "PersonName": person.get("DisplayName") if person is not None else "No individuals listed",
                    "Relationship": relationship(person) if person is not None else "",
                    "PersonalDetails": "\n".join(personal_details),
                })
        return ReportDataset.create(DIRECTORY_CONTRACT, collections)
