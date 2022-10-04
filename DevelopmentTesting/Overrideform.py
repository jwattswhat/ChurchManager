import json
import pprint

formname = "./Forms/frmHymnUsage.json"
f = open(
    formname,
)
jsonfrm = json.load(f)
HymnUsage = jsonfrm["frmHymnUsageFORM"]["FORM"]
print("frmHymnUsage")
pprint.pprint(HymnUsage)
print()

formname = "./Forms/frmService.json"
f = open(
    formname,
)
jsonfrm = json.load(f)
HymnUsageOverride = jsonfrm["frmServiceFORM"]["FORM"]["linkedform"]["frmHymnUsage"]
HymnUsageOverride.pop("name")
HymnUsageOverride.pop("label")
HymnUsageOverride.pop("pos")
HymnUsageOverride.pop("controls")
HymnUsageOverride.pop("stylelist")

print("frmService:FrmHymnUsage")
pprint.pprint(HymnUsageOverride)
print()
print()

print("Override")
HymnUsage.update(HymnUsageOverride)
#HymnUsage = {**HymnUsageOverride,**HymnUsage}

pprint.pprint(HymnUsage)