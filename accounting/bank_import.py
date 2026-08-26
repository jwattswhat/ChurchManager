"""Pure parsing and fingerprinting for non-posting bank import staging."""
from __future__ import annotations
import csv,hashlib,io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal,InvalidOperation

class BankImportError(ValueError):pass
@dataclass(frozen=True)
class CsvMapping:
    date_column:str; description_column:str; date_format:str="%m/%d/%Y"
    amount_column:str|None=None; debit_column:str|None=None; credit_column:str|None=None
    reference_column:str|None=None; external_id_column:str|None=None
@dataclass(frozen=True)
class BankRow:
    row_number:int; transaction_date:object; description:str; reference:str
    amount:Decimal; external_id:str; fingerprint:str

def file_hash(content:bytes)->str:return hashlib.sha256(content).hexdigest()


def csv_headers(content: bytes):
    """Return CSV column headings using the same supported encodings as parsing."""
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = content.decode("cp1252")
        except UnicodeDecodeError as error:
            raise BankImportError("The CSV text encoding is not supported.") from error
    reader = csv.reader(io.StringIO(text))
    try:
        headings = next(reader)
    except StopIteration as error:
        raise BankImportError("The CSV file has no header row.") from error
    headings = tuple(value.strip() for value in headings)
    if not headings or any(not value for value in headings):
        raise BankImportError("Every CSV column must have a heading.")
    if len(set(headings)) != len(headings):
        raise BankImportError("CSV column headings must be unique.")
    return headings
def _amount(row,mapping):
    def number(text):
        clean=(text or "").strip().replace(",","").replace("$","")
        if clean.startswith("(") and clean.endswith(")"):clean="-"+clean[1:-1]
        return Decimal(clean or "0")
    try:
        if mapping.amount_column:return number(row.get(mapping.amount_column))
        if not mapping.debit_column or not mapping.credit_column:raise BankImportError("Map either one amount column or both debit and credit columns.")
        return number(row.get(mapping.credit_column))-number(row.get(mapping.debit_column))
    except InvalidOperation as error:raise BankImportError("A bank amount is not a valid number.") from error
def parse_csv(content:bytes,mapping:CsvMapping):
    try:text=content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:text=content.decode("cp1252")
        except UnicodeDecodeError as error:raise BankImportError("The CSV text encoding is not supported.") from error
    reader=csv.DictReader(io.StringIO(text));rows=[]
    if not reader.fieldnames:raise BankImportError("The CSV file has no header row.")
    required={mapping.date_column,mapping.description_column}
    required.add(mapping.amount_column) if mapping.amount_column else required.update((mapping.debit_column,mapping.credit_column))
    missing=[name for name in required if not name or name not in reader.fieldnames]
    if missing:raise BankImportError("CSV columns are missing: {}.".format(", ".join(sorted(str(v) for v in missing))))
    for number,row in enumerate(reader,2):
        try:transaction_date=datetime.strptime(row[mapping.date_column].strip(),mapping.date_format).date()
        except (ValueError,AttributeError) as error:raise BankImportError("Row {} has an invalid date.".format(number)) from error
        description=(row.get(mapping.description_column) or "").strip()
        if not description:raise BankImportError("Row {} has no description.".format(number))
        amount=_amount(row,mapping).quantize(Decimal("0.01"))
        reference=(row.get(mapping.reference_column) or "").strip() if mapping.reference_column else ""
        external=(row.get(mapping.external_id_column) or "").strip() if mapping.external_id_column else ""
        key="|".join((transaction_date.isoformat(),str(amount),description.casefold(),reference.casefold(),external))
        rows.append(BankRow(number,transaction_date,description,reference,amount,external,hashlib.sha256(key.encode()).hexdigest()))
    if not rows:raise BankImportError("The CSV file contains no transaction rows.")
    return tuple(rows)
