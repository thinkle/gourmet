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

!define GTK_INSTALLER_NEEDED			"A GTK+ futtat krnyezet hinyzik vagy frisstse szksges.$\rKrem teleptse a v${GTK_VERSION} vagy magasabb verzij GTK+ futtat krnyezetet."

!define INSTALLER_IS_RUNNING			"A telept mr fut."

!define GOURMET_IS_RUNNING			"Jelenleg fut a Gourmet egy pldnya. Lpjen ki a Gourmetbl s prblja jra."



; License Page

!define GOURMET_LICENSE_BUTTON			"Tovbb >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"A $(^Name) a GNU General Public License (GPL) alatt kerl terjesztsre. Az itt olvashat licenc csak tjkoztatsi clt szolgl. $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (szksges)"

!define GTK_SECTION_TITLE			"GTK+ futtat krnyezet (szksges)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ tmk"

!define GTK_NOTHEME_SECTION_TITLE		"Nincs tma"

!define GTK_WIMP_SECTION_TITLE		"Wimp tma"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve tma"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue tma"

!define GOURMET_SHORTCUTS_SECTION_TITLE "Parancsikonok"

!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "Asztal"

!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Start Men"

!define GOURMET_SECTION_DESCRIPTION		"Gourmet fjlok s dll-ek"

!define GTK_SECTION_DESCRIPTION		"A Gourmet ltal hasznlt tbbplatformos grafikus krnyezet"

!define GTK_THEMES_SECTION_DESCRIPTION	"A GTK+ tmk megvltoztatjk a GTK+ alkalmazsok kinzett."

!define GTK_NO_THEME_DESC			"Ne teleptse a GTK+ tmkat"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows utnzat) egy Windows krnyezettel harmonizl GTK tma."

!define GTK_BLUECURVE_THEME_DESC		"A Bluecurve tma."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"A Lighthouseblue tma."

!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Parancsikonok a Gourmet indtshoz"

!define GOURMET_DESKTOP_SHORTCUT_DESC   "Parancsikon ltrehozsa aGourmethoz az asztalon"

!define GOURMET_STARTMENU_SHORTCUT_DESC   "Start Men bejegyzs ltrehozsa a Gourmethoz"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Egy rgi verzij GTK+ futtatkrnyezet van teleptve. Kvnja frissteni?$\rMegjegyzs: a Gourmet nem fog mkdni, ha nem frissti."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"A Windows Gourmet weboldalnak felkeresse"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (csak eltvolts)"

!define GOURMET_PROMPT_WIPEOUT			"Az n korbbi Gourmet knyvtra trlve lesz. Folytatni szeretn?$\r$\rMegjegyzs: Minden n ltal teleptett bvtmny trlve lesz.$\rA Gourmet felhasznli belltsokra ez nincs hatssal."

!define GOURMET_PROMPT_DIR_EXISTS		"A megadott teleptsi knyvtr mr ltezik. A tartalma trlve lesz.$\rFolytatni szeretn?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Hiba a GTK+ futtatkrnyezet teleptse kzben."

!define GTK_BAD_INSTALL_PATH			"A megadott elrsi t nem rhet el, vagy nem hozhat ltre."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Nincs jogosultsga a GTK+ tmk teleptshez."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Az eltvolt nem tallta a Gourmet registry bejegyzseket.$\rValsznleg egy msik felhasznl teleptette az alkalmazst."

!define un.GOURMET_UNINSTALL_ERROR_2         "Nincs jogosultsga az alkalmazs eltvoltshoz."
