from datetime import date
import unittest

from accounting.period_close_service import PeriodCloseService


class Checklist:
    def __init__(self, blocked=False): self.blocked=blocked
    def run(self, organization_id, period_id):
        return {"checks":[{"check":"Drafts","status":"BLOCKED" if self.blocked else "CLEAR"}]}


class Cursor:
    def __init__(self, mode="close", policy="INDEPENDENT_PREFERRED", closer=7):
        self.mode=mode;self.policy=policy;self.closer=closer
        self.calls=[];self.one=None;self.rowcount=0
    def execute(self,sql,values=()):
        self.calls.append((sql,values))
        if sql.startswith("SELECT p.Status,p.Name,p.StartDate"):
            self.one=("OPEN","January",date(2026,1,1),date(2026,1,31))
        elif sql.startswith("SELECT p.Status,p.Name,o.ApprovalPolicy"):
            self.one=("CLOSED","January",self.policy)
        elif sql.startswith("SELECT UserID"):
            self.one=(self.closer,)
        elif sql.startswith("UPDATE tblAccountingFiscalPeriod"):
            self.rowcount=1
    def fetchone(self):return self.one
    def close(self):pass


class Connection:
    def __init__(self,**values):self.cursor_value=Cursor(**values);self.commits=0;self.rollbacks=0
    def cursor(self):return self.cursor_value
    def commit(self):self.commits+=1
    def rollback(self):self.rollbacks+=1


class PeriodCloseTests(unittest.TestCase):
    def test_close_requires_clear_checklist_and_audits(self):
        connection=Connection()
        PeriodCloseService(connection,7,Checklist()).close(1,12)
        self.assertEqual(connection.commits,1)
        sql="\n".join(item[0] for item in connection.cursor_value.calls)
        self.assertIn("Status='CLOSED'",sql);self.assertIn("PERIOD_CLOSED",sql)

    def test_close_refuses_checklist_blockers(self):
        connection=Connection()
        with self.assertRaisesRegex(ValueError,"Drafts"):
            PeriodCloseService(connection,7,Checklist(True)).close(1,12)
        self.assertEqual(connection.commits,0)

    def test_preferred_policy_allows_reasoned_audited_reopen_by_closer(self):
        connection=Connection(mode="reopen",closer=7)
        PeriodCloseService(connection,7,Checklist()).reopen(1,12,"Late bank correction")
        audit=next(item for item in connection.cursor_value.calls if "INSERT INTO tblAccountingAuditEvent" in item[0])
        self.assertIn("PERIOD_REOPENED_OVERRIDE",audit[1])
        self.assertIn("Late bank correction",audit[1])

    def test_required_policy_needs_different_user_to_reopen(self):
        connection=Connection(mode="reopen",policy="INDEPENDENT_REQUIRED",closer=7)
        with self.assertRaisesRegex(ValueError,"different authorized user"):
            PeriodCloseService(connection,7,Checklist()).reopen(1,12,"Correction")

    def test_reopen_requires_reason_before_database_access(self):
        connection=Connection(mode="reopen")
        with self.assertRaisesRegex(ValueError,"reason"):
            PeriodCloseService(connection,7,Checklist()).reopen(1,12," ")
        self.assertEqual(connection.cursor_value.calls,[])


if __name__=="__main__":unittest.main()
