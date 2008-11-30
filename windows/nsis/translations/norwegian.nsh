;;

;;  norwegian.nsh

;;

;;  Norwegian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Jørgen_Vinne_Iversen <jorgenvi@tihlde.org>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ runtime environment mangler eller trenger en oppgradering.$\rVennligst installér GTK+ v${GTK_VERSION} eller høyere"



; License Page

!define GOURMET_LICENSE_BUTTON			"Neste >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) er utgitt under GPL (GNU General Public License). Lisensen er oppgitt her kun med henblikk på informasjon. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (obligatorisk)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Environment (obligatorisk)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ Tema"

!define GTK_NOTHEME_SECTION_TITLE		"Ingen tema"

!define GTK_WIMP_SECTION_TITLE		"Wimp-tema"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve-tema"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue-tema"

!define GOURMET_SECTION_DESCRIPTION		"Gourmets kjernefiler og dll'er"

!define GTK_SECTION_DESCRIPTION		"Et GUI-verktøy for flere ulike plattformer, brukes av GOURMET."

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ Tema kan endre utseendet og følelsen av GTK+ applikasjoner."

!define GTK_NO_THEME_DESC			"Ikke installér noe GTK+ tema."

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows-imitator) er et GTK-tema som passer godt inn i Windows-miljø."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve-tema."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue-tema."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"En eldre versjon av GTK+ runtime ble funnet. Ønsker du å oppgradere?$\rMerk: Gourmet vil kanskje ikke virke hvis du ikke oppgraderer."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Besøk Gourmet for Windows' Nettside"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (kun avinstallering)"

!define GOURMET_PROMPT_WIPEOUT			"Din gamle Gourmet-katalog holder på å slettes. Ønsker du å fortsette?$\r$\rMerk: Eventuelle ikke-standard plugin'er du har installert vil bli slettet.$\rGourmets brukerinstillinger vil ikke bli berørt."

!define GOURMET_PROMPT_DIR_EXISTS		"Installasjonskatalogen du har spesifisert finnes fra før. Eventuelt innhold$\rvil bli slettet. Ønsker du å fortsette?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"En feil oppstod ved installering av GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Stien du oppga kan ikke aksesseres eller lages."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Du har ikke rettigheter til å installere et GTK+ tema."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"Avinstalleringsprogrammet kunne ikke finne noen registeroppføring for Gourmet.$\rTrolig har en annen bruker installert denne applikasjonen."

!define un.GOURMET_UNINSTALL_ERROR_2		"Du har ikke rettigheter til å avinstallere denne applikasjonen."

