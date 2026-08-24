"""Canonical report codes and aliases for layouts saved before standardization."""

LEGACY_REPORT_CODES = {
    "CMGN01": "CMAS01", "CMGN02": "CMDO01", "CMGN03": "CMRP01",
    "CMWS01": "CMWP01", "CMWS02": "CMWS01", "CMWS03": "CMHU01",
    "CMWS04": "CMHU02", "CMWS05": "CMHU03", "CMWS06": "CMHU04",
    "CMWS07": "CMHU05",
    "CMMB01": "CMMD01", "CMMB02": "CMMI01", "CMMB03": "CMMI02",
    "CMMB04": "CMMI03", "CMMB05": "CMML01", "CMMB06": "CMML02",
    "CMMB07": "CMPE01", "CMMB08": "CMPH02", "CMMB09": "CMML03",
    "CMMB10": "CMML04",
    "CMPC03": "CMJR01", "CMPC04": "CMPA01", "CMPC05": "CMPR01",
    "CMFI01": "ACCT-TB", "CMFI02": "ACCT-GL", "CMFI03": "ACCT-FP",
    "CMFI04": "ACCT-ACT", "CMFI05": "ACCT-FUND", "CMFI06": "ACCT-REC",
    "CMFI07": "ACCT-BVA", "CMFI08": "ACCT-FUNC", "CMFI09": "ACCT-AUDIT",
    "CMFI10": "ACCT-BUD", "CMFI11": "ACCT-CLOSE", "CMFI12": "ACCT-JE",
    "CMFI13": "ACCT-REG", "CMFI14": "ACCT-YE",
    "CMGV01": "GIVE-BATCH", "CMGV02": "GIVE-BATCH-DETAIL",
    "CMGV03": "GIVE-HISTORY", "CMGV04": "GIVE-STMT",
    "CMGV05": "GIVE-STMT-EXCEPTIONS", "CMGV06": "GIVE-FUND-PERIOD",
    "CMGV07": "GIVE-DIRECTED", "CMGV08": "GIVE-TRIBUTE",
    "CMGV09": "GIVE-ENVELOPE-LABELS", "CMGV10": "GIVE-ENVELOPE-REGISTER",
    "CMGV11": "GIVE-ENVELOPE-EXCEPTIONS", "CMGV12": "GIVE-RECONCILE",
}


def legacy_report_code(canonical_code):
    """Return the prior code for a canonical report, if that report was renamed."""
    return LEGACY_REPORT_CODES.get(canonical_code)
