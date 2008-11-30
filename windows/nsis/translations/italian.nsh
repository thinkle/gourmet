;;

;;  italian.nsh

;;

;;  Italian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Author: Claudio Satriano <satriano@na.infn.it>, 2003.

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"L'ambiente di runtime GTK+ non è presente o deve essere aggiornato.$\rInstallare GTK+ versione ${GTK_VERSION} o maggiore"



; License Page

!define GOURMET_LICENSE_BUTTON			"Avanti >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) è distribuito sotto licenza GPL. La licenza è mostrata qui solamente a scopo informativo. $_CLICK" 



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (richiesto)"

!define GTK_SECTION_TITLE			"Ambiente di Runtime GTK+ (richiesto)"

!define GTK_THEMES_SECTION_TITLE		"Temi GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Nessun Tema"

!define GTK_WIMP_SECTION_TITLE		"Tema Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Tema Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Tema Light House Blue"

!define GOURMET_SECTION_DESCRIPTION		"File principali di Gourmet e dll"

!define GTK_SECTION_DESCRIPTION		"Un toolkit multipiattaforma per interfacce grafiche, usato da Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"I temi GTK+ modificano l'aspetto delle applicazioni GTK+."

!define GTK_NO_THEME_DESC			"Non installare nessun tema GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) è un tema GTK che si adatta bene all'aspetto di Windows."

!define GTK_BLUECURVE_THEME_DESC		"Il tema Bluecurve."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Il tema Lighthouseblue."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"È stata trovata una versione precedente di GTK+. Vuoi aggiornarla?$\rNota: Gourmet potrebbe non funzionare senza l'aggiornamento."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Visita la pagina web di Gourmet per Windows"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (solo rimozione)"

!define GOURMET_PROMPT_WIPEOUT			"La tua vecchia directory di Gourmet sta per essere cancellata. Vuoi andare avanti?$\r$\rNota: Tutti i plugin non standard che hai installato saranno cancellati.$\rLe impostazioni di Gourmet non saranno rimosse."

!define GOURMET_PROMPT_DIR_EXISTS		"La directory di installazione specificata esiste già. Tutto il contenuto$\rverrà cancellato. Vuoi continuare?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Errore di installazione di GTK+."

!define GTK_BAD_INSTALL_PATH			"Il percorso scelto non può essere raggiunto o creato."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Non hai il permesso per installare un tema GTK+."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Il programma di rimozione non è in grado di trovare le voci di registro per Gourmet.$\rProbabilmente un altro utente ha installato questa applicazione."

!define un.GOURMET_UNINSTALL_ERROR_2         "Non hai il permesso per rimuovere questa applicazione."

