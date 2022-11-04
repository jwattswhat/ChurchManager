import json
import os
import argparse
import pprint
from typing import OrderedDict

def pttoch(pt):
    p = pt*.083
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
    inputformname = input("Enter Form:")
else:
    inputformname = args.form[0]

FormLocation = ".\\Forms\\"
formname = FormLocation + inputformname + ".json"
saveform = FormLocation + "sv." + inputformname +".json"
print ("Processing form:",formname)
f = open(
    formname,
)
jsonfrm = json.load(f,object_pairs_hook=OrderedDict)
f.close()

os.rename(formname,saveform)
for fld in jsonfrm[inputformname+"FORM"]["FORM"].copy():
    if fld == "pos":
        jsonfrm[inputformname+"FORM"]["FORM"]["posch"] = convpostoch(jsonfrm[inputformname+"FORM"]["FORM"][fld])
        jsonfrm[inputformname+"FORM"]["FORM"].pop("pos")
    if fld == "size":
        jsonfrm[inputformname+"FORM"]["FORM"]["sizech"] = convpostoch(jsonfrm[inputformname+"FORM"]["FORM"][fld])
        jsonfrm[inputformname+"FORM"]["FORM"].pop("size")
    if fld == "linkedform":
        for frm in jsonfrm[inputformname+"FORM"]["FORM"][fld].copy():
            for f in jsonfrm[inputformname+"FORM"]["FORM"][fld][frm].copy():
                if f == "pos":
                    jsonfrm[inputformname+"FORM"]["FORM"][fld][frm]["posch"] = convpostoch(jsonfrm[inputformname+"FORM"]["FORM"][fld][frm][f])
                    jsonfrm[inputformname+"FORM"]["FORM"][fld][frm].pop("pos")
                if f == "size":
                    jsonfrm[inputformname+"FORM"]["FORM"][fld][frm]["sizech"] = convpostoch(jsonfrm[inputformname+"FORM"]["FORM"][fld][frm][f])
                    jsonfrm[inputformname+"FORM"]["FORM"][fld].pop("size")
    if fld == "subform":
        for frm in jsonfrm[inputformname+"FORM"]["FORM"][fld].copy():
            for f in jsonfrm[inputformname+"FORM"]["FORM"][fld][frm].copy():
                if f == "pos":
                    jsonfrm[inputformname+"FORM"]["FORM"][fld][frm]["posch"] = convpostoch(jsonfrm[inputformname+"FORM"]["FORM"][fld][frm][f])
                    jsonfrm[inputformname+"FORM"]["FORM"][fld][frm].pop("pos")
                if f == "size":
                    jsonfrm[inputformname+"FORM"]["FORM"][fld][frm]["sizech"] = convpostoch(jsonfrm[inputformname+"FORM"]["FORM"][fld][frm][f])
                    jsonfrm[inputformname+"FORM"]["FORM"][fld].pop("size")


for control in jsonfrm[inputformname+"FORM"]["CONTROLS"].copy():
    for fld in jsonfrm[inputformname+"FORM"]["CONTROLS"][control].copy():
        if fld == "pos":
            jsonfrm[inputformname+"FORM"]["CONTROLS"][control]["posch"] = convpostoch(jsonfrm[inputformname+"FORM"]["CONTROLS"][control][fld])
            jsonfrm[inputformname+"FORM"]["CONTROLS"][control].pop("pos")
        if fld == "size":
            jsonfrm[inputformname+"FORM"]["CONTROLS"][control]["sizech"] = convpostoch(jsonfrm[inputformname+"FORM"]["CONTROLS"][control][fld])
            jsonfrm[inputformname+"FORM"]["CONTROLS"][control].pop("size")

pprint.pprint(jsonfrm[inputformname+"FORM"])
print (formname)
f = open(
    formname,"w"
)
f.write(json.dumps(jsonfrm))
f.close()