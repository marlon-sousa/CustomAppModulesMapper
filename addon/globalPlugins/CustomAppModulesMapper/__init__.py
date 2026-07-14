# -*- coding: UTF-8 -*-
# A part of the CustomAppModulesMapper addon for NVDA
# Copyright (C) 2024 Marlon Sousa
# This file is covered by the MIT  License.
# See the file COPYING.txt for more details.

import addonHandler
import globalPluginHandler
import globalVars
import gui
import gui.settingsDialogs
from . import mapperHandler
from .mapperHandler import loadCustomMappings
from .guiHelper import CustomAppModuleMapperSettingPanel
from logHandler import log


# for detailed explanations, see guiHelper.py file
__ = _

addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		# appModuleHandler.registerExecutableWithAppModule("notepad", "code")
		log.info("addon loaded")
		if not globalVars.appArgs.secure:
			loadCustomMappings()
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(CustomAppModuleMapperSettingPanel)

	def event_foreground(self, obj, nextHandler):
		# Remember the last real application that had the foreground so the settings panel can offer to
		# act on it. NVDA raises this event for its own windows too (menus, dialogs, the Settings window
		# this add-on's panel lives in); skipping "nvda" keeps the stored value pointing at the actual
		# application the user was in before opening NVDA's own UI.
		try:
			appModule = obj.appModule
			if appModule is not None and appModule.appName and appModule.appName != "nvda":
				mapperHandler.setLastForegroundApp(appModule.appName, appModule.appModuleName)
		except Exception:
			log.debugWarning("Could not record foreground application", exc_info=True)
		nextHandler()

	def terminate(self):
		super(GlobalPlugin, self).terminate()
		if not globalVars.appArgs.secure:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(CustomAppModuleMapperSettingPanel)
