;;
;;  portuguese.nsh
;;
;;  Portuguese (PT) language strings for the Windows Gourmet NSIS installer.
;;  Windows Code page: 1252
;;
;;  Author: Duarte Henriques <duarte.henriques@gmail.com>, 2003-2005.
;;  Version 3
;;

; Startup Checks
!define INSTALLER_IS_RUNNING			"O instalador já está a ser executado."
!define GOURMET_IS_RUNNING			"Uma instância do Gourmet já está a ser executada. Saia do Gourmet e tente de novo."
!define GTK_INSTALLER_NEEDED			"O ambiente de GTK+ está ausente ou precisa de ser actualizado.$\rPor favor instale a versão v${GTK_VERSION} ou mais recente do ambiente de GTK+."

; License Page
!define GOURMET_LICENSE_BUTTON			"Seguinte >"
!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) está disponível sob a licença GNU General Public License (GPL). O texto da licença é fornecido aqui meramente a título informativo. $_CLICK"

; Components Page
!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (obrigatório)"
!define GTK_SECTION_TITLE			"Ambiente de Execução GTK+ (obrigatório)"
!define GTK_THEMES_SECTION_TITLE		"Temas do GTK+"
!define GTK_NOTHEME_SECTION_TITLE		"Nenhum tema"
!define GTK_WIMP_SECTION_TITLE		"Tema Wimp"
!define GTK_BLUECURVE_SECTION_TITLE		"Tema Bluecurve"
!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Tema Light House Blue"
!define GOURMET_SHORTCUTS_SECTION_TITLE "Atalhos"
!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "Ambiente de Trabalho"
!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Menu de Iniciar"
!define GOURMET_SECTION_DESCRIPTION		"Ficheiros e bibliotecas principais do Gourmet"
!define GTK_SECTION_DESCRIPTION		"Um conjunto de ferramentas de interface gráfica multi-plataforma, usado pelo Gourmet"
!define GTK_THEMES_SECTION_DESCRIPTION	"Os Temas do GTK+ podem mudar a aparência dos programas GTK+."
!define GTK_NO_THEME_DESC			"Não instalar um tema do GTK+"
!define GTK_WIMP_THEME_DESC			"O tema GTK-Wimp (Windows impersonator, personificador do Windows) é um tema GTK+ que combina bem com o ambiente de trabalho do Windows."
!define GTK_BLUECURVE_THEME_DESC		"O tema Bluecurve."
!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"O tema Lighthouseblue."
!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Atalhos para iniciar o Gourmet"
!define GOURMET_DESKTOP_SHORTCUT_DESC   "Criar um atalho para o Gourmet no Ambiente de Trabalho"
!define GOURMET_STARTMENU_SHORTCUT_DESC   "Criar uma entrada para o Gourmet na Barra de Iniciar"

; GTK+ Directory Page
!define GTK_UPGRADE_PROMPT			"Foi encontrada uma versão antiga do ambiente de execução GTK+. Deseja actualizá-lo?$\rNota: O Gourmet poderá não funcionar se não o fizer."

; Installer Finish Page
!define GOURMET_FINISH_VISIT_WEB_SITE		"Visite a Página Web do Gourmet para Windows"

; Gourmet Section Prompts and Texts
!define GOURMET_UNINSTALL_DESC			"Gourmet (remover apenas)"
!define GOURMET_PROMPT_WIPEOUT			"A directoria antiga do Gourmet está prestes a ser removida. Deseja continuar?$\r$\rNota: Quaisquer plugins não-padrão que poderá ter instalado serão removidos.$\rAs configurações de utilizador do Gourmet não serão afectadas."
!define GOURMET_PROMPT_DIR_EXISTS		"A directoria de instalação que especificou já existe. Qualquer conteúdo$\rserá removido. Deseja continuar?"

; GTK+ Section Prompts
!define GTK_INSTALL_ERROR			"Erro ao instalar o ambiente de execução GTK+."
!define GTK_BAD_INSTALL_PATH			"O caminho que digitou não pode ser acedido nem criado."

; GTK+ Themes section
!define GTK_NO_THEME_INSTALL_RIGHTS	"Não tem permissão para instalar um tema do GTK+."

; Uninstall Section Prompts
!define un.GOURMET_UNINSTALL_ERROR_1		"O desinstalador não encontrou entradas de registo do Gourmet.$\rÉ provável que outro utilizador tenha instalado este programa."
!define un.GOURMET_UNINSTALL_ERROR_2		"Não tem permissão para desinstalar este programa."
