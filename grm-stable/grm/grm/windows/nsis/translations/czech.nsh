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

!define GTK_INSTALLER_NEEDED			"GTK+ runtime buïto chybí, nebo je potøeba provést upgrade.$\rProveïte instalaci verze${GTK_VERSION} nebo vyšší."



; License Page

!define GAIM_LICENSE_BUTTON			"Další >"

!define GAIM_LICENSE_BOTTOM_TEXT		"K použití $(^Name) se vztahuje GPL licence. Licence je zde uvedena pouze pro Vaší informaci. $_CLICK"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (nutné)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Environment (nutné)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ témata"

!define GTK_NOTHEME_SECTION_TITLE		"Bez témat"

!define GTK_WIMP_SECTION_TITLE		"Wimp téma"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve téma"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue téma"

!define GAIM_SECTION_DESCRIPTION		"Základní soubory a DLL pro Gourmet"

!define GTK_SECTION_DESCRIPTION		"Multi-platform GUI toolkit používaný Gourmetem"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ témata umožòují mìnit vzhled a zpùsob ovládání GTK+ aplikací."

!define GTK_NO_THEME_DESC			"Neinstalovat GTK+ téma"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) je GTK téma které zapadne do Vašeho pracovního prostøedí ve Windows."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve téma."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue téma."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Byla nalezena starší verze GTK+ runtime. Chcete provést upgrade?$\rUpozornìní: Bez upgradu Gourmet nemusí pracovat správnì."



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"Navštívit Windows Gourmet Web Page"



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (odinstalovat)"

!define GAIM_PROMPT_WIPEOUT			"Váš starý adresáø pro Gourmet bude vymazán. Chcete pokraèovat?$\r$\rUpozornìní: Jakákoli nestandardní rozšíøení (plugin) , která máte nainstalována budou ztracena.$\rUživatelská nastavení pro Gourmet budou zachována."

!define GAIM_PROMPT_DIR_EXISTS		"Adresáø který byl zadán pro instalaci již existuje. Veškerý obsah$\rbude smazán. Chcete pokraèovat?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Chyba pøi instalaci GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Zadaná cesta je nedostupná, nebo ji nelze vytvoøit."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nemáte oprávnìní k instalaci GTK+ tématu."



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1		"Odinstalèní proces nemùže najít záznamy pro Gourmet v registrech.$\rPravdìpodobnì instalaci této aplikace provedl jiný uživatel."

!define un.GAIM_UNINSTALL_ERROR_2		"Nemáte oprávnìní k odinstalaci této aplikace."

