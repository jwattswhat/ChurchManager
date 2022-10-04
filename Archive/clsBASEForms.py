# !/usr/bin/env python3
#
#   frmForms.py - Church Manager Forms Classes
#
# 	Rev. Jonathan C. Watt
# 	July 1, 2021
#
import pprint
from numpy import true_divide
import wx
import wx.dataview
from wx.core import (
    BATTERY_NORMAL_STATE,
    CONTROL_ISDEFAULT,
    ELLIPSIZE_START,
    Control,
    ID_ANY,
    SaveFileSelector,
    StaticText,
)
import mysql
import json
from datetime import date
import pprint
import pyautogui

from clsForms import clsForm
import clsValidators
import clsDB
from clsDB import parse_SQL
import clsFields
from clsFields import clsField, getcontrolparameters
import clsConfig
import clsFont


#
#   Global Constants Variables and Functions
#
#
forms_CONTINUE = wx.ID_OK
forms_CANCEL = wx.ID_CANCEL

btnNavigationCONTROLS = {
    "Navigation": {
        "btnNew": {
            "type": "Button",
            "label": "Ne&w",
            "pos": (0, 0),
            "size": (50, 30),
            "name": "btnNew",
        },
        "btnUpdate": {
            "type": "Button",
            "label": "&Update",
            "pos": (0, 0),
            "size": (70, 30),
            "name": "btnUpdate",
        },
        "btnDelete": {
            "type": "Button",
            "label": "&Delete",
            "pos": (0, 0),
            "size": (70, 30),
            "name": "btnDelete",
        },
        "btnFirst": {
            "type": "Button",
            "label": "<<",
            "pos": ((0, 0)),
            "size": (40, 30),
            "name": "btnFirst",
        },
        "btnPrev": {
            "type": "Button",
            "label": "<",
            "pos": (0, 0),
            "size": (40, 30),
            "name": "btnPrev",
        },
        "btnNext": {
            "type": "Button",
            "label": ">",
            "pos": (0, 0),
            "size": (40, 30),
            "name": "btnNext",
        },
        "btnLast": {
            "type": "Button",
            "label": ">>",
            "pos": (0, 0),
            "size": (40, 30),
            "name": "btnLast",
        },
    },
    "Close": {
        "btnClose": {
            "type": "Button",
            "label": "&Close",
            "pos": (0, 0),
            "name": "btnClose",
        },
    },
}


