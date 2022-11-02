import json
import argparse
import pprint
from typing import OrderedDict

def pttoch(pt):
    p = pt*.125
    p = p + .5
    p = int(p)
    return p

def convpostoch(dict):
        x = pttoch(dict[0])
        y = pttoch(dict[1])
        print ("[",dict[0],",",dict[1],"] to [",x,',',y,"]")
        return [x,y]


parser = argparse.ArgumentParser(
    prog="CvtPxtoChar.py", description="PX to Char Converter"
)
parser.add_argument(
    "-F",
    "--Form",
    dest="form",
    action="store",
    type=str,
    nargs=1,
    help="Enter Form:",
)
args = parser.parse_args()
if not args.form:
    print("no form")
    exit()

FormLocation = ".\\Forms\\"
formname = FormLocation + args.form[0] + ".json"
print ("Processing form:",formname)
f = open(
    formname,
)
jsonfrm = json.load(f,object_pairs_hook=OrderedDict)
f.close()
for fld in jsonfrm[args.form[0]+"FORM"]["FORM"].copy():
    if fld == "pos":
        jsonfrm[args.form[0]+"FORM"]["FORM"]["posch"] = convpostoch(jsonfrm[args.form[0]+"FORM"]["FORM"][fld])
        jsonfrm[args.form[0]+"FORM"]["FORM"].pop("pos")
    if fld == "size":
        jsonfrm[args.form[0]+"FORM"]["FORM"]["sizech"] = convpostoch(jsonfrm[args.form[0]+"FORM"]["FORM"][fld])
        jsonfrm[args.form[0]+"FORM"]["FORM"].pop("size")
    if fld == "linkedform":
        for frm in jsonfrm[args.form[0]+"FORM"]["FORM"][fld].copy():
            for f in jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm].copy():
                if f == "pos":
                    jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm]["posch"] = convpostoch(jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm][f])
                    jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm].pop("pos")
                if f == "size":
                    jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm]["sizech"] = convpostoch(jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm][f])
                    jsonfrm[args.form[0]+"FORM"]["FORM"][fld].pop("size")
    if fld == "subform":
        for frm in jsonfrm[args.form[0]+"FORM"]["FORM"][fld].copy():
            for f in jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm].copy():
                if f == "pos":
                    jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm]["posch"] = convpostoch(jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm][f])
                    jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm].pop("pos")
                if f == "size":
                    jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm]["sizech"] = convpostoch(jsonfrm[args.form[0]+"FORM"]["FORM"][fld][frm][f])
                    jsonfrm[args.form[0]+"FORM"]["FORM"][fld].pop("size")


for control in jsonfrm[args.form[0]+"FORM"]["CONTROLS"].copy():
    for fld in jsonfrm[args.form[0]+"FORM"]["CONTROLS"][control].copy():
        if fld == "pos":
            jsonfrm[args.form[0]+"FORM"]["CONTROLS"][control]["posch"] = convpostoch(jsonfrm[args.form[0]+"FORM"]["CONTROLS"][control][fld])
            jsonfrm[args.form[0]+"FORM"]["CONTROLS"][control].pop("pos")
        if fld == "size":
            jsonfrm[args.form[0]+"FORM"]["CONTROLS"][control]["sizech"] = convpostoch(jsonfrm[args.form[0]+"FORM"]["CONTROLS"][control][fld])
            jsonfrm[args.form[0]+"FORM"]["CONTROLS"][control].pop("size")

pprint.pprint(jsonfrm[args.form[0]+"FORM"])
f = open(
    formname,"w"
)
f.write(json.dumps(jsonfrm))
f.close()