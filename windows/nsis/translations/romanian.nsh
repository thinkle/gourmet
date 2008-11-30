;;

;;  romanian.nsh

;;

;;  Romanian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Author: Miºu Moldovan <dumol@gnome.ro>, (c) 2004 - 2005.

;;



; Startup Checks

!define INSTALLER_IS_RUNNING                     "Instalarea este deja pornitã."

!define GOURMET_IS_RUNNING                  "O instanþã a programului Gourmet este deja pornitã. Închideþi-o ºi încercaþi din nou."

!define GTK_INSTALLER_NEEDED			"Mediul GTK+ nu e prezent sau aveþi o versiune prea veche.$\rInstalaþi cel puþin versiunea v${GTK_VERSION} a mediului GTK+"



; License Page

!define GOURMET_LICENSE_BUTTON                      "Înainte >"

!define GOURMET_LICENSE_BOTTOM_TEXT         "$(^Name) are licenþã GPL (GNU Public License). Licenþa este inclusã aici doar pentru scopuri informative. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (obligatoriu)"

!define GTK_SECTION_TITLE			"Mediu GTK+ (obligatoriu)"

!define GTK_THEMES_SECTION_TITLE		"Teme GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Fãrã teme"

!define GTK_WIMP_SECTION_TITLE		"Temã Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Temã Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Temã Light House Blue"

!define GOURMET_SHORTCUTS_SECTION_TITLE "Scurtãturi"

!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "Desktop"

!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Meniu Start"

!define GOURMET_SECTION_DESCRIPTION		"Fiºiere Gourmet ºi dll-uri"

!define GTK_SECTION_DESCRIPTION		"Un mediu de dezvoltare multiplatformã utilizat de Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"Temele GTK+ schimbã aparenþa aplicaþiilor GTK+."

!define GTK_NO_THEME_DESC			"Fãrã teme GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp este o temã GTK+ ce imitã mediul grafic Windows."

!define GTK_BLUECURVE_THEME_DESC		"Tema Bluecurve."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Tema Lighthouseblue."

!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Scurtãturi pentru pornirea Gourmet"

!define GOURMET_DESKTOP_SHORTCUT_DESC   "Creeazã iconiþe Gourmet pe Desktop"

!define GOURMET_STARTMENU_SHORTCUT_DESC   "Creeazã o intrare Gourmet în meniul Start"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Aveþi o versiune veche a mediului GTK+. Doriþi sã o actualizaþi?$\rNotã: E posibil ca Gourmet sã nu funcþioneze cu versiunea veche."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE               "Vizitaþi pagina de web Windows Gourmet"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (doar dezinstalare)"

!define GOURMET_PROMPT_WIPEOUT			"Vechiul director Gourmet va fi ºters. Doriþi sã continuaþi?$\r$\rNotã: Orice module externe vor fi ºterse.$\rSetãrile utilizatorilor Gourmet nu vor fi afectate."

!define GOURMET_PROMPT_DIR_EXISTS		"Directorul ales pentru instalare existã deja.$\rConþinutul sãu va fi ºters. Doriþi sã continuaþi?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Eroare la instalarea mediului GTK+."

!define GTK_BAD_INSTALL_PATH			"Directorul specificat nu poate fi accesat sau creat."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nu aveþi drepturile de acces necesare instalãrii unei teme GTK+."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Programul de dezinstalare nu a gãsit intrãri Gourmet în regiºtri.$\rProbabil un alt utilizator a instalat aceastã aplicaþie."

!define un.GOURMET_UNINSTALL_ERROR_2         "Nu aveþi drepturile de acces necesare dezinstalãrii acestei aplicaþii."

