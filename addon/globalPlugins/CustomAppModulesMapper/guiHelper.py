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
        # Translators: This is the button to check for new updates of the add-on.
        self.addButton = actionsHelper.addItem(wx.Button(self, label=_("&Add mapping")))
        # Translators: This is the label for the IBMTTS folder address.
        self.removeButton = actionsHelper.addItem(wx.Button(self, label=_("&Remove mapping")))
        sHelper.addItem(actionsHelper)
        settingsSizer.Fit(self)
        self.bindEvents()
        self.buildMappingsList()

    def bindEvents(self):
        self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        self.removeButton.Bind(wx.EVT_BUTTON, self.onRemove)

    def buildMappingsList(self):
        customModulesMapping = mapperHandler.getCustomModulesMapping()
        self.mappings = reduce(
            lambda acc, item: acc.update({
                item.app: CustomMappingItem(
                    item.app,
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
            self.mappingsList.Append((mapping.app, mapping.appModule))

    def onAddDialogResumed(self, item: CustomMappingItem):
        self.mappings[item.app] = item
        self.refreshList()

    def onAdd(self, evt):
        title = _("add mapping")
        gui.mainFrame.prePopup()
        # Pass the mappings currently staged in this panel so the dialog can tell whether the app
        # the user types is already mapped (MODIFY) or new (ADD), and preserve its original module.
        dialog = ModuleMappingDialog(self, title, self.mappings)
        if dialog.ShowModal() == wx.ID_OK:
            self.onAddDialogResumed(dialog.result)
        dialog.Destroy()
        gui.mainFrame.postPopup()

    def onRemove(self, evt):
        selected = self.mappingsList.GetFirstSelected()
        if selected == -1:
            return
        app = self.mappingsList.GetItemText(selected)
        self.mappings[app].action = CustomMappingAction.REMOVE
        self.refreshList()

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

    def __init__(self, parent, title, currentMappings):
        super(ModuleMappingDialog, self).__init__(parent, title=title)
        self.result = None
        # currentMappings maps an app name to the CustomMappingItem currently staged for it.
        self.currentMappings = currentMappings
        self.availableModules = mapperHandler.getAllAvailableAppModules()
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        # Translators: label test for app field in add mapping dialog
        appLabelText = _("&App")
        self.AppTextCtrl = sHelper.addLabeledControl(appLabelText, wx.TextCtrl)

        # Translators: label test for app module field in add mapping dialog
        appModuleLabelText = _("App &module")
        appLabel = wx.StaticText(self, label=appModuleLabelText)
        self.appModulesComboBox = wx.ComboBox(self, choices=self.availableModules, style=wx.CB_READONLY)
        sHelper.addItem(appLabel)
        sHelper.addItem(self.appModulesComboBox)

        sHelper.addDialogDismissButtons(wx.OK | wx.CANCEL, separated=True)

        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        mainSizer.Fit(self)
        self.SetSizer(mainSizer)
        self.AppTextCtrl.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)

    def onOk(self, evt):
        app = self.AppTextCtrl.GetValue()
        appModule = self.appModulesComboBox.GetValue()
        if not app or not appModule:
            wx.MessageBox(_("Please fill all fields"), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        originalMapping = mapperHandler.getAllConfiguredMappings()
        if app in self.currentMappings:
            # The app is already mapped: keep the module NVDA had before any custom mapping so that
            # removing the mapping later restores the correct original.
            action = CustomMappingAction.MODIFY
            originalModule = self.currentMappings[app].appOriginalModule
        else:
            action = CustomMappingAction.ADD
            originalModule = originalMapping.get(app, None)
        self.result = CustomMappingItem(app, appModule, originalModule, action)
        evt.Skip()
