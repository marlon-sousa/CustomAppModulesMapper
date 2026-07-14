# CustomAppModulesMapper 0.3.0

NVDA add-on for dynamically mapping applications to existing app modules, and for detaching applications from their app module, without writing code.

## download
Download the [CustomAppModulesMapper 0.3.0 addon](https://github.com/marlon-sousa/CustomAppModulesMapper/releases/download/0.3.0/CustomAppModulesMapper-0.3.0.nvda-addon)

## How it works

Sometimes it is necessary to map a known application to a known NVDA app module.

The module might ship with NVDA out of the box or be provided by a third party add-on.

A good example is DBeaver, which is based on Eclipse but has a different executable name. NVDA provides this mapping out of the box, so that DBeaver reuses the same functionality as Eclipse.

But such a mapping might not exist yet, or might be waiting for a merge that could take months to happen.

Traditionally, the only ways to provide a new mapping are to build a dedicated add-on that exports it, or to merge the mapping into NVDA's appModules package.

Conversely, an application may already be picked up by an app module you would rather it did not use, and there is no built-in way to detach it.

This add-on lets you do both dynamically, straight from the NVDA Settings dialog, so that:

1. If you need to map an app to a module, you can do it immediately, without coding an add-on or waiting for a merge into NVDA's source code.
2. You can have several modules providing functionality to an app and alternate between them, to test how a given module deals with the app.
3. If an app is associated with a module you do not want, you can detach it so that NVDA applies no app specific behavior to it.

## Usage

Custom mappings are managed in NVDA's Settings dialog, in the **Custom Application Module Mapper** category. It lists your current custom mappings, each showing the application executable name and the module it is mapped to (detached applications are shown as `(not associated)`), with the following actions:

- **Add mapping**: opens a dialog where you choose an application and the module to map it to. The dialog is pre-filled with the application you were in right before opening NVDA's Settings, and with the module that application currently uses, so in the common case you only need to change the module. You can still type any executable name manually.
- **Unassociate current app**: detaches the application you were in right before opening NVDA's Settings from any app module, so NVDA applies no app specific behavior to it. This is the reliable way to detach the app you are working with: focus it, open NVDA's Settings, and press this button.
- **Remove mapping**: removes the selected custom mapping and restores the module the application originally used.

Changes take effect when you confirm the Settings dialog.

### Features

1. Map any executable to any available app module, whether it is a native NVDA module or one exposed by another add-on.
2. Detach any application from its app module, so it behaves as if no app module were present.
3. The application to add or unassociate is detected automatically from the app you were last in, so you rarely need to type executable names by hand.
4. Custom mappings are persisted, so they are kept between NVDA runs.
5. At any time, remove a custom mapping and the original mapping is restored.
6. Everything is managed through the NVDA Settings dialog, in the Custom Application Module Mapper category.
