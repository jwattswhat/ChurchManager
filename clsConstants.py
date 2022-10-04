import wx

__version__ = "0.1"
__author__ = "Rev. Jonathan C. Watt"


class clsConstantsNameSpace:
    #    __slots__ = ()

    # Forms Constants

    FORM_CONTINUE = wx.ID_OK
    FORM_CANCEL = wx.ID_CANCEL
    FORM_FIRST = 0
    FORM_PREV = 1
    FORM_NEXT = 2
    FORM_LAST = 3

    wxpythoncallparmameters = {
        #   screen types
        "Dialog": [
            "id",
            "name",
            "title",
            "pos",
            "size",
            "style",
        ],
        "Frame": [
            "name",
            "title",
            "pos",
            "size",
            "style",
        ],
        "Panel": [
            "name",
            "pos",
            "size",
            "style",
        ],
        #   internal use only
        "navButton": [
            "name",
            "label",
            "pos",
            "size",
            "style",
        ],
        #   screen fields
        "StaticText": [
            "name",
            "label",
            "pos",
            "size",
            "style",
        ],
        "TextNumber": [
            "name",
            "label",
            "pos",
            "size",
            "style",
        ],
        "StaticBox": [
            "name",
            "label",
            "pos",
            "size",
            "style",
        ],
        "TextCtrl": [
            "name",
            "pos",
            "size",
            "style",
            "validator",
        ],
        "MultiLine": [
            "name",
            "value",
            "pos",
            "size",
            "style",
            "validator",
        ],
        "ComboBox": [
            "name",
            "value",
            "choices",
            "pos",
            "size",
            "style",
            "validator",
        ],
        "ListCtrl": ["name", "pos", "size", "style", "validator"],
        "ListCtrlID": ["name", "pos", "size", "style", "validator"],
        "CheckBox": [
            "name",
            "label",
            "pos",
            "size",
            "style",
        ],
        "CheckListBox": [
            "name",
            "value",
            "pos",
            "size",
            "choices",
            "style",
            "validator",
        ],
        "Button": [
            "id",
            "name",
            "label",
            "pos",
            "size",
            "style",
        ],
        "DateTime": [
            "id",
            "name",
            "dt",
            "pos",
            "size",
            "style",
            "validator",
        ],
        "DataViewListCtrl": ["id", "pos", "size", "style", "validator"],
        "DatePickerCtrl": [
            "id",
            "name",
            "dt",
            "pos",
            "size",
            "style",
            "validator",
        ],
        "TimePickerCtrl": [
            "id",
            "name",
            "dt",
            "pos",
            "size",
            "style",
            "validator",
        ],
        "CalendarCtrl": [
            "id",
            "name",
            "date",
            "pos",
            "size",
            "style",
        ],
        "FilePickerCtrl": [
            "id",
            "name",
            "path",
            "message",
            "wildcard",
            "pos",
            "size",
            "style",
        ],
    }

    btnNavigationCONTROLS = {
        "Navigation": {
            "btnNew": {
                "type": "Button",
                "label": "New",
                "posch": (0, 0),
                "sizech": (3, 2),
                "name": "btnNew",
            },
            "btnUpdate": {
                "type": "Button",
                "label": "Update",
                "posch": (0, 0),
                "sizech": (6, 2),
                "name": "btnUpdate",
            },
            "btnDelete": {
                "type": "Button",
                "label": "Delete",
                "posch": (0, 0),
                "sizech": (6, 2),
                "name": "btnDelete",
            },
            "btnFirst": {
                "type": "Button",
                "label": "<<",
                "posch": (0, 0),
                "sizech": (2, 2),
                "name": "btnFirst",
            },
            "btnPrev": {
                "type": "Button",
                "label": "<",
                "posch": (0, 0),
                "sizech": (2, 2),
                "name": "btnPrev",
            },
            "btnNext": {
                "type": "Button",
                "label": ">",
                "posch": (0, 0),
                "sizech": (2, 2),
                "name": "btnNext",
            },
            "btnLast": {
                "type": "Button",
                "label": ">>",
                "posch": (0, 0),
                "sizech": (2, 2),
                "name": "btnLast",
            },
        },
        "Close": {
            "btnClose": {
                "type": "Button",
                "label": "Close",
                "posch": (0, 0),
                "sizech": (5, 2),
                "name": "btnClose",
            },
        },
    }


CONST = clsConstantsNameSpace()
