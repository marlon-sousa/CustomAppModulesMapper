# CustomAppModulesMapper ${addon_version}

NVDA add-on for dynamically mapping applications to existing app modules, and for detaching applications from their app module, without writing code.

## download
Download the [CustomAppModulesMapper ${addon_version} addon](https://github.com/marlon-sousa/CustomAppModulesMapper/releases/download/${addon_version}/CustomAppModulesMapper-${addon_version}.nvda-addon)

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

Custom mappings are managed in NVDA's Settings dialog, in the **Custom Application Module Mapper** category. It lists your current custom mappings, each showing the application executable name and the module it is associated with (applications associated with no module are shown as `(not associated)`), with the following actions:

- **Associate app**: opens a dialog where you choose an application and the module to associate it with.
  - The **application** field is a combo box pre-filled with the applications you currently have open, with the app you were in right before opening NVDA's Settings selected. You can pick another open app or type any executable name by hand.
  - The **module** list offers `(not associated)` first, then every available module. Choosing a real module associates the app with it; choosing `(not associated)` associates the app with no module, so NVDA applies no app specific behavior to it. This single dialog is how you associate any application, running or not, with a module or with nothing.
  - The confirm button stays disabled until you have both chosen an application and a module, and it will not let you re-select the association the app already has.
- **Remove mapping**: removes the selected custom mapping (disassociates the application), restoring the module the application originally used.

When you open the category, if the application you were last in already has a custom mapping, its row is selected automatically, ready to remove or re-associate.

Changes take effect when you confirm the Settings dialog. Application names are matched case-insensitively, the same way NVDA matches executables.

### Features

1. Associate any executable with any available app module, whether it is a native NVDA module or one exposed by another add-on.
2. Associate any application with no module (`(not associated)`), so it behaves as if no app module were present.
3. The applications you have open are offered for selection, with the app you were last in pre-selected, so you rarely need to type executable names by hand.
4. Custom mappings are persisted, so they are kept between NVDA runs, and are protected against duplicates.
5. At any time, remove a custom mapping and the original mapping is restored.
6. Everything is managed through the NVDA Settings dialog, in the Custom Application Module Mapper category.
