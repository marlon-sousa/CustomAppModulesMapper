# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _


addon_info = AddonInfo(
    addon_name="CustomAppModulesMapper",
    # Translators: Summary/title for this add-on.
    addon_summary=_("Custom App Modules Mapper"),
    # Translators: Long description for this add-on in add-on store.
    addon_description=_("""Lets you dynamically map any application to any existing NVDA app module, straight from the NVDA settings dialog, without writing an add-on or waiting for a mapping to be merged into NVDA."""),
    # Translators: what's new text for this add-on version shown in add-on store.
    addon_changelog=_("""Version 1.0.0:
* Associate any application with any app module — one bundled with NVDA or provided by another add-on — or with no module ("not associated"), straight from the NVDA Settings dialog, without writing an add-on or waiting for a mapping to be merged into NVDA.
* Change an association at any time, or remove it to restore the module the application originally used.
* The applications you currently have open are offered for selection, with the app you were last in pre-selected; you can still type any executable name.
* Application names are matched case-insensitively.
* Associations are stored in the NVDA configuration directory, so they survive updating or reinstalling the add-on, and are protected against duplicates. Mappings saved by previous versions are migrated automatically.
* Compatible with NVDA 2026.1."""),
    addon_version="1.0.0",
    addon_author="Marlon Brandão de Sousa <marlon.bsousa@gmail.com>",
    addon_url="https://github.com/marlon-sousa/CustomAppModulesMapper",
    addon_sourceURL="https://github.com/marlon-sousa/CustomAppModulesMapper",
    addon_docFileName="readme.html",
    addon_minimumNVDAVersion="2024.1",
    addon_lastTestedNVDAVersion="2026.1.0",
    addon_updateChannel=None,
    addon_license="Mit License",
    addon_licenseURL="https://github.com/marlon-sousa/CustomAppModulesMapper/blob/main/LICENSE",
)


pythonSources: list[str] = [
    "addon/globalPlugins/CustomAppModulesMapper/*.py",
    "addon/appModules/*.py",
]
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Paths are relative to the addon directory when building the bundle.
excludedFiles: list[str] = [
    "doc/*/contributing*.*",
    "doc/*/*.tpl.md",
]

baseLanguage: str = "en"
markdownExtensions: list[str] = []

brailleTables: BrailleTables = {}
symbolDictionaries: SymbolDictionaries = {}
