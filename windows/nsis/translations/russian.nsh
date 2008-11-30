;;

;;  russian.nsh

;;

;;  Russian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1251

;;

;;  Author: Tasselhof <anr@nm.ru>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"   GTK+     .$\r  v${GTK_VERSION}     GTK+."



; License Page

!define GOURMET_LICENSE_BUTTON			" >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name)    GPL.      . $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager ()."

!define GTK_SECTION_TITLE			"GTK+    ()."

!define GTK_THEMES_SECTION_TITLE		"  GTK+."

!define GTK_NOTHEME_SECTION_TITLE		" ."

!define GTK_WIMP_SECTION_TITLE		" 'Wimp Theme'"

!define GTK_BLUECURVE_SECTION_TITLE		" 'Bluecurve'."

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	" 'Light House Blue'."

!define GOURMET_SECTION_DESCRIPTION		"  Gourmet  ."

!define GTK_SECTION_DESCRIPTION		"  ,  Gourmet."

!define GTK_THEMES_SECTION_DESCRIPTION	"  GTK+       ."

!define GTK_NO_THEME_DESC			"    GTK+."

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows-)    GTK,            Windows."

!define GTK_BLUECURVE_THEME_DESC		" 'The Bluecurve'."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	" 'The Lighthouseblue'."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"   GTK+.       ?$\r: Gourmet        ."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		" - Gourmet   Windows."



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet ( )"

!define GOURMET_PROMPT_WIPEOUT			"   Gourmet   .    ?$\r$\r:        ..$\r  Gourmet  ."

!define GOURMET_PROMPT_DIR_EXISTS		",       .  $\r .   ?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"    GTK+."

!define GTK_BAD_INSTALL_PATH			"       ."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"        GTK+."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"      Gourmet  ..$\r     ."

!define un.GOURMET_UNINSTALL_ERROR_2		"       ."

