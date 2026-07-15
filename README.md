# CustomAppModulesMapper 1.0.0

NVDA add-on for dynamically associating applications with existing app modules — and for associating them with no module — without writing code.

## download
Download the [CustomAppModulesMapper 1.0.0 addon](https://github.com/marlon-sousa/CustomAppModulesMapper/releases/download/1.0.0/CustomAppModulesMapper-1.0.0.nvda-addon)

## What is an app module association?

To give an application accessible, app specific behavior, NVDA loads an **app module** for it — a small component that improves how that application is read and interacted with. NVDA decides which app module to load for a running application from its **executable name**:

- Most app modules are matched by having the **same name** as the executable (for example `notepad.exe` uses the `notepad` app module).
- Some applications are matched through a built-in **alias** (for example DBeaver, whose executable is `dbeaver.exe`, is associated with the `eclipse` app module, because DBeaver is based on Eclipse).
- App modules can also be provided by **other add-ons**.
- When nothing matches, NVDA uses a generic, empty app module, so the application gets **no** app specific behavior.

This link between an application and the app module NVDA loads for it is its **association**. This add-on lets you control that association: associate an application with any available app module, associate it with **no** module, change an existing association, or remove your change and restore what NVDA used originally.

## Why would you use this add-on?

Sometimes the association you want does not exist out of the box:

- A new application behaves like one NVDA already supports (for example an Eclipse or Electron/VS Code based tool with a different executable name), and you want it to reuse that app module.
- You want to try how a particular app module deals with an application, and switch between modules to compare.
- An application is associated with an app module that gets in your way, and you want to detach it (associate it with no module) so NVDA applies no app specific behavior.

Traditionally the only ways to change this are to build a dedicated add-on that exports the association, or to get it merged into NVDA's source — which can take months. This add-on lets you do it immediately, from the NVDA Settings dialog. Your associations are persisted between NVDA runs and are fully reversible.

## Usage

Associations are managed in NVDA's Settings dialog, in the **Custom Application Module Mapper** category. It lists your current custom associations, each showing the application executable name and the module it is associated with (applications associated with no module are shown as `(not associated)`).

When you open the category, if the application you were in right before opening NVDA's Settings already has a custom association, its row is selected automatically, ready to disassociate or re-associate.

Two actions are available:

### Associate app

Opens a dialog where you choose an application and the module to associate it with.

- The **application** field is a combo box pre-filled with the applications you currently have open, with the app you were in right before opening NVDA's Settings selected. You can pick another open application or type any executable name by hand (so you can prepare an association for an application that is not currently running).
- The **module** list offers `(not associated)` first, then every available app module — both those bundled with NVDA and those provided by other add-ons. Choosing a real module associates the application with it; choosing `(not associated)` associates it with no module, so NVDA applies no app specific behavior to it.
- When you choose an application that already has a custom association, its current module is pre-selected, and choosing a **different** module **changes** the association (re-associates the application). The module pre-selection follows the application you choose.
- The confirm button stays disabled until you have chosen both an application and a module, and it will not let you re-select the association the application already has (which would do nothing).

### Disassociate

Removes the selected custom association, restoring the module the application originally used — that is, the module NVDA loaded before you made any change. This original is preserved even if you re-associated the application several times, so disassociating always returns it to its true original. The button is enabled only when a custom association is selected in the list.

### Applying changes

Changes take effect when you confirm the Settings dialog; the running app modules are reloaded so the new associations apply immediately. Application names are matched case-insensitively, the same way NVDA matches executables.

## Features

1. Associate any application with any available app module, whether it is bundled with NVDA or provided by another add-on.
2. Associate any application with no module (`(not associated)`), so it behaves as if no app module were present.
3. Change (re-associate) an existing association to a different module; the module restored on disassociation is always the true original, no matter how many times you re-associate.
4. The applications you have open are offered for selection, with the app you were last in pre-selected, so you rarely need to type executable names by hand; you can still type any executable, including one that is not running.
5. Disassociate an application at any time and its original module is restored.
6. Application names are handled case-insensitively, matching how NVDA matches executables.
7. Associations are persisted between NVDA runs, stored in the NVDA configuration directory so they survive updating or reinstalling the add-on, and protected against duplicates.
8. Everything is managed through the NVDA Settings dialog, in the Custom Application Module Mapper category.
