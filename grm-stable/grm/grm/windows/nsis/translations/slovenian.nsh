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

!define INSTALLER_IS_RUNNING			"Namešèanje že poteka."

!define GAIM_IS_RUNNING				"Trenutno že teèe razlièica Gourmeta. Prosimo zaprite Gourmet in poskusite znova."

!define GTK_INSTALLER_NEEDED			"Izvajalno okolje GTK+ manjka ali pa ga je potrebno nadgraditi.$\rProsimo namestite v${GTK_VERSION} ali višjo razlièico izvajalnega okolja GTK+"



; License Page

!define GAIM_LICENSE_BUTTON			"Naprej >"

!define GAIM_LICENSE_BOTTOM_TEXT		"$(^Name) je na voljo pod licenco GPL. Ta licenca je tu na voljo le v informativne namene. $_CLICK"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (zahtevano)"

!define GTK_SECTION_TITLE			"GTK+ izvajalno okolje (zahtevano)"

!define GTK_THEMES_SECTION_TITLE		"Teme GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Brez teme"

!define GTK_WIMP_SECTION_TITLE			"Tema Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Tema Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Tema Light House Blue"

!define GAIM_SHORTCUTS_SECTION_TITLE		"Bližnjice"

!define GAIM_DESKTOP_SHORTCUT_SECTION_TITLE	"Namizje"

!define GAIM_STARTMENU_SHORTCUT_SECTION_TITLE	"Zaèetni meni"

!define GAIM_SECTION_DESCRIPTION		"Temeljne datoteke Gourmeta"

!define GTK_SECTION_DESCRIPTION			"Veèplatformna orodjarna GUI, ki jo uporablja Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION		"Teme GTK+ lahko spremenijo izgled programov GTK+."

!define GTK_NO_THEME_DESC			"Brez namestitve teme GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (oponaševalec Oken) je tema GTK, ki se lepo vklaplja v namizno okolje Windows."

!define GTK_BLUECURVE_THEME_DESC		"Tema Bluecurve."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC		"Tema Lighthouseblue."

!define GAIM_SHORTCUTS_SECTION_DESCRIPTION	"Bližnjice za zagon Gourmeta"

!define GAIM_DESKTOP_SHORTCUT_DESC		"Ustvari bližnjico za Gourmet na namizju"

!define GAIM_STARTMENU_SHORTCUT_DESC		"Ustvari vnos Gourmet v meniju Start"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Našel sem starejšo razlièico izvajalnega okolja GTK+. Jo želite nadgraditi?$\rOpomba: èe je ne boste nadgradili, Gourmet morda ne bo deloval."



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"Obišèite spletno stran Windows Gourmet"



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (samo odstrani)"

!define GAIM_PROMPT_WIPEOUT			"Vaš star imenik Gourmet bo zbrisan. Želite nadaljevati?$\r$\rOpomba: Vsi nestandardni vtièniki, ki ste jih namestili, bodo zbrisani.$\rUporabniške nastavitve za Gourmet se bodo ohranile."

!define GAIM_PROMPT_DIR_EXISTS			"Namestitveni imenik, ki ste ga navedli, že obstaja. Vsa vsebina$\rbo zbrisana. Želite nadaljevati?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Napaka pri namestitvi izvajalnega okolja GTK+."

!define GTK_BAD_INSTALL_PATH			"Pot, ki ste jo vnesli, ni dosegljiva ali je ni mogoèe ustvariti."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Za namestitev teme GTK+ nimate ustreznih pravic."



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1		"Ne morem najti vnosov v registru za Gourmet.$\rNajverjetneje je ta program namestil drug uporabnik."

!define un.GAIM_UNINSTALL_ERROR_2		"Za odstranitev programa nimate ustreznih pravic."

