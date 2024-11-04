# -*- coding: UTF-8 -*-
# A part of the EnhancedDictionaries addon for NVDA
# Copyright (C) 2020 Marlon Sousa
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

import addonHandler
import globalPluginHandler
import globalVars
import gui
import gui.settingsDialogs
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
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(CustomAppModuleMapperSettingPanel)

	def terminate(self):
		super(GlobalPlugin, self).terminate()
		if not globalVars.appArgs.secure:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(CustomAppModuleMapperSettingPanel)