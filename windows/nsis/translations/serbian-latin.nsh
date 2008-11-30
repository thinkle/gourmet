;;

;;  serbian-latin.nsh

;;

;;  Serbian (Latin) language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Author: Danilo Segan <dsegan@gmx.net>

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ okolina za izvravanje ili nije naena ili se moraunaprediti.$\rMolimo instalirajte v${GTK_VERSION} ili veu GTK+ okoline za izvravanje"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (neophodno)"

!define GTK_SECTION_TITLE			"GTK+ okolina za izvr暚avanje (neophodno)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ teme"

!define GTK_NOTHEME_SECTION_TITLE		"Bez teme"

!define GTK_WIMP_SECTION_TITLE		"Wimp tema"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve tema"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue tema"

!define GOURMET_SECTION_DESCRIPTION		"Osnovne Gourmet datoteke i dinamike biblioteke"

!define GTK_SECTION_DESCRIPTION		"Skup orua za grafiko okruenje, za vi螚e platformi, koristi ga Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ teme menjaju izgled i nain rada GTK+ aplikacija."

!define GTK_NO_THEME_DESC			"Ne instaliraj GTK+ temu"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows imitator) je GTK tema koja se dobro uklapa u Windows radno okruenje."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve tema."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue tema."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Naena je stara verzija GTK+ izvrne okoline. Da li ?elite da je unapredite?$\rPrimedba: Ukoliko to ne uradite, Gourmet mo?da nee raditi."



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (samo uklanjanje)"

!define GOURMET_PROMPT_WIPEOUT			"Va stari Gourmet direktorijum e biti obrisan. Da li elite da nastavite?$\r$\rPrimedba: Svi nestandardni dodaci koje ste instalirali e biti obrisani.$\rGourmet postavke korisnika nee biti promenjene."

!define GOURMET_PROMPT_DIR_EXISTS		"Instalacioni direktorijum koji ste naveli ve postoji. Sav sadraj$\re biti obrisan. Da li elite da nastavite?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Gre枚ka prilikom instalacije GTK+ okoline za izvravanje."

!define GTK_BAD_INSTALL_PATH			"Putanja koju ste naveli se ne moe ni napraviti niti joj se moe prii."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nemate ovlaenja za instalaciju GTK+ teme."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Program za uklanjanje instalacije ne moe da pronae stavke registra za Gourmet.$\rVerovatno je ovu aplikaciju instalirao drugi korisnik."

!define un.GOURMET_UNINSTALL_ERROR_2         "Nemate ovlaenja za deinstalaciju ove aplikacije."

