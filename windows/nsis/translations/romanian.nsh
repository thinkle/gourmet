;;

;;  romanian.nsh

;;

;;  Romanian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Author: Miu Moldovan <dumol@gnome.ro>, (c) 2004 - 2005.

;;



; Startup Checks

!define INSTALLER_IS_RUNNING                     "Instalarea este deja pornit."

!define GOURMET_IS_RUNNING                  "O instan a programului Gourmet este deja pornit. nchidei-o i ncercai din nou."

!define GTK_INSTALLER_NEEDED			"Mediul GTK+ nu e prezent sau avei o versiune prea veche.$\rInstalai cel puin versiunea v${GTK_VERSION} a mediului GTK+"



; License Page

!define GOURMET_LICENSE_BUTTON                      "nainte >"

!define GOURMET_LICENSE_BOTTOM_TEXT         "$(^Name) are licen GPL (GNU Public License). Licena este inclus aici doar pentru scopuri informative. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (obligatoriu)"

!define GTK_SECTION_TITLE			"Mediu GTK+ (obligatoriu)"

!define GTK_THEMES_SECTION_TITLE		"Teme GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Fr teme"

!define GTK_WIMP_SECTION_TITLE		"Tem Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Tem Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Tem Light House Blue"

!define GOURMET_SHORTCUTS_SECTION_TITLE "Scurtturi"

!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "Desktop"

!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Meniu Start"

!define GOURMET_SECTION_DESCRIPTION		"Fiiere Gourmet 㺺i dll-uri"

!define GTK_SECTION_DESCRIPTION		"Un mediu de dezvoltare multiplatform utilizat de Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"Temele GTK+ schimb aparena aplicaiilor GTK+."

!define GTK_NO_THEME_DESC			"Fr teme GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp este o tem GTK+ ce imit mediul grafic Windows."

!define GTK_BLUECURVE_THEME_DESC		"Tema Bluecurve."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Tema Lighthouseblue."

!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Scurtturi pentru pornirea Gourmet"

!define GOURMET_DESKTOP_SHORTCUT_DESC   "Creeaz iconie Gourmet pe Desktop"

!define GOURMET_STARTMENU_SHORTCUT_DESC   "Creeaz o intrare Gourmet n meniul Start"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Avei o versiune veche a mediului GTK+. Dorii s o actualizai?$\rNot: E posibil ca Gourmet s nu funcioneze cu versiunea veche."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE               "Vizitai pagina de web Windows Gourmet"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (doar dezinstalare)"

!define GOURMET_PROMPT_WIPEOUT			"Vechiul director Gourmet va fi ters. Dorii s continuai?$\r$\rNot: Orice module externe vor fi terse.$\rSetrile utilizatorilor Gourmet nu vor fi afectate."

!define GOURMET_PROMPT_DIR_EXISTS		"Directorul ales pentru instalare exist deja.$\rConinutul su va fi ters. Dorii s continuai?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Eroare la instalarea mediului GTK+."

!define GTK_BAD_INSTALL_PATH			"Directorul specificat nu poate fi accesat sau creat."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nu avei drepturile de acces necesare instalrii unei teme GTK+."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Programul de dezinstalare nu a gsit intrri Gourmet n regitri.$\rProbabil un alt utilizator a instalat aceast aplicaie."

!define un.GOURMET_UNINSTALL_ERROR_2         "Nu avei drepturile de acces necesare dezinstalrii acestei aplicaii."

