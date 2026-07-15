# -*- coding: UTF-8 -*-
# A part of the CustomModulesMapper addon for NVDA
# Copyright (C) 2024 Marlon Sousa
# This file is covered by the MIT License.
# See the file COPYING.txt for more details.

import os
import pickle
import shutil
import ctypes
from ctypes import wintypes
import addonHandler
import appModules
import appModuleHandler
import globalVars
import pkgutil
import winUser
from logHandler import log
from dataclasses import dataclass
from typing import List, Optional, Tuple


# Name of the deliberately empty app module shipped with this add-on (see appModules/notAssociated.py).
# Mapping an application to this module detaches it from whatever module NVDA would otherwise load.
# It is a sentinel rather than a real mapping target, so it is hidden from the module list offered in
# the GUI and instead reached through the dedicated "unassociate" action.
NOT_ASSOCIATED_MODULE = "notAssociated"

# On-disk format version of the mappings pickle. Bump this whenever the stored structure changes, so
# older files can be recognised and migrated. Version 0 is the original bare list of Mapping objects
# written before 1.0; version 1 wraps that list in a dict carrying this version number.
PICKLE_FORMAT_VERSION = 1


@dataclass
class Mapping:
	app: str
	appModule: str
	appOriginalModule: str


customModulesMapping: List[Mapping]

# Executable name and current module of the last real (non NVDA) application that had the focus. The
# settings panel lives inside NVDA's own Settings window, so by the time it is built the focused
# application is NVDA itself. The global plugin keeps this up to date via event_gainFocus so the panel
# can pre-fill the associate dialog with, and select the row for, the application the user was in right
# before opening Settings.
_lastForegroundApp: Optional[Tuple[str, str]] = None


def setLastForegroundApp(appName: str, moduleName: str):
	global _lastForegroundApp
	_lastForegroundApp = (appName, moduleName)


def getLastForegroundApp() -> Optional[Tuple[str, str]]:
	# Returns a (executableName, currentModuleName) tuple, or None if no real application has been seen.
	return _lastForegroundApp


def getCustomModulesMapping():
	global customModulesMapping
	return customModulesMapping


def getAllConfiguredMappings() -> dict[str, str]:
	return appModules.EXECUTABLE_NAMES_TO_APP_MODS | appModuleHandler._executableNamesToAppModsAddons


def filterUnmappedModules(modName):
	# These are generic host/internal modules that are not meaningful mapping targets:
	# nvda is NVDA itself, and the others are shared hosts (Java, the Edge WebView, the modern
	# touch keyboard, etc.) that back many unrelated apps, so offering them as targets would be
	# misleading. notAssociated is this add-on's detach sentinel, reached through the dedicated
	# "unassociate" action instead of by picking it as a module. They are all hidden from the list
	# of available modules.
	return modName not in (
		'javaw',
		'messengerWindow',
		'msgComposeWindow',
		'msedgewebview2',
		'nvda',
		NOT_ASSOCIATED_MODULE,
		'windowsinternal_composableshell_experiences_textinput_inputapp',
	)


def getUnmappedModules() -> List[str]:
	# appModules.EXECUTABLE_NAMES_TO_APP_MODS only lists the special executable->module aliases
	# (e.g. dbeaver -> eclipse). The vast majority of NVDA's app modules are matched implicitly by
	# having the same name as the executable, so they never appear in that mapping. To offer every
	# available module as a mapping target we enumerate the appModules package directly. This also
	# picks up modules provided by other add-ons, since they are merged into the appModules
	# namespace package.
	modules = []
	for _importer, modName, _ispkg in pkgutil.iter_modules(appModules.__path__):
		modules.append(modName)
	return modules


def getRunningApps() -> List[str]:
	# Executable names of the applications the user currently has open, used to populate the app picker
	# so mappings can be chosen without typing. appModuleHandler.runningTable is not enough on its own:
	# it only lists apps NVDA has already built an app module for this session, which misses many open
	# apps. So enumerate the processes owning a visible, titled, top-level window (what the user can
	# actually switch to) and merge in whatever NVDA is already tracking. Names come from the helper
	# NVDA uses to match executables, so they are lowercased and can be compared and stored as-is.
	processIDs = set()

	@ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
	def collect(hwnd, _lParam):
		try:
			if winUser.isWindowVisible(hwnd) and winUser.getWindowText(hwnd):
				processIDs.add(winUser.getWindowThreadProcessID(hwnd)[0])
		except Exception:
			pass
		return True

	try:
		ctypes.windll.user32.EnumWindows(collect, 0)
	except Exception:
		log.debugWarning("Could not enumerate top-level windows", exc_info=True)

	apps = set()
	for processID in processIDs:
		try:
			appName = appModuleHandler.getAppNameFromProcessID(processID, includeExt=False)
		except Exception:
			continue
		if appName:
			apps.add(appName)
	for mod in list(appModuleHandler.runningTable.values()):
		try:
			if mod.appName:
				apps.add(mod.appName)
		except Exception:
			continue
	# NVDA itself is never a meaningful mapping target.
	apps.discard("nvda")
	return sorted(apps)


