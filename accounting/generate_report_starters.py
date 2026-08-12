"""Generate the official accounting statement starter definitions."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "report_definitions"


def column(name, label, width, data_type=None, align=None):
    result = {"name": name, "label": label, "collection": "records",
              "field": name, "width": width}
    if data_type: result["format"] = data_type
    if align: result["align"] = align
    return result


def definition(code, title, dataset, columns, totals, orientation="landscape"):
    width = 720 if orientation == "landscape" else 540
    controls = {
        "ChurchLogo": {"type":"image","band":"ReportHeader","position":[0,0],"size":[68,68],
                       "collection":"church","field":"Logo"},
        "ChurchName": {"type":"text","band":"ReportHeader","position":[80,0],"size":[width-160,22],
                       "collection":"church","field":"Church","fontsize":15,"bold":True,"align":"center"},
        "OrganizationName": {"type":"text","band":"ReportHeader","position":[80,25],"size":[width-160,17],
                             "collection":"organization","field":"LegalName","fontsize":9,"align":"center"},
        "ReportTitle": {"type":"systemtext","band":"ReportHeader","position":[80,45],"size":[width-160,20],
                        "systemvalue":"report_title","fontsize":13,"bold":True,"align":"center"},
        "Period": {"type":"text","band":"ReportHeader","position":[80,71],"size":[width-160,16],
                   "collection":"parameters","field":"Display","fontsize":8,"align":"center"},
        "RunUser": {"type":"systemtext","band":"ReportHeader","position":[width-210,89],"size":[210,14],
                    "systemvalue":"run_user","prefix":"Run by: ","fontsize":8,"align":"right","color":"#555555"},
        "HeaderRule": {"type":"line","band":"PageHeader","position":[0,4],"size":[width,1],
                       "bordercolor":"#6D7780","borderwidth":0.7},
        "Records": {"type":"table","band":"Detail","position":[0,0],"size":[width,40],
                    "repeatcollection":"records","columns":columns},
        "TotalsRule": {"type":"line","band":"ReportFooter","position":[0,3],"size":[width,1],
                       "bordercolor":"#202020","borderwidth":0.8},
        "FooterLine": {"type":"line","band":"PageFooter","position":[0,0],"size":[width,1],
                       "bordercolor":"#808080","borderwidth":0.5},
        "ReportCode": {"type":"systemtext","band":"PageFooter","position":[0,6],"size":[180,14],
                       "systemvalue":"report_code","prefix":"ChurchManager report ","fontsize":8,"color":"#555555"},
        "Classification": {"type":"systemtext","band":"PageFooter","position":[(width-180)/2,6],"size":[180,14],
                           "systemvalue":"classification","fontsize":8,"bold":True,"align":"center","color":"#555555"},
        "PageNumber": {"type":"systemtext","band":"PageFooter","position":[width-90,6],"size":[90,14],
                       "systemvalue":"page_number","prefix":"Page ","fontsize":8,"align":"right","color":"#555555"},
    }
    count = len(totals)
    item_width = width / count
    for index, (name, label, field_name) in enumerate(totals):
        x = item_width * index
        controls[name + "Label"] = {"type":"label","band":"ReportFooter","position":[x,10],
                                     "size":[item_width,14],"label":label,"fontsize":8,"bold":True,"align":"right"}
        controls[name] = {"type":"text","band":"ReportFooter","position":[x,28],
                          "size":[item_width,17],"collection":"totals","field":field_name,
                          "format":"currency","fontsize":9,"bold":True,"align":"right"}
    report = {
        "schema_version":1,"name":code,"title":title,"dataset":dataset,"datasetversion":1,
        "pagesize":"letter","orientation":orientation,
        "margins":{"top":30,"right":36,"bottom":30,"left":36},
        "theme":"churchmanager.accounting","classification":"official",
        "emptytext":"No posted activity matches the selected reporting period.",
        "bands":{
            "ReportHeader":{"type":"reportheader","height":108},
            "PageHeader":{"type":"pageheader","height":8,"repeat":True},
            "Detail":{"type":"detail","height":42},
            "ReportFooter":{"type":"reportfooter","height":54},
            "PageFooter":{"type":"pagefooter","height":24,"repeat":True},
        },
    }
    return {code + "REPORT":{"REPORT":report,"CONTROLS":controls}}


REPORTS = (
    definition("ACCT-FP", "Statement of Financial Position", "accounting.position", (
        column("Section","Section",170), column("Code","Code",70),
        column("Name","Account",360), column("Amount","Amount",120,"currency","right"),
    ), (("TotalAssets","Total assets","TotalAssets"),
        ("LiabilitiesAndNetAssets","Liabilities and net assets","LiabilitiesAndNetAssets"),
        ("Difference","Difference","Difference"))),
    definition("ACCT-ACT", "Statement of Activities", "accounting.activities", (
        column("Section","Section",90), column("Code","Code",55), column("Name","Account",245),
        column("WithoutRestrictions","Without restrictions",110,"currency","right"),
        column("WithRestrictions","With restrictions",110,"currency","right"),
        column("Total","Total",110,"currency","right"),
    ), (("ChangeWithout","Change without restrictions","WithoutRestrictions"),
        ("ChangeWith","Change with restrictions","WithRestrictions"),
        ("ChangeTotal","Change in net assets","Total"))),
    definition("ACCT-FUND", "Fund Activity and Balances", "accounting.funds", (
        column("Code","Code",45), column("Name","Fund",120), column("NetAssetClass","Restriction class",115),
        column("Beginning","Beginning",75,"currency","right"), column("Revenue","Revenue",70,"currency","right"),
        column("Expense","Expense",70,"currency","right"), column("Transfers","Transfers",75,"currency","right"),
        column("Other","Other",65,"currency","right"), column("Ending","Ending",85,"currency","right"),
    ), (("BeginningTotal","Total beginning","Beginning"), ("EndingTotal","Total ending","Ending"))),
)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for item in REPORTS:
        code = next(iter(item))[:-6]
        (ROOT / f"{code}.json").write_text(
            json.dumps(item, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
        )


if __name__ == "__main__":
    main()
