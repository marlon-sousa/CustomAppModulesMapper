# CustomAppModulesMapper 0.3.0

Nvda ADDON for allowing dynamic mapping of existing app modules for other applications.

## download
Download the [CustomAppModulesMapper 0.3.0 addon](https://github.com/marlon-sousa/CustomAppModulesMapper/releases/download/0.3.0/CustomAppModulesMapper-0.3.0.nvda-addon)

## How it works

Some times, it is necessary to map a known application to a known NVDA app module.

This module might exist out of the box or be implemented by a third part addon.

A good example is Dbeaver, which is based on Eclipse but has a different executable name.

In case of Dbeaver, NVDA offers this mapping out of the box, so that DbEaver reuses the same functionality of Eclipse.

But this mapping could either not be provided or could be wairting for a merge which might take months to happen.

As of now, the only way to provide a new mapping is either tu build a new addon exporting the mapping or to merge the mapping into NVDAs appModules package.

This addon provides a way of performing dynamic mapping of apps to modules, so that:

1. If you need to map an app to a module, you can do it imediately without having to code an addon or wait for a merge on NVDA's source code.
2. You can have several modules providing functionality to an app and alternate between them, so that you can test how a given module would deal with thr app.

### Features:

1. Map any executable to any provided app module, either a native NVDA module or a custom addon exposed module.
2. Custom mappings are persisted, so that you can keep them between NVDA runs.
3. At any time, remove a custom mapping and the original mapping will be restored.
4. You can manage custom mappings through NVDA setings dialog, in the Custom Applications module mapper category.
