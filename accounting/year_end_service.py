"""Read-only validation and fund summary for a fiscal year close."""
import json
from decimal import Decimal


class YearEndService:
    def __init__(self, connection, acting_user_id=None):
        self.connection = connection
        self.acting_user_id = None if acting_user_id is None else int(acting_user_id)
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

    def years(self, organization_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID,CONCAT(Name,' (',Status,')') FROM tblAccountingFiscalYear WHERE OrganizationID=? ORDER BY StartDate DESC", (organization_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    def preview(self, organization_id, year_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT y.Name,y.StartDate,y.EndDate,y.Status,y.ClosingTransactionID,o.ApprovalPolicy FROM tblAccountingFiscalYear y JOIN tblAccountingOrganization o ON o.ID=y.OrganizationID WHERE y.ID=? AND y.OrganizationID=?", (year_id, organization_id))
            year = cursor.fetchone()
            if year is None:
                raise ValueError("Select a fiscal year for this organization.")
            blockers = []
            if year[3] != "OPEN":
                blockers.append("The fiscal year is already {}.".format(year[3].lower()))
            if year[5] == "INDEPENDENT_REQUIRED":
                blockers.append("A different authorized user must approve this year-end close under the current policy.")
            self._execute(cursor, "SELECT COUNT(*) FROM tblAccountingFiscalPeriod WHERE FiscalYearID=? AND Status<>'CLOSED'", (year_id,))
            open_periods = cursor.fetchone()[0]
            if open_periods:
                blockers.append("{} fiscal period(s) are not closed.".format(open_periods))
            self._execute(cursor, "SELECT COUNT(*) FROM tblAccountingTransaction WHERE OrganizationID=? AND TransactionDate BETWEEN ? AND ? AND Status IN ('DRAFT','READY','APPROVED')", (organization_id, year[1], year[2]))
            unposted = cursor.fetchone()[0]
            if unposted:
                blockers.append("{} unposted transaction(s) remain in the fiscal year.".format(unposted))
            self._execute(cursor, "SELECT COALESCE(SUM(l.Debit-l.Credit),0) FROM tblAccountingTransaction t JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID WHERE t.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate<=?", (organization_id, year[2]))
            difference = Decimal(cursor.fetchone()[0])
            if difference != 0:
                blockers.append("The posted ledger is out of balance by {}.".format(difference))
            self._execute(cursor,
                "SELECT f.ID,f.Code,f.Name,f.NetAssetAccountID,COALESCE(na.Code,''),COALESCE(na.Name,''),"
                "COALESCE(na.Active,0),COALESCE(na.PostingAllowed,0),COALESCE(na.AccountType,''),"
                "COALESCE(SUM(CASE WHEN a.AccountType='REVENUE' THEN l.Credit-l.Debit ELSE 0 END),0),"
                "COALESCE(SUM(CASE WHEN a.AccountType='EXPENSE' THEN l.Debit-l.Credit ELSE 0 END),0),"
                "COALESCE(SUM(CASE WHEN a.AccountType='TRANSFER' THEN l.Credit-l.Debit ELSE 0 END),0) "
                "FROM tblAccountingFund f LEFT JOIN tblAccountingAccount na ON na.ID=f.NetAssetAccountID "
                "JOIN tblAccountingTransactionLine l ON l.FundID=f.ID JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "WHERE f.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate BETWEEN ? AND ? "
                "AND a.AccountType IN ('REVENUE','EXPENSE','TRANSFER') "
                "GROUP BY f.ID,f.Code,f.Name,f.NetAssetAccountID,na.Code,na.Name,na.Active,na.PostingAllowed,na.AccountType ORDER BY f.Code",
                (organization_id, year[1], year[2]))
            rows = []
            for fund_id, code, name, net_asset_id, account_code, account_name, account_active, posting_allowed, account_type, revenue, expense, transfer in cursor.fetchall():
                revenue, expense, transfer = Decimal(revenue), Decimal(expense), Decimal(transfer)
                change = revenue - expense + transfer
                if net_asset_id is None:
                    blockers.append("Fund {} has activity but no net-asset account.".format(code))
                elif not account_active or not posting_allowed or account_type != "NET_ASSET":
                    blockers.append("Fund {} needs an active, postable net-asset account.".format(code))
                rows.append((fund_id, code, name, revenue, expense, transfer, change,
                             "{} - {}".format(account_code, account_name) if net_asset_id else "Not configured"))
            return {"year": year, "rows": rows, "blockers": blockers, "ready": not blockers}
        finally:
            cursor.close()

    def close(self, organization_id, year_id, reason, can_override=False):
        reason = (reason or "").strip()
        if not reason:
            raise ValueError("Enter a reason for closing the fiscal year.")
        if self.acting_user_id is None:
            raise ValueError("An authenticated user is required to close a fiscal year.")
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT y.Name,y.EndDate,y.Status,o.ApprovalPolicy,o.NextTransactionNumber "
                "FROM tblAccountingFiscalYear y JOIN tblAccountingOrganization o ON o.ID=y.OrganizationID "
                "WHERE y.ID=? AND y.OrganizationID=? FOR UPDATE", (year_id, organization_id))
            year = cursor.fetchone()
            if year is None or year[2] != "OPEN":
                raise ValueError("Select an open fiscal year.")
            if year[3] == "INDEPENDENT_REQUIRED":
                raise ValueError("This organization requires a different authorized user to approve the year-end close.")
            if not can_override:
                raise ValueError("Year-end close requires approval-override authority under the current policy.")
            report = self.preview(organization_id, year_id)
            if not report["ready"]:
                raise ValueError("The fiscal year is not ready to close: {}".format(" ".join(report["blockers"])))
            self._execute(cursor, "SELECT ID FROM tblAccountingFiscalPeriod WHERE FiscalYearID=? ORDER BY EndDate DESC,PeriodNumber DESC LIMIT 1 FOR UPDATE", (year_id,))
            period = cursor.fetchone()
            if period is None:
                raise ValueError("The fiscal year has no fiscal periods.")
            self._execute(cursor,
                "SELECT l.AccountID,l.FundID,l.FunctionID,COALESCE(SUM(l.Debit-l.Credit),0) "
                "FROM tblAccountingTransaction t JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "WHERE t.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate BETWEEN ? AND ? "
                "AND a.AccountType IN ('REVENUE','EXPENSE','TRANSFER') "
                "GROUP BY l.AccountID,l.FundID,l.FunctionID HAVING COALESCE(SUM(l.Debit-l.Credit),0)<>0 "
                "ORDER BY l.FundID,l.AccountID,l.FunctionID",
                (organization_id, report["year"][1], report["year"][2]))
            balances = cursor.fetchall()
            if not balances:
                raise ValueError("There is no revenue, expense, or transfer activity to close.")
            self._execute(cursor, "SELECT ID,NetAssetAccountID FROM tblAccountingFund WHERE OrganizationID=? FOR UPDATE", (organization_id,))
            fund_accounts = dict(cursor.fetchall())
            number = year[4]
            self._execute(cursor, "UPDATE tblAccountingOrganization SET NextTransactionNumber=? WHERE ID=? AND NextTransactionNumber=?", (number + 1, organization_id, number))
            if cursor.rowcount != 1:
                raise ValueError("The next transaction number changed. Try again.")
            self._execute(cursor,
                "INSERT INTO tblAccountingTransaction (OrganizationID,TransactionNumber,TransactionDate,FiscalPeriodID,TransactionType,Status,Description,Reference,CreatedByUserID,ReviewedByUserID,ReviewedAt,PostedByUserID,PostedAt) "
                "VALUES (?,?,?,?, 'YEAR_END_CLOSE','POSTED',?,?,?, ?,CURRENT_TIMESTAMP(6),?,CURRENT_TIMESTAMP(6))",
                (organization_id, number, year[1], period[0], "Year-end close for {}".format(year[0]), "Fiscal year {}".format(year[0]), self.acting_user_id, self.acting_user_id, self.acting_user_id))
            transaction_id = cursor.lastrowid
            line_number = 0
            fund_debits = {}
            fund_credits = {}
            total_debit = Decimal("0")
            total_credit = Decimal("0")
            for account_id, fund_id, function_id, balance in balances:
                balance = Decimal(balance)
                debit = -balance if balance < 0 else Decimal("0")
                credit = balance if balance > 0 else Decimal("0")
                line_number += 1
                self._execute(cursor,
                    "INSERT INTO tblAccountingTransactionLine (TransactionID,LineNumber,AccountID,FundID,FunctionID,Description,Debit,Credit) VALUES (?,?,?,?,?,'Close nominal account',?,?)",
                    (transaction_id, line_number, account_id, fund_id, function_id, debit, credit))
                fund_debits[fund_id] = fund_debits.get(fund_id, Decimal("0")) + debit
                fund_credits[fund_id] = fund_credits.get(fund_id, Decimal("0")) + credit
                total_debit += debit; total_credit += credit
            for fund_id in sorted(set(fund_debits) | set(fund_credits)):
                account_id = fund_accounts.get(fund_id)
                if account_id is None:
                    raise ValueError("A fund used by the closing entry has no net-asset account.")
                difference = fund_credits.get(fund_id, Decimal("0")) - fund_debits.get(fund_id, Decimal("0"))
                debit = difference if difference > 0 else Decimal("0")
                credit = -difference if difference < 0 else Decimal("0")
                if debit == 0 and credit == 0:
                    continue
                line_number += 1
                self._execute(cursor,
                    "INSERT INTO tblAccountingTransactionLine (TransactionID,LineNumber,AccountID,FundID,Description,Debit,Credit) VALUES (?,?,?,?,'Close to fund net assets',?,?)",
                    (transaction_id, line_number, account_id, fund_id, debit, credit))
                total_debit += debit; total_credit += credit
            if total_debit <= 0 or total_debit != total_credit:
                raise ValueError("The generated year-end closing transaction is not balanced.")
            self._execute(cursor, "UPDATE tblAccountingFiscalYear SET Status='CLOSED',ClosingTransactionID=? WHERE ID=? AND Status='OPEN'", (transaction_id, year_id))
            if cursor.rowcount != 1:
                raise ValueError("The fiscal year changed. Preview the close again.")
            after = json.dumps({"status":"CLOSED","closing_transaction_id":transaction_id,"transaction_number":number,"total":str(total_debit),"solo_override":True}, separators=(",",":"))
            self._execute(cursor, "INSERT INTO tblAccountingAuditEvent (OrganizationID,EntityType,EntityID,Action,AfterJSON,Reason,UserID) VALUES (?,'FISCAL_YEAR',?,'FISCAL_YEAR_CLOSED_OVERRIDE',?,?,?)", (organization_id, str(year_id), after, reason, self.acting_user_id))
            self._execute(cursor, "INSERT INTO tblAccountingAuditEvent (OrganizationID,EntityType,EntityID,Action,AfterJSON,Reason,UserID) VALUES (?,'TRANSACTION',?,'YEAR_END_CLOSE_POSTED',?,?,?)", (organization_id, str(transaction_id), after, reason, self.acting_user_id))
            self.connection.commit()
            return number
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
