# -*- coding: UTF-8 -*-
# A part of the CustomAppModulesMapper addon for NVDA
# Copyright (C) 2024 Marlon Sousa
# This file is covered by the MIT License.
# See the file COPYING.txt for more details.

from dataclasses import dataclass
from enum import Enum
from functools import reduce
from . import mapperHandler
from .mapperHandler import Mapping
import addonHandler
from gui import guiHelper
from logHandler import log
import wx
import gui
import gui.settingsDialogs

addonHandler.initTranslation()


# Translators: shown in the module column for an application that has been deliberately detached from
# any app module (see the "Unassociate" action), instead of the internal notAssociated module name.
NOT_ASSOCIATED_LABEL = _("(not associated)")


class CustomMappingAction(Enum):
    ADD = 1
    IGNORE = 2
    MODIFY = 3
    REMOVE = 4


@dataclass
class CustomMappingItem(mapperHandler.Mapping):
    action: CustomMappingAction


class CustomAppModuleMapperSettingPanel(gui.settingsDialogs.SettingsPanel):
    # Translators: This is the label for the Custom Application Module Mapper settings category in NVDA Settings screen. # noqa E501
    title = _("Custom Application Module Mapper")

    def makeSettings(self, settingsSizer):
        self.mappings = {}
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        # Translators: label used to toggle the auto check update.
        self.mappingsList = sHelper.addLabeledControl(
            _("Mappings"),
            wx.ListCtrl,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL
        )
        self.mappingsList.InsertColumn(0, _("App Name"))
        self.mappingsList.InsertColumn(1, _("Module Name"))
        actionsHelper = guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
        # Translators: button that opens the dialog to associate an application with an app module
        # (mapping it to a module, or detaching it by choosing "not associated").
        self.addButton = actionsHelper.addItem(wx.Button(self, label=_("&Associate app...")))
        # Translators: button that disassociates the selected application, removing its custom mapping
        # and restoring the module it originally used.
        self.removeButton = actionsHelper.addItem(wx.Button(self, label=_("&Disassociate")))
        sHelper.addItem(actionsHelper)
        settingsSizer.Fit(self)
        self.bindEvents()
        self.buildMappingsList()
        self.selectCurrentApp()
        self.updateDisassociateButton()

    def bindEvents(self):
        self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        self.removeButton.Bind(wx.EVT_BUTTON, self.onRemove)
        # Disassociate acts on the selected mapping, so keep its enabled state in sync with the selection.
        self.mappingsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSelectionChanged)
        self.mappingsList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSelectionChanged)

    def updateDisassociateButton(self):
        # There is nothing to disassociate unless a mapping is selected.
        self.removeButton.Enable(self.mappingsList.GetFirstSelected() != -1)

    def onListSelectionChanged(self, evt):
        self.updateDisassociateButton()
        evt.Skip()

    def selectCurrentApp(self):
        # Convenience: when the application the user was last in already has a custom mapping, select it
        # in the list on open, so it is immediately ready to remove or re-associate.
        current = mapperHandler.getLastForegroundApp()
        if current:
            self.selectApp(current[0])

    def buildMappingsList(self):
        customModulesMapping = mapperHandler.getCustomModulesMapping()
        # Key the model by the lowercased executable name so lookups and duplicate detection are
        # case-insensitive, matching how NVDA matches executables (it lowercases their names).
        self.mappings = reduce(
            lambda acc, item: acc.update({
                item.app.lower(): CustomMappingItem(
                    item.app.lower(),
                    item.appModule,
                    item.appOriginalModule,
                    CustomMappingAction.IGNORE
                )
            }) or acc,
            customModulesMapping,
            {}
        )
        self.refreshList()

    def refreshList(self):
        self.mappingsList.DeleteAllItems()
        mappingModel = dict(
            filter(
                lambda item: item[1].action != CustomMappingAction.REMOVE,
                self.mappings.items()
            )
        )
        sorted_keys = sorted(mappingModel.keys())
        for key in sorted_keys:
            mapping = self.mappings[key]
            self.mappingsList.Append((mapping.app, self.moduleDisplayName(mapping.appModule)))
        self.updateDisassociateButton()

    def moduleDisplayName(self, moduleName: str) -> str:
        # Detached applications are stored as a mapping to the notAssociated sentinel module, but that
        # internal name is meaningless to users, so show a friendly label for them instead.
        if moduleName == mapperHandler.NOT_ASSOCIATED_MODULE:
            return NOT_ASSOCIATED_LABEL
        return moduleName

    def onAddDialogResumed(self, item: CustomMappingItem):
        self.mappings[item.app] = item
        self.refreshList()

    def onAdd(self, evt):
        # Translators: title of the dialog used to associate an application with an app module.
        title = _("Associate application")
        gui.mainFrame.prePopup()
        # Pass the mappings currently staged in this panel so the dialog can tell whether the app
        # the user types is already mapped (MODIFY) or new (ADD), and preserve its original module.
        # Also pass the last real foreground application so the dialog can pre-fill it, saving the user
        # from typing the exact executable name of the app they just came from.
        dialog = ModuleMappingDialog(self, title, self.mappings, mapperHandler.getLastForegroundApp())
        if dialog.ShowModal() == wx.ID_OK:
            self.onAddDialogResumed(dialog.result)
        dialog.Destroy()
        gui.mainFrame.postPopup()

    def selectApp(self, app: str):
        # Move selection/focus to the row for the given app if present, so it is announced and visible.
        app = app.lower()
        for index in range(self.mappingsList.GetItemCount()):
            if self.mappingsList.GetItemText(index) == app:
                self.mappingsList.Select(index)
                self.mappingsList.Focus(index)
                return

    def onRemove(self, evt):
        selected = self.mappingsList.GetFirstSelected()
        if selected == -1:
            return
        app = self.mappingsList.GetItemText(selected).lower()
        self.mappings[app].action = CustomMappingAction.REMOVE
        self.refreshList()
        # Keep focus on the list instead of letting it jump to the dialog's OK button when the
        # Disassociate button we were on becomes disabled. Select a neighbouring row when one remains.
        count = self.mappingsList.GetItemCount()
        if count:
            neighbour = min(selected, count - 1)
            self.mappingsList.Select(neighbour)
            self.mappingsList.Focus(neighbour)
        self.mappingsList.SetFocus()

    def onSave(self):
        mustRestart = False
        newMappings = []
        for item in self.mappings.values():
            if item.action == CustomMappingAction.ADD:
                mapperHandler.associateAppModule(item.app, item.appModule)
                newMappings.append(Mapping(item.app, item.appModule, item.appOriginalModule))
                mustRestart = True
                log.info(f"Associating new mapping: {item.app} app with {item.appModule} module")
            elif item.action == CustomMappingAction.REMOVE:
                mapperHandler.disassociateAppModule(item.app)
                mustRestart = True
                log.info(f"Disassociating mapping: {item.app} app with {item.appModule} module")
                if item.appOriginalModule is not None:
                    mapperHandler.associateAppModule(item.app, item.appOriginalModule)
                    log.info(f"Restoring original mapping: {item.app} app with {item.appOriginalModule} module") # noqa E501
            elif item.action == CustomMappingAction.MODIFY:
                mapperHandler.associateAppModule(item.app, item.appModule)
                log.info(f"Modifying mapping: {item.app} app with {item.appModule} module")
                newMappings.append(Mapping(item.app, item.appModule, item.appOriginalModule))
                mustRestart = True
            else:
                newMappings.append(Mapping(item.app, item.appModule, item.appOriginalModule))
        if mustRestart:
            mapperHandler.restart()
        mapperHandler.customModulesMapping = newMappings
        mapperHandler.persist()


