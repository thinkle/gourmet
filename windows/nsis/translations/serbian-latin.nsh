;;

;;  serbian-latin.nsh

;;

;;  Serbian (Latin) language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1250

;;

;;  Author: Danilo Segan <dsegan@gmx.net>

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ okolina za izvršavanje ili nije naðena ili se moraunaprediti.$\rMolimo instalirajte v${GTK_VERSION} ili veæu GTK+ okoline za izvršavanje"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (neophodno)"

!define GTK_SECTION_TITLE			"GTK+ okolina za izvršavanje (neophodno)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ teme"

!define GTK_NOTHEME_SECTION_TITLE		"Bez teme"

!define GTK_WIMP_SECTION_TITLE		"Wimp tema"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve tema"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue tema"

!define GOURMET_SECTION_DESCRIPTION		"Osnovne Gourmet datoteke i dinamièke biblioteke"

!define GTK_SECTION_DESCRIPTION		"Skup oruða za grafièko okruženje, za više platformi, koristi ga Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ teme menjaju izgled i naèin rada GTK+ aplikacija."

!define GTK_NO_THEME_DESC			"Ne instaliraj GTK+ temu"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows imitator) je GTK tema koja se dobro uklapa u Windows radno okruženje."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve tema."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue tema."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Naðena je stara verzija GTK+ izvršne okoline. Da li želite da je unapredite?$\rPrimedba: Ukoliko to ne uradite, Gourmet možda neæe raditi."



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (samo uklanjanje)"

!define GOURMET_PROMPT_WIPEOUT			"Vaš stari Gourmet direktorijum æe biti obrisan. Da li želite da nastavite?$\r$\rPrimedba: Svi nestandardni dodaci koje ste instalirali æe biti obrisani.$\rGourmet postavke korisnika neæe biti promenjene."

!define GOURMET_PROMPT_DIR_EXISTS		"Instalacioni direktorijum koji ste naveli veæ postoji. Sav sadržaj$\ræe biti obrisan. Da li želite da nastavite?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Greška prilikom instalacije GTK+ okoline za izvršavanje."

!define GTK_BAD_INSTALL_PATH			"Putanja koju ste naveli se ne može ni napraviti niti joj se može priæi."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nemate ovlašæenja za instalaciju GTK+ teme."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Program za uklanjanje instalacije ne može da pronaðe stavke registra za Gourmet.$\rVerovatno je ovu aplikaciju instalirao drugi korisnik."

!define un.GOURMET_UNINSTALL_ERROR_2         "Nemate ovlašæenja za deinstalaciju ove aplikacije."

