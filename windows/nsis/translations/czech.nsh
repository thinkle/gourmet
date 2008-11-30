;;

;;  czech.nsh

;;

;;  Czech language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Author: Jan Kolar <jan@e-kolar.net>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ runtime buto chyb, nebo je poteba provst upgrade.$\rProvete instalaci verze${GTK_VERSION} nebo vy."



; License Page

!define GOURMET_LICENSE_BUTTON			"Dal >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"K pouit $(^Name) se vztahuje GPL licence. Licence je zde uvedena pouze pro Va informaci. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (nutn)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Environment (nutn)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ tmata"

!define GTK_NOTHEME_SECTION_TITLE		"Bez tmat"

!define GTK_WIMP_SECTION_TITLE		"Wimp tma"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve tma"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue tma"

!define GOURMET_SECTION_DESCRIPTION		"Zkladn soubory a DLL pro Gourmet"

!define GTK_SECTION_DESCRIPTION		"Multi-platform GUI toolkit pouvan Gourmetem"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ tmata umouj mnit vzhled a zpsob ovldn GTK+ aplikac."

!define GTK_NO_THEME_DESC			"Neinstalovat GTK+ tma"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) je GTK tma kter zapadne do Vaeho pracovnho prosted ve Windows."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve tma."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue tma."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Byla nalezena star verze GTK+ runtime. Chcete provst upgrade?$\rUpozornn: Bez upgradu Gourmet nemus pracovat sprvn."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Navtvit Windows Gourmet Web Page"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (odinstalovat)"

!define GOURMET_PROMPT_WIPEOUT			"V star adres pro Gourmet bude vymazn. Chcete pokraovat?$\r$\rUpozornn: Jakkoli nestandardn rozen (plugin) , kter mte nainstalovna budou ztracena.$\rUivatelsk nastaven pro Gourmet budou zachovna."

!define GOURMET_PROMPT_DIR_EXISTS		"Adres kter byl zadn pro instalaci ji existuje. Veរker obsah$\rbude smazn. Chcete pokraovat?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Chyba pi instalaci GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Zadan cesta je nedostupn, nebo ji nelze vytvoit."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nemte oprvnn k instalaci GTK+ tmatu."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"Odinstaln proces neme najt zznamy pro Gourmet v registrech.$\rPravdpodobn instalaci tto aplikace provedl jin uivatel."

!define un.GOURMET_UNINSTALL_ERROR_2		"Nemte oprvnn k odinstalaci tto aplikace."