class ModuleMappingDialog(
    gui.contextHelp.ContextHelpMixin,
    wx.Dialog,  # wxPython does not seem to call base class initializer, put last in MRO
):

    def __init__(self, parent, title, currentMappings, prefill=None):
        super(ModuleMappingDialog, self).__init__(parent, title=title)
        self.result = None
        # currentMappings maps a lowercased app name to the CustomMappingItem currently staged for it.
        self.currentMappings = currentMappings
        # prefill is an optional (executableName, currentModuleName) tuple describing the last real
        # foreground application, used to pre-populate the fields.
        self.prefill = prefill
        self.availableModules = mapperHandler.getAllAvailableAppModules()
        # Modules offered to the user: the friendly "not associated" label first (so detaching an app is
        # just another choice in this list, and is easy to reach), then the real modules alphabetically.
        self.moduleChoices = [NOT_ASSOCIATED_LABEL] + self.availableModules
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        # Translators: label for the application field in the associate application dialog.
        appLabelText = _("&App")
        # Editable combo: pre-populated with the applications currently open so the user can pick one
        # without typing, while still being free to type an executable name that is not running.
        appChoices = self.buildAppChoices()
        self.appComboBox = sHelper.addLabeledControl(appLabelText, wx.ComboBox, choices=appChoices)

        # Translators: label for the app module field in the associate application dialog.
        appModuleLabelText = _("App &module")
        appLabel = wx.StaticText(self, label=appModuleLabelText)
        self.appModulesComboBox = wx.ComboBox(self, choices=self.moduleChoices, style=wx.CB_READONLY)
        sHelper.addItem(appLabel)
        sHelper.addItem(self.appModulesComboBox)

        sHelper.addDialogDismissButtons(wx.OK | wx.CANCEL, separated=True)
        # CreateButtonSizer parents the OK button to the dialog, so it can be found and toggled directly.
        self.okButton = self.FindWindow(wx.ID_OK)

        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        mainSizer.Fit(self)
        self.SetSizer(mainSizer)
        self.applyPrefill()
        self.bindDialogEvents()
        self.updateOkState()
        self.appComboBox.SetFocus()

    def buildAppChoices(self):
        apps = list(mapperHandler.getRunningApps())
        # Make sure the pre-filled application is offered even if NVDA is not currently tracking it.
        if self.prefill and self.prefill[0] and self.prefill[0] not in apps:
            apps.append(self.prefill[0])
        return sorted(apps)

    def moduleToDisplay(self, moduleName):
        # Map an internal module name to what is shown in the combo (the detach sentinel is friendlier).
        if moduleName == mapperHandler.NOT_ASSOCIATED_MODULE:
            return NOT_ASSOCIATED_LABEL
        return moduleName

    def displayToModule(self, display):
        # Inverse of moduleToDisplay: turn the selected combo entry back into an internal module name.
        if display == NOT_ASSOCIATED_LABEL:
            return mapperHandler.NOT_ASSOCIATED_MODULE
        return display

    def applyPrefill(self):
        # Pre-populate the app field with the last real foreground application and preselect the module
        # it currently uses (including "not associated" if it is already detached).
        if not self.prefill:
            return
        self.appComboBox.SetValue(self.prefill[0])
        self.preselectModuleForApp()

    def preselectModuleForApp(self):
        # Show the module the entered application is currently associated with, so a re-association
        # starts from its current state (and the duplicate guard is visible). Clear the module when the
        # application is unknown. Called whenever the app field changes, so switching apps mid-dialog
        # keeps the module in sync with the chosen app rather than the one originally pre-filled.
        currentModule = self.currentModuleFor(self.getEnteredApp())
        if currentModule is not None:
            display = self.moduleToDisplay(currentModule)
            if display in self.moduleChoices:
                self.appModulesComboBox.SetValue(display)
                return
        self.appModulesComboBox.SetSelection(wx.NOT_FOUND)

    def bindDialogEvents(self):
        # When the app changes, re-sync the module preselection to the chosen app; on any field change,
        # re-evaluate whether OK should be enabled.
        self.appComboBox.Bind(wx.EVT_TEXT, self.onAppChanged)
        self.appComboBox.Bind(wx.EVT_COMBOBOX, self.onAppChanged)
        self.appModulesComboBox.Bind(wx.EVT_COMBOBOX, self.onFieldChanged)
        self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)

    def onAppChanged(self, evt):
        self.preselectModuleForApp()
        self.updateOkState()
        evt.Skip()

    def getEnteredApp(self):
        # NVDA matches executables by their lowercased name, so normalise typed input the same way.
        return self.appComboBox.GetValue().strip().lower()

    def getSelectedModule(self):
        display = self.appModulesComboBox.GetValue()
        if not display:
            return None
        return self.displayToModule(display)

    def currentModuleFor(self, app):
        # The module the app is already associated with, if known: either a mapping already staged in the
        # panel, or (for the pre-filled current app) the module it is running under. Used to reject a
        # selection that would only re-create the association the app already has.
        item = self.currentMappings.get(app)
        if item is not None and item.action != CustomMappingAction.REMOVE:
            return item.appModule
        if self.prefill and app == self.prefill[0]:
            return self.prefill[1]
        return None

    def isDuplicate(self, app, module):
        return module is not None and module == self.currentModuleFor(app)

    def updateOkState(self):
        if self.okButton is None:
            return
        app = self.getEnteredApp()
        module = self.getSelectedModule()
        # OK is available only when an app is given, a module is chosen, and the pair is not a duplicate
        # of what the app already uses (which would be a no-op and could add a duplicate entry).
        self.okButton.Enable(bool(app) and module is not None and not self.isDuplicate(app, module))

    def onFieldChanged(self, evt):
        self.updateOkState()
        evt.Skip()

    def onOk(self, evt):
        app = self.getEnteredApp()
        module = self.getSelectedModule()
        # OK is disabled in these cases; the guard is purely defensive.
        if not app or module is None or self.isDuplicate(app, module):
            return
        if app in self.currentMappings:
            # The app is already mapped: keep the module NVDA had before any custom mapping so that
            # removing the mapping later restores the correct original.
            action = CustomMappingAction.MODIFY
            originalModule = self.currentMappings[app].appOriginalModule
        else:
            action = CustomMappingAction.ADD
            originalModule = mapperHandler.getAllConfiguredMappings().get(app, None)
        self.result = CustomMappingItem(app, module, originalModule, action)
        evt.Skip()
