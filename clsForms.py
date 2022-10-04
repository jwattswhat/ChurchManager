"""
    frmForms.py - Church Manager Forms Classes
    Rev. Jonathan C. Watt
    July 1, 2021
"""
#
#   import wx classes
#
import os
import wx
import wx.dataview

#
#   import Pyhton classes
#
import json
import pyautogui

#
#   import framework classes
#
from clsConstants import CONST
from clsConfig import CONFIG
from clsFont import FONT
from clsLog import lg
import clsFont
import clsDB
from clsFields import getcontrolparameters, clsField
from clsSQL import clsSQL
import clsValidators
import fnUtil


class clsBASEForm:
    """
    clsBASEForm: Process a form
    Rev. Jonathan C. Watt
    July 2021

       Class Variables.

       Parameters

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
                panel,
                CONST.FORM_CONTINUE,
                label="Continue",
                size=(100, 30),
                pos=(10, 100),
            )
            self.btn = wx.Button(
                panel, CONST.FORM_CANCEL, label="Cancel", size=(100, 30), pos=(120, 100)
            )

    def __init__(
        self,
        parent,
        dbconnection,
        formname,
        controls=None,
        frmdescription=None,
        position=None,
        parentkey=None,
    ):
        lg.log(
            formname=formname,
            controls=controls,
            frmdescription=frmdescription,
            position=position,
        )

        self.PARENT = parent
        self.DBConnection = dbconnection  # Save the Connection Locally
        self.position = position
        self.parentkey = parentkey
        self.RECORDS = None

        self.LINKEDFORM = {}
        self.SUBFORM = {}

        self.FORMDESCRIPTON, self.CONTROLDESCRIPTION = self.load_form_from_json(
            formname
        )

        #   if form override is present do it here.
        if frmdescription is not None:
            self.FORMDESCRIPTON.update(frmdescription)

        self.override_linked_and_sub_forms()

        if "controls" not in self.FORMDESCRIPTON:
            self.FORMDESCRIPTON["controls"] = ["Navigation","Close"]
        if controls != None:
            self.FORMDESCRIPTON["controls"] = controls

        self.FORMDESCRIPTON, self.CONTROLDESCRIPTION = fnUtil.charactertopoint(
            self.FORMDESCRIPTON, self.CONTROLDESCRIPTION
        )

        #   add predfined controls to the control
        self.CONTROLDESCRIPTION = {
            **self.CONTROLDESCRIPTION,
            **self.process_predefined_controls(self.FORMDESCRIPTON["controls"]),
        }

        self.FRAME, self.FORM = self.process_form_type(self.FORMDESCRIPTON, position)

        self.CONTROLID = self.build_form()

        self.RECORDS = self.initialize_data_record(self.FORMDESCRIPTON)

        self.initialize_linked_forms()
        self.initialize_sub_forms()

        self.bind_form_controls()

    def override_linked_and_sub_forms(self):
        lg.log()
        if "linkedform" in self.FORMDESCRIPTON:
            for linkedform in self.FORMDESCRIPTON["linkedform"]:
                formdesc, controldesc = self.load_form_from_json(linkedform)
                formdesc.update(self.FORMDESCRIPTON["linkedform"][linkedform])
                self.FORMDESCRIPTON["linkedform"][linkedform] = formdesc
        if "subform" in self.FORMDESCRIPTON:
            for subform in self.FORMDESCRIPTON["subform"]:
                formdesc, controldesc = self.load_form_from_json(subform)
                formdesc.update(self.FORMDESCRIPTON["subform"][subform])
                self.FORMDESCRIPTON["subform"][subform] = formdesc

    def process_predefined_controls(self, controls):
        lg.log(controls=controls)

        lastcolumn = self.FORMDESCRIPTON["size"][0]
        lastline = self.FORMDESCRIPTON["size"][1] - 5

        NavControls = {}
        self.NavControlsPresent = False
        x = 5  # start 5 in
        if "Navigation" in controls:
            self.NavControlsPresent = True

            for key in CONST.btnNavigationCONTROLS["Navigation"]:
                NavControls[key] = CONST.btnNavigationCONTROLS["Navigation"][key]
                NavControls[key]["pos"] = [
                    x,
                    lastline,
                ]  # - CONST.btnNavigationCONTROLS["Navigation"][key]["size"][1]]
                x += CONST.btnNavigationCONTROLS["Navigation"][key]["size"][0]
        else:
            if "Update" in controls:
                NavControls["btnUpdate"] = CONST.btnNavigationCONTROLS["Navigation"][
                    "btnUpdate"
                ]
                NavControls["btnUpdate"]["pos"] = [
                    x,
                    lastline,
                ]  # -CONST.btnNavigationCONTROLS["Navigation"]["btnUpdate"]["size"][1]]

        #   Predefined Controls "Close"
        self.ClosePresent = False
        if "Close" in controls:
            self.ClosePresent = True
            NavControls["btnClose"] = CONST.btnNavigationCONTROLS["Close"]["btnClose"]
            NavControls["btnClose"]["pos"] = [
                lastcolumn
                - CONST.btnNavigationCONTROLS["Close"]["btnClose"]["size"][0],
                lastline,
            ]  # -CONST.btnNavigationCONTROLS["Close"]["btnClose"]["size"][1]]

        return NavControls

    def process_form_type(self, formdescription, position):
        """
        parameters
            formdescription["type"]
                "Dialog" - for Modal Forms
                "Panel" - Normal
                "StaticBox" - for SubForms
            position - override position for form

        """
        lg.log(formdescription=formdescription, position=position)
        if position is not None:
            formdescription["pos"] = [position[0], position[1]]

        if formdescription["type"] == "Dialog":
            formdescription["size"][0] += 30
            formdescription["size"][1] += 70
            FRAME = wx.Dialog(
                None, id=wx.ID_ANY, **getcontrolparameters(formdescription)
            )
            FORM = FRAME
        elif formdescription["type"] == "Panel":
            #   Panel must have a frame as a Parent.
            #   Invisible to the user.
            size = [formdescription["size"][0] + 30, formdescription["size"][1] + 70]
            FRAME = wx.Frame(
                None,
                id=wx.ID_ANY,
                title=formdescription["title"],
                pos=formdescription["pos"],
                size=size,
            )
            formdescription["pos"] = [0, 0]
            FORM = wx.Panel(FRAME, wx.ID_ANY, **getcontrolparameters(formdescription))
        elif formdescription["type"] == "StaticBox":
            FORM = wx.StaticBox(
                self.PARENT.FORM, wx.ID_ANY, **getcontrolparameters(formdescription)
            )
            FRAME = FORM
            FRAME.SetFont(FONT.Get_Current_Font())

        return FRAME, FORM

    def load_form_from_json(self, Form):
        """
        loads form description from a JSON file.
        """
        global CONFIG
        lg.log(Form=Form)

        FormLocation = CONFIG.get_Config_Value("Location", "Form")

        formname = FormLocation + Form + ".json"
        f = open(
            formname,
        )
        jsonfrm = json.load(f)
        return jsonfrm[Form + "FORM"]["FORM"], jsonfrm[Form + "FORM"]["CONTROLS"]

    def build_form(self):
        lg.log()
        controlid = {}
        if "readonly" in self.FORMDESCRIPTON:
            readonly = True
        else:
            readonly = False
        for key in self.CONTROLDESCRIPTION.copy():

            if readonly:
                self.CONTROLDESCRIPTION[key].update({"readonly": True})

            if "readonlyfields" in self.FORMDESCRIPTON:
                if key in self.FORMDESCRIPTON["readonlyfields"]:
                    self.CONTROLDESCRIPTION[key].update({"readonly": True})

            fld = clsField(
                self, wx.ID_ANY, self.CONTROLDESCRIPTION[key], self.DBConnection
            )
            controlid.update({key: fld.FIELD})
        return controlid

    def initialize_data_record(self, formdescription):
        lg.log(formdescription=formdescription)
        if "table" in formdescription:
            return clsDB.clsRecord(self.DBConnection, formdescription["table"])

    def display_form_data(self, table=None, parentrecord=None):
        lg.log(table=table, parentrecord=parentrecord)
        if "table" not in self.FORMDESCRIPTON:
            return None

        if table is None:
            table = self.FORMDESCRIPTON["table"].copy()

        result = self.RECORDS.load_records(table, parentrecord)
        if result == "NewRecord":
            if self.parentkey != None:
                self.RECORDS._record[self.RECORDS._position][
                    self.parentkey[0]
                ] = self.parentkey[1]
        self._display_records(table, parentrecord)

    def _load_DataViewListCtrl(self):
        for field in self.CONTROLID:
            if self.CONTROLDESCRIPTION[field]["type"] == "DataViewListCtrl":
                self.CONTROLID[field].SetValueTable(
                    self.RECORDS.current(), self.CONTROLDESCRIPTION[field]["table"]
                )
        return None

    def _display_records(self, table=None, parentrecord=None):
        lg.log(table=table, parentrecord=parentrecord)
        if "table" not in self.FORMDESCRIPTON:
            return None

        if table is None:
            table = self.FORMDESCRIPTON["table"]

        self.fill_form(self.RECORDS.current())

        for linkedfrm in self.LINKEDFORM:
            self.LINKEDFORM[linkedfrm].display_form_data(
                self.FORMDESCRIPTON["linkedform"][linkedfrm]["table"],
                self.RECORDS.current(),
            )

        for subfrm in self.SUBFORM:
            self.SUBFORM[subfrm].display_form_data(
                self.FORMDESCRIPTON["subform"][subfrm]["table"], self.RECORDS.current()
            )

        self._load_DataViewListCtrl()

    def update_choices(self):
        lg.log()
        for field in self.CONTROLID:
            if self.CONTROLDESCRIPTION[field]["type"] == "ComboBox":
                choices = self.CONTROLID[field].choices.Load_Choices(
                    self.CONTROLDESCRIPTION[field]
                )
                if choices != None:
                    self.CONTROLDESCRIPTION.update({"choices": choices})
                    value = self.CONTROLID[field].GetValue()
                    self.CONTROLID[field].Set(choices)
                    self.CONTROLID[field].ChangeValue(value)

    def fill_form(self, record):
        """
        fill the form with editable data from the Read record
        """
        lg.log(record=record)
        for key in record:
            if key == "ID":
                continue
            if key not in self.CONTROLDESCRIPTION:
                continue
            match self.CONTROLDESCRIPTION[key]["type"]:
                case "TextCtrl":
                    self.CONTROLID[key].ChangeValue(record[key])
                case "TextNumber":
                    self.CONTROLID[key].ChangeValue(record[key])
                case "ComboBox":
                    self.CONTROLID[key].ChangeValue(record[key])

                case _:
                    self.CONTROLID[key].SetValue(record[key])

    def initialize_linked_forms(self):
        lg.log()

        if "linkedform" not in self.FORMDESCRIPTON:
            return

        for lnkdfrm in self.FORMDESCRIPTON["linkedform"]:
            if "bindbtn" not in self.FORMDESCRIPTON["linkedform"][lnkdfrm]:
                self.open_linked_form(lnkdfrm)

    def open_linked_form(self, lnkdfrm, record=None):
        """
        open_linked_form - setup open linked form.
        """
        lg.log(lnkdfrm=lnkdfrm, record=record)

        pk = []
        parentkey = self.FORMDESCRIPTON["linkedform"][lnkdfrm].get("parentkey")
        if parentkey != None:
            pk.append(parentkey[0])
            pk.append(self.RECORDS._record[self.RECORDS._position][parentkey[1]])
        if pk == []:
            pk = None

        LinkedForm = clsForm(
            self,
            dbconnection=self.DBConnection,
            formname=lnkdfrm,
            frmdescription=self.FORMDESCRIPTON["linkedform"][lnkdfrm],
            controls=self.FORMDESCRIPTON["linkedform"][lnkdfrm]["controls"],
            # position=pyautogui.position(),
            parentkey=pk,
        )
        LinkedForm.display_form_data(
            self.FORMDESCRIPTON["linkedform"][lnkdfrm].get("table", None),
            self.RECORDS.current(),
        )
        self.LINKEDFORM.update({lnkdfrm: LinkedForm})
        return LinkedForm.show()

    def initialize_sub_forms(self):
        lg.log()
        if "subform" not in self.FORMDESCRIPTON:
            return

        for subfrm in self.FORMDESCRIPTON["subform"]:

            SubForm = clsForm(
                self,
                dbconnection=self.DBConnection,
                formname=subfrm,
                controls=self.FORMDESCRIPTON["subform"][subfrm]["controls"],
                frmdescription=self.FORMDESCRIPTON["subform"][subfrm],
            )

            self.SUBFORM.update({subfrm: SubForm})
            return SubForm.show()

    def bind_form_controls(self):
        lg.log()
        self.FORM.Bind(wx.EVT_CLOSE, self._on_close)

        if "linkedform" in self.FORMDESCRIPTON:
            for lnkdfrm in self.FORMDESCRIPTON["linkedform"]:
                if "bindbtn" in self.FORMDESCRIPTON["linkedform"][lnkdfrm]:
                    self.FORM.Bind(
                        wx.EVT_BUTTON,
                        self._buttonclick,
                        self.CONTROLID[
                            self.FORMDESCRIPTON["linkedform"][lnkdfrm]["bindbtn"]
                        ],
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
            if "openbtn" in self.CONTROLDESCRIPTION[field]:
                self.CONTROLID[field].Bind(wx.EVT_BUTTON, self._openfileevent)

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
        elif "controls" in self.FORMDESCRIPTON:
            if "Update" in self.FORMDESCRIPTON["controls"]:
                self.FORM.Bind(
                    wx.EVT_BUTTON,
                    self._on_update_record_click,
                    self.CONTROLID["btnUpdate"],
                )

        for field in self.CONTROLID:
            if type(self.CONTROLID[field]).__name__ == "clsComboBox":
                if self.CONTROLDESCRIPTION[field].get("refreshform") == True:
                    self.FORM.Bind(
                        wx.EVT_TEXT, self._captureevent, self.CONTROLID[field]
                    )

    def disable_button(self, name):
        lg.log()
        self.CONTROLID[name].Disable()

    def enable_button(self, name):
        lg.log()
        self.CONTROLID[name].Enbable()

    def enable_navigation_buttons(self):
        lg.log()
        # pre-defined buttons
        if self.NavControlsPresent:
            self.CONTROLID["btnNew"].Enable()
            self.CONTROLID["btnDelete"].Enable()
            self.CONTROLID["btnFirst"].Enable()
            self.CONTROLID["btnPrev"].Enable()
            self.CONTROLID["btnNext"].Enable()
            self.CONTROLID["btnLast"].Enable()
            self.CONTROLID["btnUpdate"].Enable()

    def disable_navigation_buttons(self):
        lg.log()
        # pre-defined buttons
        if self.NavControlsPresent:
            self.CONTROLID["btnNew"].Disable()
            self.CONTROLID["btnDelete"].Disable()
            self.CONTROLID["btnFirst"].Disable()
            self.CONTROLID["btnPrev"].Disable()
            self.CONTROLID["btnNext"].Disable()
            self.CONTROLID["btnLast"].Disable()
            self.CONTROLID["btnUpdate"].Disable()

    def validate_form(self):
        lg.log()
        if self.FORM.Validate():
            return True
        else:
            return False

    def update_screen_to_record(self):
        lg.log()
        if self.RECORDS.isempty():
            return None
        for field in self.RECORDS.current().keys():
            if field == "ID":
                continue
            self.RECORDS.setfieldvalue(field, self.CONTROLID[field].GetValue())

    def show(self):
        lg.log()
        if "modal" in self.FORMDESCRIPTON:
            return self.FRAME.ShowModal()
        try:
            self.FRAME.Show()
        except:
            pass
        finally:
            self.FORM.Show()

    def showmodal(self):
        lg.log()
        return self.FRAME.ShowModal()

    def new_record(self):
        lg.log()
        if not self.FORMDirty():
            self.RECORDS.add(self.RECORDS.sql.get_blank_record())
            if self.parentkey != None:
                self.RECORDS._record[self.RECORDS._position][
                    self.parentkey[0]
                ] = self.parentkey[1]
            self.fill_form(self.RECORDS._record[self.RECORDS._position])
            self._close_linked_forms()
            if self.NavControlsPresent:
                self.disable_navigation_buttons()
                self.CONTROLID["btnUpdate"].Enable()

    def set_all_controls_to_normal_color(self):
        lg.log()
        for field in self.CONTROLID:
            self.CONTROLID[field].SetNormalColor()

    #
    #   Evant Handlers
    #
    def _translateevent(self, eventstring):
        lg.log()
        evt = None
        if eventstring == "EVT_TEXT":
            evt = wx.EVT_TEXT
        return evt

    def _buttonclick(self, event):
        lg.log()
        btn = event.GetEventObject().GetName()
        for lnkdfrm in self.FORMDESCRIPTON["linkedform"]:
            if btn == self.FORMDESCRIPTON["linkedform"][lnkdfrm]["bindbtn"]:
                if "linkedfield" in self.CONTROLDESCRIPTION[btn]:
                    row = self.CONTROLID[
                        self.CONTROLDESCRIPTION[btn]["linkedfield"]
                    ].GetSelectedRow()
                    returnvalue = self.open_linked_form(lnkdfrm, row)
                    if returnvalue == wx.ID_OK:
                        row = self.CONTROLID[
                            self.CONTROLDESCRIPTION[btn]["linkedfield"]
                        ].GetSelectedRowID()
                        rec = self.LINKEDFORM[lnkdfrm].update_form_to_record()
                        self.CONTROLID[
                            self.CONTROLDESCRIPTION[btn]["linkedfield"]
                        ].SetValueRecord(row, rec)
                        self.CONTROLID[
                            self.CONTROLDESCRIPTION[btn]["linkedfield"]
                        ].Refresh()
                else:
                    self.open_linked_form(lnkdfrm)

    def _capturemouse(self, event):  # <TODO> implement.
        lg.log()
        field = event.GetEventObject().GetName()

    def _captureevent(self, event):
        lg.log()
        if "table" not in self.FORMDESCRIPTON:
            return
        if "name" not in self.FORMDESCRIPTON["table"]:
            return
        field = event.GetEventObject().GetName()
        evnttype = event.GetEventType()
        if evnttype == wx.EVT_TEXT.typeId:

            self.RECORDS.setfieldvalue(field, self.CONTROLID[field].GetValue())
            self._display_records(self.FORMDESCRIPTON["table"])

            for linkedform in self.LINKEDFORM:
                table = self.LINKEDFORM[linkedform].FORMDESCRIPTON["table"].copy()
                if "condition" in table:
                    table["condition"] = self.RECORDS.sql.condition(
                        table["condition"], self.RECORDS.current()
                    )
                self.LINKEDFORM[linkedform].display_form_data(table)

            for subform in self.SUBFORM:
                table = self.SUBFORM[subform].FORMDESCRIPTON["table"].copy()
                table["condition"] = self.RECORDS.sql.condition(
                    table["condition"], self.RECORDS.current()
                )
                self.SUBFORM[subform].display_form_data(table)

    def _openfileevent(self, event):
        lg.log()
        file = None
        field = event.GetEventObject().GetName()
        evnttype = event.GetEventType()
        openctrl = self.CONTROLDESCRIPTION[field]["openbtn"]
        match self.CONTROLDESCRIPTION[openctrl]["type"]:
            case "FilePickerCtrl":
                path = CONFIG.get_Config_Value(
                    self.CONTROLDESCRIPTION[openctrl]["directory"][0],
                    self.CONTROLDESCRIPTION[openctrl]["directory"][1],
                )
                file = path + self.CONTROLID[openctrl].GetPath()
            case "TextCtrl":
                file = self.CONTROLID[openctrl].GetValue()
            case "ComboBox":
                table = self.CONTROLDESCRIPTION[openctrl]["table"]
                sql = clsSQL(self.DBConnection, table, self.RECORDS.current())
                SQL = sql.select()
                cursor = self.DBConnection.cursor()
                cursor.execute(SQL)
                row = cursor.fetchone()
                file = row[0]
            case otherwise:
                file = None
        if file != None:
            os.startfile(file)

    def _on_close_click(self, event):
        lg.log()
        self.FORM.Close()

    def _on_close(self, event):
        lg.log()
        if self.RECORDS == None:  # for no record forms.
            try:
                self.FRAME.Destroy()
            except:
                #            pass
                #        finally:
                self.FORM.Destroy()
            return

        if self.RECORDS.isempty():
            return

        if not self.FORMDirty():

            if self.LINKEDFORM:
                for linkedform in self.LINKEDFORM.copy().keys():
                    if self.LINKEDFORM[linkedform].FRAME is not None:
                        self.LINKEDFORM[linkedform].FRAME.Close()
                    else:
                        self.LINKEDFORM[linkedform].FORM.Close()
                    if linkedform in self.LINKEDFORM:
                        return

            if self.SUBFORM:
                for subform in self.SUBFORM.copy().keys():
                    self.SUBFORM[subform].FORM.Close()
                    if subform in self.SUBFORM:
                        return

            if self.PARENT:
                if self.FORM.Name in self.PARENT.LINKEDFORM:
                    self.PARENT.LINKEDFORM.pop(self.FORM.Name)
                    self.PARENT.update_choices()
                if self.FORM.Name in self.PARENT.SUBFORM:
                    self.PARENT.SUBFORM.pop(self.FORM.Name)

            try:
                self.FRAME.Destroy()
            except:
                #            pass
                #        finally:
                self.FORM.Destroy()

    def FORMDirty(self):
        lg.log()

        if "readonly" not in self.FORMDESCRIPTON:
            self.update_screen_to_record()

            dirtyfields = self.RECORDS.recordisdirty()
            if dirtyfields:
                for field in dirtyfields:
                    self.CONTROLID[field].SetWarningColor()
                dlg = self._dirtydialog(self.FORM, title="Form Modified(dirty)")
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == CONST.FORM_CANCEL:
                    return True

        return False

    def _on_new_record_click(self, event):
        lg.log()
        self.new_record()

    def _on_delete_record_click(self, event):
        lg.log()
        if not self.FORMDirty():
            self.RECORDS.delete_record_from_DB()
            dlg = wx.MessageDialog(
                self.FORM,
                "Record Deleted.",
                "Deleted",
                wx.OK,
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            self.fill_form(self.RECORDS.current())
            self._close_linked_forms()

    def _close_linked_forms(self):
        lg.log()
        linked = self.LINKEDFORM.copy()
        for frm in linked:
            self.LINKEDFORM[frm].FORM.Close()
            self.LINKEDFORM.pop(frm)

    def _on_update_record_click(self, event):
        lg.log()
        self.update_screen_to_record()
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
        self.set_all_controls_to_normal_color()

    def _first_prev_next_last(self, firstprevnextlast):
        lg.log()
        if not self.FORMDirty():

            self.RECORDS._record[
                self.RECORDS._position
            ] = self.RECORDS.original.restore()

            if firstprevnextlast == CONST.FORM_FIRST:
                self.RECORDS.first()
            elif firstprevnextlast == CONST.FORM_PREV:
                self.RECORDS.prev()
            elif firstprevnextlast == CONST.FORM_NEXT:
                self.RECORDS.next()
            elif firstprevnextlast == CONST.FORM_LAST:
                self.RECORDS.last()

            self._display_records(self.FORMDESCRIPTON["table"], self.RECORDS.current())

    def _on_first_record_click(self, event):
        lg.log()
        self._first_prev_next_last(CONST.FORM_FIRST)

    def _on_prev_record_click(self, event):
        lg.log()
        self._first_prev_next_last(CONST.FORM_PREV)

    def _on_next_record_click(self, event):
        lg.log()
        self._first_prev_next_last(CONST.FORM_NEXT)

    def _on_last_record_click(self, event):
        lg.log()
        self._first_prev_next_last(CONST.FORM_LAST)


class clsForm(clsBASEForm):
    class MergeorReplaceChecklist(wx.Dialog):
        def __init__(self, parent, title):
            super().__init__(parent, title=title, size=(400, 200))
            panel = wx.Panel(self)
            self.text = wx.StaticText(
                panel,
                wx.ID_ANY,
                label="Merge or Replace this CheckList with existing?",
                pos=(10, 50),
            )
            self.btn = wx.Button(
                panel, wx.ID_OK, label="Merge", size=(100, 30), pos=(10, 100)
            )
            self.btn = wx.Button(
                panel, wx.ID_CANCEL, label="Replace", size=(100, 30), pos=(120, 100)
            )

    def bind_form_controls(self):
        lg.log()
        if "CheckListID" in self.CONTROLID:
            self.CONTROLID["CheckListID"].Bind(wx.EVT_TEXT, self._fillchecklist)
            self.CONTROLID["CheckList"].Bind(
                wx.EVT_CHECKLISTBOX, self._checkboxallchecked
            )
        if "btnHymnSearchByHymn" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByHymn"],
            )
        if "btnHymnSearchByTitle" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByTitle"],
            )
        if "btnHymnSearchByBible" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByBible"],
            )
        if "btnHymnSearchByCategory" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByCategory"],
            )
        if "btnHymnSearchByNote" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchByNote"],
            )

        if "btnHymnSearchAdd" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnsearch,
                self.CONTROLID["btnHymnSearchAdd"],
            )

        if "btnHymnUsageUpdate" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON,
                self._processhymnusage,
                self.CONTROLID["btnHymnUsageUpdate"],
            )

        if "btnHymnUsageAdd" in self.CONTROLID:
            self.FORM.Bind(
                wx.EVT_BUTTON, self._processhymnusage, self.CONTROLID["btnHymnUsageAdd"]
            )

        super().bind_form_controls()

    def _fillchecklist(self, event):
        field = event.GetEventObject().GetName()
        evnttype = event.GetEventType()
        ID = self.CONTROLID[field].GetValue()
        if ID is None:
            return None
        sql = "SELECT CheckList FROM tblCheckList WHERE ID = {ID};".format(ID=ID)
        cursor = self.DBConnection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        newchecklist = json.loads(row[0])
        fld = self.CONTROLID["CheckList"].GetValue()
        if fld != None:
            existingchecklist = json.loads(fld)
            if len(existingchecklist) == 0:
                self.CONTROLID["CheckList"].SetValue(json.dumps(newchecklist))
                self.CONTROLID["CheckListComplete"].SetValue(False)
                return
        dlg = self.MergeorReplaceChecklist(self.FORM, title="CheckList Merge / Replace")
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:  # ok is merge
            self.CONTROLID["CheckList"].SetValue(
                json.dumps(newchecklist | existingchecklist)
            )
        else:  # cancel is replace
            self.CONTROLID["CheckList"].SetValue(json.dumps(newchecklist))
        self.CONTROLID["CheckListComplete"].SetValue(False)

    def _checkboxallchecked(self, event):
        lg.log()
        field = event.GetEventObject().GetName()
        evnttype = event.GetEventType()
        ID = self.CONTROLID[field].GetValue()
        if len(self.CONTROLID[field].Items) == len(
            self.CONTROLID[field].GetCheckedItems()
        ):
            self.CONTROLID["CheckListComplete"].SetValue(True)
        else:
            self.CONTROLID["CheckListComplete"].SetValue(False)

    def _processhymnsearch(self, event):
        lg.log()
        field = event.GetEventObject().GetName()
        eventtype = event.GetEventType()
        if field == "btnHymnSearchAdd":
            if self.CONTROLID["UsedAs"].GetValueText() is None:
                dlg = wx.MessageDialog(self.FORM, "'Used As' cannot be blank")
                dlg.ShowModal()
                dlg.Destroy()
                return
            usedas = self.CONTROLID["UsedAs"].GetValueText()
            row = self.CONTROLID["dvlHymnList"].GetSelectedRow()
            if row is None:
                dlg = wx.MessageDialog(self.FORM, "No Hymn Selected")
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.PARENT.CONTROLID["HymnID"].ChangeValue(row["ID"])
            self.PARENT.CONTROLID["UsedAs"].ChangeValue(usedas)
            self.PARENT.LINKEDFORM.pop("frmHymnSearch")
            try:
                self.FRAME.Destroy()
            except:
                pass
            finally:
                self.FORM.Destroy()

        elif "Search" in self.CONTROLID:
            search = self.CONTROLID["Search"].GetValue()
            if search == "":
                return None
            table = {}
            table["name"] = "tblHymn"
            table["fields"] = ["ID", "Hymn", "Title", "BibleText", "Category", "Note"]
            table["condition"] = "{column} LIKE '%{search}%'"

            if field == "btnHymnSearchByHymn":
                table["condition"] = table["condition"].format(
                    column="Hymn", search=search
                )
            elif field == "btnHymnSearchByTitle":
                table["condition"] = table["condition"].format(
                    column="Title", search=search
                )
            elif field == "btnHymnSearchByBible":
                table["condition"] = table["condition"].format(
                    column="BibleText", search=search
                )
            elif field == "btnHymnSearchByCategory":
                table["condition"] = table["condition"].format(
                    column="Category", search=search
                )
            elif field == "btnHymnSearchByNote":
                table["condition"] = table["condition"].format(
                    column="Note", search=search
                )
            if "dvlHymnList" in self.CONTROLID:
                self.CONTROLID["dvlHymnList"].SetValueTable(table=table)

    def _processhymnusage(self, event):
        lg.log()
        field = event.GetEventObject().GetName()
        eventtype = event.GetEventType()
        if field == "btnHymnSearchAdd":
            row = self.CONTROLID["dvlHymnList"].GetSelectedRow()
            self.CONTROLID["dvlHymnUsage"].SetValue(row)
        if field == "btnHymnUsageUpdate":
            row = self.CONTROLID["dvlHymnUsage"].GetSelectedRow()
            self.open_linked_form("frmHymnUsage")
