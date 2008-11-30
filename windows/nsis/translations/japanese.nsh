;;

;;  japanese.nsh

;;

;;  Japanese language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 932

;;

;;  Author: "Takeshi Kurosawa" <t-kuro@abox23.so-net.ne.jp>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+^Cµ̓AbvO[hK镗v܂B$\rv${GTK_VERSION}µ͂ȏGTK+̃^CCビXg[ĂB"



; License Page

!define GOURMET_LICENSE_BUTTON			" >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name)ւGPL̓CZX̌Ń[XĂ܂BCZX͂ɎQl̂߂ɒ񋟂Ă܂B $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (K{)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Environment (K{)"

!define GTK_THEMES_SECTION_TITLE		"GTK+̃e[}"

!define GTK_NOTHEME_SECTION_TITLE		"e[}Ȃ"

!define GTK_WIMP_SECTION_TITLE		"Wimpe[}"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurvee[}"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Bluee[}"

!define GOURMET_SECTION_DESCRIPTION		"Gourmet̊jƂȂt郃@Cdll"

!define GTK_SECTION_DESCRIPTION		"GourmetƂ̎gBĂ}郃`vbgtH[GUIc[Lbg"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+̃e[}́AGTK+̃AvP[ṼbNtB[ς܂B"

!define GTK_NO_THEME_DESC			"GTK+̃e[}CビXg[Ȃ"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator)Windows͂̃fXNgbvƂ悭ae[}łB"

!define GTK_BLUECURVE_THEME_DESC		"Bluecurvee[}B"

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthousebluee[}B"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Âo[WGTK+̃^C܂BAbvO[h܂?$\r: Gourmetӂ̓AbvO[hȂ蓮Ȃł傤B"



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Windows GourmetWeb̃y[WK?ĂB"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (폜̂)"

!define GOURMET_PROMPT_WIPEOUT			"݌ÂGourmet̃tH_̍폜ɊւāBs܂?$\r$\r: ӂȂ̃CXg[ׂĂ̔W񕏀ȃvOC͍폜܂B$\rGourmet̐ݒ͉e󂯂܂B"

!define GOURMET_PROMPT_DIR_EXISTS		"񁂠Ȃ̎w肵CXg[̃tH_͂łɑ݂Ă܂Beׂׂ͂$\rč폜܂Bs܂?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"GTK+^C̃CXg[ŃG[܂B"

!define GTK_BAD_INSTALL_PATH			"Ȃ̓͂pXɃANZX܂͍쐬ł܂B"



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"񁂠ȂGTK+͂̃e[}CビXg[錠BĂ܂B"



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"?A?CXg[Gourmet͂̃WXgGg𔭌ł܂łB$\r炭ʂ̃[UɃCXg[ꂽł傤B"

!define un.GOURMET_UNINSTALL_ERROR_2		"Ȃ͂̃AvP[VAビCXg[錠BĂ܂B"

