import wx
from wx.core import Point, Size, Choice, TE_MULTILINE
from collections import defaultdict

from CMFormDescriptionChurch import frmChurchCONTROLS


wxpythoncallparmameters = {
    "StaticText": ["label", "pos", "size", "style", "name"],
    "TextCtrl": ["value", "pos", "size", "style", "validator", "name"],
    "ComboBox": ["value", "pos", "size", "choices", "style", "validator", "name"],
    "CheckBox": ["label", "pos", "size", "style", "validator", "name"],
    "CheckListBox": [
        "value",
        "pos",
        "size",
        "choices",
        "style",
        "validator",
        "name",
    ],
    "Button": ["label", "pos", "size", "style", "validator", "name"],
    "DataViewListCtrl": ["pos", "size", "style", "validator"],
}


def getcontrolparameters(controldictionary):
    newdict = {}
    for key in wxpythoncallparmameters[controldictionary["type"]]:
        if key in controldictionary.keys():
            newdict.update({key: controldictionary[key]})
    return newdict


#
# 	Main Program
#

p = getcontrolparameters(frmChurchCONTROLS["Church"])
print(p)
