;;

;;  slovenian.nsh

;;

;;  Slovenian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Author: Martin Srebotnjak <miles@filmsi.net>

;;  Version 3

;;



; Startup GTK+ check

!define INSTALLER_IS_RUNNING			"Nameanje e poteka."

!define GOURMET_IS_RUNNING				"Trenutno 螞e tee razliica Gourmeta. Prosimo zaprite Gourmet in poskusite znova."

!define GTK_INSTALLER_NEEDED			"Izvajalno okolje GTK+ manjka ali pa ga je potrebno nadgraditi.$\rProsimo namestite v${GTK_VERSION} ali vijo razliico izvajalnega okolja GTK+"



; License Page

!define GOURMET_LICENSE_BUTTON			"Naprej >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) je na voljo pod licenco GPL. Ta licenca je tu na voljo le v informativne namene. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (zahtevano)"

!define GTK_SECTION_TITLE			"GTK+ izvajalno okolje (zahtevano)"

!define GTK_THEMES_SECTION_TITLE		"Teme GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Brez teme"

!define GTK_WIMP_SECTION_TITLE			"Tema Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Tema Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Tema Light House Blue"

!define GOURMET_SHORTCUTS_SECTION_TITLE		"Blinjice"

!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE	"Namizje"

!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE	"Zaetni meni"

!define GOURMET_SECTION_DESCRIPTION		"Temeljne datoteke Gourmeta"

!define GTK_SECTION_DESCRIPTION			"Veplatformna orodjarna GUI, ki jo uporablja Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION		"Teme GTK+ lahko spremenijo izgled programov GTK+."

!define GTK_NO_THEME_DESC			"Brez namestitve teme GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (oponaevalec Oken) je tema GTK, ki se lepo vklaplja v namizno okolje Windows."

!define GTK_BLUECURVE_THEME_DESC		"Tema Bluecurve."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC		"Tema Lighthouseblue."

!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION	"Bli蚞njice za zagon Gourmeta"

!define GOURMET_DESKTOP_SHORTCUT_DESC		"Ustvari blinjico za Gourmet na namizju"

!define GOURMET_STARTMENU_SHORTCUT_DESC		"Ustvari vnos Gourmet v meniju Start"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Nael sem starejo razliico izvajalnega okolja GTK+. Jo elite nadgraditi?$\rOpomba: e je ne boste nadgradili, Gourmet morda ne bo deloval."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Obiite spletno stran Windows Gourmet"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (samo odstrani)"

!define GOURMET_PROMPT_WIPEOUT			"Va star imenik Gourmet bo zbrisan. 蚎elite nadaljevati?$\r$\rOpomba: Vsi nestandardni vtiniki, ki ste jih namestili, bodo zbrisani.$\rUporabnike nastavitve za Gourmet se bodo ohranile."

!define GOURMET_PROMPT_DIR_EXISTS			"Namestitveni imenik, ki ste ga navedli, 蚞e obstaja. Vsa vsebina$\rbo zbrisana. elite nadaljevati?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Napaka pri namestitvi izvajalnega okolja GTK+."

!define GTK_BAD_INSTALL_PATH			"Pot, ki ste jo vnesli, ni dosegljiva ali je ni mogoe ustvariti."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Za namestitev teme GTK+ nimate ustreznih pravic."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"Ne morem najti vnosov v registru za Gourmet.$\rNajverjetneje je ta program namestil drug uporabnik."

!define un.GOURMET_UNINSTALL_ERROR_2		"Za odstranitev programa nimate ustreznih pravic."

