;;

;;  albanian.nsh

;;

;;  Albanian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Version 2

;;  Author: Besnik Bleta <besnik@spymac.com>

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"Ose mungon mjedisi GTK+ runtime ose lyp përditësim.$\rJu lutem instaloni GTK+ runtime v${GTK_VERSION} ose më të vonshëm"



; License Page

!define GOURMET_LICENSE_BUTTON			"Më tej >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) qarkullon nën licensën GPL. Licensa këtu sillet vetëm për qëllime njoftimi. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (i nevojshëm)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Environment (i nevojshëm)"

!define GTK_THEMES_SECTION_TITLE		"Tema GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Pa Tema"

!define GTK_WIMP_SECTION_TITLE		"Temë Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Temë Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Temë Light House Blue"

!define GOURMET_SECTION_DESCRIPTION		"Kartela dhe dll bazë të Gourmet-it"

!define GTK_SECTION_DESCRIPTION		"Një grup mjetesh shumëplatformësh për GUI, përdorur nga Gourmet-i"

!define GTK_THEMES_SECTION_DESCRIPTION	"Temat GTK+ mund të ndryshojnë pamjen dhe sjelljen e zbatimeve GTK+."

!define GTK_NO_THEME_DESC			"Mos instalo temë GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) është një temë GTK që ndërthuret mirë mjedisin Windows."

!define GTK_BLUECURVE_THEME_DESC		"Tema Bluecurve."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Tema Lighthouseblue."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"U gjet një version i vjetër për GTK+ runtime. Doni të përditësohet?$\rShënim: Gourmet-i mund të mos punojë nëse nuk e bëni."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Vizitoni Faqen Web të Gourmet-it për Windows"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (vetëm hiq)"

!define GOURMET_PROMPT_WIPEOUT			"Është gati për t'u fshirë drejtoria juaj e vjetër Gourmet. Doni të vazhdohet?$\r$\rShënim: Do të fshihet çfarëdo shtojceë jo standarde që mund të keni instaluar.$\rNuk do të preken rregullime Gourmet përdoruesash."

!define GOURMET_PROMPT_DIR_EXISTS		"Drejtoria e instalimit që treguat ekziston tashmë. Çfarëdo përmbajtje$\rdo të fshihet. Do të donit të vazhdohet?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"gabim gjatë instalimit të GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Shtegu që treguat nuk mund të arrihet ose krijohet."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nuk keni leje të instaloni tema GTK+."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"Çinstaluesi nuk gjeti dot zëra regjistri për Gourmet-in.$\rKa mundësi që këtë zbatim ta ketë instaluar një tjetër përdorues."

!define un.GOURMET_UNINSTALL_ERROR_2		"Nuk keni leje të çinstaloni këtë zbatim."

