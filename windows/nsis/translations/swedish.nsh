;;

;;  swedish.nsh

;;

;;  Swedish language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Author: Tore Lundqvist <tlt@mima.x.se>, 2003.

;;  Author: Peter Hjalmarsson <xake@telia.com>, 2005.

;;  Version 3



; Make sure to update the GOURMET_MACRO_LANGUAGEFILE_END macro in

; langmacros.nsh when updating this file



; Startup Checks

!define INSTALLER_IS_RUNNING			"Installationsprogrammet körs redan."

!define GOURMET_IS_RUNNING			"En instans av Giam körs redan. Avsluta Gourmet och försök igen."

!define GTK_INSTALLER_NEEDED			"Körmiljön GTK+ är antingen inte installerat eller behöver uppgraderas.$\rVar god installera v${GTK_VERSION} eller högre av GTK+-körmiljön."



; License Page

!define GOURMET_LICENSE_BUTTON			"Nästa >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) är utgivet under GPL. Licensen finns tillgänglig här för infromationssyften enbart. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (obligatorisk)"

!define GTK_SECTION_TITLE			"GTK+-körmiljö (obligatorisk)"

!define GTK_THEMES_SECTION_TITLE		"GTK+-teman"

!define GTK_NOTHEME_SECTION_TITLE		"Inget tema"

!define GTK_WIMP_SECTION_TITLE		"Wimp-tema"

!define GTK_BLUECURVE_SECTION_TITLE	"Bluecurve-tema"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue-tema"
!define GOURMET_SHORTCUTS_SECTION_TITLE "Genvägar"
!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "Skrivbord"
!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Startmeny"
!define GOURMET_SECTION_DESCRIPTION		"Gourmets kärnfiler och DLL:er"

!define GTK_SECTION_DESCRIPTION		"En GUI-verktygsuppsättning för flera olika plattformar som Gourmet använder."

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+-teman kan ändra känslan av och utseendet på GTK+-applikationer."

!define GTK_NO_THEME_DESC			"Installera inte något GTK+-tema"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) ett GTK-tema som smälter bra in i Windows-miljön."

!define GTK_BLUECURVE_THEME_DESC		"The Bluecurve-tema."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"The Lighthouseblue-tema."

!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Genvägar för att starta Gourmet"
!define GOURMET_DESKTOP_SHORTCUT_DESC   "Skapar en genväg till Gourmet på skrivbordet"
!define GOURMET_STARTMENU_SHORTCUT_DESC   "Skapar ett tillägg i startmenyn för Gourmet"


; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"En äldre version av GTK+ runtime hittades, vill du uppgradera den?$\rOBS! Gourmet kommer kanske inte att fungera om du inte uppgraderar."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Besök Windows-Gourmets hemsida"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (enbart för avinstallation)"

!define GOURMET_PROMPT_WIPEOUT			"Din gamla Gourmet-katalog kommer att raderas, vill du fortsätta?$\r$\rOBS! om du har installerat några extra insticksmoduler kommer de raderas.$\rGourmets användarinställningar kommer inte påverkas."

!define GOURMET_PROMPT_DIR_EXISTS		"Den katalog du vill installera i finns redan. Allt i katalogen$\rkommer att raderas, vill du fortsätta?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Fel vid installation av GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Den sökväg du angivit går inte att komma åt eller skapa."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Du har inte rättigheter att installera ett GTK+tema."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Avinstalleraren kunde inte hitta registervärden för Gourmet.$\rAntagligen har en annan användare installerat applikationen."

!define un.GOURMET_UNINSTALL_ERROR_2         "Du har inte rättigheter att avinstallera den här applikationen."

