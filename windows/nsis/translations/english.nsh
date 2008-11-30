;;
;;  english.nsh
;;
;;  Default language strings for the Windows Gourmet NSIS installer.
;;  Windows Code page: 1252
;;
;;  Version 3
;;  Note: If translating this file, replace "!insertmacro GOURMET_MACRO_DEFAULT_STRING"
;;  with "!define".

; Make sure to update the GOURMET_MACRO_LANGUAGEFILE_END macro in
; langmacros.nsh when updating this file

; Startup Checks
!insertmacro GOURMET_MACRO_DEFAULT_STRING INSTALLER_IS_RUNNING			"The installer is already running."
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_IS_RUNNING			"An instance of Gourmet is currently running. Exit Gourmet and then try again."
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_INSTALLER_NEEDED			"The GTK+ runtime environment is either missing or needs to be upgraded.$\rPlease install v${GTK_VERSION} or higher of the GTK+ runtime"

; License Page
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_LICENSE_BUTTON			"Next >"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) is released under the GNU General Public License (GPL). The license is provided here for information purposes only. $_CLICK"

; Components Page
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (required)"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_SECTION_TITLE			"GTK+ Runtime Environment (required)"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_THEMES_SECTION_TITLE		"GTK+ Themes"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_NOTHEME_SECTION_TITLE		"No Theme"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_WIMP_SECTION_TITLE		"Wimp Theme"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_BLUECURVE_SECTION_TITLE	"Bluecurve Theme"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue Theme"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_SHORTCUTS_SECTION_TITLE "Shortcuts"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "Desktop"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Start Menu"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_SECTION_DESCRIPTION		"Core Gourmet files and dlls"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_SECTION_DESCRIPTION		"A multi-platform GUI toolkit, used by Gourmet"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_THEMES_SECTION_DESCRIPTION	"GTK+ Themes can change the look and feel of GTK+ applications."
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_NO_THEME_DESC			"Don't install a GTK+ theme"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) is a GTK theme that blends well into the Windows desktop environment."
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_BLUECURVE_THEME_DESC		"The Bluecurve theme."
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_LIGHTHOUSEBLUE_THEME_DESC	"The Lighthouseblue theme."
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Shortcuts for starting Gourmet"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_DESKTOP_SHORTCUT_DESC   "Create a shortcut to Gourmet on the Desktop"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_STARTMENU_SHORTCUT_DESC   "Create a Start Menu entry for Gourmet"

; GTK+ Directory Page
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_UPGRADE_PROMPT			"An existing version of the GTK+ runtime was found. Do you wish to upgrade to version ${GTK_VERSION}?$\rNote: Gourmet may not work unless you do.$\r\
                                                                                Specifically note, that if you have the GTK+ package that was installed with GOURMET,$\r it is NOT SUFFICIENT to run Gourmet, since Gourmet also requires Glade, which GOURMET does not install."

; Installer Finish Page
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_FINISH_VISIT_WEB_SITE		"Visit the Windows Gourmet Web Page"

; Gourmet Section Prompts and Texts
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_UNINSTALL_DESC			"Gourmet (remove only)"
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_PROMPT_WIPEOUT			"Your old Gourmet directory is about to be deleted. Would you like to continue?$\r$\rNote: Any non-standard plugins that you may have installed will be deleted.$\rGourmet user settings will not be affected."
!insertmacro GOURMET_MACRO_DEFAULT_STRING GOURMET_PROMPT_DIR_EXISTS		"The installation directory you specified already exists. Any contents$\rwill be deleted. Would you like to continue?"

; GTK+ Section Prompts
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_INSTALL_ERROR			"Error installing GTK+ runtime."
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_BAD_INSTALL_PATH			"The path you entered can not be accessed or created."

; GTK+ Themes section
!insertmacro GOURMET_MACRO_DEFAULT_STRING GTK_NO_THEME_INSTALL_RIGHTS	"You do not have permission to install a GTK+ theme."

; Uninstall Section Prompts
!insertmacro GOURMET_MACRO_DEFAULT_STRING un.GOURMET_UNINSTALL_ERROR_1		"The uninstaller could not find registry entries for Gourmet.$\rIt is likely that another user installed this application."
!insertmacro GOURMET_MACRO_DEFAULT_STRING un.GOURMET_UNINSTALL_ERROR_2		"You do not have permission to uninstall this application."
