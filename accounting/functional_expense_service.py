"""Read-only functional expense report from posted transaction lines."""
from decimal import Decimal


class FunctionalExpenseService:
    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def organizations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID,LegalName FROM tblAccountingOrganization WHERE Active=1 ORDER BY LegalName")
            return cursor.fetchall()
        finally:
            cursor.close()

    def report(self, organization_id, start_date, end_date):
        if start_date > end_date:
            raise ValueError("The report start date cannot be after the end date.")
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT a.Code,a.Name,COALESCE(fn.ID,0),COALESCE(fn.Name,'Unassigned'),"
                "COALESCE(SUM(l.Debit-l.Credit),0) "
                "FROM tblAccountingTransaction t JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "LEFT JOIN tblAccountingFunction fn ON fn.ID=l.FunctionID "
                "WHERE t.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') "
                "AND t.TransactionDate BETWEEN ? AND ? AND a.AccountType='EXPENSE' "
                "GROUP BY a.ID,a.Code,a.Name,fn.ID,fn.Name,a.DisplayOrder,fn.DisplayOrder "
                "ORDER BY a.DisplayOrder,a.Code,COALESCE(fn.DisplayOrder,999999),fn.Name",
                (organization_id, start_date, end_date))
            raw = cursor.fetchall()
            functions = []
            accounts = {}
            for code, name, function_id, function_name, amount in raw:
                function = (function_id, function_name)
                if function not in functions:
                    functions.append(function)
                key = (code, name)
                accounts.setdefault(key, {})[function_id] = Decimal(amount)
            rows = []
            for (code, name), amounts in accounts.items():
                values = [amounts.get(function_id, Decimal("0")) for function_id, _ in functions]
                rows.append((code, name, values, sum(values, Decimal("0"))))
            totals = [sum((row[2][index] for row in rows), Decimal("0")) for index in range(len(functions))]
            return {"functions": functions, "rows": rows, "totals": totals,
                    "grand_total": sum(totals, Decimal("0"))}
        finally:
            cursor.close()
