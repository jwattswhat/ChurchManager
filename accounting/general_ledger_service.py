"""Read-only general-ledger detail from permanently posted entries."""

from decimal import Decimal


def normal_balance(raw_balance, normal):
    value = Decimal(raw_balance)
    return value if normal == "DEBIT" else -value


class GeneralLedgerService:
    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def organizations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID,LegalName FROM tblAccountingOrganization "
                                  "WHERE Active=1 ORDER BY LegalName")
            return cursor.fetchall()
        finally:
            cursor.close()

    def choices(self, organization_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID,CONCAT(Code,' - ',Name) "
                                  "FROM tblAccountingAccount WHERE OrganizationID=? "
                                  "AND PostingAllowed=1 ORDER BY Code", (organization_id,))
            accounts = cursor.fetchall()
            self._execute(cursor, "SELECT ID,CONCAT(Code,' - ',Name) "
                                  "FROM tblAccountingFund WHERE OrganizationID=? "
                                  "ORDER BY Code", (organization_id,))
            return accounts, cursor.fetchall()
        finally:
            cursor.close()

    def report(self, organization_id, account_id, date_from, date_to, fund_id=None):
        if date_to < date_from:
            raise ValueError("The Through date cannot be before the From date.")
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT Code,Name,NormalBalance FROM tblAccountingAccount "
                "WHERE ID=? AND OrganizationID=?", (account_id, organization_id))
            account = cursor.fetchone()
            if account is None:
                raise ValueError("Select an account belonging to this organization.")
            fund_clause = " AND l.FundID=?" if fund_id is not None else ""
            opening_values = [organization_id, account_id, date_from]
            if fund_id is not None:
                opening_values.append(fund_id)
            self._execute(cursor,
                "SELECT COALESCE(SUM(l.Debit-l.Credit),0) "
                "FROM tblAccountingTransactionLine l "
                "JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "WHERE t.OrganizationID=? AND l.AccountID=? "
                "AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate<?" +
                fund_clause, tuple(opening_values))
            raw = Decimal(cursor.fetchone()[0])
            opening_raw = raw
            detail_values = [organization_id, account_id, date_from, date_to]
            if fund_id is not None:
                detail_values.append(fund_id)
            self._execute(cursor,
                "SELECT t.TransactionDate,t.TransactionNumber,t.TransactionType,"
                "t.Description,t.Reference,CONCAT(f.Code,' - ',f.Name),"
                "l.Description,l.Debit,l.Credit "
                "FROM tblAccountingTransactionLine l "
                "JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "JOIN tblAccountingFund f ON f.ID=l.FundID "
                "WHERE t.OrganizationID=? AND l.AccountID=? "
                "AND t.Status IN ('POSTED','REVERSED') "
                "AND t.TransactionDate BETWEEN ? AND ?" + fund_clause +
                " ORDER BY t.TransactionDate,t.TransactionNumber,l.LineNumber",
                tuple(detail_values))
            detail = []
            for row in cursor.fetchall():
                raw += Decimal(row[7]) - Decimal(row[8])
                detail.append((*row, normal_balance(raw, account[2])))
            return {
                "account": "{} - {}".format(account[0], account[1]),
                "normal_balance": account[2],
                "opening_balance": normal_balance(opening_raw, account[2]),
                "rows": detail,
            }
        finally:
            cursor.close()
