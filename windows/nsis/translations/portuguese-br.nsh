;;

;;  portuguese-br.nsh

;;

;;  Portuguese (BR) language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Author: Maurcio de Lemos Rodrigues Collares Neto <mauricioc@myrealbox.com>, 2003-2005.

;;  Version 3

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"O ambiente de tempo de execuo do GTK+ est ausente ou precisa ser atualizado.$\rFavor instalar a verso v${GTK_VERSION} ou superior do ambiente de tempo de execuo do GTK+."



; License Page

!define GOURMET_LICENSE_BUTTON			"Avanar >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name)  distribudo sob a licena GPL. Esta licena  disponibilizada aqui apenas para fins informativos. $_CLICK" 



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (requerido)"

!define GTK_SECTION_TITLE			"Ambiente de tempo de execuo do GTK+ (requerido)"

!define GTK_THEMES_SECTION_TITLE		"Temas do GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Nenhum tema"

!define GTK_WIMP_SECTION_TITLE		"Tema 'Wimp'"

!define GTK_BLUECURVE_SECTION_TITLE		"Tema 'Bluecurve'"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Tema 'Light House Blue'"
!define GOURMET_SHORTCUTS_SECTION_TITLE "Atalhos"
!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "rea de Trabalho"
!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Menu Iniciar"

!define GOURMET_SECTION_DESCRIPTION		"Arquivos e bibliotecas principais do Gourmet"

!define GTK_SECTION_DESCRIPTION		"Um conjunto de ferramentas multi-plataforma para interface do usurio, usado pelo Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"Os temas do GTK+ podem mudar a aparncia e o funcionamento dos aplicativos GTK+."

!define GTK_NO_THEME_DESC			"No instalar um tema do GTK+"

!define GTK_WIMP_THEME_DESC			"O tema 'GTK-Wimp' ('Windows impersonator', personificador do Windows)  um tema GTK que combina bem com o ambiente de rea de trabalho do Windows."

!define GTK_BLUECURVE_THEME_DESC		"O tema 'Bluecurve'."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"O tema 'Lighthouseblue'."
!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Atalhos para iniciar o Gourmet"
!define GOURMET_DESKTOP_SHORTCUT_DESC   "Crie um atalho para o Gourmet na rea de Trabalho"
!define GOURMET_STARTMENU_SHORTCUT_DESC   "Crie uma entrada no Menu Iniciar para o Gourmet"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Uma verso antiga do ambiente de tempo de execuo do GTK+ foi encontrada. Voc deseja atualiz-lo?$\rNota: O Gourmet poder no funcionar a menos que voc o faa."



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (apenas remover)"

!define GOURMET_PROMPT_WIPEOUT			"Sua antiga instalao do Gourmet est prestes a ser removida. Voc gostaria de continuar?$\r$\rNota: Quaisquer plugins no-padro que voc pode ter instalado sero removidos.$\rAs configuraes de usurio do Gourmet no sero afetadas."

!define GOURMET_PROMPT_DIR_EXISTS		"O diretrio de instalao do que voc especificou j existe. Qualquer contedo$\rser deletado. Deseja continuar?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Erro ao instalar o ambiente de tempo de execuo do GTK+."

!define GTK_BAD_INSTALL_PATH			"O caminho que voc digitou no pde ser acessado ou criado."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Voc no tem permisso para instalar um tema do GTK+."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Visite a pgina da web do Gourmet para Windows"



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		"O desinstalador no pde encontrar entradas de registro do Gourmet.$\r provvel que outro usurio tenha instalado esta aplicao."

!define un.GOURMET_UNINSTALL_ERROR_2		"Voc no tem permisso para desinstalar essa aplicao."

