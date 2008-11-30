;;

;;  spanish.nsh

;;

;;  Spanish language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;  Translator: Javier Fernandez-Sanguino Pea

;;

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"El entorno de ejecucin de GTK+ falta o necesita ser actualizado.$\rPor favor, instale la versin v${GTK_VERSION} del ejecutable GTK+ o alguna posterior."



; License Page

!define GOURMET_LICENSE_BUTTON			"Siguiente >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) se distribuye bajo la licencia GPL. Esta licencia se incluye aqu slo con propsito informativo: $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (necesario)"

!define GTK_SECTION_TITLE			"Entorno de ejecucin de GTK+ (necesario)"

!define GTK_THEMES_SECTION_TITLE		"Temas GTK+" 

!define GTK_NOTHEME_SECTION_TITLE		"Sin tema"

!define GTK_WIMP_SECTION_TITLE		"Tema Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Tema Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Tema Light House Blue"

!define GOURMET_SECTION_DESCRIPTION		"Ficheros y dlls principales de Core"

!define GTK_SECTION_DESCRIPTION		"Una suite de herramientas GUI multiplataforma, utilizada por Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"Los temas pueden cambiar la apariencia de aplicaciones GTK+."

!define GTK_NO_THEME_DESC			"No instalar un tema GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) es un tema GTK que se fusiona muy bien con el entorno de escritorio de Windows."

!define GTK_BLUECURVE_THEME_DESC		"El tema Bluecurve."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"El tema Lighthouseblue."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Se ha encontrado una versin antiga del ejecutable de GTK+. Desea actualizarla?$\rObservacin: Gourmet no funcionar a menos que lo haga."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Visite la pgina Web de Gourmet Windows"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (slo eliminar)"

!define GOURMET_PROMPT_WIPEOUT			"Su directorio antigo de Gourmet va a ser borrado. Desea continuar?$\r$\rObservacin: cualquier aplique no estndar que pudiera haber instalado ser borrado.$\rsto no afectar a sus preferencias de usuario en Gourmet."

!define GOURMET_PROMPT_DIR_EXISTS		"El directorio de instalacin que ha especificado ya existe. Todos los contenidos$\rser borrados. Desea continuar?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Error al instalar el ejecutable GTK+."

!define GTK_BAD_INSTALL_PATH			"No se pudo acceder o crear la ruta que vd. indic."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"No tiene permisos para instalar un tema GTK+."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "El desinstalador no pudo encontrar las entradas en el registro de Gourmet.$\rEs probable que otro usuario instalara la aplicacin."

!define un.GOURMET_UNINSTALL_ERROR_2         "No tiene permisos para desinstalar esta aplicacin."

