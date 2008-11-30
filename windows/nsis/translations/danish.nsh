;;

;;  danish.nsh

;;

;;  Danish language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Author: Ewan Andreasen <wiredloose@myrealbox.com>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ runtime environment enten mangler eller skal opgraderes.$\rInstallr venligst GTK+ runtime version v${GTK_VERSION} eller hjere."



; License Page

!define GOURMET_LICENSE_BUTTON			"Nste >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) er frigivet under GPL licensen. Licensen er kun medtaget her til generel orientering. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (obligatorisk)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Environment (obligatorisk)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ Temaer"

!define GTK_NOTHEME_SECTION_TITLE		"Intet Tema"

!define GTK_WIMP_SECTION_TITLE		"Wimp Tema"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve Tema"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue Tema"

!define GOURMET_SECTION_DESCRIPTION		"Basale Gourmet filer og biblioteker"

!define GTK_SECTION_DESCRIPTION		"Et multi-platform grafisk interface udviklingsvrktj, bruges af Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ Temaer kan ndre GTK+ programmers generelle udseende."

!define GTK_NO_THEME_DESC			"Installr ikke noget GTK+ tema"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows efterligner) er et GTK tema som falder i med Windows skrivebordsmiljet."

!define GTK_BLUECURVE_THEME_DESC		"The Bluecurve tema."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"The Lighthouseblue tema."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Der blev fundet en ldre version af GTK+ runtime. nsker du at opgradere?$\rNB: Gourmet virker muligvis ikke uden denne opgradering."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Besg Windows Gourmet's hjemmeside"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (fjern)"

!define GOURMET_PROMPT_WIPEOUT			"Din gamle Gourmet folder vil blive slettet. nsker du at fortstte? $\r$\rNB: Alle ikke-standard plugins du mtte have installeret vil blive slettet.$\rGourmet brugerindstillinger vil ikke blive pvirket af dette."

!define GOURMET_PROMPT_DIR_EXISTS		"Den nskede installationsfolder eksisterer allerede. Ethvert indhold$\ri folderen vil blive slettet. nsker du at fortstte?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Fejl under installeringen af GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Stien du har angivet kan ikke findes eller oprettes."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Du har ikke tilladelse til at installere et GTK+ tema."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"Afinstallationen kunne ikke finde Gourmet i registreringsdatabasen.$\rMuligvis har en anden bruger installeret programmet."

!define un.GOURMET_UNINSTALL_ERROR_2		"Du har ikke tilladelse til at afinstallere dette program."



