;;

;;  hungarian.nsh

;;

;;  Default language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Authors: Sutto Zoltan <suttozoltan@chello.hu>, 2003

;;	     Gabor Kelemen <kelemeng@gnome.hu>, 2005

;;



; Startup Checks

!define GTK_INSTALLER_NEEDED			"A GTK+ futtató környezet hiányzik vagy frissítése szükséges.$\rKérem telepítse a v${GTK_VERSION} vagy magasabb verziójú GTK+ futtató környezetet."

!define INSTALLER_IS_RUNNING			"A telepítõ már fut."

!define GAIM_IS_RUNNING			"Jelenleg fut a Gourmet egy példánya. Lépjen ki a Gourmetból és próbálja újra."



; License Page

!define GAIM_LICENSE_BUTTON			"Tovább >"

!define GAIM_LICENSE_BOTTOM_TEXT		"A $(^Name) a GNU General Public License (GPL) alatt kerül terjesztésre. Az itt olvasható licenc csak tájékoztatási célt szolgál. $_CLICK"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (szükséges)"

!define GTK_SECTION_TITLE			"GTK+ futtató környezet (szükséges)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ témák"

!define GTK_NOTHEME_SECTION_TITLE		"Nincs téma"

!define GTK_WIMP_SECTION_TITLE		"Wimp téma"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve téma"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue téma"

!define GAIM_SHORTCUTS_SECTION_TITLE "Parancsikonok"

!define GAIM_DESKTOP_SHORTCUT_SECTION_TITLE "Asztal"

!define GAIM_STARTMENU_SHORTCUT_SECTION_TITLE "Start Menü"

!define GAIM_SECTION_DESCRIPTION		"Gourmet fájlok és dll-ek"

!define GTK_SECTION_DESCRIPTION		"A Gourmet által használt többplatformos grafikus környezet"

!define GTK_THEMES_SECTION_DESCRIPTION	"A GTK+ témák megváltoztatják a GTK+ alkalmazások kinézetét."

!define GTK_NO_THEME_DESC			"Ne telepítse a GTK+ témákat"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows utánzat) egy Windows környezettel harmonizáló GTK téma."

!define GTK_BLUECURVE_THEME_DESC		"A Bluecurve téma."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"A Lighthouseblue téma."

!define GAIM_SHORTCUTS_SECTION_DESCRIPTION   "Parancsikonok a Gourmet indításához"

!define GAIM_DESKTOP_SHORTCUT_DESC   "Parancsikon létrehozása aGourmethoz az asztalon"

!define GAIM_STARTMENU_SHORTCUT_DESC   "Start Menü bejegyzés létrehozása a Gourmethoz"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Egy régi verziójú GTK+ futtatókörnyezet van telepítve. Kívánja frissíteni?$\rMegjegyzés: a Gourmet nem fog mûködni, ha nem frissíti."



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"A Windows Gourmet weboldalának felkeresése"



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (csak eltávolítás)"

!define GAIM_PROMPT_WIPEOUT			"Az Ön korábbi Gourmet könyvtára törölve lesz. Folytatni szeretné?$\r$\rMegjegyzés: Minden Ön által telepített bõvítmény törölve lesz.$\rA Gourmet felhasználói beállításokra ez nincs hatással."

!define GAIM_PROMPT_DIR_EXISTS		"A megadott telepítési könyvtár már létezik. A tartalma törölve lesz.$\rFolytatni szeretné?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Hiba a GTK+ futtatókörnyezet telepítése közben."

!define GTK_BAD_INSTALL_PATH			"A megadott elérési út nem érhetõ el, vagy nem hozható létre."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nincs jogosultsága a GTK+ témák telepítéséhez."



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1         "Az eltávolító nem találta a Gourmet registry bejegyzéseket.$\rValószínüleg egy másik felhasználó telepítette az alkalmazást."

!define un.GAIM_UNINSTALL_ERROR_2         "Nincs jogosultsága az alkalmazás eltávolításához."
