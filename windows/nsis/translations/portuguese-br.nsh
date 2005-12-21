;;

;;  portuguese-br.nsh

;;

;;  Portuguese (BR) language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Author: Maurício de Lemos Rodrigues Collares Neto <mauricioc@myrealbox.com>, 2003-2005.

;;  Version 3

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"O ambiente de tempo de execução do GTK+ está ausente ou precisa ser atualizado.$\rFavor instalar a versão v${GTK_VERSION} ou superior do ambiente de tempo de execução do GTK+."



; License Page

!define GAIM_LICENSE_BUTTON			"Avançar >"

!define GAIM_LICENSE_BOTTOM_TEXT		"$(^Name) é distribuído sob a licença GPL. Esta licença é disponibilizada aqui apenas para fins informativos. $_CLICK" 



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (requerido)"

!define GTK_SECTION_TITLE			"Ambiente de tempo de execução do GTK+ (requerido)"

!define GTK_THEMES_SECTION_TITLE		"Temas do GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Nenhum tema"

!define GTK_WIMP_SECTION_TITLE		"Tema 'Wimp'"

!define GTK_BLUECURVE_SECTION_TITLE		"Tema 'Bluecurve'"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Tema 'Light House Blue'"
!define GAIM_SHORTCUTS_SECTION_TITLE "Atalhos"
!define GAIM_DESKTOP_SHORTCUT_SECTION_TITLE "Área de Trabalho"
!define GAIM_STARTMENU_SHORTCUT_SECTION_TITLE "Menu Iniciar"

!define GAIM_SECTION_DESCRIPTION		"Arquivos e bibliotecas principais do Gourmet"

!define GTK_SECTION_DESCRIPTION		"Um conjunto de ferramentas multi-plataforma para interface do usuário, usado pelo Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"Os temas do GTK+ podem mudar a aparência e o funcionamento dos aplicativos GTK+."

!define GTK_NO_THEME_DESC			"Não instalar um tema do GTK+"

!define GTK_WIMP_THEME_DESC			"O tema 'GTK-Wimp' ('Windows impersonator', personificador do Windows) é um tema GTK que combina bem com o ambiente de área de trabalho do Windows."

!define GTK_BLUECURVE_THEME_DESC		"O tema 'Bluecurve'."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"O tema 'Lighthouseblue'."
!define GAIM_SHORTCUTS_SECTION_DESCRIPTION   "Atalhos para iniciar o Gourmet"
!define GAIM_DESKTOP_SHORTCUT_DESC   "Crie um atalho para o Gourmet na Área de Trabalho"
!define GAIM_STARTMENU_SHORTCUT_DESC   "Crie uma entrada no Menu Iniciar para o Gourmet"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Uma versão antiga do ambiente de tempo de execução do GTK+ foi encontrada. Você deseja atualizá-lo?$\rNota: O Gourmet poderá não funcionar a menos que você o faça."



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (apenas remover)"

!define GAIM_PROMPT_WIPEOUT			"Sua antiga instalação do Gourmet está prestes a ser removida. Você gostaria de continuar?$\r$\rNota: Quaisquer plugins não-padrão que você pode ter instalado serão removidos.$\rAs configurações de usuário do Gourmet não serão afetadas."

!define GAIM_PROMPT_DIR_EXISTS		"O diretório de instalação do que você especificou já existe. Qualquer conteúdo$\rserá deletado. Deseja continuar?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Erro ao instalar o ambiente de tempo de execução do GTK+."

!define GTK_BAD_INSTALL_PATH			"O caminho que você digitou não pôde ser acessado ou criado."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Você não tem permissão para instalar um tema do GTK+."



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"Visite a página da web do Gourmet para Windows"



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1		"O desinstalador não pôde encontrar entradas de registro do Gourmet.$\rÉ provável que outro usuário tenha instalado esta aplicação."

!define un.GAIM_UNINSTALL_ERROR_2		"Você não tem permissão para desinstalar essa aplicação."

