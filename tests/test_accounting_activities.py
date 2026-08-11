from datetime import date
from decimal import Decimal
import unittest
from accounting.activities_service import ActivitiesService

class Cursor:
    def __init__(self):self.rows=[];self.statements=[]
    def execute(self,sql,values=()):
        self.statements.append((sql,values));self.rows=[
            ("4000","Offerings","REVENUE","WITHOUT_DONOR_RESTRICTIONS",0,Decimal("1000")),
            ("4100","Restricted gifts","REVENUE","WITH_DONOR_RESTRICTIONS",0,Decimal("500")),
            ("5600","Property","EXPENSE","WITHOUT_DONOR_RESTRICTIONS",Decimal("250"),0),
            ("5600","Property","EXPENSE","WITH_DONOR_RESTRICTIONS",Decimal("100"),0),
            ("8000","Transfers out","TRANSFER","WITHOUT_DONOR_RESTRICTIONS",Decimal("200"),0),
            ("8100","Transfers in","TRANSFER","WITHOUT_DONOR_RESTRICTIONS",0,Decimal("200"))]
    def fetchall(self):return self.rows
    def close(self):pass
class Connection:
    def __init__(self):self.cursor_value=Cursor()
    def cursor(self):return self.cursor_value

class TestActivities(unittest.TestCase):
    def test_activity_keeps_restriction_classes_and_transfers_separate(self):
        connection=Connection();rows=ActivitiesService(connection).rows(1,date(2027,1,1),date(2027,1,31))
        revenue=sum((r[3] for r in rows if r[2]=="REVENUE"),Decimal("0"));restricted=sum((r[4] for r in rows if r[2]=="REVENUE"),Decimal("0"))
        expense=sum((r[3]+r[4] for r in rows if r[2]=="EXPENSE"),Decimal("0"));transfer=sum((r[3]+r[4] for r in rows if r[2]=="TRANSFER"),Decimal("0"))
        self.assertEqual((revenue,restricted,expense,transfer),(Decimal("1000"),Decimal("500"),Decimal("350"),Decimal("0")))
        self.assertIn("t.Status IN ('POSTED','REVERSED')",connection.cursor_value.statements[0][0])
    def test_invalid_date_range_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"start date"):
            ActivitiesService(Connection()).rows(1,date(2027,2,1),date(2027,1,1))
    def test_screen_has_restriction_columns_and_permission(self):
        from pathlib import Path
        source=(Path(__file__).parents[1]/"accounting"/"activities_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn('title="Statement of Activities"',source);self.assertIn("Without restrictions",source);self.assertIn("With restrictions",source)
        self.assertIn('authorization.require("accounting.reports.run"',source)
        self.assertIn("format=wx.LIST_FORMAT_RIGHT if index>=3",source)

if __name__=="__main__":unittest.main()
