;;
;;  german.nsh
;;
;;  German language strings for the Windows Gourmet NSIS installer.
;;  Windows Code page: 1252
;;
;;  Author: Bjoern Voigt <bjoern@cs.tu-berlin.de>, 2005.
;;  Version 3
;;
 
; Startup checks
!define INSTALLER_IS_RUNNING			"Der Installer läuft schon."
!define GOURMET_IS_RUNNING				"Eine Instanz von Gourmet läuft momentan schon. Beenden Sie Gourmet und versuchen Sie es nochmal."
!define GTK_INSTALLER_NEEDED			"Die GTK+ Runtime Umgebung fehlt entweder oder muß aktualisiert werden.$\rBitte installieren Sie v${GTK_VERSION} oder höher der GTK+ Runtime"
 
; License Page
!define GOURMET_LICENSE_BUTTON			"Weiter >"
!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) wird unter der GNU General Public License (GPL) veröffentlicht. Die Lizenz dient hier nur der Information. $_CLICK"
 
; Components Page
!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (erforderlich)"
!define GTK_SECTION_TITLE			"GTK+ Runtime Umgebung (erforderlich)"
!define GTK_THEMES_SECTION_TITLE		"GTK+ Themen"
!define GTK_NOTHEME_SECTION_TITLE		"Kein Thema"
!define GTK_WIMP_SECTION_TITLE		"Wimp Thema"
!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve Thema"
!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue Thema"
!define GOURMET_SHORTCUTS_SECTION_TITLE	"Verknüpfungen"
!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE	"Desktop"
!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE	"Startmenü"
!define GOURMET_SECTION_DESCRIPTION		"Gourmet Basis-Dateien und -DLLs"
!define GTK_SECTION_DESCRIPTION		"Ein Multi-Plattform GUI Toolkit, verwendet von Gourmet"
!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ Themen können Aussehen und Bedienung von GTK+ Anwendungen verändern."
!define GTK_NO_THEME_DESC			"Installiere kein GTK+ Thema"
!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows Imitator) ist ein GTK Theme, daß sich besonders gut in den Windows Desktop integriert."
!define GTK_BLUECURVE_THEME_DESC		"Das Bluecurve Thema."
!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Das Lighthouseblue Thema."
!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION	"Verknüpfungen zum Start von Gourmet"
!define GOURMET_DESKTOP_SHORTCUT_DESC   "Erstellt eine Verknüpfung zu Gourmet auf dem Desktop"
!define GOURMET_STARTMENU_SHORTCUT_DESC   "Erstellt einen Eintrag für Gourmet im Startmenü"
 
; GTK+ Directory Page
!define GTK_UPGRADE_PROMPT			"Eine alte Version der GTK+ Runtime wurde gefunden. Möchten Sie aktualisieren?$\rHinweis: Gourmet funktioniert evtl. nicht, wenn Sie nicht aktualisieren."
 
; Installer Finish Page
!define GOURMET_FINISH_VISIT_WEB_SITE		"Besuchen Sie die Windows Gourmet Webseite"
 
; Gourmet Section Prompts and Texts
!define GOURMET_UNINSTALL_DESC			"Gourmet (nur entfernen)"
!define GOURMET_PROMPT_WIPEOUT			"Ihre altes Gourmet-Verzeichnis soll gelöscht werden. Möchten Sie fortfahren?$\r$\rHinweis: Alle nicht-Standard Plugins, die Sie evtl. installiert haben werden$\rgelöscht. Gourmet-Benutzereinstellungen sind nicht betroffen."
!define GOURMET_PROMPT_DIR_EXISTS		"Das Installationsverzeichnis, daß Sie angegeben haben, existiert schon. Der Verzeichnisinhalt$\rwird gelöscht. Möchten Sie fortfahren?"
 
; GTK+ Section Prompts
!define GTK_INSTALL_ERROR			"Fehler beim Installieren der GTK+ Runtime."
!define GTK_BAD_INSTALL_PATH			"Der Pfad, den Sie eingegeben haben, existiert nicht und kann nicht erstellt werden."
 
; GTK+ Themes section
!define GTK_NO_THEME_INSTALL_RIGHTS		"Sie haben keine Berechtigung, um ein GTK+ Theme zu installieren."
 
; Uninstall Section Prompts
!define un.GOURMET_UNINSTALL_ERROR_1		"Der Deinstaller konnte keine Registrierungsschlüssel für Gourmet finden.$\rEs ist wahrscheinlich, daß ein anderer Benutzer diese Anwendunng installiert hat."
!define un.GOURMET_UNINSTALL_ERROR_2		"Sie haben keine Berechtigung, diese Anwendung zu deinstallieren."
