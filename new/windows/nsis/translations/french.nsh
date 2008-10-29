;;

;;  french.nsh

;;

;;  French language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Version 3

;;  Author: Eric Boumaour <zongo_fr@users.sourceforge.net>, 2003-2005.

;;



; Make sure to update the GAIM_MACRO_LANGUAGEFILE_END macro in

; langmacros.nsh when updating this file



; Startup Checks

!define INSTALLER_IS_RUNNING			"Le programme d'installation est déjà en cours d'exécution."

!define GAIM_IS_RUNNING			"Une instance de Gourmet est en cours d'exécution. Veuillez quitter Gourmet et réessayer."

!define GTK_INSTALLER_NEEDED			"Les bibliothèques de l'environnement GTK+ ne sont pas installées ou ont besoin d'une mise à jour.$\rVeuillez installer la version ${GTK_VERSION} ou plus récente des bibliothèques GTK+."



; License Page

!define GAIM_LICENSE_BUTTON			"Suivant >"

!define GAIM_LICENSE_BOTTOM_TEXT		"$(^Name) est disponible sous licence GNU General Public License (GPL). Le texte de licence suivant est fourni uniquement à titre informatif. $_CLICK" 



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (obligatoire)"

!define GTK_SECTION_TITLE			"Bibliothèques GTK+ (obligatoire)"

!define GTK_THEMES_SECTION_TITLE		"Thèmes GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Pas de thème"

!define GTK_WIMP_SECTION_TITLE		"Thème Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Thème Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Thème Light House Blue"

!define GAIM_SHORTCUTS_SECTION_TITLE "Raccourcis"

!define GAIM_DESKTOP_SHORTCUT_SECTION_TITLE "Bureau"

!define GAIM_STARTMENU_SHORTCUT_SECTION_TITLE "Menu Démarrer"

!define GAIM_SECTION_DESCRIPTION		"Fichiers et DLLs de base de Gourmet"

!define GTK_SECTION_DESCRIPTION		"Un ensemble d'outils pour interfaces graphiques multi-plateforme, utilisé par Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"Les thèmes GTK+ permettent de changer l'aspect des applications GTK+."

!define GTK_NO_THEME_DESC			"Ne pas installer de thème GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (imitateur de Windows) est un thème de GTK+ qui se fond dans l'environnement graphique de Windows."

!define GTK_BLUECURVE_THEME_DESC		"Thème Bluecurve"

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Thème Lighthouseblue"

!define GAIM_SHORTCUTS_SECTION_DESCRIPTION   "Raccourcis pour lancer Gourmet"

!define GAIM_DESKTOP_SHORTCUT_DESC   "Créer un raccourci pour Gourmet sur le bureau"

!define GAIM_STARTMENU_SHORTCUT_DESC   "Créer un raccourci pour Gourmet dans le menu Démarrer"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Une ancienne version des bibliothèques GTK+ a été trouvée. Voulez-vous la mettre à jour ?$\rNote : Gourmet peut ne pas fonctionner si vous ne le faites pas."



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"Visitez la page web de Gourmet Windows"



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (supprimer uniquement)"

!define GAIM_PROMPT_WIPEOUT			"L'ancien dossier de Gourmet va être supprimé. Voulez-vous continuer ?$\r$\rNote : Tous les plugins non standards que vous avez installés seront aussi supprimés.$\rLes configurations et les comptes utilisateurs de Gourmet ne sont pas touchés."

!define GAIM_PROMPT_DIR_EXISTS		"Le dossier d'installation que vous avez choisi existe déjà. Son contenu sera effacé.$\rVoulez-vous continuer ?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Erreur lors de l'installation des bibliothèques GTK+"

!define GTK_BAD_INSTALL_PATH			"Le dossier d'installation ne peut pas être créé ou n'est pas accessible."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Vous n'avez pas les permissions pour installer un thème GTK+."



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1         "Le programme de désinstallation n'a pas retrouvé les entrées de Gourmet dans la base de registres.$\rL'application a peut-être été installée par un utilisateur différent."

!define un.GAIM_UNINSTALL_ERROR_2         "Vous n'avez pas les permissions pour supprimer cette application."

