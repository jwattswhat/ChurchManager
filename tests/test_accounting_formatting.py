from decimal import Decimal
import unittest
from accounting.formatting import money

class TestAccountingFormatting(unittest.TestCase):
    def test_money_uses_thousands_separators(self):
        self.assertEqual(money(Decimal("11700")), "11,700.00")
        self.assertEqual(money(Decimal("11700"), True), "$11,700.00")
        self.assertEqual(money(Decimal("-1250.5"), True), "$-1,250.50")

if __name__=="__main__": unittest.main()
