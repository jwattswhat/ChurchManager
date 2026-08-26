import unittest

from schema_hygiene import require_clean_schema, scan_schema_sql


class SchemaHygieneTests(unittest.TestCase):
    def codes(self, sql):
        return {item.code for item in scan_schema_sql(sql)}

    def test_accepts_current_schema_statements(self):
        sql = (
            "CREATE TABLE tblChurch (ID int NOT NULL, Church varchar(255));\n"
            "CREATE VIEW rpt_church AS SELECT ID, Church FROM tblChurch;"
        )
        self.assertTrue(require_clean_schema(sql))

    def test_rejects_old_id_and_retired_tables(self):
        codes = self.codes(
            "CREATE TABLE tblReading (OldID int);\n"
            "CREATE TABLE tblAltReading (ID int);"
        )
        self.assertEqual(codes, {"obsolete_identifier", "retired_table"})

    def test_rejects_definers_accounts_and_database_selection(self):
        codes = self.codes(
            "CREATE DEFINER=`church`@`localhost` VIEW sample AS SELECT 1;\n"
            "GRANT ALL ON example.* TO 'user'@'localhost';\n"
            "USE ChurchDB;"
        )
        self.assertEqual(codes, {"object_definer", "account_statement", "database_statement"})

    def test_rejects_test_names_paths_and_dump_state(self):
        codes = self.codes(
            "-- Database ChurchDBTest\n"
            "CREATE TABLE x (p varchar(255) DEFAULT 'C:\\Users\\Pastor\\file') AUTO_INCREMENT=42;\n"
            "CREATE VIEW JSFormTest_view AS SELECT 1;"
        )
        self.assertEqual(codes, {"machine_path", "dump_state", "test_database"})

    def test_rejects_data_and_destructive_statements(self):
        codes = self.codes(
            "INSERT INTO tblChurch VALUES (1);\n"
            "DROP TABLE IF EXISTS tblChurch;"
        )
        self.assertEqual(codes, {"data_statement", "destructive_statement"})

    def test_comments_do_not_create_findings(self):
        self.assertEqual(scan_schema_sql("-- OldID from ChurchDBTest"), ())


if __name__ == "__main__":
    unittest.main()
