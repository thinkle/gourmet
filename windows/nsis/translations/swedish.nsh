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

!define INSTALLER_IS_RUNNING			"Installationsprogrammet krs redan."

!define GOURMET_IS_RUNNING			"En instans av Giam krs redan. Avsluta Gourmet och frsk igen."

!define GTK_INSTALLER_NEEDED			"Krmiljn GTK+ r antingen inte installerat eller behver uppgraderas.$\rVar god installera v${GTK_VERSION} eller hgre av GTK+-krmiljn."



; License Page

!define GOURMET_LICENSE_BUTTON			"Nsta >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) r utgivet under GPL. Licensen finns tillgnglig hr fr infromationssyften enbart. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (obligatorisk)"

!define GTK_SECTION_TITLE			"GTK+-krmilj (obligatorisk)"

!define GTK_THEMES_SECTION_TITLE		"GTK+-teman"

!define GTK_NOTHEME_SECTION_TITLE		"Inget tema"

!define GTK_WIMP_SECTION_TITLE		"Wimp-tema"

!define GTK_BLUECURVE_SECTION_TITLE	"Bluecurve-tema"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue-tema"
!define GOURMET_SHORTCUTS_SECTION_TITLE "Genvgar"
!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "Skrivbord"
!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Startmeny"
!define GOURMET_SECTION_DESCRIPTION		"Gourmets krnfiler och DLL:er"

!define GTK_SECTION_DESCRIPTION		"En GUI-verktygsuppsttning fr flera olika plattformar som Gourmet anvnder."

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+-teman kan ndra knslan av och utseendet p GTK+-applikationer."

!define GTK_NO_THEME_DESC			"Installera inte ngot GTK+-tema"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) ett GTK-tema som smlter bra in i Windows-miljn."

!define GTK_BLUECURVE_THEME_DESC		"The Bluecurve-tema."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"The Lighthouseblue-tema."

!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Genvgar fr att starta Gourmet"
!define GOURMET_DESKTOP_SHORTCUT_DESC   "Skapar en genvg till Gourmet p skrivbordet"
!define GOURMET_STARTMENU_SHORTCUT_DESC   "Skapar ett tillgg i startmenyn fr Gourmet"


; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"En ldre version av GTK+ runtime hittades, vill du uppgradera den?$\rOBS! Gourmet kommer kanske inte att fungera om du inte uppgraderar."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Besk Windows-Gourmets hemsida"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (enbart fr avinstallation)"

!define GOURMET_PROMPT_WIPEOUT			"Din gamla Gourmet-katalog kommer att raderas, vill du fortstta?$\r$\rOBS! om du har installerat ngra extra insticksmoduler kommer de raderas.$\rGourmets anvndarinstllningar kommer inte pverkas."

!define GOURMET_PROMPT_DIR_EXISTS		"Den katalog du vill installera i finns redan. Allt i katalogen$\rkommer att raderas, vill du fortstta?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Fel vid installation av GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Den skvg du angivit gr inte att komma t eller skapa."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Du har inte rttigheter att installera ett GTK+tema."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Avinstalleraren kunde inte hitta registervrden fr Gourmet.$\rAntagligen har en annan anvndare installerat applikationen."

!define un.GOURMET_UNINSTALL_ERROR_2         "Du har inte rttigheter att avinstallera den hr applikationen."