class clsBASEForm:
    """
    clsBASEForm: Process a form

       Class Variables.
           PARENT - Calling clsBASEForm object
           FRAME - Frame Created if form is a Panel
           FORM - wxPython Frame for this form
           SUBFORM - Dictionary of Subforms called by this form
           LINKEDFORM - Dictionary of Linked forms called by this form
           DBConnection - SQL Database Connection
           SQL - Query for this form

       Parameters
           self
           parent - calling form or "none"
           dbconnection - DB Connection (MySQL)
           formname - name of this form
           controls - Additional Predefined Button Controls
            "Navigation" - Navigation Buttons
                New - Add a New Records
                Update - Update Displayed Record
                Delete - Delete Record
                << - First Record
                < - Previous Record
                > - Next Record
                >> - Last Record
            "Close" - Close Buttion

       Uses
            clsConfig.py - Application Configuration Class
            clsRecords.py - Record Classs
            clsFields.py - Field Classs
            clsValidators.py - Validator Classs
            clsDB.py - Database Classes
    """

    class _dirtydialog(wx.Dialog):
        def __init__(self, parent, title):
            super().__init__(parent, title=title, size=(400, 200))
            panel = wx.Panel(self)
            self.text = wx.StaticText(
                panel,
                wx.ID_ANY,
                label="This form has been modified?",
                pos=(10, 50),
            )
            self.btn = wx.Button(
                panel, forms_CONTINUE, label="Continue", size=(100, 30), pos=(10, 100)
            )
            self.btn = wx.Button(
                panel, forms_CANCEL, label="Cancel", size=(100, 30), pos=(120, 100)
            )

    def __init__(
        self,
        parent,
        dbconnection,
        formname,
        controls=[],
        sql=None,
        overridefrm=None,
        position=None,
    ):
        self.PARENT = parent
        self.DBConnection = dbconnection  # Save the Connection Locally
        self.load_form_from_json(formname)
        self._defaultFont = clsFont.clsFont(dbconnection)
        self._defaultFont.Get_Config_Font()
        if overridefrm != None:
            self.FORMDESC.update(overridefrm)

        #   Predifined Controls "Navigation"
        NavControls = {}
        self.NavControlsPresent = False
        if "Navigation" in controls:
            self.NavControlsPresent = True
            x = 10  # left edget + 10
            for key in btnNavigationCONTROLS["Navigation"]:
                NavControls.update({key: {}})
                NavControls[key].update(btnNavigationCONTROLS["Navigation"][key])
                NavControls[key].update(
                    {"pos": wx.Point(x, self.FORMDESC["size"][1] - 85)}
                )
                x += btnNavigationCONTROLS["Navigation"][key]["size"][0] + 5
            NavControls.update({"btnClose": {}})
            NavControls["btnClose"].update(btnNavigationCONTROLS["Close"]["btnClose"])
            NavControls["btnClose"].update(
                {
                    "pos": wx.Point(
                        self.FORMDESC["size"][0] - 125,
                        self.FORMDESC["size"][1] - 85,
                    )
                }
            )

        #   Predefined Controls "Close"
        self.ClosePresent = False
        if "Close" in controls:
            self.ClosePresent = True
            NavControls.update({"btnClose": {}})
            NavControls["btnClose"].update(btnNavigationCONTROLS["Close"]["btnClose"])
            NavControls["btnClose"].update(
                {
                    "pos": wx.Point(
                        self.FORMDESC["size"][0] - 100,
                        self.FORMDESC["size"][1] - 85,
                    )
                }
            )

        self.CONTROLDESCRIPTION = {**self.CONTROLDESCRIPTION, **NavControls}

        self.LINKEDFORM = {}
        self.SUBFORM = {}
        self.SUBFORMFIELD = {}
        self.RECORDS = None

        #   if not parent is specified make a frame

        if self.FORMDESC["type"] == "Panel":
            #   Panel must have a frame as a Parent.
            #   Invisible to the user.
            if position != None:
                self.FORMDESC["pos"] = [position[0], position[1]]
            self.FRAME = wx.Frame(
                None,
                id=wx.ID_ANY,
                title=self.FORMDESC["title"],
                pos=self.FORMDESC["pos"],
                size=self.FORMDESC["size"],
            )
            self.FRAME.SetFont(self._defaultFont.Get_Current_Font())
            self.FORM = wx.Panel(
                self.FRAME, wx.ID_ANY, **getcontrolparameters(self.FORMDESC)
            )
        elif self.FORMDESC["type"] == "StaticBox":
            self.FORM = wx.StaticBox(
                self.PARENT.FORM, wx.ID_ANY, **getcontrolparameters(self.FORMDESC)
            )

        self.CONTROLID = self.build_form()

        # sql parm is not none
        if sql != None:
            self.FORMDESC["SQL"] = sql

        if "tablename" in self.FORMDESC:
            self.RECORDS = clsDB.clsRecord(
                self.DBConnection,
                self.FORMDESC["tablename"],
                self.FORMDESC["SQL"],
            )

            rec = self.RECORDS.current()
            if rec == None:
                self.new_record()
            else:
                self.fill_form(rec)

        self.linked_forms()
        self.subforms()
        self.bind_form_controls()

    def load_form_from_json(self, Form):
        config = clsConfig.clsConfig(self.DBConnection)
        FormLocation = config.get_Config_Value("FormLocation")

        formname = FormLocation + Form + ".json"
        f = open(
            formname,
        )
        jsonfrm = json.load(f)
        self.FORMDESC = jsonfrm[Form + "FORM"]["FORM"]
        self.CONTROLDESCRIPTION = jsonfrm[Form + "FORM"]["CONTROLS"]

    def build_form(self):
        controlid = {}
        if "readonly" in self.FORMDESC:
            readonly = True
        else:
            readonly = False
        for key in self.CONTROLDESCRIPTION:
            if readonly:
                self.CONTROLDESCRIPTION[key].update({"readonly": True})
            self.CONTROLDESCRIPTION[key].update(
                {"name": key}
            )  # <TODO> find a better place for this, make sure name is valid.
            if key[:3] == "dvl":
                self.SUBFORMFIELD.update({key: self.CONTROLDESCRIPTION[key]})
            fld = clsField(
                self, wx.ID_ANY, self.CONTROLDESCRIPTION[key], self.DBConnection
            )
            controlid.update({key: fld.FIELD})
        return controlid

    def open_linked_form(self, lnkdfrm):
        """
        open_linked_form - setup for subsclass override.
        """
        sql = None
        if "SQL" in self.FORMDESC["linkedform"][lnkdfrm]:
            if self.RECORDS != None:
                sql = parse_SQL(
                    self.FORMDESC["linkedform"][lnkdfrm]["SQL"],
                    self.RECORDS.current(),
                )
            else:
                sql = self.FORMDESC["linkedform"][lnkdfrm]["SQL"]

        LinkedForm = clsForm(
            self,
            dbconnection=self.DBConnection,
            formname=lnkdfrm,
            controls=self.FORMDESC["linkedform"][lnkdfrm]["controls"],
            sql=sql,
            position=pyautogui.position(),
        )

        LinkedForm.show()
        LinkedForm.FORM.SetFocus()
        self.LINKEDFORM.update({lnkdfrm: LinkedForm})

    def linked_forms(self):
        if "linkedform" not in self.FORMDESC:
            return

        for lnkdfrm in self.FORMDESC["linkedform"]:
            if "bindbtn" not in self.FORMDESC["linkedform"][lnkdfrm]:
                self.open_linked_form(lnkdfrm)

    def subforms(self):
        if "subform" not in self.FORMDESC:
            return

        for subfrm in self.FORMDESC["subform"]:

            if "SQL" in self.FORMDESC["subform"][subfrm]:
                if self.RECORDS != None:
                    sql = parse_SQL(
                        self.FORMDESC["subform"][subfrm]["SQL"],
                        self.RECORDS.current(),
                    )
                else:
                    sql = self.FORMDESC["subform"][subfrm]["SQL"]

            SubForm = clsBASEForm(
                self,
                dbconnection=self.DBConnection,
                formname=subfrm,
                controls=self.FORMDESC["subform"][subfrm]["controls"],
                overridefrm=self.FORMDESC["subform"][subfrm],
                sql=sql,
            )

            SubForm.show()
            SubForm.FORM.SetFocus()
            self.SUBFORM.update({subfrm: SubForm})

    def fill_form(self, record):
        """
        fill the form with editable data from the Read record
        """
        for key in record:
            if key != "ID":
                if key in record:
                    if (self.CONTROLDESCRIPTION[key]["type"] == "TextCtrl") or (
                        self.CONTROLDESCRIPTION[key]["type"] == "ComboBox"
                    ):  # So changes do send EVT_TEXT
                        self.CONTROLID[key].ChangeValue(record[key])
                    else:
                        self.CONTROLID[key].SetValue(record[key])
        for key in self.SUBFORMFIELD:
            self.CONTROLID[key].ResetSQL(
                clsDB.parse_SQL(
                    self.SUBFORMFIELD[key]["columnSQL"], self.RECORDS.current()
                )
            )

        self.FORM.Refresh()

    def bind_form_controls(self):
        self.FORM.Bind(wx.EVT_CLOSE, self._on_close)

        if "linkedform" in self.FORMDESC:
            for lnkdfrm in self.FORMDESC["linkedform"]:
                if "bindbtn" in self.FORMDESC["linkedform"][lnkdfrm]:
                    self.FORM.Bind(
                        wx.EVT_BUTTON,
                        self._buttonclick,
                        self.CONTROLID[self.FORMDESC["linkedform"][lnkdfrm]["bindbtn"]],
                    )

        for field in self.CONTROLDESCRIPTION:
            if "bindmouse" in self.CONTROLDESCRIPTION[field]:
                self.CONTROLID[field].Bind(
                    self.CONTROLDESCRIPTION[field]["bindmouse"],
                    self._capturemouse,
                )
            if "bindevent" in self.CONTROLDESCRIPTION[field]:
                self.CONTROLID[field].Bind(
                    self._translateevent(self.CONTROLDESCRIPTION[field]["bindevent"]),
                    self._captureevent,
                )

        if self.ClosePresent:
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_close_click, self.CONTROLID["btnClose"]
            )

        if self.NavControlsPresent:
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_new_record_click, self.CONTROLID["btnNew"]
            )
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_update_record_click, self.CONTROLID["btnUpdate"]
            )
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_first_record_click, self.CONTROLID["btnFirst"]
            )
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_prev_record_click, self.CONTROLID["btnPrev"]
            )
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_next_record_click, self.CONTROLID["btnNext"]
            )
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_last_record_click, self.CONTROLID["btnLast"]
            )
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_delete_record_click, self.CONTROLID["btnDelete"]
            )
            self.FORM.Bind(
                wx.EVT_BUTTON, self._on_close_click, self.CONTROLID["btnClose"]
            )

    def disable_button(self, name):
        self.CONTROLID[name].Disable()

    def enable_navigation_buttons(self):
        # pre-defined buttons
        self.CONTROLID["btnNew"].Enable()
        self.CONTROLID["btnDelete"].Enable()
        self.CONTROLID["btnFirst"].Enable()
        self.CONTROLID["btnPrev"].Enable()
        self.CONTROLID["btnNext"].Enable()
        self.CONTROLID["btnLast"].Enable()
        self.CONTROLID["btnUpdate"].Enable()

    def disable_navigation_buttons(self):
        # pre-defined buttons
        self.CONTROLID["btnNew"].Disable()
        self.CONTROLID["btnDelete"].Disable()
        self.CONTROLID["btnFirst"].Disable()
        self.CONTROLID["btnPrev"].Disable()
        self.CONTROLID["btnNext"].Disable()
        self.CONTROLID["btnLast"].Disable()
        self.CONTROLID["btnUpdate"].Disable()

    def validate_form(self):
        if self.FORM.Validate():
            return True
        else:
            return False

    def FORMDirty(self):
        if not self.RECORDS.isempty():
            dirty = False
            for field in self.RECORDS.current():
                if field == "ID":
                    continue
                if not str(self.RECORDS.getoriginalrecvalue(field)) == str(
                    self.CONTROLID[field].GetValue()
                ):
                    # print("Original Record Value","Note=",self.RECORDS.getoriginalrecvalue(field))
                    # print("Current Record Value","Note=",self.CONTROLID[field].GetValue())
                    # print(
                    #    self.RECORDS.getoriginalrecvalue(field)
                    #    == self.CONTROLID[field].GetValue()
                    # )
                    dirty = True
                    self.CONTROLID[field].SetWarningColor()
            if dirty:
                dlg = self._dirtydialog(self.FORM, title="Form Modified(dirty)")
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == forms_CANCEL:
                    return True
        return False

        return dirtyfields

    def show(self):
        try:
            self.FRAME.Show()
        except:
            pass
        finally:
            self.FORM.Show()

    def new_record(self):
        if not self.FORMDirty():
            self.RECORDS.add(self.RECORDS.blank_record())
            self.RECORDS._save_original_record_values()
            rec = self.RECORDS.last()
            for key in self.LINKEDFORM.copy().keys():
                self.LINKEDFORM[key].FORM.Close(True)
                self.LINKEDFORM.pop(key)
                rec = self.LINKEDFORM[key].RECORDS.current()
            self.fill_form(rec)
            self._close_linked_forms()
            # self.subforms()
            self.disable_navigation_buttons()
            self.CONTROLID["btnUpdate"].Enable()
            self.FORM.Refresh()

    #
    #   Evant Handlers
    #
    def _translateevent(self, eventstring):
        evt = None
        if eventstring == "EVT_TEXT":
            evt = wx.EVT_TEXT
        return evt

    def _buttonclick(self, event):
        btn = event.GetEventObject().GetName()
        for lnkdfrm in self.FORMDESC["linkedform"]:
            if lnkdfrm not in self.LINKEDFORM:
                if btn == self.FORMDESC["linkedform"][lnkdfrm]["bindbtn"]:
                    self.open_linked_form(lnkdfrm)

    def _capturemouse(self, event):  # <TODO> implement.
        field = event.GetEventObject().GetName()

    def _captureevent(self, event):
        field = event.GetEventObject().GetName()
        evnttype = event.GetEventType()
        if evnttype == wx.EVT_TEXT.typeId:
            self.RECORDS.setfieldvalue(field, self.CONTROLID[field].GetValue())
        if not self.FORMDirty():
            self.subforms()  # use try with error code

    def _on_close_click(self, event):
        self.FORM.Close()

    def _on_close(self, event):
        if event.CanVeto():

            if not self.FORMDirty:
                for field in self.RECORDS.current().keys():
                    self.RECORDS.setfieldvalue(key, self.CONTROLID[field].GetValue())

                if self.LINKEDFORM == []:
                    return
                for key in self.LINKEDFORM.copy().keys():
                    if self.LINKEDFORM[key].FRAME != None:
                        self.LINKEDFORM[key].FRAME.Close()
                    else:
                        self.LINKEDFORM[key].FORM.Close(False)
                    if event.GetVeto():
                        event.Veto()
                        return

                if self.SUBFORM == []:
                    return
                for key in self.SUBFORM.copy().keys():
                    self.SUBFORM[key].FORM.Close(False)
                    if event.GetVeto():
                        event.Veto()
                        return
                if self.PARENT != None:
                    if self.FORM.Name in self.PARENT.LINKEDFORM:
                        self.PARENT.LINKEDFORM.pop(self.FORM.Name)
                    if self.FORM.Name in self.PARENT.SUBFORM:
                        self.PARENT.SUBFORM.pop(self.FORM.Name)

            else:
                event.Veto()

        try:
            self.FRAME.Destroy()
        except:
            pass
        finally:
            self.FORM.Destroy()

    def _setfieldsinrecord(self):
        if self.RECORDS == None:
            return
        cur = self.RECORDS.current().copy()
        if (cur == None) or cur["ID"] == None:
            return
        if "ID" in cur:
            cur.pop("ID")
        for key in cur:
            self.RECORDS.setfieldvalue(key, self.CONTROLID[key].GetValue())

    def _on_new_record_click(self, event):
        self.new_record()

    def _on_delete_record_click(self, event):
        if not self.FORMDirty():
            self.RECORDS.delete_record_from_DB()
            self.RECORDS.delete()
            rec = self.RECORDS.current()
            self.fill_form(rec)
            self._close_linked_forms()
            # self.linked_forms()
            self.subforms()
            self.FORM.Refresh()

    def _close_linked_forms(self):
        linked = self.LINKEDFORM.copy()
        for frm in linked:
            self.LINKEDFORM[frm].FORM.Close()
            self.LINKEDFORM.pop(frm)

    def _on_update_record_click(self, event):
        if self.validate_form() == True:
            for key in self.CONTROLID:
                if "readonly" in self.CONTROLDESCRIPTION[key]:
                    continue
                cur = self.RECORDS.current()
                if cur == None:
                    cur = self.RECORDS.blank_record()
                if key in cur:
                    self.RECORDS.setfieldvalue(key, self.CONTROLID[key].GetValue())
            self.RECORDS.update_current_record_in_DB()
            self.enable_navigation_buttons()
            dlg = wx.MessageDialog(
                self.FORM,
                "Record Updated.",
                "Updated",
                wx.OK,
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            return True
        else:
            self.disable_navigation_buttons()
            self.CONTROLID["btnUpdate"].Enable()
            self.FORM.Refresh()
            return False

    def _on_first_record_click(self, event):
        if not self.FORMDirty():
            self.RECORDS._restore_oringinal_records_values()
            self.RECORDS.first()
            rec = self.RECORDS.current()
            self.fill_form(rec)
            self._close_linked_forms()
            # self.linked_forms()
            self.subforms()
            self.FORM.Refresh()

    def _on_prev_record_click(self, event):
        if not self.FORMDirty():
            self.RECORDS._restore_oringinal_records_values()
            self.RECORDS.prev()
            rec = self.RECORDS.current()
            self.fill_form(rec)
            self._close_linked_forms()
            # self.linked_forms()
            self.subforms()
            self.FORM.Refresh()

    def _on_next_record_click(self, event):
        if not self.FORMDirty():
            self.RECORDS._restore_oringinal_records_values()
            self.RECORDS.next()
            rec = self.RECORDS.current()
            self.fill_form(rec)
            self._close_linked_forms()
            # self.linked_forms()
            self.subforms()
            self.FORM.Refresh()

    def _on_last_record_click(self, event):
        if not self.FORMDirty():
            self.RECORDS._restore_oringinal_records_values()
            self.RECORDS.last()
            rec = self.RECORDS.current()
            self.fill_form(rec)
            self._close_linked_forms()
            # self.linked_forms()
            self.subforms()
            self.FORM.Refresh()
