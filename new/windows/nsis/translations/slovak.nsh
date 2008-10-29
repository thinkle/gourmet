;;

;;  slovak.nsh

;;

;;  Slovak language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Author: dominik@internetkosice.sk

;;  Version 2



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ runtime prostredie chıba alebo musí by upgradované.$\rNainštalujte, prosím, GTK+ runtime verziu v${GTK_VERSION}, alebo novšiu"



; License Page

!define GAIM_LICENSE_BUTTON			"Ïalej >"

!define GAIM_LICENSE_BOTTOM_TEXT		"$(^Name) je vydanı pod GPL licenciou. Táto licencia je len pre informaèné úèely. $_CLICK"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (nevyhnutné)"

!define GTK_SECTION_TITLE			"GTK+ Runtime prostredie (nevyhnutné)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ témy"

!define GTK_NOTHEME_SECTION_TITLE		"iadna grafická téma"

!define GTK_WIMP_SECTION_TITLE		"Wimp grafická téma"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve grafická téma"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue grafická téma"

!define GAIM_SECTION_DESCRIPTION		"Jadro Gourmet-u a nevyhnutné DLL súbory"

!define GTK_SECTION_DESCRIPTION		"Multiplatformové GUI nástroje, pouívané Gourmet-om"

!define GTK_THEMES_SECTION_DESCRIPTION	"Pomocou GTK+ grafickıch tém môete zmeni vzh¾ad GTK+ aplikácií."

!define GTK_NO_THEME_DESC			"Neinštalova GTK+ grafickú tému"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) je GTK grafická téma, ktorá pekne ladí s prostredím Windows."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve grafická téma."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue grafická téma"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Bola nájdená staršia verzia GTK+ runtime. Prajete si upgradova súèasnú verziu?$\rPoznámka: Gourmet nemusí po upgradovaní fungova správne."



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"Navštívi webstránku Windows Gourmet"



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (len odstráni)"

!define GAIM_PROMPT_WIPEOUT			"Váš adresár Gourmet bude zmazanı. Chcete pokraèova?$\r$\rPoznámka: Všetky prídavne pluginy, ktoré ste nainštalovali budú tie zmazané.$\rNastavenia uivate¾ského úètu Gourmet-u budú ponechané."

!define GAIM_PROMPT_DIR_EXISTS		"Adresár, ktorı ste zadali, u existuje. Jeho obsah bude zmazanı. Chcete pokraèova?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Chyba pri inštalácii GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Zadaná cesta nie je prístupná alebo ju nie je moné vytvori."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nemáte oprávnenie na inštaláciu GTK+ grafickej témy."



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1		"Inštalátoru sa nepodarilo nájs poloky v registri pre Gourmet.$\rJe moné, e túto aplikáciu nainštaloval inı pouívate¾."

!define un.GAIM_UNINSTALL_ERROR_2		"Nemáte oprávnenie na odinštaláciu tejto aplikácie."

