;;

;;  slovak.nsh

;;

;;  Slovak language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Author: dominik@internetkosice.sk

;;  Version 2



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ runtime prostredie chba alebo mus by upgradovan.$\rNaintalujte, prosm, GTK+ runtime verziu v${GTK_VERSION}, alebo noviu"



; License Page

!define GOURMET_LICENSE_BUTTON			"alej >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) je vydan pod GPL licenciou. Tto licencia je len pre informan ely. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (nevyhnutn)"

!define GTK_SECTION_TITLE			"GTK+ Runtime prostredie (nevyhnutn)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ tmy"

!define GTK_NOTHEME_SECTION_TITLE		"iadna grafick tma"

!define GTK_WIMP_SECTION_TITLE		"Wimp grafick tma"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve grafick tma"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue grafick tma"

!define GOURMET_SECTION_DESCRIPTION		"Jadro Gourmet-u a nevyhnutn DLL sbory"

!define GTK_SECTION_DESCRIPTION		"Multiplatformov GUI nstroje, pouvan Gourmet-om"

!define GTK_THEMES_SECTION_DESCRIPTION	"Pomocou GTK+ grafickch tm mete zmeni? vzh?ad GTK+ aplikci."

!define GTK_NO_THEME_DESC			"Neintalova횝 GTK+ grafick tmu"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) je GTK grafick tma, ktor pekne lad s prostredm Windows."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve grafick tma."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue grafick tma"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Bola njden staria verzia GTK+ runtime. Prajete si upgradova᚝ sasn verziu?$\rPoznmka: Gourmet nemus po upgradovan fungova sprvne."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Navtvi webstrnku Windows Gourmet"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (len odstrni)"

!define GOURMET_PROMPT_WIPEOUT			"V adresr Gourmet bude zmazan. Chcete pokraova?$\r$\rPoznmka: Vetky prdavne pluginy, ktor ste naintalovali bud tie zmazan.$\rNastavenia uivate鞾skho tu Gourmet-u bud ponechan."

!define GOURMET_PROMPT_DIR_EXISTS		"Adresr, ktor ste zadali, u existuje. Jeho obsah bude zmazan. Chcete pokraova?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Chyba pri in蝚talcii GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Zadan cesta nie je prstupn alebo ju nie je mon vytvori."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nemte oprvnenie na intalciu GTK+ grafickej tmy."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"Intaltoru sa nepodarilo njs polo᝞ky v registri pre Gourmet.$\rJe mon, e tto aplikciu naintaloval in pouvate."

!define un.GOURMET_UNINSTALL_ERROR_2		"Nemte oprvnenie na odintalciu tejto aplikcie."

