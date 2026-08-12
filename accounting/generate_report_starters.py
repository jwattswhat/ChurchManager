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


def definition(code, title, dataset, columns, totals, orientation="landscape", page_size="letter", content_width=None):
    width = content_width or (720 if orientation == "landscape" else 540)
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
    for index, total in enumerate(totals):
        name,label,field_name=total[:3]
        data_format=total[3] if len(total)>3 else "currency"
        x = item_width * index
        controls[name + "Label"] = {"type":"label","band":"ReportFooter","position":[x,10],
                                     "size":[item_width,14],"label":label,"fontsize":8,"bold":True,"align":"right"}
        controls[name] = {"type":"text","band":"ReportFooter","position":[x,28],
                          "size":[item_width,17],"collection":"totals","field":field_name,
                          "format":data_format,"fontsize":9,"bold":True,"align":"right"}
    report = {
        "schema_version":1,"name":code,"title":title,"dataset":dataset,"datasetversion":1,
        "pagesize":page_size,"orientation":orientation,
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


def budget_definition(code,title,dataset):
    summary=(
        column("Account","General account",117),column("Fund","Fund",76),column("Function","Function",63),
        column("PeriodBudget","Period budget",68,"currency","right"),column("PeriodActual","Period actual",68,"currency","right"),
        column("PeriodVariance","Variance",63,"currency","right"),column("PeriodPercent","%",36,"decimal","right"),
        column("YTDBudget","YTD budget",68,"currency","right"),column("YTDActual","YTD actual",68,"currency","right"),
        column("YTDVariance","Variance",63,"currency","right"),column("YTDPercent","%",30,"decimal","right"),
    )
    item=definition(code,title,dataset,summary,(
        ("PeriodBudgetTotal","Period budget","PeriodBudget"),("PeriodActualTotal","Period actual","PeriodActual"),
        ("YTDBudgetTotal","YTD budget","YTDBudget"),("YTDActualTotal","YTD actual","YTDActual"),
    ))
    root=item[code+"REPORT"]
    root["REPORT"]["bands"]["Detail"]["height"]=76
    root["CONTROLS"]["Records"]["repeatcollection"]="summary"
    for value in root["CONTROLS"]["Records"]["columns"]:value["collection"]="summary"
    root["CONTROLS"]["Records"]["size"]=[720,38]
    root["CONTROLS"]["Details"]={
        "type":"table","band":"Detail","position":[0,40],"size":[720,34],
        "repeatcollection":"details","visiblewhen":{"collection":"parameters","field":"ShowDetails","operator":"equals","value":True},
        "columns":[
            {**column("Period","Period",65),"collection":"details"},
            {**column("Account","General account",140),"collection":"details"},
            {**column("Fund","Fund",95),"collection":"details"},
            {**column("Function","Function",80),"collection":"details"},
            {**column("LineItem","Detailed line item",150),"collection":"details"},
            {**column("Budget","Budget",75,"currency","right"),"collection":"details"},
            {**column("Note","Note",115),"collection":"details"},
        ],
    }
    return item


def journal_definition():
    item=definition("ACCT-JE","Journal Entry","accounting.journalentry",(
        column("Line","#",30,"integer"),column("Account","Account",165),column("Fund","Fund",120),
        column("Function","Function",90),column("Payee","Payee",90),column("Description","Description",175),
        column("Debit","Debit",70,"currency","right"),column("Credit","Credit",70,"currency","right"),
    ),(("DebitTotal","Debits","Debit"),("CreditTotal","Credits","Credit"),("Difference","Difference","Difference")),
       page_size="legal",content_width=810)
    root=item["ACCT-JEREPORT"]
    root["REPORT"]["bands"]["ReportHeader"]["height"]=154
    root["REPORT"]["bands"]["Detail"]["height"]=76
    controls=root["CONTROLS"]
    controls["ChurchName"]["size"]=[650,22];controls["OrganizationName"]["size"]=[650,17]
    controls["ReportTitle"]["size"]=[650,20];controls["Period"]["size"]=[650,16]
    controls["RunUser"]["position"]=[600,89]
    for name,label,field_name,y in (
        ("Created","Created","Created",106),("Reviewed","Reviewed","Reviewed",121),("Posted","Posted","Posted",136)):
        controls[name]={"type":"text","band":"ReportHeader","position":[80,y],"size":[650,14],
                        "collection":"parameters","field":field_name,"prefix":label+": ","fontsize":8}
    controls["Attachments"]={"type":"table","band":"Detail","position":[0,40],"size":[810,34],
        "repeatcollection":"attachments","visiblewhen":{"collection":"parameters","field":"HasAttachments","operator":"equals","value":True},
        "columns":[
            {**column("Name","Attachment",180),"collection":"attachments"},
            {**column("Type","Type",100),"collection":"attachments"},
            {**column("Hash","SHA-256 hash",390),"collection":"attachments"},
            {**column("AddedAt","Added",140,"datetime"),"collection":"attachments"}]}
    return item


def reconciliation_definition():
    item=definition("ACCT-REC","Bank Reconciliation Report","accounting.reconciliation",(
        column("Status","Status",80),column("Date","Transaction date",85,"date"),column("Number","No.",55,"integer"),
        column("Description","Description",260),column("Reference","Reference",145),
        column("Amount","Amount",100,"currency","right"),column("ClearedDate","Cleared date",95,"date"),
    ),(("Beginning","Beginning","Beginning"),("Cleared","Cleared activity","Cleared"),
       ("Ending","Statement ending","Ending"),("Difference","Difference","Difference"),
       ("Outstanding","Outstanding","Outstanding")),page_size="legal",content_width=820)
    root=item["ACCT-RECREPORT"];root["REPORT"]["bands"]["ReportHeader"]["height"]=132
    controls=root["CONTROLS"]
    controls["PreparedBy"]={"type":"text","band":"ReportHeader","position":[80,106],"size":[300,14],
                            "collection":"parameters","field":"PreparedBy","prefix":"Prepared by: ","fontsize":8}
    controls["CompletedAt"]={"type":"text","band":"ReportHeader","position":[440,106],"size":[300,14],
                             "collection":"parameters","field":"CompletedAt","format":"datetime","prefix":"Completed: ","fontsize":8,"align":"right"}
    return item


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
    budget_definition("ACCT-BVA","Budget to Actual","accounting.budgetactual"),
    budget_definition("ACCT-BUD","Adopted Budget","accounting.adoptedbudget"),
    definition("ACCT-GL","General Ledger","accounting.generalledger",(
        column("Date","Date",60,"date"),column("Number","No.",40,"integer"),column("Type","Type",95),
        column("Transaction","Transaction",150),column("Reference","Reference",100),column("Fund","Fund",140),
        column("Description","Line description",135),column("Debit","Debit",60,"currency","right"),
        column("Credit","Credit",60,"currency","right"),column("Balance","Balance",60,"currency","right"),
    ),(("OpeningBalance","Opening balance","OpeningBalance"),("DebitTotal","Debits","DebitTotal"),
       ("CreditTotal","Credits","CreditTotal"),("EndingBalance","Ending balance","EndingBalance")),
       page_size="legal",content_width=900),
    definition("ACCT-REG","Posted Transaction Register","accounting.register",(
        column("Number","No.",55,"integer"),column("Organization","Organization",165),
        column("Date","Date",65,"date"),column("Type","Type",100),column("Status","Status",65),
        column("Description","Description",250),column("Reference","Reference",120),
        column("Total","Total",80,"currency","right"),
    ),(("TransactionCount","Transactions","TransactionCount","integer"),("RegisterTotal","Register total","Total")),
       page_size="legal",content_width=900),
    journal_definition(),
    reconciliation_definition(),
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
