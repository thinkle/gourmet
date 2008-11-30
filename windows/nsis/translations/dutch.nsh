;;

;;  dutch.nsh

;;

;;  Default language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Author: Vincent van Adrighem <vincent@dirck.mine.nu>

;;  Version 2

;;

; Startup Checks

!define INSTALLER_IS_RUNNING			"Er is al een installatie actief."

!define GOURMET_IS_RUNNING			"Gourmet wordt op dit moment uitgevoerd. Sluit Gourmet af en start de installatie opnieuw."

!define GTK_INSTALLER_NEEDED			"De GTK+ runtime-omgeving is niet aanwezig of moet vernieuwd worden.$\rInstalleer v${GTK_VERSION} of nieuwer van de GTK+ runtime-omgeving"





; License Page

!define GOURMET_LICENSE_BUTTON			"Volgende >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) wordt uitgegeven onder de GPL licentie. Deze licentie wordt hier slechts ter informatie aangeboden. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (vereist)"

!define GTK_SECTION_TITLE			"GTK+ runtime-omgeving (vereist)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ thema's"

!define GTK_NOTHEME_SECTION_TITLE		"Geen thema"

!define GTK_WIMP_SECTION_TITLE		"Wimp thema"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve thema"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue thema"

!define GOURMET_SECTION_DESCRIPTION		"Gourmet hoofdbestanden en dlls"

!define GTK_SECTION_DESCRIPTION		"Een multi-platform gebruikersinterface, gebruikt door Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ thema's veranderen het uiterlijk en gedrag van GTK+ programma's."

!define GTK_NO_THEME_DESC			"Geen GTK+ thema installeren"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) is een GTK+ thema wat goed past in een windows omgeving."

!define GTK_BLUECURVE_THEME_DESC		"Het Bluecurve thema (standaardthema voor RedHat Linux)."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Het Lighthouseblue thema."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Er is een oude versie van GTK+ gevonden. Wilt u deze bijwerken?$\rLet op: Gourmet werkt misschien niet als u dit niet doet."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Neem een kijkje op de Windows Gourmet webpagina"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (alleen verwijderen)"

!define GOURMET_PROMPT_WIPEOUT			"Uw oude Gourmet map staat op het punt om verwijderd te worden. Wilt u doorgaan?$\r$\rLet op: Alle door uzelf genstalleerde plugins zullen ook verwijderd worden.$\rDe gebruikersinstellingen van Gourmet worden niet aangeraakt."

!define GOURMET_PROMPT_DIR_EXISTS		"De gegeven installatiemap bestaat al. Eventuele inhoud zal verwijderd worden. Wilt u doorgaan?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Fout bij installatie van GTK+ runtime omgeving."

!define GTK_BAD_INSTALL_PATH			"Het door u gegeven pad kan niet benaderd worden."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"U heeft geen toestemming om een GTK+ thema te installeren."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Het verwijderingsprogramma voor Gourmet kon geen register-ingangen voor Gourmet vinden.$\rWaarschijnlijk heeft een andere gebruiker het programma genstalleerd."

!define un.GOURMET_UNINSTALL_ERROR_2         "U mag dit programma niet verwijderen."