def getAllAvailableAppModules() -> List[str]:
	# The full list of modules a user can map an app to is the union of every module physically
	# present in the appModules package and the targets of the currently configured aliases,
	# minus the generic host modules filtered out above.
	unmappedModules = getUnmappedModules()
	mappings = getAllConfiguredMappings()
	return sorted(
		filter(
			filterUnmappedModules,
			set(list(mappings.values()) + unmappedModules),
		)
	)


def associateAppModule(appName: str, moduleName: str):
	appModuleHandler.registerExecutableWithAppModule(appName, moduleName)


def disassociateAppModule(appName: str):
	appModuleHandler.unregisterExecutable(appName)


def restart():
	appModuleHandler.terminate()
	appModuleHandler.initialize._alreadyInitialized = False
	appModuleHandler.initialize()


def getCustomMappingsFilePath():
	# Store the mappings in NVDA's user configuration directory rather than in the add-on folder.
	# The add-on folder is wiped whenever the add-on is updated or reinstalled, which would
	# silently discard the user's custom mappings. globalVars.appArgs.configPath points at the
	# active NVDA configuration directory (installed, portable, or the one passed with -c), so
	# files placed there survive add-on reinstalls.
	return os.path.join(globalVars.appArgs.configPath, "customModulesMapping.pickle")


def getLegacyCustomMappingsFilePath():
	# Location used by version 0.2.0 (inside the add-on folder). Kept only so that existing
	# mappings can be migrated to the new, reinstall-safe location.
	addon = addonHandler.getCodeAddon()
	return os.path.join(addon.path, "customModulesMapping.pickle")


def migrateLegacyMappingsFile():
	newPath = getCustomMappingsFilePath()
	legacyPath = getLegacyCustomMappingsFilePath()
	if os.path.isfile(newPath) or not os.path.isfile(legacyPath):
		return
	try:
		shutil.move(legacyPath, newPath)
		log.info("Migrated custom mappings to the NVDA configuration directory")
	except Exception as e:
		log.error(f"Could not migrate custom mappings file: {e}")


def dedupeMappings(mappings: List[Mapping]) -> List[Mapping]:
	# Guarantee at most one mapping per application. Executables are matched by their lowercased name,
	# so applications are compared case-insensitively; later entries win, keeping the most recent choice.
	# This protects the persisted file from ever holding duplicates, even if a caller passes some in.
	byApp = {}
	for mapping in mappings:
		byApp[mapping.app.lower()] = mapping
	return list(byApp.values())


def persist():
	global customModulesMapping
	customModulesMapping = dedupeMappings(customModulesMapping)
	with open(getCustomMappingsFilePath(), "wb") as f:
		pickle.dump({"formatVersion": PICKLE_FORMAT_VERSION, "mappings": customModulesMapping}, f)
	log.info("Custom mappings saved to file")


def readMappingsFile(path) -> List[Mapping]:
	# Returns the list of Mapping objects stored at path, understanding both the current versioned
	# format (a dict with "formatVersion" and "mappings") and the original bare list of Mapping objects
	# written before 1.0 (treated as format version 0). Future format changes branch on the version here.
	with open(path, "rb") as f:
		data = pickle.load(f)
	if isinstance(data, dict):
		return data.get("mappings", [])
	return data


def loadCustomMappings():
	global customModulesMapping
	migrateLegacyMappingsFile()
	try:
		customModulesMapping = dedupeMappings(readMappingsFile(getCustomMappingsFilePath()))
		log.info("Custom mappings loaded from file")
		mustRestart = False
		for mapping in customModulesMapping:
			log.info(f"Associating {mapping.app} app with {mapping.appModule} module")
			associateAppModule(mapping.app, mapping.appModule)
			mustRestart = True
		if mustRestart:
			restart()
			log.info("Custom mappings applied")
	except FileNotFoundError:
		customModulesMapping = []
		log.info("Custom mappings created")
	except Exception as e:
		customModulesMapping = []
		log.error(f"Error loading custom mappings: {e}")
