;;

;;  polish.nsh

;;

;;  Polish language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Author: Jan Eldenmalm <jan.eldenmalm@amazingports.com>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"Runtime œrodowiska GTK+ zosta³ zagubiony lub wymaga upgrade-u.$\r Proszê zainstaluj v${GTK_VERSION} albo wy¿sz¹ wersjê runtime-u GTK+."



; License Page

!define GOURMET_LICENSE_BUTTON			"Dalej >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) jest wydzielone w licencji GPL. Udziela siê licencji wy³¹cznie do celów informacyjnych. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Wymagany jest Gourmet Recipe Manager"

!define GTK_SECTION_TITLE			"Wymagany jest runtime œrodowiska GTK+"

!define GTK_THEMES_SECTION_TITLE		"Temat GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Brak tematów"

!define GTK_WIMP_SECTION_TITLE		"Temat Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Temat Bluecurve "

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Temat Light House Blue"

!define GOURMET_SECTION_DESCRIPTION		"Zbiory Core Gourmet oraz dll"

!define GTK_SECTION_DESCRIPTION		"Wieloplatformowe narzêdzie GUI, u¿ywane w Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"Tematy GTK+ mog¹ zmieniæ wygl¹d i dzia³anie aplikacji GTK+ ."

!define GTK_NO_THEME_DESC			"Nie instaluj tematów GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) to temat GTK który doskonale wkomponowuje siê w œrodowisko systemu Windows."

!define GTK_BLUECURVE_THEME_DESC		"Temat The Bluecurve."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Temat Lighthouseblue."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Znaleziono star¹ wersjê runtime-u GTK+. Czy chcesz upgrade-owaæ?$\rNote: Gourmet mo¿e nie dzia³aæ jeœli nie wykonasz procedury."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"WejdŸ na stronê Gourmet Web Page"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (usuñ program)"

!define GOURMET_PROMPT_WIPEOUT			"Stary katalog Gourmet zosta³ usuniêty. Czy chcesz kontunuowaæ?$\r$\rNote: Wszystkie stare - niestandardowe plugin-y zosta³y usuniête.$\r Ustawienia u¿utkownika Gourmet bêd¹ wy³¹czone."

!define GOURMET_PROMPT_DIR_EXISTS		"Wybrany katalog instalacyjny ju¿ istnieje. Jego zawartoœæ $\r zostanie skasowana. Czy chcesz kontunuowaæ?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"B³¹d instalacji runtime-a GTK+."

!define GTK_BAD_INSTALL_PATH			"Nie ma dostêpu do wybranej œcie¿ki / ³aty."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nie masz uprawnieñ do zainstalowania tematu GTK+."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"Deinstalator nie mo¿e znaleŸæ rejestrów dla Gourmet.$\r Wskazuje to na to, ¿e instalacjê przeprowadzi³ inny u¿ytkownik."

!define un.GOURMET_UNINSTALL_ERROR_2		"Nie masz uprawnieñ do deinstalacji tej aplikacji."

